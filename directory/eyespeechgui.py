import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import speech_recognition as sr
import threading
from tkinter import Tk, Button

pyautogui.FAILSAFE = False

def mouse_control():
    try:
        cam = cv2.VideoCapture(0)

        if not cam.isOpened():
            print("Error: Could not open video capture.")
            return

        face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
        screen_w, screen_h = pyautogui.size()
        pyautogui.moveTo(screen_w // 2, screen_h // 2)
        prev_x, prev_y = 0, 0

        while True:
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
                nose_tip = landmarks[1]
                x, y = int(nose_tip.x * frame_w), int(nose_tip.y * frame_h)
                distance = np.sqrt((x - prev_x) ** 2 + (y - prev_y) ** 2)

                if distance < 3:
                    movement_factor = 2
                elif distance < 10:
                    movement_factor = 5
                else:
                    movement_factor = 20

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
    except Exception as e:
        print(f"An error occurred: {e}")
        cam.release()
        cv2.destroyAllWindows()

def trigger_click(text):
    print(text)
    if "click" in text.lower():
        pyautogui.click()
        print("Mouse clicked.")

def listen_for_click():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        print("Listening for 'click'...")
        while True:
            try:
                audio = r.listen(source)
                text = r.recognize_google(audio)
                trigger_click(text)
            except sr.UnknownValueError:
                pass
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")

def on_click():
    threading.Thread(target=mouse_control, daemon=True).start()
    threading.Thread(target=listen_for_click, daemon=True).start()

def create_gui():
    root = Tk()
    root.title("Control Center")

    btn = Button(root, text="Start", command=on_click)
    btn.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
