import cv2
import difflib
import mediapipe as mp
import pyautogui
import numpy as np
import threading
import speech_recognition as sr
from tkinter import Tk, Canvas, Button
from PIL import Image, ImageTk

pyautogui.FAILSAFE = False
eye_tracking_active = False
scroll_mode = False  # Track whether scroll mode is active
app_running = True  # Global variable to control the application running state

def start_eye_tracking():
    global eye_tracking_active, scroll_mode
    eye_tracking_active = True

    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("Error: Could not open video capture.")
        return

    face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
    screen_w, screen_h = pyautogui.size()
    pyautogui.moveTo(screen_w // 2, screen_h // 2)
    prev_x, prev_y = 0, 0

    while eye_tracking_active and app_running:
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

            if scroll_mode:
                pyautogui.scroll(-int(dy))
            else:
                pyautogui.moveTo(new_x, new_y)

        cv2.imshow('Eye Controlled Mouse', frame)
        cv2.waitKey(1)

    cam.release()
    cv2.destroyAllWindows()

def listen_in_background():
    global app_running, scroll_mode
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.2)
        while app_running:
            try:
                print("Listening for commands...")
                audio = r.listen(source, timeout=1, phrase_time_limit=2)
                text = r.recognize_google(audio).lower()
                print(f"Recognized: {text}")

                commands = ["click", "right click", "start", "stop", "scroll on", "scroll off", "type", "enter"]
                closest_match = difflib.get_close_matches(text, commands, n=1, cutoff=0.6)

                if closest_match:
                    command = closest_match[0]
                    print(f"Interpreted command: {command}")

                    if command == "type":
                        print("Say what you want to type:")
                        audio = r.listen(source)
                        typing_phrase = r.recognize_google(audio).lower()
                        print(f"Typing out: {typing_phrase}")
                        pyautogui.typewrite(typing_phrase)
                    elif command == "enter":
                        pyautogui.press('enter')
                    elif command == "start":
                        toggle_eye_tracking()
                    elif command == "click":
                        pyautogui.click()
                    elif command == "right click":
                        pyautogui.rightClick()
                    elif command == "scroll on":
                        scroll_mode = True
                    elif command == "scroll off":
                        scroll_mode = False
                    elif command == "stop":
                        stop_application()

            except sr.WaitTimeoutError:
                pass
            except sr.UnknownValueError:
                print("Did not understand. Please repeat.")
            except sr.RequestError as e:
                print(f"Could not request results; {e}")

def toggle_eye_tracking():
    global eye_tracking_active
    if not eye_tracking_active:
        threading.Thread(target=start_eye_tracking, daemon=True).start()
    else:
        eye_tracking_active = False

def create_rounded_button(canvas, text, command, x, y, width, height, radius, color):
    button = Button(canvas, text=text, command=command, bg=color, activebackground=color, bd=0, highlightthickness=0, relief="flat")
    button_window = canvas.create_window(x + width / 2, y + height / 2, anchor="center", window=button)
    return button

def main():
    global app_running
    root = Tk()
    root.title("Look 'N Go")

    width = 768
    height = 768
    root.geometry(f'{width}x{height}')

    image_path = './background_image.png'
    image = Image.open(image_path)
    new_image = image.resize((width, height))
    background_image = ImageTk.PhotoImage(new_image)

    canvas = Canvas(root, width=width, height=height)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=background_image, anchor="nw")

    rounded_button = create_rounded_button(canvas, "Start", toggle_eye_tracking, width/2 - 112.5, height/2 - 50, 225, 100, 20, '#ab23ff')

    def on_closing():
        global app_running
        app_running = False
        eye_tracking_active = False
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    threading.Thread(target=listen_in_background, daemon=True).start()

    root.mainloop()

if __name__ == "__main__":
    main()
