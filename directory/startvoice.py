import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import threading
import speech_recognition as sr
from tkinter import Tk, Button

pyautogui.FAILSAFE = False
eye_tracking_active = False

def start_eye_tracking():
    global eye_tracking_active
    eye_tracking_active = True

    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("Error: Could not open video capture.")
        return

    face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
    screen_w, screen_h = pyautogui.size()
    pyautogui.moveTo(screen_w // 2, screen_h // 2)
    prev_x, prev_y = 0, 0

    while eye_tracking_active:
        ret, frame = cam.read()
        if not ret:
            print("Error: No frame captured from the camera.")
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output = face_mesh.process(rgb_frame)
        landmark_points = output.multi_face_landmarks
        frame_h, frame_w, _ = frame.shape

        if landmark_points:
            landmarks = landmark_points[0].landmark
            nose_tip = landmarks[1]  # Adjust the index if necessary
            x, y = int(nose_tip.x * frame_w), int(nose_tip.y * frame_h)
            distance = np.sqrt((x - prev_x) ** 2 + (y - prev_y) ** 2)

            movement_factor = 2 if distance < 3 else 5 if distance < 10 else 20

            mouse_x, mouse_y = pyautogui.position()
            dx, dy = (x - prev_x) * movement_factor, (y - prev_y) * movement_factor
            prev_x, prev_y = x, y
            new_x, new_y = max(1, min(screen_w - 1, mouse_x + dx)), max(1, min(screen_h - 1, mouse_y + dy))
            pyautogui.moveTo(new_x, new_y)

        cv2.imshow('Eye Controlled Mouse', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

def toggle_eye_tracking():
    global eye_tracking_active
    if eye_tracking_active:
        eye_tracking_active = False
    else:
        threading.Thread(target=start_eye_tracking, daemon=True).start()

def listen_in_background():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.2)  # Briefly adjust for ambient noise
        while True:
            try:
                print("Listening...")
                audio = r.listen(source, timeout=1, phrase_time_limit=2)
                text = r.recognize_google(audio)
                print(f"Recognized: {text}")

                if "start" in text.lower():
                    toggle_eye_tracking()
                elif "click" in text.lower():
                    pyautogui.click()
                    print("Mouse clicked.")

            except sr.WaitTimeoutError:
                pass  # Ignore timeout errors
            except sr.UnknownValueError:
                pass  # Ignore unrecognized speech
            except sr.RequestError as e:
                print(f"Could not request results; {e}")

def create_gui():
    root = Tk()
    root.title("Control Center")

    btn = Button(root, text="Toggle Eye Tracking", command=toggle_eye_tracking)
    btn.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    threading.Thread(target=listen_in_background, daemon=True).start()
    create_gui()
