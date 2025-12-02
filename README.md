# Argument Resolver System

Complete system for recording, resolving, and browsing arguments using Raspberry Pi and AI.

## 🏗️ Architecture (Simplified!)

```
Raspberry Pi:
  → Records Audio (30 seconds)
  → Processes Locally (speaker ID, transcription, fact-check)
  → Saves to local database
  → Sends results to laptop
                ↓
Laptop:
  → Receives results (results_receiver.py)
  → Stores in local database
  → Browse via web interface (browse_arguments.py)
```

**Benefits:**
- ✅ Pi does all the heavy processing
- ✅ Works offline (saves locally even if laptop is unavailable)
- ✅ Laptop only needs to receive and display results
- ✅ Much simpler architecture

## 📁 File Structure

```
aiot_project/
├── pi_processor.py             # 🆕 Main script for Raspberry Pi (records + processes)
├── results_receiver.py         # 🆕 Laptop receives results from Pi
├── browse_arguments.py         # Web UI to view past arguments
├── storage.py                  # Database manager (JSON-based)
├── .env                        # API keys (POE_API_KEY, HUGGINGFACE_TOKEN, LAPTOP_IP)
├── .env.example                # Template for environment variables
├── arguments_db/               # Data storage (on both Pi and laptop)
│   ├── arguments.json          # Index of all arguments
│   └── arguments/
│       ├── 20251112_182945/    # Each argument in its own folder
│       │   ├── audio.wav       # Original recording
│       │   ├── metadata.json   # Structured data
│       │   └── transcript.txt  # Full conversation text
│       └── ...
├── audio_processor.py          # (Legacy - old architecture)
├── argument_resolver.py        # (Legacy - old architecture)
└── record_and_send.py          # (Legacy - old architecture)
```

## 🚀 How to Use (New Simplified Architecture)

### Setup (One-time)

**1. On Raspberry Pi:**
```bash
cd ~
git clone https://github.com/ifesiTinkering/aiot_project.git
cd aiot_project

# Create .env file
nano .env
# Add these lines:
POE_API_KEY=your_poe_api_key
HUGGINGFACE_TOKEN=your_huggingface_token
LAPTOP_IP=172.22.129.179

# Install dependencies
pip install python-dotenv whisper torch torchaudio pyannote.audio fastapi_poe requests
```

**2. On Laptop:**
```bash
cd /Users/dimmaonubogu/aiot_project

# .env file already exists with your tokens
# Just verify LAPTOP_IP is correct
```

---

### Running the System

**Step 1: Start Results Receiver on Laptop (optional)**
```bash
cd /Users/dimmaonubogu/aiot_project
python results_receiver.py
```
- Runs on port 7864
- Receives processed results from Pi
- Not required - Pi saves locally even if laptop is offline

**Step 2: Record & Process on Raspberry Pi**
```bash
cd ~/aiot_project
python3 pi_processor.py
```

**This will:**
- ✅ Check USB microphone
- ✅ Record 30 seconds of audio
- ✅ Identify speakers using diarization
- ✅ Transcribe conversation with Whisper
- ✅ Save results locally on Pi (`/home/ifesiras/arguments_db/`)
- ✅ Send results to laptop (if available)
- ✅ Display processing summary

**Step 3: Browse Results on Laptop**
```bash
cd /Users/dimmaonubogu/aiot_project
python browse_arguments.py
```

**Opens web interface at:** http://127.0.0.1:7863

**Features:**
- Browse all arguments sorted by date
- View full transcripts with timestamps
- Listen to audio playback
- Search by keywords
- View statistics

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

All configuration is done via the `.env` file:

```bash
# .env file (create on both Pi and laptop)
POE_API_KEY=your_poe_api_key_here
HUGGINGFACE_TOKEN=your_huggingface_token_here
LAPTOP_IP=172.22.129.179  # Update when laptop IP changes
```

### Update Laptop IP (if needed)

If your laptop's IP changes, update `.env` on the Pi:

```bash
# On Pi
cd ~/aiot_project
nano .env
# Change LAPTOP_IP to your new IP
```

### Adjust Recording Duration

Edit `pi_processor.py` on Pi:
```python
RECORD_DURATION = 30  # Change to 60 for 1 minute, etc.
```

### Ports Used

- `results_receiver.py`: Port 7864 (receives results from Pi)
- `browse_arguments.py`: Port 7863 (web interface)

## 🎯 Key Features

✅ **Pi-Based Processing**: All heavy processing on Raspberry Pi
✅ **Offline Capable**: Works even if laptop is unavailable
✅ **Speaker Identification**: Knows who said what
✅ **Automatic Transcription**: Using OpenAI Whisper
✅ **Persistent Storage**: Saved on both Pi and laptop
✅ **Web Interface**: Easy browsing and search
✅ **Audio Playback**: Listen to original recordings
✅ **Sync to Laptop**: Optional result syncing for viewing

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
