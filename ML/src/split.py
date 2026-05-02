import json
from functools import lru_cache
from transformers import AutoModelForCausalLM, AutoTokenizer

from config import MAX_NEW_TOKENS, LLM_MODEL

@lru_cache(maxsize=1)
def load_model():
    tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL)
    model = AutoModelForCausalLM.from_pretrained(LLM_MODEL)

    return tokenizer, model

def generate(prompt):
    tokenizer, model = load_model()

    messages = [{"role": "user", "content": prompt}]

    inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    ).to(model.device)

    outputs = model.generate(
        **inputs,
        max_new_tokens=MAX_NEW_TOKENS,
    )

    return tokenizer.decode(outputs[0][inputs["input_ids"].shape[-1]:], skip_special_tokens=True).strip()


def parse_json(text):
    start = text.find("{")
    end = text.find("}")

    if start == -1 or end == -1:
        raise ValueError("Invalid JSON format")

    return json.loads(text[start:end + 1])


def reverse_query(query):
    prompt = f"""
Return the qualities that mean the opposite of the following attribute.
Return only the antonym phrase, with no explanation.

Attribute: {query}
""".strip()

    return generate(prompt)


def split_query(query):
    prompt = f"""
Split the user request into two search queries.

- "attribute": generic qualities of the desired place.
- "type": the kinds of place or facility the user wants.

Return exactly one JSON object with these keys:
Do not include anything else.

User request: {query}
""".strip()

    response = generate(prompt)
    parsed = parse_json(response)

    attribute = parsed["attribute"]
    reversed_attribute = reverse_query(attribute)
    place_type = parsed["type"]

    return reversed_attribute, place_type