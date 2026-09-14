# Computer Vision Controlled Simulation System v2.1

A real-time **hand-gesture-controlled 3D simulation system** built using **Python, OpenCV, MediaPipe, and OpenGL**.

The project uses a webcam to detect and track the user's hands and converts hand movements and gestures into controls for interacting with 3D objects inside an OpenGL environment.

Instead of using a mouse or keyboard for every interaction, the user can manipulate virtual objects using natural hand gestures such as movement and pinching.

---

## 🚀 Features

* ✋ Real-time hand tracking using **MediaPipe Hands**
* 📷 Webcam input using **OpenCV**
* 🎮 Interactive 3D environment using **PyOpenGL**
* 🔄 Rotate 3D objects using hand movement
* 🤏 Pinch gesture detection
* 🫳 Grab and move objects using pinch gestures
* 📏 Two-hand scaling of objects
* 🧊 Multiple 3D object types

  * Cube
  * Sphere
  * Cylinder
* 🎯 Object selection system
* 🧰 Interactive tool system
* 🖐️ Supports tracking up to **two hands**
* 📉 Hand-position smoothing for more stable controls
* 🗺️ 3D grid environment
* 🔍 Configurable movement, rotation, pinch and scaling sensitivity
* ⚡ Real-time computer vision and rendering

---

## 🧠 How It Works

The system combines a computer-vision pipeline with a real-time OpenGL rendering loop.

```text
Webcam
   │
   ▼
OpenCV
   │
   ▼
MediaPipe Hands
   │
   ▼
Hand Landmark Detection
   │
   ├── Hand Position
   ├── Pinch Detection
   ├── Hand Movement
   └── Two-Hand Distance
   │
   ▼
Gesture Processing
   │
   ▼
3D Object Transformations
   │
   ├── Translation
   ├── Rotation
   └── Scaling
   │
   ▼
PyOpenGL / GLUT
   │
   ▼
Real-Time 3D Simulation
```

MediaPipe detects landmarks on each visible hand. The program then extracts information such as palm position and the distance between the thumb and index finger.

These values are converted into transformations applied to objects in the OpenGL scene.

---

# 🤏 Gesture Controls

## Hand Movement

The position of the hand in the camera frame is tracked continuously.

Depending on the current interaction mode, movement can be used to manipulate the selected object.

---

## Pinch

A pinch is detected when the distance between the:

```text
Thumb Tip  → Landmark 4
Index Tip  → Landmark 8
```

drops below a predefined threshold.

```text
Thumb       Index

   \         /
    \       /
     ●-----●
      PINCH
```

The pinch gesture can be used for interactions such as grabbing an object.

---

## Grab & Move

Pinch while interacting with an object to grab it.

Moving your hand while the object is grabbed changes the object's position inside the 3D scene.

Releasing the pinch releases the object.

---

## Two-Hand Scaling

The application can track up to two hands simultaneously.

The distance between both detected hands is used to calculate the scale of the selected object.

```text
Hands closer together
        ↓
   Smaller object


Hands farther apart
        ↓
    Larger object
```

Object scaling is limited to prevent extremely large or extremely small values.

---

# 🎮 3D Simulation

Each scene object stores its own transformation information:

```text
Position
├── X
├── Y
└── Z

Rotation
├── X
├── Y
└── Z

Scale
└── Uniform Scale
```

The simulation currently supports:

### 🧊 Cube

A colored OpenGL cube constructed using quadrilateral faces.

### 🔵 Sphere

Generated using an OpenGL quadric sphere.

### 🟠 Cylinder

Generated using an OpenGL quadric cylinder.

---

# 🛠️ Tech Stack

| Technology  | Purpose                             |
| ----------- | ----------------------------------- |
| Python      | Main programming language           |
| OpenCV      | Webcam capture and image processing |
| MediaPipe   | Real-time hand landmark detection   |
| PyOpenGL    | 3D rendering                        |
| OpenGL GLU  | 3D utility functions                |
| OpenGL GLUT | Window creation and render loop     |
| Math        | Gesture-distance calculations       |
| Threading   | Concurrent processing               |

