# Glance Guide

**Glance Guide** is an eye-tracking application that allows users to control their computer cursor with head and eye movements. This project uses the OpenCV and MediaPipe libraries for real-time face mesh tracking, along with the `pyautogui` library for cursor control. It features a user-friendly interface built with `ttkbootstrap`.

## Features

- Move the cursor with head and eye movements.
- Single click with a left eye blink.
- Scroll vertically by closing the right eye and moving the head up or down.

## Requirements

To run this project, you need to have the following installed:

- Python 3.x
- Libraries:
  - OpenCV
  - MediaPipe
  - PyAutoGUI
  - Ttkbootstrap

You can install the required libraries using pip:

```bash
pip install opencv-python mediapipe pyautogui ttkbootstrap
