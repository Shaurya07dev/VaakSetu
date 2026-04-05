import asyncio
from task1_ai_core.tts import get_tts_pipeline
import logging

logging.basicConfig(level=logging.INFO)

async def test():
    tts = get_tts_pipeline()
    try:
        print("Testing Kannada with hitesh...")
        res = await tts.synthesise('ನಮಸ್ಕಾರ', language_code='kn-IN', speaker='hitesh')
        print('Hitesh Kannada audio length:', len(res) if res else 'FAILED (None)')
    except Exception as e:
        print("KANNADA ERROR:", e)

    try:
        print("\nTesting Tamil with hitesh...")
        res = await tts.synthesise('வணக்கம்', language_code='ta-IN', speaker='hitesh')
        print('Hitesh Tamil audio length:', len(res) if res else 'FAILED (None)')
    except Exception as e:
        print("TAMIL ERROR:", e)

asyncio.run(test())
