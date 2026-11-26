# SpeechBubble
## Setup of the speech recognition part
I built and tested this on Ubuntu 26.04.1 LTS

0. Clone the project repository
1. Install dependencies:
   ```bash
   sudo apt update
   sudo apt install portaudio19-dev python3-venv unzip wget
2. Create and activate virtual environment. Install Python packages:

   (Make sure you're in the project folder)
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
4. Download and extract Vosk model:
   ```bash
   wget [https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip](https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip)
   unzip vosk-model-small-en-us-0.15.zip
   rm vosk-model-small-en-us-0.15.zip
5. Activate Python environment:
   ```bash
   source venv/bin/activate
6. Start script:
   ```bash
   python3 voice_filter.py
