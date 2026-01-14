from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from config.constants import GROQ_API_KEY
from ai.base_models import BioOutput, FinalLLMOutput, SideEffectsOutput
from ai.model_prompts import (
    BIOGPT_PROMPT,
    FINAL_LLM_SYS_PROMPT,
    FINAL_LLM_USER_PROMPT,
    SIDE_EFFECTS_LLM_PROMPT,
)

base_llm = init_chat_model(
    model="llama-3.3-70b-versatile",
    model_provider="groq",
    temperature=0.2,
    api_key=GROQ_API_KEY,
)

# LLama 3 70b -> used as biogpt
bio_prompt = ChatPromptTemplate.from_template(BIOGPT_PROMPT)
bio_llm = base_llm.with_structured_output(BioOutput)
bio_chain = bio_prompt | bio_llm

# LLama 3 70b -> to give the side effects of medicines
side_effects_prompt = ChatPromptTemplate.from_template(SIDE_EFFECTS_LLM_PROMPT)
side_effects_llm = base_llm.with_structured_output(SideEffectsOutput)
side_effects_chain = side_effects_prompt | side_effects_llm

# To combine all the responses
final_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", FINAL_LLM_SYS_PROMPT),
        ("user", FINAL_LLM_USER_PROMPT),
    ]
)
final_llm = base_llm.with_structured_output(FinalLLMOutput)
final_chain = final_prompt | final_llm
