import speech_recognition as sr
import pyttsx3
import time
from datetime import datetime
import webbrowser
import wikipedia
import requests
import pyautogui
import os
import subprocess

class VoiceChatbot:
    def __init__(self):
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        # Initialize text-to-speech
        self.engine = pyttsx3.init()
        # Set voice properties
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[1].id)  # Use female voice
        self.engine.setProperty('rate', 150)  # Speed of speech

    def speak(self, text):
        """Convert text to speech"""
        print(f"Bot: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        """Listen to user's voice input"""
        with sr.Microphone() as source:
            print("Listening...")
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)

        try:
            text = self.recognizer.recognize_google(audio)
            print(f"You: {text}")
            return text.lower()
        except sr.UnknownValueError:
            self.speak("Sorry, I didn't understand that.")
            return ""
        except sr.RequestError:
            self.speak("Sorry, my speech service is down.")
            return ""

    def search_web(self, query):
        """Search the web for information"""
        try:
            self.speak(f"Searching for {query}")
            webbrowser.open(f"https://www.google.com/search?q={query}")
            return True
        except Exception as e:
            self.speak("Sorry, I couldn't perform the search.")
            return False

    def search_wikipedia(self, query):
        """Search Wikipedia for information"""
        try:
            self.speak(f"Looking up {query} on Wikipedia")
            result = wikipedia.summary(query, sentences=2)
            self.speak("According to Wikipedia:")
            self.speak(result)
            return True
        except wikipedia.exceptions.DisambiguationError:
            self.speak("There are multiple results for this search. Please be more specific.")
            return False
        except Exception as e:
            self.speak("Sorry, I couldn't find information on Wikipedia.")
            return False

    def open_app(self, app_name):
        """Open a Windows application"""
        try:
            self.speak(f"Opening {app_name}")
            # Common Windows applications
            app_paths = {
                "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                "notepad": "C:\\Windows\\notepad.exe",
                "calculator": "C:\\Windows\\System32\\calc.exe",
                "paint": "C:\\Windows\\System32\\mspaint.exe"
            }
            
            # Try to find the application in our dictionary
            if app_name.lower() in app_paths:
                subprocess.Popen(app_paths[app_name.lower()])
                return True
            
            # Try to open using start
            try:
                os.startfile(app_name)
                return True
            except:
                self.speak(f"Sorry, I couldn't find {app_name}.")
                return False
        except Exception as e:
            self.speak(f"Sorry, I couldn't open {app_name}.")
            return False

    def process_command(self, command):
        """Process user commands"""
        if "hello" in command or "hi" in command:
            self.speak("Hello! How can I assist you today?")
        elif "time" in command:
            current_time = datetime.now().strftime("%I:%M %p")
            self.speak(f"The current time is {current_time}")
        elif "search" in command or "google" in command:
            query = command.replace("search", "").replace("google", "").strip()
            if query:
                self.search_web(query)
        elif "wikipedia" in command:
            query = command.replace("wikipedia", "").strip()
            if query:
                self.search_wikipedia(query)
        elif "open" in command:
            app_name = command.replace("open", "").strip()
            if app_name:
                self.open_app(app_name)
        elif "stop" in command or "exit" in command:
            self.speak("Goodbye! Have a great day!")
            return False
        else:
            self.speak("I'm not sure how to respond to that. Could you please rephrase?")
        return True

    def run(self):
        """Run the chatbot"""
        self.speak("Hello! I'm your voice chatbot. How can I help you?")
        
        while True:
            command = self.listen()
            if command:
                if not self.process_command(command):
                    break
            time.sleep(1)

if __name__ == "__main__":
    chatbot = VoiceChatbot()
    chatbot.run()
