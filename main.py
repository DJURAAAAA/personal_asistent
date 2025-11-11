import random
import webbrowser
import customtkinter
import sounddevice as sd
import wavio
import speech_recognition as sr
import os
import time
from datetime import datetime


customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("🤖 Personal Assistant")
        self.geometry("650x600")
        self.resizable(False, False)


        self.chat_frame = customtkinter.CTkFrame(self, width=610, height=400, corner_radius=20, fg_color="#1E1E2F")
        self.chat_frame.place(x=20, y=20)


        self.chatbox = customtkinter.CTkTextbox(self.chat_frame, width=580, height=360, corner_radius=15)
        self.chatbox.place(x=15, y=15)
        self.chatbox.configure(state="disabled", fg_color="#2A2A3B", text_color="#FFFFFF", font=("Arial", 14))


        self.entry = customtkinter.CTkEntry(self, width=380, height=40, placeholder_text="Type your message...")
        self.entry.place(x=20, y=440)
        self.entry.bind("<Return>", lambda event: self.send_text())


        self.speak_button = customtkinter.CTkButton(self, text="🎤 Speak", width=100, height=40, corner_radius=15,
                                                    fg_color="#4F98FF", hover_color="#6AA9FF",
                                                    command=self.handle_speak)
        self.speak_button.place(x=420, y=440)


        self.send_button = customtkinter.CTkButton(self, text="❓Send", width=100, height=40, corner_radius=15,
                                                   fg_color="#4F98FF", hover_color="#6AA9FF",
                                                   command=self.send_text)
        self.send_button.place(x=530, y=440)


        self.chatbox.tag_config("user", foreground="#4F98FF")
        self.chatbox.tag_config("bot", foreground="#FFFFFF")
        self.chatbox.tag_config("system", foreground="#00FFAB")


    def add_message(self, sender, message):
        self.chatbox.configure(state="normal")
        if sender == "You":
            self.chatbox.insert("end", f"💙 {sender}: {message}\n", "user")
        elif sender == "You (voice)":
            self.chatbox.insert("end", f"🎤 {sender}: {message}\n", "user")
        elif sender == "Bot":
            self.chatbox.insert("end", f"🤖 {sender}: {message}\n", "bot")
        else:
            self.chatbox.insert("end", f"🟢 {sender}: {message}\n", "system")
        self.chatbox.configure(state="disabled")
        self.chatbox.see("end")


    def send_text(self):
        text = self.entry.get().strip().lower()
        if text == "":
            return
        self.add_message("You", text)
        self.entry.delete(0, "end")


        self.react_command(text)


    def react_command(self, text):
        commonApps = ["notepad", "calc", "mspaint", "explorer", "cmd", "powershell", "winver", "control", "msedge", "python", "code"]
        basicSites = {
            "youtube": "https://www.youtube.com/",
            "chatgpt": "https://chat.openai.com/",
            "google": "https://www.google.com/"
        }

        words = text.split()

        # OPEN COMMAND
        if "open" in words:
            for app in commonApps:
                if app in words:
                    self.add_message("System", f"Opening {app}...")
                    os.system(app)
                    return
            for site in basicSites.keys():
                if site in words:
                    self.add_message("System", f"Opening {site}...")
                    webbrowser.open(basicSites[site])
                    return
            self.add_message("System", "Sorry, I don’t recognize that app or site.")
            return

        # SEARCH COMMAND
        if "search" in words:
            index = words.index("search")
            query = " ".join(words[index + 1:])
            if query:
                self.add_message("System", f"Searching for '{query}'...")
                webbrowser.open(f"https://www.google.com/search?q={query}")
            else:
                self.add_message("System", "Please type what you want to search for.")
            return


        if "who" in words and "you" in words:
            self.add_message("Bot", "I'm your personal assistant, always ready to help 💻.")
            return

        if "time" in words:
            current_time = datetime.now().strftime("%H:%M:%S")
            self.add_message("Bot", f"The current time is {current_time}.")
            return

        if "date" in words:
            current_date = datetime.now().strftime("%d.%m.%Y")
            self.add_message("Bot", f"Today's date is {current_date}.")
            return

        if "help" in words:
            self.add_message("Bot",
                "Here’s what I can do:\n"
                "- open [app/site] → open an app or site\n"
                "- search [query] → search on Google\n"
                "- tell me the time/date\n"
                "- who are you → about me"
            )
            return
        if "hello" in words or "hi" in words:
            greets = ["Hii what's up ?" , "How i can help you today :)" , "Wanna chat ? I'm beginner but i can try !"]
            self.add_message("Bot",random.choice(greets))
            return

        self.add_message("Bot", "Sorry, I didn’t understand that. Type 'help' to see what I can do!")

    # --- AUDIO INPUT LOGIC ---
    def get_audio_input(self):
        def record_audio(filename, duration=5, samplerate=44100):
            self.add_message("System", "🎙️ Listening...")
            audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1)
            sd.wait()
            wavio.write(filename, audio, samplerate, sampwidth=2)
            self.add_message("System", "✅ Recording finished!")

        def recognize_audio(filename):
            r = sr.Recognizer()
            with sr.AudioFile(filename) as source:
                audio = r.record(source)
            try:
                text = r.recognize_google(audio, language="en-US")
                return text
            except Exception as e:
                self.add_message("System", f"❌ Error: {e}")
                return None

        filename = "temp.wav"
        record_audio(filename)
        text = recognize_audio(filename)
        return text

    # --- VOICE HANDLER ---
    def handle_speak(self):
        text = self.get_audio_input()
        if text:
            self.add_message("You (voice)", text)
            self.react_command(text.lower())


# --- RUN APP ---
if __name__ == "__main__":
    app = App()
    app.mainloop()
