#!/usr/bin/env python3
"""
Browse Arguments - Web UI
View and search previously resolved arguments
"""

import gradio as gr
from storage import ArgumentStorage
from datetime import datetime

storage = ArgumentStorage()

def format_timestamp(iso_timestamp: str) -> str:
    """Format ISO timestamp to readable string"""
    try:
        dt = datetime.fromisoformat(iso_timestamp)
        return dt.strftime("%B %d, %Y at %I:%M %p")
    except:
        return iso_timestamp

def get_arguments_list():
    """Get formatted list of all arguments"""
    arguments = storage.list_arguments(limit=100)

    if not arguments:
        return "No arguments recorded yet. Start by recording from the Raspberry Pi!"

    # Format as HTML table
    rows = []
    for arg in arguments:
        timestamp_formatted = format_timestamp(arg["timestamp"])
        winner = arg.get("winner", "Unknown")
        num_speakers = arg.get("num_speakers", 2)
        title = arg.get("title", arg['id'])

        rows.append(f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><b>{title}</b><br><small style="color: #888;">ID: {arg['id']}</small></td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{timestamp_formatted}</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{num_speakers}</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><b>{winner}</b></td>
        </tr>
        """)

    table = f"""
    <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
        <thead>
            <tr style="background-color: #f0f0f0;">
                <th style="padding: 10px; text-align: left; border-bottom: 2px solid #ddd;">Title</th>
                <th style="padding: 10px; text-align: left; border-bottom: 2px solid #ddd;">Date & Time</th>
                <th style="padding: 10px; text-align: left; border-bottom: 2px solid #ddd;">Speakers</th>
                <th style="padding: 10px; text-align: left; border-bottom: 2px solid #ddd;">Winner</th>
            </tr>
        </thead>
        <tbody>
            {''.join(rows)}
        </tbody>
    </table>
    """

    return table

def view_argument_details(argument_id: str):
    """View full details of a specific argument"""
    if not argument_id or not argument_id.strip():
        return "Enter an Argument ID to view details", "", "", "", ""

    arg = storage.get_argument(argument_id.strip())

    if not arg:
        return f"Argument '{argument_id}' not found", "", "", "", ""

    # Format metadata
    timestamp = format_timestamp(arg["timestamp"])
    num_speakers = arg.get("num_speakers", 2)
    duration = arg.get("duration_seconds", 0)
    title = arg.get("title", arg['id'])

    metadata = f"""
# {title}

**Argument ID:** {arg['id']}
**Date & Time:** {timestamp}
**Duration:** {duration:.1f} seconds
**Number of Speakers:** {num_speakers}
"""

    # Get speaker emotions if available
    speakers_data = arg.get("speakers", {})
    emotion_analysis = ""

    if speakers_data:
        emotion_analysis = "\n## 🎭 Speaker Emotion Analysis\n\n"
        for speaker_id, speaker_info in speakers_data.items():
            emotion = speaker_info.get("emotion", "unknown")
            emotion_conf = speaker_info.get("emotion_confidence", 0.0)
            uncertainty = speaker_info.get("uncertainty", 0.0)
            confidence = speaker_info.get("confidence", 0.0)

            # Only show if emotion data exists
            if emotion != "unknown":
                emotion_analysis += f"**{speaker_id}:**\n"
                emotion_analysis += f"- Emotion: {emotion.upper()} ({emotion_conf:.1%} confidence)\n"
                emotion_analysis += f"- Uncertainty: {uncertainty:.3f}\n"
                emotion_analysis += f"- Speaker Confidence: {confidence:.3f}\n\n"

    # Get transcript
    transcript = arg.get("transcript", "No transcript available")

    # Get verdict
    verdict = arg.get("full_verdict_text", "No verdict available")

    # Get audio path
    audio_path = arg.get("audio_path", "")

    return metadata, emotion_analysis, transcript, verdict, audio_path

def search_arguments(query: str):
    """Search arguments by keyword"""
    if not query or not query.strip():
        return "Enter a search query"

    results = storage.search_arguments(query.strip())

    if not results:
        return f"No arguments found containing '{query}'"

    # Format results
    rows = []
    for arg in results:
        timestamp_formatted = format_timestamp(arg["timestamp"])
        winner = arg.get("winner", "Unknown")
        title = arg.get("title", arg['id'])

        rows.append(f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><b>{title}</b><br><small style="color: #888;">ID: {arg['id']}</small></td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{timestamp_formatted}</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;"><b>{winner}</b></td>
        </tr>
        """)

    table = f"""
    <h3>Found {len(results)} result(s) for "{query}"</h3>
    <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
        <thead>
            <tr style="background-color: #f0f0f0;">
                <th style="padding: 10px; text-align: left; border-bottom: 2px solid #ddd;">Title</th>
                <th style="padding: 10px; text-align: left; border-bottom: 2px solid #ddd;">Date & Time</th>
                <th style="padding: 10px; text-align: left; border-bottom: 2px solid #ddd;">Winner</th>
            </tr>
        </thead>
        <tbody>
            {''.join(rows)}
        </tbody>
    </table>
    """

    return table

