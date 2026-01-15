from fastapi import HTTPException, status, APIRouter
from utilities.scraper_utilities import cities
from client.rq_client import queue
from utilities.scraper_job import scrape_hospitals_job as scrape

router = APIRouter()


@router.get("/hospitals_data", status_code=status.HTTP_200_OK)
async def get_hospital_data(city: str):
    if city.title() not in cities:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="no hospitals found for the given city, please check your city name and try again.",
        )
    try:
        job = queue.enqueue(scrape, city)
        return {"status": "queued", "job_id": job.get_id()}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/job_status/{job_id}", status_code=status.HTTP_200_OK)
async def get_job_status(job_id: str):
    try:
        job = queue.fetch_job(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="job not found, please check your job id and try again.",
            )
        if job.is_finished:
            result = job.result
            if result["success"]:
                return {
                    "status": "completed",
                    "data": result,
                }
            else:
                raise HTTPException(
                    status_code=result["status_code"],
                    detail=result["message"],
                )
        elif job.is_queued:
            return {"status": "queued"}
        elif job.is_started:
            return {"status": "in progress"}
        else:
            return {"status": "failed"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
