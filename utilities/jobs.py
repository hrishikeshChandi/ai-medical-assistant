import time
from utilities.driver import get_driver
from utilities.scraper_utilities import hospitals_info
from fastapi import status, UploadFile
from utilities.upload_utilities import check_uploads, process_query, cleanup
from fastapi import HTTPException
from config.constants import IMAGE_FILE_EXTENSIONS, AUDIO_FILE_EXTENSIONS
from typing import Literal, List


async def process_query_job(
    diet: str,
    symptoms: str,
    current_medicines: str,
    exercise: str,
    user_id: str,
    additional_info: str,
    files: List[UploadFile],
    file_type=Literal["image", "audio"],
):
    additional_info = additional_info or "NA"
    extensions = (
        IMAGE_FILE_EXTENSIONS if file_type == "image" else AUDIO_FILE_EXTENSIONS
    )

    check_uploads(files=files, file_extensions=extensions, file_type=file_type)

    try:
        start = time.perf_counter()

        response = await process_query(
            files=files,
            current_medicines=current_medicines,
            symptoms=symptoms,
            model_type=file_type,
            diet=diet,
            exercise=exercise,
            additional_info=additional_info,
            user_id=user_id,
        )

        end = time.perf_counter()
        return {
            "data": response,
            "success": True,
            "time_taken": f"{int(end - start)} seconds",
        }

    except Exception as e:
        return {
            "success": False,
            "message": str(e),
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        }
    finally:
        cleanup(user_id=user_id)


def scrape_hospitals_job(city: str):
    print(f"Scraping hospitals data for city: {city}")
    driver = None
    try:
        driver = get_driver()
        start = time.time()
        results = hospitals_info(city=city.title(), driver=driver)
        if results and len(results) > 0:
            time_taken = time.time() - start
            return {
                "success": True,
                "count": len(results),
                "data": results,
                "time_taken": f"{time_taken:.2f} seconds",
            }
        else:
            return {
                "success": False,
                "message": "no hospitals found for the given city, please check your city name and try again.",
                "status_code": status.HTTP_404_NOT_FOUND,
            }
    except Exception as e:
        print(f"Error scraping {city}: {str(e)}")
        return {
            "success": False,
            "message": f"Scraping error: {str(e)}",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        }
    finally:
        if driver:
            try:
                driver.quit()
                print(f"Driver closed for city: {city}")
            except Exception as e:
                print(f"Error quitting driver: {str(e)}")
