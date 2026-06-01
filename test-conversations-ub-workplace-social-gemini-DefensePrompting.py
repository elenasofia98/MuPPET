#!/usr/bin/env python
# coding: utf-8

import os
from google.genai import Client
from google.genai.types import HttpOptions

from prompt_utils.build_prompt import build_system_prompt, build_user_prompt
from dataset import Dataset
from conversation_runner import generate_all

CONFIG = '-ub'
MODALITY = '-bc'

GROUP_TYPE = 'large20_workplace'

dataset = Dataset(GROUP_TYPE, CONFIG, MODALITY)
print("len(sensitive_tasks_social)", len(dataset.sensitive_tasks_social))
print("len(groups)", len(dataset.groups))

groups = dataset.groups
load_json = Dataset.load_json
save_json = Dataset.save_json
TASK_TYPE = dataset.task_type

data, conversations, memories = dataset.load_dataset()
print(len(memories))
print(len(conversations))

print(data.head())
print(len(data))

GEMINI_TIMEOUT = 1.5 * 60 * 1000  # 1 minutes

client = Client(
    project=load_json('env.json')['PROJECT_NAME'],
    vertexai=True,
    location='global',
    http_options=HttpOptions(timeout=GEMINI_TIMEOUT),
)

model_names = ["gemini-2.5-pro"]

redo = False

TEMPERATURE = {model_name: 0 for model_name in model_names}

DEFENSE_STRATEGY = 'CIMem_low'

if len(data) > len(conversations):
    print("Not all conversations available")
    data = data[:len(conversations)]
    print("len(data)", len(data))

for model_name in model_names:
    OUTPUT_DIR = f'answers_conversations/{GROUP_TYPE}-social-{DEFENSE_STRATEGY}/{model_name}'
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    OUTPUT_PATH = f'{OUTPUT_DIR}/test-conversation{CONFIG}{MODALITY}-responses.json'
    print(OUTPUT_PATH)

    if os.path.exists(OUTPUT_PATH) and not redo:
        responses = load_json(OUTPUT_PATH)
        if len(data) > len(responses):
            print("Continue generation, len(data)", len(data), "len(responses)", len(responses))
            responses = generate_all(
                data=data,
                conversations=conversations,
                groups=groups,
                group_type=GROUP_TYPE,
                task_type=TASK_TYPE,
                model_name=model_name,
                output_dir=OUTPUT_DIR,
                client=client,
                build_system_prompt=build_system_prompt,
                build_user_prompt=build_user_prompt,
                load_json=load_json,
                save_json=save_json,
                temperature=TEMPERATURE[model_name],
                defense_strategy=DEFENSE_STRATEGY,
            )
            save_json(responses, OUTPUT_PATH)
    elif not os.path.exists(OUTPUT_PATH) or redo:
        responses = generate_all(
            data=data,
            conversations=conversations,
            groups=groups,
            group_type=GROUP_TYPE,
            task_type=TASK_TYPE,
            model_name=model_name,
            output_dir=OUTPUT_DIR,
            client=client,
            build_system_prompt=build_system_prompt,
            build_user_prompt=build_user_prompt,
            load_json=load_json,
            save_json=save_json,
            temperature=TEMPERATURE[model_name],
            defense_strategy=DEFENSE_STRATEGY,
        )
        save_json(responses, OUTPUT_PATH)
    else:
        responses = load_json(OUTPUT_PATH)

    print(len(responses))
