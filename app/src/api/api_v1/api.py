from fastapi import APIRouter
from api.api_v1.endpoints import video_socket

api_router = APIRouter()
api_router.include_router(video_socket.router, tags=["socket"])
