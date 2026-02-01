import uvicorn
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from routers import scraper, uploads, jobs
from config.constants import HOST, PORT, MODULE

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scraper.router, prefix="/scraper", tags=["Scraper"])
app.include_router(uploads.router, prefix="/uploads", tags=["Uploads"])
app.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])


@app.get("/", status_code=status.HTTP_200_OK)
async def root():
    return {"message": "yeye api is working :)"}


if __name__ == "__main__":
    print(f"\n\n\nAccess the api docs at: http://localhost:{PORT}/docs\n\n\n")
    uvicorn.run(MODULE, host=HOST, port=PORT, reload=True)
