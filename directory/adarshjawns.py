import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import speech_recognition as sr
pyautogui.FAILSAFE = False

def recognize_speech_from_mic(recognizer, microphone):
    # Check that recognizer and microphone arguments are appropriate type
    if not isinstance(recognizer, sr.Recognizer) or not isinstance(microphone, sr.Microphone):
        raise TypeError("recognizer must be Recognizer instance and microphone must be Microphone instance")

    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    # Set up the response object
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    try:
        response["transcription"] = recognizer.recognize_google(audio)
    except sr.RequestError:
        # API was unreachable or unresponsive
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        # Speech was unintelligible
        response["error"] = "Unable to recognize speech"

    return response

try:
    cam = cv2.VideoCapture(0)
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    # Check if the camera opened successfully
    if not cam.isOpened():
        print("Error: Could not open video capture.")
        exit()

    face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
    screen_w, screen_h = pyautogui.size()
    pyautogui.moveTo(screen_w // 2, screen_h // 2)
    prev_x, prev_y = 0, 0

    while True:
        _, frame = cam.read()
        if frame is None:
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
            distance = np.sqrt((x - prev_x) * 2 + (y - prev_y) * 2)

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

        # Speech recognition to detect "click"
        speech_result = recognize_speech_from_mic(recognizer, microphone)
        if speech_result["transcription"] and "click" in speech_result["transcription"].lower():
            pyautogui.click()

        cv2.imshow('Eye Controlled Mouse', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()
except Exception as e:
    print(f"An error occurred: {e}")
    if 'cam' in locals() or 'cam' in globals():
        cam.release()
    cv2.destroyAllWindows()