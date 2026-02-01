import os
from fastapi import HTTPException, status, File, UploadFile, APIRouter
from fastapi.responses import FileResponse
from typing import List, Optional
from config.constants import FOLDER, REPORT_FILE_NAME
from client.rq_client import queue
from utilities.jobs import process_query_job as process

router = APIRouter()


@router.post("/image_upload", status_code=status.HTTP_201_CREATED)
async def image_upload(
    diet: str,
    symptoms: str,
    current_medicines: str,
    exercise: str,
    user_id: str,
    additional_info: Optional[str] = None,
    files: List[UploadFile] = File(...),
):
    job = queue.enqueue(
        process,
        diet,
        symptoms,
        current_medicines,
        exercise,
        user_id,
        additional_info,
        files,
        file_type="image",
    )
    return {"status": "queued", "job_id": job.get_id()}


@router.post("/audio_upload", status_code=status.HTTP_201_CREATED)
async def audio_upload(
    diet: str,
    symptoms: str,
    current_medicines: str,
    exercise: str,
    user_id: str,
    additional_info: Optional[str] = None,
    files: List[UploadFile] = File(...),
):
    job = queue.enqueue(
        process,
        diet,
        symptoms,
        current_medicines,
        exercise,
        user_id,
        additional_info,
        files,
        file_type="audio",
    )
    return {"status": "queued", "job_id": job.get_id()}


@router.get("/download/{user_id}", status_code=status.HTTP_200_OK)
async def download(user_id: str):
    path = os.path.join(FOLDER, user_id, REPORT_FILE_NAME)
    if os.path.exists(path):
        return FileResponse(filename=REPORT_FILE_NAME, path=path)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Please upload image or audio files to get a report.",
        )
