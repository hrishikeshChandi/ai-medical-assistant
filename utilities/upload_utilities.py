import os, shutil
from fastapi import HTTPException, status, UploadFile
from typing import List, Literal
from ai.service import (
    get_biogpt_response,
    get_final_response,
    analyze_uploads,
    side_effects,
)
from config.constants import FOLDER, REPORT_FILE_NAME
from utilities.scraper_utilities import price_comp
from utilities.driver import get_driver


def check_uploads(
    files: List[UploadFile],
    file_extensions: list,
    file_type: str,
) -> None:
    for file in files:
        if (
            "." not in file.filename
            or file.filename.rsplit(".")[-1].lower() not in file_extensions
        ):
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Only {file_type} files are allowed",
            )


def save_files(files: List[UploadFile]) -> list[str]:
    if not os.path.exists(FOLDER):
        os.mkdir(FOLDER)

    file_paths = []

    for file in files:
        path = os.path.join(FOLDER, file.filename)
        print(f"added : {path}")
        file_paths.append(path)

        with open(path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    return file_paths


def cleanup() -> None:
    if os.path.exists(FOLDER):
        current_files = os.listdir(FOLDER)

        if REPORT_FILE_NAME in current_files:
            current_files.remove(REPORT_FILE_NAME)

        if len(current_files):
            for file_name in current_files:
                path = os.path.join(FOLDER, file_name)
                os.remove(path)


async def process_query(
    files: List[UploadFile],
    current_medicines: str,
    symptoms: str,
    model_type: Literal["image", "audio"],
    diet: str,
    exercise: str,
    additional_info: str,
) -> str:

    # report -> llm response + side effects + new medicines (just names)
    # api response -> llm response + side effects + price comparison links

    file_paths = save_files(files)
    driver = get_driver()
    medicines = [med.strip() for med in current_medicines.split(",")]

    # side effects
    current_medicines_side_effects = await side_effects(medicines)

    # model predictions
    uploaded_file_results = analyze_uploads(
        file_paths=file_paths, model_type=model_type
    )

    # bio gpt response
    bio_gpt_summary = await get_biogpt_response(
        symptoms=symptoms,
        current_medication=current_medicines,
        uploaded_file_results=uploaded_file_results,
    )

    # final response -> summary + medicine names as a list
    final_llm_response = await get_final_response(
        additional_info=additional_info,
        summary=bio_gpt_summary,
        diet=diet,
        exercise=exercise,
    )

    # report contains -> final response summary, current medicine side effects and new medicines that were suggested.
    report_content = (
        final_llm_response.summary
        + "\n"
        + current_medicines_side_effects
        + "\n"
        + "Suggested medicines "
        + ", ".join([m.medicine_name for m in final_llm_response.medicines])
    )

    path = os.path.join(FOLDER, REPORT_FILE_NAME)
    with open(path, "w") as f:
        f.write(report_content)

    try:
        # final api response contains -> final llm response (summary) + side effects + price comparison (for newly suggested medicines)
        response = (
            final_llm_response.summary
            + "\nSide effects of the current medicines:\n"
            + current_medicines_side_effects
            + price_comp(
                medicines=[m.medicine_name for m in final_llm_response.medicines],
                driver=driver,
            )
        )
    finally:
        driver.quit()
    return response
