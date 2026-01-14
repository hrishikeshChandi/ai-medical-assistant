import time
from utilities.driver import get_driver
from utilities.scraper_utilities import hospitals_info
from fastapi import status


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
