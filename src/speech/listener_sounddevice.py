"""
Voice Recognition Module - Python 3.13 Compatible
Uses sounddevice instead of PyAudio
"""
import sounddevice as sd
import numpy as np
import wave
import tempfile
import os
import speech_recognition as sr
from colorama import Fore, Style, init

init(autoreset=True)


class VoiceListener:
    def __init__(self):
        self.sample_rate = 16000
        self.channels = 1
        self.recognizer = sr.Recognizer()
        
        print(f"{Fore.YELLOW}Initializing microphone...{Style.RESET_ALL}")
        
        # Test microphone
        try:
            devices = sd.query_devices()
            default_input = sd.query_devices(kind='input')
            print(f"{Fore.GREEN}✓ Microphone ready: {default_input['name']}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Microphone error: {e}{Style.RESET_ALL}")
    
    def record_audio(self, duration=5):
        """Record audio from microphone"""
        print(f"{Fore.CYAN}🎤 Listening... (speak now){Style.RESET_ALL}")
        
        try:
            # Record audio
            recording = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype='int16'
            )
            sd.wait()
            
            return recording
        except Exception as e:
            print(f"{Fore.RED}Recording error: {e}{Style.RESET_ALL}")
            return None
    
    def save_to_wav(self, recording):
        """Save recording to temporary WAV file"""
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        
        with wave.open(temp_file.name, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.sample_rate)
            wf.writeframes(recording.tobytes())
        
        return temp_file.name
    
    def recognize_speech_google(self, audio_file, language='en-US'):
        """Use Google Speech Recognition API (requires internet)"""
        try:
            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)
            
            text = self.recognizer.recognize_google(audio, language=language)
            return text.lower()
            
        except sr.UnknownValueError:
            return None
        except Exception as e:
            print(f"{Fore.RED}Recognition error: {e}{Style.RESET_ALL}")
            return None
    
    def listen(self, timeout=5):
        """
        Listen to microphone and return text (bilingual: English + Spanish)
        
        Returns:
            tuple: (text, language) or (None, None) if failed
        """
        try:
            # Record audio
            recording = self.record_audio(duration=timeout)
            
            if recording is None:
                return None, None
            
            print(f"{Fore.YELLOW}Processing...{Style.RESET_ALL}")
            
            # Save to temporary file
            audio_file = self.save_to_wav(recording)
            
            # Try English first
            text_en = self.recognize_speech_google(audio_file, 'en-US')
            if text_en:
                os.unlink(audio_file)
                print(f"{Fore.GREEN}You said (EN): {text_en}{Style.RESET_ALL}")
                return text_en, 'en'
            
            # Try Spanish if English fails
            text_es = self.recognize_speech_google(audio_file, 'es-ES')
            if text_es:
                os.unlink(audio_file)
                print(f"{Fore.GREEN}Dijiste (ES): {text_es}{Style.RESET_ALL}")
                return text_es, 'es'
            
            # Cleanup
            os.unlink(audio_file)
            print(f"{Fore.RED}Could not recognize speech{Style.RESET_ALL}")
            return None, None
            
        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
            return None, None