def get_stats():
    """Get database statistics"""
    stats = storage.get_stats()

    total = stats.get("total_arguments", 0)

    if total == 0:
        return "No arguments recorded yet"

    winner_dist = stats.get("winner_distribution", {})

    # Format winner distribution
    winner_text = []
    for winner, count in winner_dist.items():
        percentage = (count / total) * 100
        winner_text.append(f"- **{winner}**: {count} ({percentage:.1f}%)")

    return f"""
## Database Statistics

**Total Arguments:** {total}

**Winner Distribution:**
{chr(10).join(winner_text)}

**Latest Recording:** {format_timestamp(stats.get("latest_timestamp", ""))}
"""

# Create Gradio Interface
with gr.Blocks(title="Argument Resolver - Browse", theme=gr.themes.Soft()) as app:
    gr.Markdown("""
    # 🎙️ Argument Resolver - Browse Past Arguments

    View and search through previously resolved arguments recorded from the Raspberry Pi.
    """)

    with gr.Tabs():
        # Tab 1: Browse All
        with gr.Tab("📋 Browse All"):
            gr.Markdown("### All Recorded Arguments")
            refresh_btn = gr.Button("🔄 Refresh List")
            arguments_display = gr.HTML()

            refresh_btn.click(
                fn=get_arguments_list,
                inputs=[],
                outputs=[arguments_display]
            )

            # Auto-load on page load
            app.load(
                fn=get_arguments_list,
                inputs=[],
                outputs=[arguments_display]
            )

        # Tab 2: View Details
        with gr.Tab("🔍 View Details"):
            gr.Markdown("### View Argument Details")
            gr.Markdown("Enter an Argument ID from the list above to view full details.")

            argument_id_input = gr.Textbox(
                label="Argument ID",
                placeholder="e.g., 20251112_182945"
            )
            view_btn = gr.Button("View Details", variant="primary")

            with gr.Row():
                with gr.Column():
                    metadata_output = gr.Markdown(label="Metadata")
                    audio_output = gr.Audio(label="🔊 Original Recording")

            emotion_output = gr.Markdown(label="🎭 Speaker Emotions")

            transcript_output = gr.Textbox(
                label="📝 Full Transcript",
                lines=10,
                max_lines=20
            )

            verdict_output = gr.Textbox(
                label="⚖️ Verdict & Analysis",
                lines=15,
                max_lines=30
            )

            view_btn.click(
                fn=view_argument_details,
                inputs=[argument_id_input],
                outputs=[metadata_output, emotion_output, transcript_output, verdict_output, audio_output]
            )

        # Tab 3: Search
        with gr.Tab("🔎 Search"):
            gr.Markdown("### Search Arguments")
            gr.Markdown("Search for arguments containing specific keywords in their transcripts.")

            search_input = gr.Textbox(
                label="Search Query",
                placeholder="e.g., climate change, AI, politics"
            )
            search_btn = gr.Button("Search", variant="primary")
            search_results = gr.HTML()

            search_btn.click(
                fn=search_arguments,
                inputs=[search_input],
                outputs=[search_results]
            )

        # Tab 4: Statistics
        with gr.Tab("📊 Statistics"):
            gr.Markdown("### Database Statistics")
            stats_refresh_btn = gr.Button("🔄 Refresh Stats")
            stats_output = gr.Markdown()

            stats_refresh_btn.click(
                fn=get_stats,
                inputs=[],
                outputs=[stats_output]
            )

            # Auto-load on page load
            app.load(
                fn=get_stats,
                inputs=[],
                outputs=[stats_output]
            )

    gr.Markdown("""
    ---
    ### How to Use:

    1. **Browse All**: See all recorded arguments sorted by date
    2. **View Details**: Enter an Argument ID to see full transcript, verdict, and play audio
    3. **Search**: Find arguments containing specific keywords
    4. **Statistics**: View overall statistics about your argument database

    **Recording New Arguments:**
    - Run `audio_processor.py` on this machine
    - Use the Raspberry Pi to record and send audio
    - New arguments will appear here automatically
    """)

def main():
    import socket

    def _pick_free_port(prefer=7863):
        try:
            with socket.socket() as s:
                s.bind(("127.0.0.1", prefer))
                return prefer
        except OSError:
            with socket.socket() as s:
                s.bind(("127.0.0.1", 0))
                return s.getsockname()[1]

    port = _pick_free_port(7863)

    print(f"\n{'='*60}")
    print(f"🌐 ARGUMENT RESOLVER - BROWSE UI")
    print(f"{'='*60}")
    print(f"Open in browser: http://127.0.0.1:{port}")
    print(f"Database: {storage.base_dir}")
    print(f"Total arguments: {storage.get_stats().get('total_arguments', 0)}")
    print(f"{'='*60}\n")

    app.launch(
        server_name="127.0.0.1",
        server_port=port,
        share=False,
        inbrowser=True
    )

if __name__ == "__main__":
    main()
