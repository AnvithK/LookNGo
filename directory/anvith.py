import cv2
import difflib
import mediapipe as mp
import pyautogui
import numpy as np
import threading
import speech_recognition as sr
from tkinter import Tk, Button, Canvas
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

    while eye_tracking_active and app_running:  # Check global running state
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
                pyautogui.scroll(-int(dy))  # Negative dy for natural scroll direction
            else:
                pyautogui.moveTo(new_x, new_y)

        cv2.imshow('Eye Controlled Mouse', frame)
        cv2.waitKey(1)  # Updated to just a simple waitKey call without 'q' check

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
                audio = r.listen(source, timeout=1, phrase_time_limit=2)  # Short phrase for commands
                text = r.recognize_google(audio).lower()
                print(f"Recognized: {text}")

                # Define the main commands including 'type'
                commands = ["click", "right click", "start", "stop", "scroll on", "scroll off", "type", "enter"]

                # Find the closest match to the recognized text within the list of commands
                closest_match = difflib.get_close_matches(text, commands, n=1, cutoff=0.6)
                if closest_match:
                    command = closest_match[0]
                    print(f"Interpreted command: {command}")

                    if command == "type":
                        print("Say what you want to type:")
                        audio = r.listen(source,phrase_time_limit=10)  # Listen without timeout for the phrase to type
                        typing_phrase = r.recognize_google(audio).lower()
                        print(f"Typing out: {typing_phrase}")
                        pyautogui.typewrite(typing_phrase)  # Type out the phrase without pressing Enter
                    elif command == "enter":
                        pyautogui.press('enter')  # Simulate pressing the Enter key
                        print("Enter key pressed.")
                    elif command == "start":
                        toggle_eye_tracking()
                    elif command == "click":
                        pyautogui.click()
                        print("Mouse clicked.")
                    elif command == "right click":
                        pyautogui.rightClick()
                        print("Right mouse clicked.")
                    elif command == "scroll on":
                        scroll_mode = True
                        print("Scroll mode activated.")
                    elif command == "scroll off":
                        scroll_mode = False
                        print("Scroll mode deactivated.")
                    elif command == "stop":
                        stop_application()

            except sr.WaitTimeoutError:
                pass  # Ignore timeout errors for the initial command listening
            except sr.UnknownValueError:
                print("Did not understand. Please repeat.")
            except sr.RequestError as e:
                print(f"Could not request results; {e}")


def stop_application():
    global app_running, eye_tracking_active, scroll_mode
    app_running = False
    eye_tracking_active = False
    scroll_mode = False
    cv2.destroyAllWindows()

    # Terminate the main application loop if running in a GUI thread
    try:
        root.destroy()  # Assuming 'root' is your Tkinter root window
    except:
        pass


def toggle_eye_tracking():
    global eye_tracking_active
    if not eye_tracking_active:
        threading.Thread(target=start_eye_tracking, daemon=True).start()
    else:
        eye_tracking_active = False
def on_click():
    toggle_eye_tracking()
def create_rounded_button(canvas, text, command, x, y, width, height, radius, color):
    # Draw rounded rectangle
    # canvas.create_rectangle(x + radius, y, x + width - radius, y + height, fill=color, outline=color)
    # canvas.create_rectangle(x, y + radius, x + width, y + height - radius, fill=color, outline=color)
    # canvas.create_arc(x, y, x + 2 * radius, y + 2 * radius, start=90, extent=90, fill=color, outline=color)
    # canvas.create_arc(x + width - 2 * radius, y, x + width, y + 2 * radius, start=0, extent=90, fill=color, outline=color)
    # canvas.create_arc(x, y + height - 2 * radius, x + 2 * radius, y + height, start=180, extent=90, fill=color, outline=color)
    # canvas.create_arc(x + width - 2 * radius, y + height - 2 * radius, x + width, y + height, start=270, extent=90, fill=color, outline=color)
    
    # Button with transparent background placed over the shape
    button = Button(canvas, text=text, command=command, bg=color, activebackground=color, bd=0, highlightthickness=0, relief="flat", font=("Helvetica", 36))
    button_window = canvas.create_window(x + width / 2, y + height / 2, anchor="w", window=button)
    
    return button

def main():
    # Create the main window
    root = Tk()
    root.title("Look 'N Go")

    # Set the size of the window to the size of the image
    width = 768
    height = 768
    root.geometry(f'{width}x{height}')

    # Load and set the background image
    image_path = './background_image.png'  # Replace with your image path
    image = Image.open(image_path)
    new_image = image.resize((width, height))
    background_image = ImageTk.PhotoImage(new_image)

    # Create a canvas and add the image to it
    canvas = Canvas(root, width=width, height=height)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=background_image, anchor="nw")

    # Create a button with an image background and text overlay
    button_image_path = './result.png'  # Replace with the path to your button image
    button_image = Image.open(button_image_path)
    button_image = button_image.resize((125, 75))  # Resize if necessary
    button_photo = ImageTk.PhotoImage(button_image)
    
    # Replace your button creation code with this
    rounded_button = create_rounded_button(canvas, "Start", on_click, width/2, height/2, 225, 100, 20, '#ffffff')

    #button = Button(canvas, image=button_photo, text="Click Me", compound="center", command=on_click)#, borderwidth=0, padx=0,pady=0)
    button_window = canvas.create_window(width* 0.4, height * 0.45, anchor="nw", window=rounded_button)
    # Keep a reference to the image to prevent garbage-collection
    #button.image = button_photo

    # Start the background threads for eye tracking and speech recognition
    threading.Thread(target=listen_in_background, daemon=True).start()
    
    # This ensures the GUI thread also stops when the application is meant to stop
    def on_closing():
        global app_running
        app_running = False
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Start the GUI event loop
    root.mainloop()

def create_gui():
    root = Tk()
    root.title("Control Center")

    btn = Button(root, text="Toggle Eye Tracking", command=toggle_eye_tracking)
    btn.pack(pady=20)

    # This ensures the GUI thread also stops when the application is meant to stop
    while app_running:
        root.update_idletasks()
        root.update()

if __name__ == "__main__":
    #threading.Thread(target=listen_in_background, daemon=True).start()
    main()
