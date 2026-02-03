from fastapi import HTTPException, status, APIRouter
from utilities.scraper_utilities import cities
from client.rq_client import queue
from utilities.jobs import scrape_hospitals_job as scrape

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
