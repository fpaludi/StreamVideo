from services import video_reader
import dependency_injector.providers as providers
from settings import settings
from services.video_reader import VideoReader


VideoReaderFactory = providers.Factory(
    VideoReader, source=settings.RTSP_SOURCE, max_size=settings.VIDEO_READER_QUEUE_SIZE
)


video_reader = VideoReaderFactory()
