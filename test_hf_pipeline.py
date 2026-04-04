import os
import sys
import asyncio

# Need to append the current directory so it can import task1_ai_core
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from task1_ai_core.diarization import SpeakerDiarizer

async def test_pipeline():
    print("Testing Diarization Pipeline initialization... (this may take a few minutes if downloading models for the first time)")
    try:
        diarizer = SpeakerDiarizer()
        diarizer._ensure_pipeline()
        print("\n✅ Pipeline is successfully authenticated and loaded!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error initializing pipeline: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_pipeline())
