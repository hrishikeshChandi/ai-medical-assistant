from fastapi import HTTPException, status, APIRouter
from client.rq_client import queue

router = APIRouter()


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
