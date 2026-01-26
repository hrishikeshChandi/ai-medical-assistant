import os, time
from fastapi import HTTPException, status, File, UploadFile, APIRouter
from fastapi.responses import FileResponse
from typing import List, Optional
from utilities.upload_utilities import cleanup, check_uploads, process_query
from config.constants import FOLDER, REPORT_FILE_NAME

router = APIRouter()

IMAGE_FILE_EXTENSIONS = ["jpg", "jpeg", "png", "gif", "bmp", "webp", "tiff"]
AUDIO_FILE_EXTENSIONS = ["mp3", "wav", "aac", "flac", "ogg", "m4a", "wma"]


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
    additional_info = additional_info or "NA"
    check_uploads(files, IMAGE_FILE_EXTENSIONS, file_type="image")

    try:
        start = time.perf_counter()

        response = await process_query(
            files=files,
            current_medicines=current_medicines,
            symptoms=symptoms,
            model_type="image",
            diet=diet,
            exercise=exercise,
            additional_info=additional_info,
            user_id=user_id,
        )

        end = time.perf_counter()
        return {
            "response": response,
            "time_taken": f"{int(end - start)} seconds",
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

    finally:
        cleanup(user_id=user_id)


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
    additional_info = additional_info or "NA"
    check_uploads(files, AUDIO_FILE_EXTENSIONS, file_type="audio")

    try:
        start = time.perf_counter()

        response = await process_query(
            files=files,
            current_medicines=current_medicines,
            symptoms=symptoms,
            model_type="audio",
            diet=diet,
            exercise=exercise,
            additional_info=additional_info,
            user_id=user_id,
        )

        end = time.perf_counter()
        return {
            "response": response,
            "time_taken": f"{int(end - start)} seconds",
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

    finally:
        cleanup(user_id=user_id)


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
