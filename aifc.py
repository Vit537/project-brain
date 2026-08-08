"""Minimal aifc shim for Python 3.13+
SpeechRecognition imports aifc, but we only use WAV input.
This stub maps to wave to satisfy imports.
"""
import wave

Error = wave.Error

open = wave.open
Aifc_read = wave.open
Aifc_write = wave.open
AIFC_read = wave.open
AIFC_write = wave.open
