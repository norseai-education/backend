import asyncio
import json
import numpy as np
import websockets
import base64

COSYVOICE_WS = "ws://172.16.0.154:8765"

async def stream_tts_audio(text_tokens):
    """
    Stream TTS audio from CosyVoice in real-time.
    
    Args:
        text_tokens: Async generator or iterable that yields text chunks
        
    Yields:
        bytes: Audio data chunks as they're generated (Float32 PCM)
    """
    # Connect immediately (like the test file) to avoid connection refused errors
    # The server expects connections to be established first, then data sent
    async with websockets.connect(COSYVOICE_WS, max_size=2**26) as ws:
        # 1) Send start message immediately after connection
        start_msg = {"type": "start"}
        await ws.send(json.dumps(start_msg))

        # 2) Receive metadata
        meta_raw = await ws.recv()
        meta = json.loads(meta_raw)
        sr = meta.get("meta", {}).get("sr", 22050)
        dtype = meta.get("meta", {}).get("dtype", "float32")
        
        # Yield metadata first so frontend knows audio format
        yield json.dumps({
            "type": "audio_metadata",
            "sample_rate": sr,
            "dtype": dtype
        }).encode('utf-8')

        # 3) Create tasks for sending tokens and receiving audio
        async def send_tokens():
            """Send tokens to TTS server in real-time"""
            try:
                # Stream tokens as they arrive from the generator
                if hasattr(text_tokens, '__aiter__'):
                    # Async generator - stream tokens in real-time
                    async for token in text_tokens:
                        if token and token.strip():
                            await ws.send(json.dumps({"type": "token", "token": token}))
                else:
                    # Regular iterable - send tokens
                    for token in text_tokens:
                        if token and token.strip():
                            await ws.send(json.dumps({"type": "token", "token": token}))
                            await asyncio.sleep(0.01)  # Small delay to avoid overwhelming
                
                # Signal end of tokens
                await ws.send(json.dumps({"type": "end"}))
            except Exception as e:
                print(f"Error sending tokens: {e}")
                try:
                    await ws.send(json.dumps({"type": "cancel"}))
                except:
                    pass

        # Start sending tokens in background
        send_task = asyncio.create_task(send_tokens())

        # 4) Stream audio chunks as they arrive in real-time
        try:
            while True:
                msg = await ws.recv()
                
                if isinstance(msg, str):
                    # JSON control message
                    obj = json.loads(msg)
                    if obj.get("eos"):
                        print("TTS stream complete")
                        break
                    if obj.get("error"):
                        print(f"TTS error: {obj}")
                        yield json.dumps({
                            "type": "error",
                            "message": obj.get("error")
                        }).encode('utf-8')
                        break
                    continue

                # Binary audio data - yield directly (real-time streaming)
                yield msg
                
        except websockets.exceptions.ConnectionClosed:
            print("TTS connection closed")
        finally:
            # Ensure send task completes
            if not send_task.done():
                send_task.cancel()
                try:
                    await send_task
                except asyncio.CancelledError:
                    pass