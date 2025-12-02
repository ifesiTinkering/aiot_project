# Argument Resolver System

Complete system for recording, resolving, and browsing arguments using Raspberry Pi and AI.

## 🏗️ Architecture

```
Raspberry Pi → Records Audio → Sends via WiFi
                                    ↓
                            Laptop receives at audio_processor.py
                                    ↓
                            Auto-processes (speakers, transcript, fact-check)
                                    ↓
                            Saves to local database (arguments_db/)
                                    ↓
                            Browse via web interface (browse_arguments.py)
```

## 📁 File Structure

```
aiot_project/
├── storage.py                  # Database manager (JSON-based)
├── audio_processor.py          # Receives & processes audio from Pi
├── browse_arguments.py         # Web UI to view past arguments
├── argument_resolver.py        # Original file (keep for reference)
├── arguments_db/               # Data storage
│   ├── arguments.json          # Index of all arguments
│   └── arguments/
│       ├── 20251112_182945/    # Each argument in its own folder
│       │   ├── audio.wav       # Original recording
│       │   ├── metadata.json   # Structured data
│       │   └── transcript.txt  # Full conversation text
│       └── ...
└── received_audio/             # (Legacy, can be removed)
```

## 🚀 How to Use

### 1. Start the Audio Processor (on laptop)

This receives audio from the Pi and processes it automatically:

```bash
cd /Users/dimmaonubogu/aiot_project
python audio_processor.py
```

**This will:**
- Listen on port 7862
- Receive audio from Raspberry Pi
- Identify speakers using diarization
- Transcribe conversation
- Fact-check claims via Polymarket & web
- **Generate intelligent title using AI** (e.g., "AI Job Displacement Debate")
- Store everything in `arguments_db/`
- Return processing status to Pi

### 2. Record on Raspberry Pi

SSH into the Pi or use keyboard/mouse:

```bash
ssh ifesiras@raspberrypi.local  # password: play
python3 record_and_send.py
```

**This will:**
- Check USB microphone
- Record 30 seconds of audio
- Send to laptop for processing
- Display processing results

### 3. Browse Past Arguments (on laptop)

View all previously resolved arguments:

```bash
cd /Users/dimmaonubogu/aiot_project
python browse_arguments.py
```

**Opens web interface at:** http://127.0.0.1:7863

**Features:**
- **Browse All**: See all arguments with AI-generated titles sorted by date
- **View Details**: Full transcript, verdict, audio playback
- **Search**: Find arguments by keywords in title or transcript
- **Statistics**: Winner distribution, total arguments
- **Smart Titles**: AI generates descriptive titles like "Climate Change vs Economic Growth"

## 📊 Data Storage Format

Each argument is stored with:

### metadata.json
```json
{
  "id": "20251112_182945",
  "title": "AI Job Displacement by 2030",
  "timestamp": "2025-11-12T18:29:45Z",
  "duration_seconds": 30,
  "num_speakers": 2,
  "speakers": {
    "SPEAKER_00": {
      "transcript": "I think AI will...",
      "word_count": 145
    },
    "SPEAKER_01": {
      "transcript": "That's not true...",
      "word_count": 167
    }
  },
  "verdict": {
    "winner": "SPEAKER_01",
    "confidence": 75,
    "reasoning": "..."
  },
  "full_verdict_text": "## VERDICT: SPEAKER_01\n## CONFIDENCE: 75%\n..."
}
```

### audio.wav
Original audio recording (16kHz, mono, WAV format)

### transcript.txt
Full conversation with timestamps:
```
[0.0s] SPEAKER_00: I think AI will replace all jobs by 2030
[5.2s] SPEAKER_01: That's not true, studies show...
[12.4s] SPEAKER_00: But look at what happened with...
```

## 🔌 API Endpoints

### audio_processor.py (port 7862)

**POST /upload**
- Receives audio file
- Processes and stores argument
- Returns processing results

**GET /**
- Status check
- Database statistics

**GET /arguments**
- List all stored arguments

**GET /arguments/{argument_id}**
- Get specific argument details

## 🛠️ Dependencies

Already installed:
- `gradio` - Web interfaces
- `whisper` - Speech transcription
- `pyannote.audio` - Speaker diarization
- `fastapi` - API server
- `uvicorn` - ASGI server
- `requests` - HTTP client
- `torch` - ML framework

## 📝 Workflow Example

1. **Record**: Two people argue about climate change on Raspberry Pi
2. **Send**: Pi sends 30-second audio to laptop
3. **Process**: Laptop automatically:
   - Identifies 2 speakers
   - Transcribes what each said
   - Fact-checks claims via Polymarket & web search
   - Determines winner based on evidence
4. **Store**: Saves to `arguments_db/20251112_183045/`
5. **Browse**: View results anytime in web interface

## 🔧 Configuration

### Update Laptop IP (if needed)

If your laptop's IP changes, update the Pi script:

```bash
ssh ifesiras@raspberrypi.local
nano /home/ifesiras/record_and_send.py
# Change LAPTOP_IP = "10.46.130.179" to your new IP
```

### Adjust Recording Duration

Edit on Pi:
```python
RECORD_DURATION = 30  # Change to 60 for 1 minute, etc.
```

### Change Ports

- `audio_processor.py`: PORT = 7862
- `browse_arguments.py`: port = 7863

## 🎯 Key Features

✅ **Automatic Processing**: No manual intervention needed
✅ **Speaker Identification**: Knows who said what
✅ **Fact Checking**: Uses Polymarket & web search
✅ **Persistent Storage**: All arguments saved permanently
✅ **Web Interface**: Easy browsing and search
✅ **Audio Playback**: Listen to original recordings
✅ **Feedback to Pi**: Shows processing status

## 📈 Future Enhancements

Possible additions:
- Email notifications when arguments are resolved
- Export to PDF/CSV
- Speaker name assignment (instead of SPEAKER_00)
- Real-time processing status updates
- Mobile app interface
- Voice commands to start recording

---

**System Status:**
- ✅ Storage system ready
- ✅ Audio processor ready
- ✅ Browse interface ready
- ✅ Raspberry Pi configured
- ✅ End-to-end tested

**Ready to use!**
