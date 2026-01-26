from pydantic import BaseModel, Field
from typing import List


class Medicine(BaseModel):
    medicine_name: str = Field(..., description="Name of the medicine")


class FinalLLMOutput(BaseModel):
    summary: str = Field(
        ...,
        description="Medical summary WITHOUT medicine names",
    )
    medicines: List[Medicine] = Field(
        ...,
        description="List of medicine names mentioned",
    )


class BioOutput(BaseModel):
    summary: str = Field(
        ...,
        description="Medical summary with possible alternative medicines based on side effects.",
    )


class SideEffectsOutput(BaseModel):
    medicine_name: str = Field(
        ..., description="The medicine name that was given as the input"
    )
    side_effects: str = Field(
        ...,
        description="Some 2 - 3 most common or most serious side effects of the medicine that was given as input"
    )
