import cv2
import mediapipe as mp
import math
import threading

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


# ============================================================
# SETTINGS
# ============================================================

WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 750

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

PINCH_THRESHOLD = 0.055

ROTATION_SENSITIVITY = 250.0

MOVE_SENSITIVITY_X = 4.0
MOVE_SENSITIVITY_Y = 4.0

MIN_SCALE = 0.25
MAX_SCALE = 3.0

SMOOTHING = 0.25


# ============================================================
# GLOBAL STATE
# ============================================================

objects = []

next_object_id = 1

selected_object = None

interaction_mode = "ROTATE"

hand_detected = False

previous_hand_x = None
previous_hand_y = None

grabbed = False

grab_start_hand_x = None
grab_start_hand_y = None

grab_start_object_x = 0.0
grab_start_object_y = 0.0

scaling = False

initial_two_hand_distance = None
initial_object_scale = 1.0

smooth_hand_positions = {}


# ============================================================
# TOOL STATE
# ============================================================

active_tool = "SELECT"

tool_hover = None

tool_panel_visible = True


# ============================================================
# OBJECT CLASS
# ============================================================

class SceneObject:

    def __init__(
        self,
        object_type,
        x=0.0,
        y=0.0,
        z=0.0
    ):

        global next_object_id

        self.id = next_object_id

        next_object_id += 1

        self.type = object_type

        self.x = x
        self.y = y
        self.z = z

        self.rotation_x = 0.0
        self.rotation_y = 0.0
        self.rotation_z = 0.0

        self.scale = 1.0

        self.base_scale = 1.0

    def reset(self):

        self.x = 0.0
        self.y = 0.0
        self.z = 0.0

        self.rotation_x = 0.0
        self.rotation_y = 0.0
        self.rotation_z = 0.0

        self.scale = 1.0


# ============================================================
# ADD INITIAL CUBE
# ============================================================

objects.append(
    SceneObject(
        "cube"
    )
)

selected_object = objects[0]


# ============================================================
# MEDIAPIPE
# ============================================================

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    model_complexity=0,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)


# ============================================================
# UTILITY
# ============================================================

def distance_between_points(p1, p2):

    return math.sqrt(
        (p1[0] - p2[0]) ** 2 +
        (p1[1] - p2[1]) ** 2
    )


def is_pinching(hand_landmarks):

    thumb = hand_landmarks.landmark[4]
    index = hand_landmarks.landmark[8]

    distance = math.sqrt(
        (thumb.x - index.x) ** 2 +
        (thumb.y - index.y) ** 2
    )

    return distance < PINCH_THRESHOLD


def smooth_position(hand_id, x, y):

    if hand_id not in smooth_hand_positions:

        smooth_hand_positions[hand_id] = [
            x,
            y
        ]

    else:

        old_x, old_y = smooth_hand_positions[hand_id]

        new_x = (
            old_x * (1.0 - SMOOTHING)
            + x * SMOOTHING
        )

        new_y = (
            old_y * (1.0 - SMOOTHING)
            + y * SMOOTHING
        )

        smooth_hand_positions[hand_id] = [
            new_x,
            new_y
        ]

    return smooth_hand_positions[hand_id]


# ============================================================
# OBJECT MANAGEMENT
# ============================================================

def add_object(object_type):

    global selected_object

    new_object = SceneObject(
        object_type,
        0.0,
        0.0,
        0.0
    )

    objects.append(
        new_object
    )

    selected_object = new_object

    print(
        f">>> Added {object_type}"
    )


def delete_selected():

    global selected_object

    if selected_object is None:
        return

    if selected_object in objects:

        print(
            f">>> Deleted {selected_object.type}"
        )

        objects.remove(
            selected_object
        )

    if len(objects) > 0:

        selected_object = objects[-1]

    else:

        selected_object = None


def reset_selected():

    if selected_object is None:
        return

    selected_object.reset()

    print(
        f">>> Reset {selected_object.type}"
    )


# ============================================================
# OPENGL INITIALIZATION
# ============================================================

