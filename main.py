import cv2
import mediapipe as mp
import pyautogui
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import BooleanVar
import threading

# Initialize camera and libraries
pyautogui.FAILSAFE = False
global cam, running, counter

def eye_tracking():
    global cam, running
    cam = cv2.VideoCapture(0)

    if not cam.isOpened():
        print("Error: Could not open camera.")
        return

    face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
    screen_w, screen_h = pyautogui.size()

    # ALIGN TO CENTER WHEN SPAWN
    center_x = screen_w // 2
    center_y = screen_h // 2
    pyautogui.moveTo(center_x, center_y)  # Move cursor to center at the start

    oldX, oldY = center_x, center_y  # Set initial position to center

    while running:  # Check the running flag
        ret, frame = cam.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output = face_mesh.process(rgb_frame)

        # Check if landmarks are detected
        landmark_points = output.multi_face_landmarks
        frame_h, frame_w, _ = frame.shape

        if landmark_points:
            landmarks = landmark_points[0].landmark
            right_iris_landmarks = landmarks[474:478]
            left_iris_landmarks = landmarks[469:473]

            # Get the average x and y positions of the iris for more stable tracking
            def get_avg_position(landmarks_subset):
                x_avg = sum([landmark.x for landmark in landmarks_subset]) / len(landmarks_subset)
                y_avg = sum([landmark.y for landmark in landmarks_subset]) / len(landmarks_subset)
                return x_avg, y_avg

            right_iris_avg_x, right_iris_avg_y = get_avg_position(right_iris_landmarks)
            left_iris_avg_x, left_iris_avg_y = get_avg_position(left_iris_landmarks)

            right_iris_x = int(right_iris_avg_x * frame_w)
            right_iris_y = int(right_iris_avg_y * frame_h)
            left_iris_x = int(left_iris_avg_x * frame_w)
            left_iris_y = int(left_iris_avg_y * frame_h)

            avg_eye_x = (right_iris_avg_x + left_iris_avg_x) / 2
            avg_eye_y = (right_iris_avg_y + left_iris_avg_y) / 2

            screen_x = int(avg_eye_x * screen_w)
            screen_y = int(avg_eye_y * screen_h)

            relX = screen_x - oldX
            relY = screen_y - oldY

            left_upper_eyelid = landmarks[159]  
            left_lower_eyelid = landmarks[145]  
            right_upper_eyelid = landmarks[386]  
            right_lower_eyelid = landmarks[374]  

            left_eye_dist = abs(left_upper_eyelid.y - left_lower_eyelid.y)
            right_eye_dist = abs(right_upper_eyelid.y - right_lower_eyelid.y)
            if left_eye_dist < 0.01:  
                pyautogui.click()
                pyautogui.sleep(1)
            elif right_eye_dist < 0.01:  
                pyautogui.scroll(relY)
            else:
                pyautogui.moveRel(relX * 8, relY * 8, duration=0.01)

            oldX = screen_x
            oldY = screen_y

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()  # Ensure camera is released when done
    cv2.destroyAllWindows()  # Close all OpenCV windows

def toggle_eye_tracker(state):
    global running, counter
    if state.get():
        print("Glance Guide: ON")

        running = True  # Set the running flag to True
        threading.Thread(target=eye_tracking, daemon=True).start()  # Start eye tracking in a separate thread
        
        counter += 1  # Increment the counter when tracking starts
    else:
        print("Glance Guide: OFF")
        running = False  # Set the running flag to False

def create_ui():
    # Create a ttkbootstrap themed window
    root = ttk.Window(themename="darkly")  # You can change the theme

    # Set window title and size
    root.title("Control Panel")
    root.geometry("400x330")
    root.resizable(width=False, height=False)

    # Create a label
    label = ttk.Label(root, text="Glance Guide 1.0", font=("Helvetica", 18))
    label.pack(pady=20)

    # Create a variable to track the state of the "switch"
    switch_state = BooleanVar(value=False)

    # Create a toggle-like switch using a Checkbutton
    toggle_switch = ttk.Checkbutton(
        root,
        text="On/Off",
        bootstyle="success-round-toggle",
        variable=switch_state,
        command=lambda: toggle_eye_tracker(switch_state),
        padding=(10, 5)  # Adding padding for spacing
    )
    toggle_switch.pack(pady=30)

    # Create a label for function explanations with left alignment, fixed width
    function_explanation = (
        "Instructions:\n\n"
        "- Move the cursor with head and eye movement.\n\n"
        "- Single click with left eye blink.\n\n"
        "- Scroll up with right eye closed and head movement vertically down, and vice versa."
    )
    
    explanation_label = ttk.Label(
        root,
        text=function_explanation,
        justify='left',
        anchor='w',
        wraplength=350,  # Set wrap length for the label
        width=45  # Fixed width (characters)
    )
    explanation_label.pack(pady=15, padx=20)

    # Start the main event loop
    root.mainloop()

if __name__ == "__main__":
    running = False  # Initialize running flag
    counter = 0  # Initialize counter

    create_ui()