---

# 📦 Requirements

You need:

* Python 3.x
* A webcam
* OpenGL-capable GPU
* Windows / Linux / macOS
* Required Python packages

Install the main dependencies using:

```bash
pip install opencv-python mediapipe PyOpenGL PyOpenGL_accelerate
```

If `PyOpenGL_accelerate` fails to install, the program can generally still run with:

```bash
pip install PyOpenGL
```

---

# 📥 Installation

Clone the repository:

```bash
git clone https://github.com/maharsh1580/Computer-Vision-Controlled-Simulation-System-v2.1.git
```

Enter the project directory:

```bash
cd Computer-Vision-Controlled-Simulation-System-v2.1
```

Install the dependencies:

```bash
pip install opencv-python mediapipe PyOpenGL PyOpenGL_accelerate
```

Then run:

```bash
python main3.py
```

Make sure your webcam is connected and accessible by Python.

---

# 📁 Project Structure

```text
Computer-Vision-Controlled-Simulation-System-v2.1/
│
├── main3.py
│   ├── OpenCV camera processing
│   ├── MediaPipe hand tracking
│   ├── Gesture detection
│   ├── Object transformation logic
│   ├── OpenGL rendering
│   ├── Object management
│   └── Interaction system
│
└── README.md
```

---

# ⚙️ Configuration

Several parameters can be adjusted inside `main3.py`.

Examples include:

```python
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
```

These values control how responsive the system feels.

For example:

* `PINCH_THRESHOLD` controls how close the thumb and index finger must be for a pinch.
* `ROTATION_SENSITIVITY` controls how strongly hand motion affects rotation.
* `MOVE_SENSITIVITY_X` and `MOVE_SENSITIVITY_Y` control object movement speed.
* `MIN_SCALE` and `MAX_SCALE` restrict object size.
* `SMOOTHING` reduces jitter from hand tracking.

---

# 🧠 Hand Tracking

The project uses **MediaPipe Hands** with support for up to two simultaneously detected hands.

The detected landmarks are used to determine:

* Palm position
* Thumb position
* Index-finger position
* Pinch state
* Hand movement
* Distance between hands

The system also applies position smoothing to reduce tracking jitter and provide more natural object manipulation.

---

# 🎯 Project Goal

The goal of this project is to explore **Natural User Interfaces (NUI)** where users interact with virtual environments without traditional input devices.

The same concepts can potentially be extended to areas such as:

* Robotics control
* AR/VR interaction
* CAD interfaces
* 3D modelling
* Virtual simulations
* Computer-vision interfaces
* Gesture-controlled applications
* Human-Computer Interaction research

---

# 🔮 Possible Future Improvements

Future versions could include:

* [ ] More 3D primitives
* [ ] Custom 3D model loading
* [ ] Improved gesture recognition
* [ ] Object collision detection
* [ ] Object physics
* [ ] Better depth/Z-axis control
* [ ] Gesture-based object creation
* [ ] Gesture-based object deletion
* [ ] Improved graphical toolbar
* [ ] Lighting and shadows
* [ ] Textures and materials
* [ ] Scene saving/loading
* [ ] Undo/redo system
* [ ] Improved object selection
* [ ] Robot simulation integration
* [ ] AR integration
* [ ] OpenXR / VR support

---

# 🧪 Version

## v2.1

This version expands the original computer-vision-controlled simulation concept with more advanced object interaction and scene-management capabilities.

Key concepts include:

```text
Hand Tracking
      +
Gesture Recognition
      +
Computer Vision
      +
3D Graphics
      =
Natural 3D Interaction
```

---

# 👨‍💻 Author

**Maharsh Badheka**

GitHub: [@maharsh1580](https://github.com/maharsh1580)

---

## ⭐ Support

If you found the project interesting, consider giving the repository a ⭐.

Contributions, experiments and improvements are welcome.
