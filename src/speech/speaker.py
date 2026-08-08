"""
Text-to-Speech Module
Converts text to voice output
"""
import pyttsx3
from colorama import Fore, Style, init

init(autoreset=True)


class VoiceSpeaker:
    def __init__(self):
        self.engine = pyttsx3.init()
        
        # Configure voice properties
        self.engine.setProperty('rate', 175)  # Speed of speech
        self.engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
        
        # Get available voices
        voices = self.engine.getProperty('voices')
        
        # Try to set a male voice (optional)
        for voice in voices:
            if "male" in voice.name.lower() or "david" in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
        
        print(f"{Fore.GREEN}✓ Voice engine initialized{Style.RESET_ALL}")
    
    def speak(self, text, language='en'):
        """
        Convert text to speech (bilingual support)
        
        Args:
            text (str): Text to speak
            language (str): 'en' for English, 'es' for Spanish
        """
        if not text:
            return
        
        print(f"{Fore.MAGENTA}🔊 JARVIS: {text}{Style.RESET_ALL}")
        
        try:
            # Adjust voice properties for Spanish if needed
            voices = self.engine.getProperty('voices')
            
            if language == 'es':
                # Try to find Spanish voice
                for voice in voices:
                    if 'spanish' in voice.name.lower() or 'español' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
            else:
                # Use default English voice
                for voice in voices:
                    if "male" in voice.name.lower() or "david" in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
            
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"{Fore.RED}Speech error: {e}{Style.RESET_ALL}")
