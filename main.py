import cv2
import mediapipe as mp
import pyautogui
import tkinter as tk

# Initialize camera and libraries

pyautogui.FAILSAFE = False
cam = cv2.VideoCapture(0)
if not cam.isOpened():
    print("Error: Could not open camera.")
    exit()

face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
screen_w, screen_h = pyautogui.size()

oldX, oldY = 0, 0

while True:
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
        # Using iris landmarks for tracking eye movements
        right_iris_landmarks = landmarks[474:478]
        left_iris_landmarks = landmarks[469:473]

        # Get the average x and y positions of the iris for more stable tracking
        def get_avg_position(landmarks_subset):
            x_avg = sum([landmark.x for landmark in landmarks_subset]) / len(landmarks_subset)
            y_avg = sum([landmark.y for landmark in landmarks_subset]) / len(landmarks_subset)
            return x_avg, y_avg

        right_iris_avg_x, right_iris_avg_y = get_avg_position(right_iris_landmarks)
        left_iris_avg_x, left_iris_avg_y = get_avg_position(left_iris_landmarks)

        # Convert relative positions to frame dimensions
        right_iris_x = int(right_iris_avg_x * frame_w)
        right_iris_y = int(right_iris_avg_y * frame_h)
        left_iris_x = int(left_iris_avg_x * frame_w)
        left_iris_y = int(left_iris_avg_y * frame_h)

        # Calculate the average of both eyes for more stable control
        avg_eye_x = (right_iris_avg_x + left_iris_avg_x) / 2
        avg_eye_y = (right_iris_avg_y + left_iris_avg_y) / 2

        # Map eye movement to screen dimensions
        screen_x = int(avg_eye_x * screen_w)
        screen_y = int(avg_eye_y * screen_h)

        relX = screen_x - oldX
        relY = screen_y - oldY

        # Draw landmarks on the frame
        for iris_landmark in right_iris_landmarks + left_iris_landmarks:
            x = int(iris_landmark.x * frame_w)
            y = int(iris_landmark.y * frame_h)
            cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)

        # Blink detection using vertical distance between eyelids
        left_upper_eyelid = landmarks[159]  # Upper eyelid point
        left_lower_eyelid = landmarks[145]  # Lower eyelid point
        right_upper_eyelid = landmarks[386]  # Upper eyelid point right
        right_lower_eyelid = landmarks[374]  # Lower eyelid point right

        left_eye_dist = abs(left_upper_eyelid.y - left_lower_eyelid.y)
        right_eye_dist = abs(right_upper_eyelid.y - right_lower_eyelid.y)
        if left_eye_dist < 0.01:  # Adjust threshold based on calibration
            pyautogui.click()
            pyautogui.sleep(1)
        elif right_eye_dist < 0.01:  # Adjust threshold based on calibration
            pyautogui.scroll(relY)
            pyautogui.sleep(2)
        else:
            # Move mouse based on eye movements
            pyautogui.moveRel(relX*8, relY*8, duration=0.01)

        oldX = screen_x
        oldY = screen_y

    # cv2.imshow("Eye Controlled Mouse", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()
