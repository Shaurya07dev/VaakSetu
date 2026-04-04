import os
import logging
import torch
from pyannote.audio import Pipeline
from task1_ai_core.config import HF_TOKEN

logger = logging.getLogger(__name__)

# To use pyannote.audio diarization, you need to accept terms in HuggingFace 
# and provide an HF_TOKEN.
class SpeakerDiarizer:
    def __init__(self):
        self._pipeline = None

    def _ensure_pipeline(self):
        if self._pipeline is not None:
            return

        if not HF_TOKEN:
            logger.warning("HF_TOKEN is not set. Speaker diarization requires a HuggingFace token. "
                           "Please set HF_TOKEN in your .env file after accepting the terms for "
                           "'pyannote/speaker-diarization-3.1' and 'pyannote/segmentation-3.0' on HuggingFace.")
            raise ValueError("HF_TOKEN not set in environment.")

        logger.info("Loading Pyannote Speaker Diarization Pipeline (this may take a few minutes)...")
        try:
            # We use 3.1 which is the standard latest diarization pipeline
            pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=HF_TOKEN)
            
            # Send to GPU if available
            if torch.cuda.is_available():
                pipeline.to(torch.device("cuda"))

            self._pipeline = pipeline
            logger.info("Speaker Diarization Pipeline loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load Speaker Diarization pipeline: {e}")
            raise RuntimeError(f"Could not load pyannote pipeline: {e}")

    async def diarize(self, audio_path: str, num_speakers: int = None):
        """
        Diarize the audio file and return segments.
        
        Args:
            audio_path: Path to the audio file.
            num_speakers: Optional. If known, provide to help diarization accuracy.
        
        Returns:
            A list of dicts: [{"speaker": "SPEAKER_00", "start": 0.0, "end": 2.5}, ...]
        """
        import asyncio

        def _run():
            self._ensure_pipeline()
            # The pipeline accepts either a path or a dict: {"uri": "...", "audio": ...}
            diarization = self._pipeline(audio_path, num_speakers=num_speakers)
            
            segments = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                segments.append({
                    "speaker": speaker,
                    "start": float(turn.start),
                    "end": float(turn.end)
                })
            
            # Merge adjacent segments by the same speaker
            merged_segments = []
            for seg in segments:
                if merged_segments and merged_segments[-1]["speaker"] == seg["speaker"] and seg["start"] - merged_segments[-1]["end"] < 0.5:
                    merged_segments[-1]["end"] = seg["end"]
                else:
                    merged_segments.append(seg)
                    
            return merged_segments

        return await asyncio.to_thread(_run)
