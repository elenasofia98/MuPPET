#!/usr/bin/env python
# coding: utf-8

import os

from prompt_utils.build_prompt import build_system_prompt, build_user_prompt
from dataset import Dataset
from conversation_runner import generate_all
from agents import OpenAIAgent

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



os.environ['OPENAI_API_KEY'] = load_json('env.json')['STAI_OPENAI']

model_names = ["gpt-5.5"]

redo = False

TEMPERATURE = {model_name: 0 for model_name in model_names}

if len(data) > len(conversations):
    print("Not all conversations available")
    data = data[:len(conversations)]
    print("len(data)", len(data))

for model_name in model_names:
    OUTPUT_DIR = f'answers_conversations/{GROUP_TYPE}-social/{model_name}'
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
                client=None,
                build_system_prompt=build_system_prompt,
                build_user_prompt=build_user_prompt,
                load_json=load_json,
                save_json=save_json,
                temperature=TEMPERATURE[model_name],
                agent_factory=OpenAIAgent,
                agent_input_formatter=lambda system_prompt, user_prompt: [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
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
            client=None,
            build_system_prompt=build_system_prompt,
            build_user_prompt=build_user_prompt,
            load_json=load_json,
            save_json=save_json,
            temperature=TEMPERATURE[model_name],
            agent_factory=OpenAIAgent,
            agent_input_formatter=lambda system_prompt, user_prompt: [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        save_json(responses, OUTPUT_PATH)
    else:
        responses = load_json(OUTPUT_PATH)

    print(len(responses))
