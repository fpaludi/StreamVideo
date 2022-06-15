import uvicorn
from app_factory import app_factory
from services.factories import video_reader
from logger import get_logger

app = app_factory()


logger = get_logger("API")

@app.on_event("startup")
async def startup_event():
    video_reader.start()


@app.on_event("shutdown")
async def shutdown_event():
    await video_reader.stop()


if __name__ == "__main__":
    logger.warning("Start API")
    uvicorn.run(app, host="0.0.0.0", port=80)
