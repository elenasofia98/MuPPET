from google import genai
from google.genai import types
from openai import OpenAI

from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import snapshot_download
import torch


class VertexAIAgent:
    def __init__(self, client, model_name: str, temperature: float):
        self.client = client
        self.model_name = model_name
        self.temperature = temperature

    def generate(self, system_prompt: str, user_prompt: str, verbose: bool = False) -> str:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=self.temperature,
            ),
        )

        generated = response.text
        if verbose:
            print(generated)
        return generated


class OpenAIAgent:
    # accepts (client, model_name, temperature) for compatibility with agent_factory
    def __init__(self, client, model_name: str, temperature: float):
        self.model = OpenAI().chat.completions
        self.model_name = model_name
        self.temperature = temperature

    def generate(self, messages, verbose: bool = False) -> str:
        response = self.model.create(
            model=self.model_name,
            messages=messages,
        )

        generated = response.choices[0].message.content
        if verbose:
            print(generated)
        return generated


class HuggingFaceAgent:
    def __init__(self, client, model_name: str, temperature: float, model_maps: dict = None):
        # client param kept for signature compatibility
        self.model_name = model_name
        self.temperature = temperature
        self.model_maps = model_maps or {}

        path = snapshot_download(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(path, use_fast=False)
        device_map = self.model_maps.get(model_name, "auto")
        self.model = AutoModelForCausalLM.from_pretrained(path, device_map=device_map)

    def generate(self, messages, verbose: bool = False) -> str:
        input_text = self.tokenizer.apply_chat_template(messages, add_generation_prompt=True, tokenize=False)
        if verbose:
            print(input_text)

        inputs = self.tokenizer(input_text, return_tensors="pt").to(self.model.device)

        outputs = self.model.generate(**inputs, max_new_tokens=4096, do_sample=False, num_beams=1)

        generated = self.tokenizer.decode(outputs[0][inputs["input_ids"].shape[-1]:], skip_special_tokens=True)
        if verbose:
            print(generated)

        return generated