def init_opengl():

    glEnable(
        GL_DEPTH_TEST
    )

    glEnable(
        GL_BLEND
    )

    glBlendFunc(
        GL_SRC_ALPHA,
        GL_ONE_MINUS_SRC_ALPHA
    )

    glClearColor(
        0.035,
        0.035,
        0.055,
        1.0
    )

    glMatrixMode(
        GL_PROJECTION
    )

    glLoadIdentity()

    gluPerspective(
        45.0,
        WINDOW_WIDTH / WINDOW_HEIGHT,
        0.1,
        100.0
    )

    glMatrixMode(
        GL_MODELVIEW
    )


# ============================================================
# DRAW CUBE
# ============================================================

def draw_cube():

    glBegin(
        GL_QUADS
    )

    # FRONT
    glColor3f(
        0.0,
        0.7,
        1.0
    )

    glVertex3f(-1, -1, 1)
    glVertex3f(1, -1, 1)
    glVertex3f(1, 1, 1)
    glVertex3f(-1, 1, 1)

    # BACK
    glColor3f(
        1.0,
        0.2,
        0.2
    )

    glVertex3f(-1, -1, -1)
    glVertex3f(-1, 1, -1)
    glVertex3f(1, 1, -1)
    glVertex3f(1, -1, -1)

    # LEFT
    glColor3f(
        0.2,
        1.0,
        0.3
    )

    glVertex3f(-1, -1, -1)
    glVertex3f(-1, -1, 1)
    glVertex3f(-1, 1, 1)
    glVertex3f(-1, 1, -1)

    # RIGHT
    glColor3f(
        1.0,
        0.8,
        0.0
    )

    glVertex3f(1, -1, -1)
    glVertex3f(1, 1, -1)
    glVertex3f(1, 1, 1)
    glVertex3f(1, -1, 1)

    # TOP
    glColor3f(
        0.7,
        0.2,
        1.0
    )

    glVertex3f(-1, 1, -1)
    glVertex3f(-1, 1, 1)
    glVertex3f(1, 1, 1)
    glVertex3f(1, 1, -1)

    # BOTTOM
    glColor3f(
        0.0,
        1.0,
        0.8
    )

    glVertex3f(-1, -1, -1)
    glVertex3f(1, -1, -1)
    glVertex3f(1, -1, 1)
    glVertex3f(-1, -1, 1)

    glEnd()


# ============================================================
# DRAW SPHERE
# ============================================================

def draw_sphere():

    quadric = gluNewQuadric()

    gluSphere(
        quadric,
        1.0,
        32,
        32
    )

    gluDeleteQuadric(
        quadric
    )


# ============================================================
# DRAW CYLINDER
# ============================================================

def draw_cylinder():

    quadric = gluNewQuadric()

    gluCylinder(
        quadric,
        1.0,
        1.0,
        2.0,
        32,
        16
    )

    gluDeleteQuadric(
        quadric
    )


# ============================================================
# DRAW OBJECT
# ============================================================

def draw_object(obj):

    glPushMatrix()

    glTranslatef(
        obj.x,
        obj.y,
        obj.z
    )

    glRotatef(
        obj.rotation_x,
        1.0,
        0.0,
        0.0
    )

    glRotatef(
        obj.rotation_y,
        0.0,
        1.0,
        0.0
    )

    glRotatef(
        obj.rotation_z,
        0.0,
        0.0,
        1.0
    )

    glScalef(
        obj.scale,
        obj.scale,
        obj.scale
    )

    if obj == selected_object:

        glColor3f(
            0.2,
            1.0,
            0.3
        )

    if obj.type == "cube":

        draw_cube()

    elif obj.type == "sphere":

        glColor3f(
            0.2,
            0.6,
            1.0
        )

        draw_sphere()

    elif obj.type == "cylinder":

        glColor3f(
            1.0,
            0.5,
            0.2
        )

        draw_cylinder()

    glPopMatrix()


# ============================================================
# DRAW GRID
# ============================================================

