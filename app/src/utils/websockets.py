import asyncio as aio


async def check_gracefully_close_connection(websocket):
    try:
        _ = await aio.wait_for(websocket.receive_text(), 1e-5)
    except aio.TimeoutError:
        pass
