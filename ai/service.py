from ai.llms import bio_chain, final_chain, side_effects_chain
from ai.base_models import FinalLLMOutput, SideEffectsOutput
import torch
from typing import Literal
from PIL import Image
from torchvision import transforms

transform = transforms.Compose(
    [
        transforms.Resize((288, 288)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ]
)

IMAGE_MODEL = torch.load("./ai/image/chest_xray_results/cpu_model.pth", weights_only=False)
IMAGE_MODEL.eval()

with open("./ai/image/chest_xray_results/class_names.txt", "r") as f:
    IMAGE_CLASS_NAMES = [
        name.strip().replace("\n", "").title() for name in f.readlines()
    ]


async def get_biogpt_response(
    symptoms: str, current_medication: str, uploaded_file_results: str
) -> str:
    result = await bio_chain.ainvoke(
        {
            "symptoms": symptoms,
            "current_medications": current_medication,
            "uploaded_file_results": uploaded_file_results,
        }
    )
    return result.summary


async def get_final_response(
    summary: str,
    diet: str,
    exercise: str,
    additional_info: str,
) -> FinalLLMOutput:
    result = await final_chain.ainvoke(
        {
            "summary": summary,
            "diet": diet,
            "exercise": exercise,
            "additional_info": additional_info,
        }
    )
    return result


async def side_effects(medicines: list[str]) -> str:
    if not medicines:
        return "No medication provided"

    result = "Side effects for the current medication is:\n"

    for medicine in medicines:
        side_effect_med = await side_effects_chain.ainvoke({"medicine_name": medicine})
        result += f"{side_effect_med.medicine_name}: {side_effect_med.side_effects}\n"

    return result


def predict_image(file_path: str) -> str:
    img = Image.open(file_path).convert("RGB")
    img = transform(img).unsqueeze(dim=0)

    with torch.inference_mode():
        logits = IMAGE_MODEL(img)
        label = IMAGE_CLASS_NAMES[torch.round(torch.sigmoid(logits)).item()]

    return label


def predict_audio(file_path: str) -> str:
    # to be implemented
    return ""


def analyze_uploads(
    file_paths: list[str],
    model_type: Literal["image", "audio"],
) -> str:
    result = f"analysis of the uploaded files ({len(file_paths)}) is as follows:\n"

    for file_path, i in zip(file_paths, range(1, len(file_paths) + 1)):
        if model_type == "image":
            result += f"{i}. {predict_image(file_path)}\n"
        else:
            result += f"{i}. {predict_audio(file_path)}\n"

    return result