def draw_grid():

    glBegin(
        GL_LINES
    )

    glColor3f(
        0.15,
        0.15,
        0.18
    )

    grid_size = 10

    for i in range(
        -grid_size,
        grid_size + 1
    ):

        glVertex3f(
            i,
            -2,
            -10
        )

        glVertex3f(
            i,
            -2,
            10
        )

        glVertex3f(
            -10,
            -2,
            i
        )

        glVertex3f(
            10,
            -2,
            i
        )

    glEnd()


# ============================================================
# DISPLAY
# ============================================================

def display():

    glClear(
        GL_COLOR_BUFFER_BIT |
        GL_DEPTH_BUFFER_BIT
    )

    glLoadIdentity()

    # Camera
    glTranslatef(
        0.0,
        0.0,
        -10.0
    )

    # Grid
    draw_grid()

    # Objects
    for obj in objects:

        draw_object(
            obj
        )

    glutSwapBuffers()


# ============================================================
# WINDOW RESIZE
# ============================================================

def reshape(
    width,
    height
):

    if height == 0:

        height = 1

    glViewport(
        0,
        0,
        width,
        height
    )

    glMatrixMode(
        GL_PROJECTION
    )

    glLoadIdentity()

    gluPerspective(
        45.0,
        width / float(height),
        0.1,
        100.0
    )

    glMatrixMode(
        GL_MODELVIEW
    )


# ============================================================
# GRAB
# ============================================================

def start_grab(
    x,
    y
):

    global grabbed

    global grab_start_hand_x
    global grab_start_hand_y

    global grab_start_object_x
    global grab_start_object_y

    if selected_object is None:

        return

    grabbed = True

    grab_start_hand_x = x
    grab_start_hand_y = y

    grab_start_object_x = selected_object.x
    grab_start_object_y = selected_object.y

    print(
        ">>> OBJECT GRABBED"
    )


def update_grab(
    x,
    y
):

    if not grabbed:
        return

    if selected_object is None:
        return

    delta_x = (
        x -
        grab_start_hand_x
    )

    delta_y = (
        y -
        grab_start_hand_y
    )

    selected_object.x = (
        grab_start_object_x
        + delta_x * MOVE_SENSITIVITY_X
    )

    selected_object.y = (
        grab_start_object_y
        - delta_y * MOVE_SENSITIVITY_Y
    )


def release_grab():

    global grabbed

    if grabbed:

        grabbed = False

        print(
            ">>> OBJECT RELEASED"
        )


# ============================================================
# SCALING
# ============================================================

def start_scaling(
    hand1,
    hand2
):

    global scaling

    global initial_two_hand_distance
    global initial_object_scale

    if selected_object is None:

        return

    initial_two_hand_distance = (
        distance_between_points(
            hand1,
            hand2
        )
    )

    initial_object_scale = (
        selected_object.scale
    )

    scaling = True

    print(
        ">>> SCALING STARTED"
    )


def update_scaling(
    hand1,
    hand2
):

    if not scaling:
        return

    if selected_object is None:
        return

    current_distance = (
        distance_between_points(
            hand1,
            hand2
        )
    )

    if (
        initial_two_hand_distance is None
        or initial_two_hand_distance == 0
    ):

        return

    scale_ratio = (
        current_distance /
        initial_two_hand_distance
    )

    new_scale = (
        initial_object_scale *
        scale_ratio
    )

    selected_object.scale = max(
        MIN_SCALE,
        min(
            MAX_SCALE,
            new_scale
        )
    )


def stop_scaling():

    global scaling
    global initial_two_hand_distance

    if scaling:

        scaling = False

        initial_two_hand_distance = None

        print(
            ">>> SCALING FINISHED"
        )


# ============================================================
# ROTATION
# ============================================================

