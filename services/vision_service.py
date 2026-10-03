import torch

from io import BytesIO
from PIL import Image

from transformers import (
    AutoProcessor,
    AutoModelForImageTextToText,
)
from models.llm_model import llm_for_agent
from utils.logger import get_logger


logger = get_logger(__name__)


# ==========================================
# MODEL CONFIGURATION
# ==========================================

MODEL_ID = "HuggingFaceTB/SmolVLM-256M-Instruct"

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

logger.info("Vision device: %s", DEVICE)
logger.info("Loading vision model: %s", MODEL_ID)


# ==========================================
# LOAD MODEL ONCE
# ==========================================

processor = AutoProcessor.from_pretrained(MODEL_ID)

model = AutoModelForImageTextToText.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.float32,
).to(DEVICE)

model.eval()

logger.info("Vision model loaded successfully")

llm = llm_for_agent()

# ==========================================
# IMAGE DESCRIPTION
# ==========================================


def describe_image(image_file) -> str:
    """
    Analyze an uploaded image and return a
    concise natural-language description.
    """

    logger.info("Starting image analysis")

    # --------------------------------------
    # Read uploaded image
    # --------------------------------------

    image_bytes = image_file.read()

    if not image_bytes:
        raise ValueError("Uploaded image is empty.")

    image = Image.open(BytesIO(image_bytes)).convert("RGB")

    # --------------------------------------
    # HUMSAFAR vision prompt
    # --------------------------------------
    prompt1 = "Describe the visible objects in this image in one short sentence."
    prompt = """

    Look carefully at the image and appreciate the user for making it.

    Your response must follow these rules:
    - Write only 2 or 3 short sentences.
    - Begin with a warm, natural appreciation of what is visible.
    - If it is food, say how appetizing it looks and appreciate
    the visible presentation.
    - If it is a painting, appreciate its visible colors and creativity.
    - If it is a photograph, appreciate the scene or composition.
    - Mention only details that are clearly visible.
    - Avoid repeating sentences or ideas.
    - Do not include headings, bullet points, or explanations.

    Sound like a caring companion speaking naturally.
    """

    # --------------------------------------
    # Create multimodal message
    # --------------------------------------

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image"},
                {
                    "type": "text",
                    "text": prompt,
                },
            ],
        }
    ]

    # --------------------------------------
    # Prepare prompt
    # --------------------------------------

    formatted_prompt = processor.apply_chat_template(
        messages,
        add_generation_prompt=True,
    )

    inputs = processor(
        text=formatted_prompt,
        images=[image],
        return_tensors="pt",
    )

    inputs = inputs.to(DEVICE)

    # --------------------------------------
    # Generate description
    # --------------------------------------

    with torch.no_grad():
        generated_ids = model.generate(
            **inputs,
            max_new_tokens=100,
            do_sample=False,
            repetition_penalty=1.5,
            no_repeat_ngram_size=4,
            eos_token_id=processor.tokenizer.eos_token_id,
            pad_token_id=processor.tokenizer.pad_token_id,
        )

    # Remove the input prompt from the generated sequence.
    input_length = inputs["input_ids"].shape[1]
    new_tokens = generated_ids[:, input_length:]

    description = processor.batch_decode(
        new_tokens,
        skip_special_tokens=True,
    )[0].strip()

    logger.info("Image description: %s", description)

    return description


def image_to_text_response(image_file, user_message) -> str:
    image_description = describe_image(image_file)

    prompt = f"""
    You are HUMSAFAR, a warm and supportive AI companion.

    The user said:
    {user_message}

    The vision model generated this image description:
    {image_description}

    Your task is to turn the description into a natural response
    to the user's message.

    Rules:
    - Respond in 2 or 3 short sentences.
    - Be warm, appreciative, and conversational.
    - If the image shows food, appreciate its visible appearance.
    - If it shows a painting, appreciate its visible colors or composition.
    - If it shows a photograph, comment on the visible scene.
    - Remove repetition and irrelevant details.
    - Do not invent facts that are not in the description.
    - Do not claim that you tasted, touched, or personally experienced anything.
    - Ask at most one relevant follow-up question, if appropriate.
    - Return only the final response.

    Final response:
    """

    response = llm.invoke(prompt)

    return response.content.strip()
