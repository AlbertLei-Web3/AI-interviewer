import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv('sk-C7IhUgedVR5bHhTTCdD88aC122484690B0974a86E150D7Fe')

# Whisper Settings
WHISPER_MODEL_PATH = os.getenv('WHISPER_MODEL_PATH')
WHISPER_MODEL_TYPE = os.getenv('WHISPER_MODEL_TYPE', 'medium')

# Audio Settings
AUDIO_CHUNK_SIZE = int(os.getenv('AUDIO_CHUNK_SIZE', 4096))
AUDIO_CHANNELS = int(os.getenv('AUDIO_CHANNELS', 1))
AUDIO_RATE = int(os.getenv('AUDIO_RATE', 48000))

# Interview Settings
INTERVIEW_CONTEXT = os.getenv('INTERVIEW_CONTEXT') 