def update_rotation(
    x,
    y
):

    global previous_hand_x
    global previous_hand_y

    if selected_object is None:

        return

    if previous_hand_x is not None:

        delta_x = (
            x -
            previous_hand_x
        )

        delta_y = (
            y -
            previous_hand_y
        )

        selected_object.rotation_y += (
            delta_x *
            ROTATION_SENSITIVITY
        )

        selected_object.rotation_x += (
            delta_y *
            ROTATION_SENSITIVITY
        )

    previous_hand_x = x
    previous_hand_y = y


# ============================================================
# TOOL PANEL
# ============================================================

def draw_tool_panel():

    # This is intentionally kept simple for V2.2.
    #
    # The actual interaction is handled through the camera
    # coordinate system.
    #
    # A future version can replace this with a proper 3D UI.

    pass


# ============================================================
# TOOL SELECTION
# ============================================================

def select_tool(
    tool
):

    global active_tool

    active_tool = tool

    print(
        f">>> TOOL: {tool}"
    )


def handle_tool_action(
    x,
    y
):

    # Camera normalized coordinates
    #
    # Left side of camera = tool area
    #
    # This gives us a foundation for the future
    # floating UI.

    if x < 0.15:

        if y < 0.25:

            select_tool(
                "SELECT"
            )

        elif y < 0.50:

            select_tool(
                "ADD_CUBE"
            )

        elif y < 0.75:

            select_tool(
                "ADD_SPHERE"
            )

        else:

            select_tool(
                "ADD_CYLINDER"
            )


# ============================================================
# HAND PROCESSING
# ============================================================

