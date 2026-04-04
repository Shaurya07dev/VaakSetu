import asyncio
import websockets
import json

async def test_live_stream():
    uri = "ws://localhost:8000/sessions/test-session-123/stream"
    print(f"Connecting to {uri}")
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected! Sending chunks...")
            
            # Simulated Conversation chunks
            chunks = [
                "Dr. Venkataraman: Hello Mrs. Rao. What seems to be the problem today?",
                "Patient: I've been having continuous headaches for the past three days.",
                "Dr. Venkataraman: Has there been any fever or nausea?",
                "Patient: No fever, but slight nausea in the mornings. Also light sensitivity.",
                "Dr. Venkataraman: Let's prescribe some paracetamol and you need to rest."
            ]

            for chunk in chunks:
                print(f"\n[Client] Sending: '{chunk}'")
                await websocket.send(json.dumps({
                    "domain": "healthcare",
                    "transcript_chunk": chunk
                }))
                
                # Wait for the incremental response
                response = await websocket.recv()
                data = json.loads(response)
                print(f"[Server Response] -> Structured Data: {data.get('structured_data')}")
                print(f"[Server Response] -> Narrative Update: {data.get('narrative')}")
                
                await asyncio.sleep(2)
            
            print("\nTest completed successfully!")
    except websockets.exceptions.ConnectionClosed:
         print("Connection closed by server.")
    except Exception as e:
        print(f"Error testing websocket: {e}")

if __name__ == "__main__":
    asyncio.run(test_live_stream())
