"""
Voice Recognition Module
Captures audio from microphone and converts to text
"""
import speech_recognition as sr
from colorama import Fore, Style, init

init(autoreset=True)


class VoiceListener:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        
        # Try to initialize microphone
        try:
            self.microphone = sr.Microphone()
            
            # Adjust for ambient noise on first run
            print(f"{Fore.YELLOW}Calibrating microphone for ambient noise...{Style.RESET_ALL}")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print(f"{Fore.GREEN}✓ Microphone ready!{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Microphone initialization error: {e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Attempting alternative microphone setup...{Style.RESET_ALL}")
            self.microphone = sr.Microphone()
            print(f"{Fore.GREEN}✓ Microphone ready (basic mode)!{Style.RESET_ALL}")
    
    def listen(self, timeout=5):
        """
        Listen to microphone and return text (bilingual: English + Spanish)
        
        Args:
            timeout: Maximum time to wait for speech (seconds)
            
        Returns:
            tuple: (text, language) or (None, None) if failed
        """
        try:
            print(f"{Fore.CYAN}🎤 Listening... (English/Spanish){Style.RESET_ALL}")
            
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            
            print(f"{Fore.YELLOW}Processing...{Style.RESET_ALL}")
            
            # Try English first
            try:
                text_en = self.recognizer.recognize_google(audio, language='en-US')
                print(f"{Fore.GREEN}You said (EN): {text_en}{Style.RESET_ALL}")
                return text_en.lower(), 'en'
            except:
                pass
            
            # Try Spanish if English fails
            try:
                text_es = self.recognizer.recognize_google(audio, language='es-ES')
                print(f"{Fore.GREEN}Dijiste (ES): {text_es}{Style.RESET_ALL}")
                return text_es.lower(), 'es'
            except:
                pass
            
            # If both fail, return None
            print(f"{Fore.RED}Could not recognize speech in English or Spanish{Style.RESET_ALL}")
            return None, None
            
        except sr.WaitTimeoutError:
            print(f"{Fore.RED}No speech detected (timeout){Style.RESET_ALL}")
            return None, None
            
        except sr.UnknownValueError:
            print(f"{Fore.RED}Could not understand audio{Style.RESET_ALL}")
            return None, None
            
        except sr.RequestError as e:
            print(f"{Fore.RED}Speech recognition error: {e}{Style.RESET_ALL}")
            return None, None
        
        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
            return None, None