def process_hand(
    frame
):

    global hand_detected

    global previous_hand_x
    global previous_hand_y

    detected_hands = []

    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    results = hands.process(
        rgb_frame
    )

    if results.multi_hand_landmarks:

        for i, hand_landmarks in enumerate(
            results.multi_hand_landmarks
        ):

            palm = hand_landmarks.landmark[9]

            x = palm.x
            y = palm.y

            x, y = smooth_position(
                i,
                x,
                y
            )

            pinch = is_pinching(
                hand_landmarks
            )

            detected_hands.append({
                "x": x,
                "y": y,
                "pinch": pinch
            })

            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            if pinch:

                cv2.putText(
                    frame,
                    "PINCH",
                    (
                        int(x * CAMERA_WIDTH) - 30,
                        int(y * CAMERA_HEIGHT) - 20
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )

    hand_detected = (
        len(detected_hands) > 0
    )

    # ========================================================
    # TWO HAND SCALING
    # ========================================================

    if len(detected_hands) >= 2:

        hand1 = detected_hands[0]
        hand2 = detected_hands[1]

        if (
            hand1["pinch"]
            and
            hand2["pinch"]
        ):

            release_grab()

            if not scaling:

                start_scaling(
                    (
                        hand1["x"],
                        hand1["y"]
                    ),
                    (
                        hand2["x"],
                        hand2["y"]
                    )
                )

            update_scaling(
                (
                    hand1["x"],
                    hand1["y"]
                ),
                (
                    hand2["x"],
                    hand2["y"]
                )
            )

            previous_hand_x = None
            previous_hand_y = None

            return frame

        else:

            stop_scaling()

    else:

        stop_scaling()

    # ========================================================
    # ONE HAND
    # ========================================================

    if len(detected_hands) == 1:

        hand = detected_hands[0]

        x = hand["x"]
        y = hand["y"]

        pinch = hand["pinch"]

        # ----------------------------------------------------
        # PINCH
        # ----------------------------------------------------

        if pinch:

            if not grabbed:

                # Tool interaction area
                if x < 0.15:

                    handle_tool_action(
                        x,
                        y
                    )

                else:

                    if active_tool == "ADD_CUBE":

                        add_object(
                            "cube"
                        )

                        select_tool(
                            "SELECT"
                        )

                    elif active_tool == "ADD_SPHERE":

                        add_object(
                            "sphere"
                        )

                        select_tool(
                            "SELECT"
                        )

                    elif active_tool == "ADD_CYLINDER":

                        add_object(
                            "cylinder"
                        )

                        select_tool(
                            "SELECT"
                        )

                    elif active_tool == "DELETE":

                        delete_selected()

                        select_tool(
                            "SELECT"
                        )

                    elif active_tool == "RESET":

                        reset_selected()

                        select_tool(
                            "SELECT"
                        )

                    else:

                        start_grab(
                            x,
                            y
                        )

            if grabbed:

                update_grab(
                    x,
                    y
                )

            previous_hand_x = None
            previous_hand_y = None

        # ----------------------------------------------------
        # NO PINCH
        # ----------------------------------------------------

        else:

            if grabbed:

                release_grab()

            if active_tool == "SELECT":

                update_rotation(
                    x,
                    y
                )

    else:

        previous_hand_x = None
        previous_hand_y = None

        if grabbed:

            release_grab()

    return frame


# ============================================================
# CAMERA LOOP
# ============================================================

def camera_loop():

    cap = cv2.VideoCapture(
        0
    )

    cap.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        CAMERA_WIDTH
    )

    cap.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        CAMERA_HEIGHT
    )

    if not cap.isOpened():

        print(
            "ERROR: Could not open camera."
        )

        return

    print()
    print(
        "=============================================="
    )
    print(
        "      HAND CONTROLLED 3D WORKSPACE V2.2"
    )
    print(
        "=============================================="
    )
    print()
    print(
        "CURRENT CONTROLS"
    )
    print()
    print(
        "One hand:"
    )
    print(
        "  Move              -> Rotate selected object"
    )
    print(
        "  Pinch + move      -> Grab / move object"
    )
    print(
        "  Release           -> Place object"
    )
    print()
    print(
        "Two hands:"
    )
    print(
        "  Pinch both        -> Scale"
    )
    print(
        "  Move apart        -> Bigger"
    )
    print(
        "  Move together     -> Smaller"
    )
    print()
    print(
        "OBJECTS:"
    )
    print(
        "  Cube"
    )
    print(
        "  Sphere"
    )
    print(
        "  Cylinder"
    )
    print()
    print(
        "Press Q to quit."
    )
    print()

    while True:

        success, frame = cap.read()

        if not success:

            print(
                "ERROR: Camera frame failed."
            )

            break

        frame = cv2.flip(
            frame,
            1
        )

        frame = process_hand(
            frame
        )

        # ====================================================
        # STATUS
        # ====================================================

        if scaling:

            status = "SCALING"

        elif grabbed:

            status = "GRABBED"

        elif hand_detected:

            status = "ROTATING"

        else:

            status = "NO HAND"

        cv2.putText(
            frame,
            status,
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        if selected_object:

            selected_text = (
                f"Selected: "
                f"{selected_object.type}"
            )

            cv2.putText(
                frame,
                selected_text,
                (20, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"Scale: "
                f"{selected_object.scale:.2f}x",
                (20, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

        cv2.putText(
            frame,
            f"Tool: {active_tool}",
            (20, 130),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        cv2.imshow(
            "Hand Tracking - V2.2",
            frame
        )

        key = (
            cv2.waitKey(1)
            & 0xFF
        )

        if key == ord("q"):

            break

    cap.release()

    cv2.destroyAllWindows()

    glutLeaveMainLoop()


# ============================================================
# OPENGL IDLE
# ============================================================

def idle():

    glutPostRedisplay()


# ============================================================
# MAIN
# ============================================================

def main():

    glutInit()

    glutInitDisplayMode(
        GLUT_DOUBLE |
        GLUT_RGB |
        GLUT_DEPTH
    )

    glutInitWindowSize(
        WINDOW_WIDTH,
        WINDOW_HEIGHT
    )

    glutCreateWindow(
        b"Hand Controlled 3D Workspace V2.2"
    )

    init_opengl()

    glutDisplayFunc(
        display
    )

    glutReshapeFunc(
        reshape
    )

    glutIdleFunc(
        idle
    )

    camera_thread = threading.Thread(
        target=camera_loop,
        daemon=True
    )

    camera_thread.start()

    glutMainLoop()


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    main()