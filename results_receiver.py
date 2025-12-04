#!/usr/bin/env python3
"""
Results Receiver for Laptop
Receives processed arguments from Raspberry Pi and stores them locally for browsing
"""

import os
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
import uvicorn
from storage import ArgumentStorage
import shutil
import json

# Import emotion classifier
try:
    from emotion_classifier import EmotionAnalyzer
    EMOTION_ANALYSIS_ENABLED = True
    emotion_analyzer = None
    print("[INFO] Emotion analysis enabled")
except ImportError:
    EMOTION_ANALYSIS_ENABLED = False
    print("[INFO] Emotion analysis disabled (emotion_classifier.py not found)")

# Configuration
PORT = 7864
STORAGE_DIR = "/Users/dimmaonubogu/aiot_project/arguments_db"

app = FastAPI()
storage = ArgumentStorage(STORAGE_DIR)

@app.post("/receive_results")
async def receive_results(
    argument_id: str = Form(...),
    audio: UploadFile = File(...),
    transcript: UploadFile = File(...),
    metadata: UploadFile = File(...)
):
    """Receive processed argument results from Raspberry Pi"""
    try:
        print(f"\n📥 Receiving results for argument: {argument_id}")

        # Create directory for this argument
        arg_dir = os.path.join(STORAGE_DIR, "arguments", argument_id)
        os.makedirs(arg_dir, exist_ok=True)

        # Save audio file
        audio_path = os.path.join(arg_dir, "audio.wav")
        with open(audio_path, "wb") as f:
            shutil.copyfileobj(audio.file, f)
        print(f"  ✓ Saved audio: {audio_path}")

        # Save transcript
        transcript_path = os.path.join(arg_dir, "transcript.txt")
        with open(transcript_path, "wb") as f:
            shutil.copyfileobj(transcript.file, f)
        print(f"  ✓ Saved transcript: {transcript_path}")

        # Save metadata
        metadata_path = os.path.join(arg_dir, "metadata.json")
        with open(metadata_path, "wb") as f:
            shutil.copyfileobj(metadata.file, f)
        print(f"  ✓ Saved metadata: {metadata_path}")

        # Load metadata for emotion analysis
        with open(metadata_path, 'r') as f:
            metadata_content = json.load(f)

        # Analyze emotions if enabled
        global emotion_analyzer
        if EMOTION_ANALYSIS_ENABLED:
            print("  🎭 Analyzing speaker emotions...")
            if emotion_analyzer is None:
                try:
                    emotion_analyzer = EmotionAnalyzer()
                except Exception as e:
                    print(f"    ⚠️  Failed to load emotion analyzer: {e}")

            if emotion_analyzer and 'speakers' in metadata_content:
                for speaker_id, speaker_data in metadata_content['speakers'].items():
                    transcript = speaker_data.get('transcript', '')
                    if transcript and len(transcript.strip()) > 5:
                        try:
                            emotion_result = emotion_analyzer.analyze(transcript)
                            speaker_data['emotion'] = emotion_result['emotion']
                            speaker_data['emotion_confidence'] = emotion_result['emotion_confidence']
                            speaker_data['uncertainty'] = emotion_result['uncertainty']
                            speaker_data['confidence'] = emotion_result['confidence']
                            print(f"    {speaker_id}: {emotion_result['emotion'].upper()} ({emotion_result['emotion_confidence']:.1%})")
                        except Exception as e:
                            print(f"    ⚠️  Failed to analyze {speaker_id}: {e}")

                # Save updated metadata with emotions
                with open(metadata_path, 'w') as f:
                    json.dump(metadata_content, f, indent=2)
                print(f"  ✓ Updated metadata with emotions")

        # Add to storage index
        index_path = os.path.join(STORAGE_DIR, "arguments.json")
        if os.path.exists(index_path):
            with open(index_path, 'r') as f:
                index = json.load(f)
        else:
            index = []

        # Add new argument if not already in index
        if not any(arg['id'] == argument_id for arg in index):
            index.append({
                'id': argument_id,
                'timestamp': metadata_content.get('timestamp'),
                'title': metadata_content.get('title', f"Argument {argument_id}"),
                'num_speakers': metadata_content.get('num_speakers')
            })

            # Sort by timestamp (most recent first)
            index.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

            with open(index_path, 'w') as f:
                json.dump(index, f, indent=2)

        print(f"  ✓ Updated index")
        print(f"✅ Results saved successfully\n")

        return JSONResponse(content={
            "success": True,
            "message": "Results received and stored successfully",
            "argument_id": argument_id
        })

    except Exception as e:
        print(f"❌ Error receiving results: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.get("/")
async def root():
    """Status endpoint"""
    stats = storage.get_stats()
    return {
        "status": "running",
        "service": "Results Receiver",
        "port": PORT,
        "database": STORAGE_DIR,
        "stats": stats
    }

@app.get("/arguments")
async def list_arguments():
    """List all stored arguments"""
    arguments = storage.list_arguments()
    return {"arguments": arguments}

def main():
    print("="*60)
    print("📥 ARGUMENT RESULTS RECEIVER")
    print("="*60)
    print(f"Port: {PORT}")
    print(f"Endpoint: http://0.0.0.0:{PORT}/receive_results")
    print(f"Database: {STORAGE_DIR}")
    print(f"Stats: {storage.get_stats()}")
    print("="*60)
    print("\n⏳ Waiting for results from Raspberry Pi...\n")

    uvicorn.run(app, host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    main()
