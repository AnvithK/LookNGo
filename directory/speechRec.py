import speech_recognition as sr

# Initialize recognizer class (for recognizing the speech)
r = sr.Recognizer()

# Function to continuously listen to the microphone and convert speech to text
def listen_in_background():
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)  # Adjust for ambient noise once at the beginning
        print("Listening...")
        while True:  # Infinite loop to continuously listen
            try:
                audio = r.listen(source)  # Listen for the first phrase and extract it into audio data
                text = r.recognize_google(audio)  # Use Google Web Speech API to recognize the speech
                print(f"You said: {text}")
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")

if __name__ == "__main__":
    listen_in_background()
