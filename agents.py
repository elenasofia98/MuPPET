from google import genai
from google.genai import types
from openai import OpenAI


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
    def __init__(self, model_name: str, temperature: float):
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
