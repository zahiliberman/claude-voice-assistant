#!/usr/bin/env python3
"""
ממשק דיבור אינטראקטיבי עבור Claude
מאפשר שיחה חופשית, הפעלת פקודות וזיהוי קול
"""

import speech_recognition as sr
import pyttsx3
import asyncio
import json
import os
from datetime import datetime
import threading
import queue
import logging
from typing import Optional, Dict, Callable
import subprocess
import sys

# הגדרת logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClaudeVoiceInterface:
    """ממשק קולי חכם עבור Claude"""
    
    def __init__(self, user_name: str = "liberman", language: str = "he"):
        self.user_name = user_name
        self.language = language
        self.data_dir = os.path.expanduser("~/.claude-voice")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # הגדרת מזהה דיבור
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # הגדרת מנוע דיבור
        self.engine = pyttsx3.init()
        self.setup_voice()
        
        # תור הודעות
        self.message_queue = queue.Queue()
        
        # מפת פקודות
        self.commands = {
            "שלום": self.greet,
            "מה השעה": self.tell_time,
            "פתח טרמינל": self.open_terminal,
            "בדוק מערכת": self.check_system,
            "הקלט הודעה": self.record_message,
            "עזרה": self.show_help,
            "תודה": self.thank_you,
            "ביי": self.goodbye
        }
        
        # מצב המערכת
        self.is_listening = False
        self.conversation_mode = False
        
        logger.info(f"ממשק הדיבור מוכן למשתמש {user_name}")
    
    def setup_voice(self):
        """הגדרת המנוע הקולי"""
        voices = self.engine.getProperty('voices')
        
        # חיפוש קול בעברית או שימוש בברירת מחדל
        hebrew_voice = None
        for voice in voices:
            if 'hebrew' in voice.name.lower() or 'he' in voice.id.lower():
                hebrew_voice = voice
                break
        
        if hebrew_voice:
            self.engine.setProperty('voice', hebrew_voice.id)
        
        # הגדרת מהירות וקול
        self.engine.setProperty('rate', 170)  # מהירות דיבור
        self.engine.setProperty('volume', 1.0)  # עוצמת קול
    
    def speak(self, text: str):
        """הפעלת דיבור"""
        self.engine.say(text)
        self.engine.runAndWait()
        logger.info(f"אמרתי: {text}")
    
    def listen(self, timeout: int = 5) -> Optional[str]:
        """האזנה למיקרופון"""
        with self.microphone as source:
            # כיול רעש רקע
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            try:
                logger.info("מאזין...")
                audio = self.recognizer.listen(source, timeout=timeout)
                
                # זיהוי דיבור בעברית
                text = self.recognizer.recognize_google(audio, language="he-IL")
                logger.info(f"שמעתי: {text}")
                return text
                
            except sr.WaitTimeoutError:
                logger.debug("לא נשמע דיבור")
                return None
            except sr.UnknownValueError:
                logger.warning("לא הצלחתי להבין את הדיבור")
                return None
            except Exception as e:
                logger.error(f"שגיאה בזיהוי דיבור: {e}")
                return None
    
    def process_command(self, text: str) -> bool:
        """עיבוד פקודה"""
        text_lower = text.lower()
        
        # חיפוש פקודה מתאימה
        for command, handler in self.commands.items():
            if command in text_lower:
                handler()
                return True
        
        # אם לא נמצאה פקודה ספציפית
        return False
    
    # פקודות בסיסיות
    def greet(self):
        """ברכה"""
        hour = datetime.now().hour
        if hour < 12:
            greeting = "בוקר טוב"
        elif hour < 18:
            greeting = "צהריים טובים"
        else:
            greeting = "ערב טוב"
        
        self.speak(f"{greeting} {self.user_name}! איך אני יכול לעזור?")
    
    def tell_time(self):
        """הודעת זמן"""
        now = datetime.now()
        time_str = now.strftime("%H:%M")
        self.speak(f"השעה עכשיו {time_str}")
    
    def open_terminal(self):
        """פתיחת טרמינל"""
        self.speak("פותח טרמינל...")
        subprocess.Popen(['open', '-a', 'Terminal'])
    
    def check_system(self):
        """בדיקת מערכת"""
        self.speak("בודק את המערכת...")
        
        # בדיקת CPU
        cpu_info = subprocess.check_output(['sysctl', '-n', 'hw.ncpu']).decode().strip()
        
        # בדיקת זיכרון
        mem_info = subprocess.check_output(['vm_stat']).decode()
        
        self.speak(f"המערכת תקינה. יש {cpu_info} ליבות מעבד.")
    
    def record_message(self):
        """הקלטת הודעה"""
        self.speak("אני מקשיב, דבר אחרי הצפצוף")
        # צליל צפצוף
        os.system('afplay /System/Library/Sounds/Ping.aiff')
        
        message = self.listen(timeout=10)
        if message:
            # שמירת ההודעה
            timestamp = datetime.now().isoformat()
            with open(f"{self.data_dir}/messages.jsonl", 'a') as f:
                json.dump({"time": timestamp, "message": message}, f)
                f.write('\n')
            
            self.speak("ההודעה נשמרה בהצלחה")
        else:
            self.speak("לא הצלחתי להקליט את ההודעה")
    
    def show_help(self):
        """הצגת עזרה"""
        help_text = """
        אני יכול לעזור לך עם:
        אמור שלום לברכה
        שאל מה השעה
        בקש לפתוח טרמינל
        בקש בדיקת מערכת
        בקש להקליט הודעה
        """
        self.speak(help_text)
    
    def thank_you(self):
        """תודה"""
        self.speak("בכיף! תמיד כאן בשבילך")
    
    def goodbye(self):
        """פרידה"""
        self.speak(f"להתראות {self.user_name}, יום נעים!")
        self.conversation_mode = False
    
    async def start_conversation_mode(self):
        """מצב שיחה אינטראקטיבי"""
        self.conversation_mode = True
        self.speak(f"שלום {self.user_name}, אני כאן לשיחה. אמור ביי כדי לסיים")
        
        while self.conversation_mode:
            text = self.listen()
            
            if text:
                # בדיקה אם זו פקודת יציאה
                if "ביי" in text.lower() or "להתראות" in text.lower():
                    self.goodbye()
                    break
                
                # ניסיון לעבד כפקודה
                if not self.process_command(text):
                    # אם לא פקודה - תגובה כללית
                    self.respond_to_conversation(text)
            
            await asyncio.sleep(0.1)
    
    def respond_to_conversation(self, text: str):
        """תגובה לשיחה חופשית"""
        responses = {
            "איך אתה": "אני מצוין, תודה שאתה שואל!",
            "מה אתה יכול": "אני יכול לעזור עם הרבה דברים - פקודות מערכת, מידע, ושיחה נעימה",
            "מי אתה": "אני Claude, העוזר הדיגיטלי שלך",
            "מה נשמע": "הכל טוב! עובד קשה כדי לעזור לך",
        }
        
        # חיפוש תגובה מתאימה
        for key, response in responses.items():
            if key in text.lower():
                self.speak(response)
                return
        
        # תגובה כללית
        self.speak("מעניין, ספר לי עוד")
    
    def calibrate_microphone(self):
        """כיול המיקרופון"""
        self.speak("מכייל את המיקרופון, אנא המתן...")
        
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=3)
        
        self.speak("הכיול הושלם. עכשיו אני שומע אותך טוב יותר")
    
    def test_audio(self):
        """בדיקת אודיו"""
        self.speak("בודק את מערכת השמע...")
        self.speak("אם אתה שומע אותי, אמור כן")
        
        response = self.listen()
        if response and "כן" in response.lower():
            self.speak("מצוין! המערכת עובדת כמו שצריך")
        else:
            self.speak("נראה שיש בעיה. בוא ננסה לכייל מחדש")
            self.calibrate_microphone()

async def main():
    """הפעלת הממשק"""
    interface = ClaudeVoiceInterface()
    
    print("🎙️ Claude Voice Interface")
    print("=" * 40)
    print("1. התחל שיחה")
    print("2. כיול מיקרופון")
    print("3. בדיקת אודיו")
    print("4. פקודה בודדת")
    print("5. יציאה")
    
    choice = input("\nבחר אפשרות: ")
    
    if choice == "1":
        await interface.start_conversation_mode()
    elif choice == "2":
        interface.calibrate_microphone()
    elif choice == "3":
        interface.test_audio()
    elif choice == "4":
        interface.speak("אני מקשיב...")
        text = interface.listen()
        if text:
            interface.process_command(text)
    else:
        print("להתראות!")

if __name__ == "__main__":
    # בדיקת תלויות
    try:
        import speech_recognition
        import pyttsx3
    except ImportError:
        print("מתקין תלויות...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", 
                              "SpeechRecognition", "pyttsx3", "pyaudio"])
    
    asyncio.run(main())