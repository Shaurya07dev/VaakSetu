"""
Twilio Webhook Server
======================
Flask server that handles Twilio voice call webhooks.
When someone answers an outbound call, Twilio sends requests here.

Start this BEFORE making outbound calls:
    python -m twilio_calls.webhook_server

Then expose via ngrok:
    ngrok http 5000
"""

import os
import sys
from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# ─── Configuration ────────────────────────────────────────────────
GREETING_MESSAGES = {
    "hindi": "नमस्ते! मैं आपका एआई असिस्टेंट हूँ। कृपया बीप के बाद बोलें।",
    "english": "Hello! I am your AI assistant. Please speak after the beep.",
    "kannada": "ನಮಸ್ಕಾರ! ನಾನು ನಿಮ್ಮ ಎಐ ಸಹಾಯಕ. ದಯವಿಟ್ಟು ಬೀಪ್ ನಂತರ ಮಾತನಾಡಿ.",
}

DEFAULT_LANGUAGE = os.getenv("CALL_LANGUAGE", "english")


# ─── Routes ───────────────────────────────────────────────────────

@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return {
        "status": "running",
        "service": "Mouriyan's Voice Agent Webhook",
        "endpoints": ["/voice", "/gather", "/process", "/status"],
    }


@app.route("/voice", methods=["POST"])
def voice_handler():
    """
    Initial call handler — called when the recipient answers.
    Greets the user and starts listening for speech input.
    """
    response = VoiceResponse()

    # Get language from query param or default
    lang = request.args.get("lang", DEFAULT_LANGUAGE)
    greeting = GREETING_MESSAGES.get(lang, GREETING_MESSAGES["english"])

    # TwiML language mapping for speech recognition
    twiml_languages = {
        "hindi": "hi-IN",
        "english": "en-IN",
        "kannada": "kn-IN",
    }

    # Greet and gather speech
    gather = Gather(
        input="speech",
        action="/gather",
        method="POST",
        language=twiml_languages.get(lang, "en-IN"),
        speech_timeout="auto",
        timeout=10,
    )
    gather.say(greeting, voice="Polly.Aditi", language=twiml_languages.get(lang, "en-IN"))
    response.append(gather)

    # If no input, retry
    response.say("I didn't hear anything. Goodbye!", voice="Polly.Aditi")
    response.hangup()

    print(f"📞 [VOICE] Call answered. Greeting in {lang}.")
    return Response(str(response), mimetype="text/xml")


@app.route("/gather", methods=["POST"])
def gather_handler():
    """
    Handles the gathered speech input from the caller.
    In production, this would send audio to Shaurya's ASR pipeline.
    For now, it logs the transcript and responds.
    """
    response = VoiceResponse()

    # Get the speech result from Twilio
    speech_result = request.form.get("SpeechResult", "")
    confidence = request.form.get("Confidence", "N/A")

    print(f"🎙️  [GATHER] Speech received:")
    print(f"   Transcript: \"{speech_result}\"")
    print(f"   Confidence: {confidence}")

    if speech_result:
        # In production: Send to ASR pipeline → AI brain → TTS response
        # For now: Echo back what was heard
        ai_response = f"You said: {speech_result}. Thank you for your input. We will process your request."
        response.say(ai_response, voice="Polly.Aditi")

        # Continue gathering more input
        gather = Gather(
            input="speech",
            action="/gather",
            method="POST",
            speech_timeout="auto",
            timeout=10,
        )
        gather.say("Is there anything else you would like to say?", voice="Polly.Aditi")
        response.append(gather)
    else:
        response.say("I couldn't understand. Let me try again.", voice="Polly.Aditi")
        response.redirect("/voice")

    return Response(str(response), mimetype="text/xml")


@app.route("/process", methods=["POST"])
def process_handler():
    """
    Process endpoint — placeholder for ASR pipeline integration.
    In production, Shaurya's ASR output comes here.
    """
    response = VoiceResponse()
    
    # Placeholder: would receive processed AI response
    ai_text = request.form.get("ai_response", "Processing complete. Thank you!")
    response.say(ai_text, voice="Polly.Aditi")
    response.hangup()

    return Response(str(response), mimetype="text/xml")


@app.route("/status", methods=["POST"])
def status_callback():
    """
    Twilio status callback — logs call status changes.
    """
    call_sid = request.form.get("CallSid", "unknown")
    call_status = request.form.get("CallStatus", "unknown")
    duration = request.form.get("CallDuration", "0")

    status_icons = {
        "initiated": "🟡",
        "ringing": "🔔",
        "in-progress": "🟢",
        "completed": "✅",
        "busy": "🔴",
        "no-answer": "⚪",
        "failed": "❌",
        "canceled": "🚫",
    }
    icon = status_icons.get(call_status, "❓")
    print(f"{icon} [STATUS] Call {call_sid[:12]}... → {call_status} (duration: {duration}s)")

    return "", 204


# ─── Main ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("WEBHOOK_PORT", 5000))
    print()
    print("╔══════════════════════════════════════════════╗")
    print("║   📞  TWILIO WEBHOOK SERVER                  ║")
    print("║   Mouriyan's Voice Agent                     ║")
    print("╚══════════════════════════════════════════════╝")
    print()
    print(f"🌐 Server running on http://localhost:{port}")
    print(f"📌 Next step: Run 'ngrok http {port}' in another terminal")
    print(f"📌 Then use the ngrok URL in outbound_call.py")
    print()
    app.run(host="0.0.0.0", port=port, debug=True)
