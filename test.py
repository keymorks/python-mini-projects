import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws/1/testuser"
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({"type": "get_state"}))
        response = await websocket.recv()
        print(f"Response: {response}")

asyncio.get_event_loop().run_until_complete(test_websocket())