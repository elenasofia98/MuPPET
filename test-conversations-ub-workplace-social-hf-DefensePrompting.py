import os
cuda_devices = [1]


from dataset import Dataset

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

os.environ["CUDA_VISIBLE_DEVICES"] = ','.join([str(x) for x in cuda_devices])
os.environ['HF_TOKEN'] = load_json('env.json')['HF_TOKEN']



from prompt_utils.build_prompt import build_system_prompt, build_user_prompt
from conversation_runner import generate_all
from agents import HuggingFaceAgent


model_names = [
    "meta-llama/Meta-Llama-3-8B-Instruct",
    "meta-llama/Meta-Llama-3.1-8B-Instruct",
    "Qwen/Qwen3-4B",
    "Qwen/Qwen3-8B",
    "Qwen/Qwen3-14B",
    "google/gemma-3-1b-it",
    "google/gemma-3-4b-it",
    "google/gemma-3-12b-it",
]


model_maps = {}
for i, model_name in enumerate(model_names):
    model_maps[model_name] = {"": 0} if i < 5 and len(cuda_devices) > 0 else "auto"

DEFENSE_STRATEGY = 'PrivacyChecker'

redo = False

TEMPERATURE = {model_name: 0 for model_name in model_names}


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
                client=None,
                build_system_prompt=build_system_prompt,
                build_user_prompt=build_user_prompt,
                load_json=load_json,
                save_json=save_json,
                temperature=TEMPERATURE[model_name],
                defense_strategy=DEFENSE_STRATEGY,
                agent_factory=lambda client, mn, temp: HuggingFaceAgent(client, mn, temp, model_maps=model_maps),
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
            defense_strategy=DEFENSE_STRATEGY,
            agent_factory=lambda client, mn, temp: HuggingFaceAgent(client, mn, temp, model_maps=model_maps),
            agent_input_formatter=lambda system_prompt, user_prompt: [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        save_json(responses, OUTPUT_PATH)
    else:
        responses = load_json(OUTPUT_PATH)

    print(len(responses))
