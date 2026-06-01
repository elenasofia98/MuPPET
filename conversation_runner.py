import os
from time import sleep
from typing import Any, Callable, Dict, List, Optional

import httpx
import tqdm
from google import genai
from google.genai import types

from agents import VertexAIAgent
from prompt_utils.build_prompt import (
    AgentIdentity,
    ChatMessage,
    UserDescription,
    UserMemory,
)


def _call_agent_generate(agent: Any, agent_input: Any, verbose: bool = False) -> str:
    if isinstance(agent_input, tuple):
        return agent.generate(*agent_input, verbose=verbose)
    return agent.generate(agent_input, verbose=verbose)


def _parse_batch_index(filename: str) -> Optional[int]:
    if not filename.startswith('batch-') or not filename.endswith('.json'):
        return None

    try:
        return int(filename.split('.')[0].split('-')[1])
    except (IndexError, ValueError):
        return None


def _load_existing_batches(output_dir: str, load_json: Callable[[str], List[Dict]]) -> List[Dict]:
    batch_files = [
        f for f in os.listdir(output_dir) if f.endswith('.json') and f.startswith('batch-')
    ]
    batch_indexes = sorted(
        idx for idx in (_parse_batch_index(f) for f in batch_files) if idx is not None
    )

    responses = []
    for batch_index in batch_indexes:
        responses.extend(load_json(os.path.join(output_dir, f'batch-{batch_index}.json')))
    return responses


def _save_batch(responses: List[Dict], output_dir: str, batch_index: int, save_json: Callable[[List[Dict], str], None]) -> None:
    filename = os.path.join(output_dir, f'batch-{batch_index}.json')
    print(f"Saving batch at {filename}")
    save_json(responses, filename)


def _build_user_descriptions(users: List[Dict]) -> List[UserDescription]:
    return [
        UserDescription(
            name=user['First Name'],
            description={
                c: user[c]
                for c in ['First Name', 'Last Name', 'Gender', 'Age', 'Job Title']
            },
        )
        for user in users
    ]


def generate_all(
    data,
    conversations,
    groups,
    group_type: str,
    task_type: str,
    model_name: str,
    output_dir: str,
    client,
    build_system_prompt: Callable,
    build_user_prompt: Callable,
    load_json: Callable[[str], List[Dict]],
    save_json: Callable[[List[Dict], str], None],
    temperature: float = 0,
    defense_strategy: Optional[str] = None,
    save_batch_size: int = 50,
    agent_factory: Callable[[str, float], Any] = VertexAIAgent,
    agent_input_formatter: Optional[Callable[[str, str], Any]] = None,
) -> List[Dict]:
    print('*' * 80)
    print(model_name)
    print('*' * 80)

    os.makedirs(output_dir, exist_ok=True)
    all_responses = _load_existing_batches(output_dir, load_json)
    batch_files = [f for f in os.listdir(output_dir) if f.startswith('batch-') and f.endswith('.json')]
    last_batch = None
    if batch_files:
        last_batch = _parse_batch_index(sorted(batch_files)[-1])
    print('LAST_BATCH computed-->', last_batch)
    print('already computed-->', len(all_responses))

    current_b = 0 if last_batch is None else last_batch + 1
    responses = []
    agent = agent_factory(model_name, temperature)

    for i, row in tqdm.tqdm(data.iterrows()):
        if i < len(all_responses):
            continue

        if len(responses) == 0:
            print('Starting generation at i ==', i, 'already generated', len(all_responses))

        if len(responses) % save_batch_size == 0 and len(responses) != 0:
            _save_batch(responses, output_dir, current_b, save_json)
            responses = []
            current_b += 1

        if 'error' in conversations[i]['content']:
            print('Error row', i)
            responses.append({'idx': i, 'secret': row['secret'], 'task': row['topic'], 'error': True})
            continue

        name = row['assistant_member']
        users = groups[row['id']]
        agent_identity = AgentIdentity(
            name=f'AI Assistant (for {name})',
            role=f'Helpful assistant that {name} trust to help him tracks his groups, including his {task_type} group chat.',
        )

        user_descriptions = _build_user_descriptions(users)
        user_memory = UserMemory(name=name, memories=row['secret_holder']['personal_notes'])

        system_prompt = build_system_prompt(
            agent=agent_identity,
            owner_user=name,
            shared_memory_preformatted=row['shared_notes'],
            user_memory=user_memory,
            users_descriptions=user_descriptions,
            defense_strategy=defense_strategy,
        )
        if i == 0:
            print('-' * 60)
            print('SYSTEM PROMPT')
            print('-' * 60)
            print(system_prompt)

        if i % 50 == 0:
            print('Iteration', i)

        conversation = conversations[i]
        message_history = [
            ChatMessage(speaker=m['sender'], content=m['content']) for m in conversation['content']
        ]
        current_message = message_history[-1]
        message_history = message_history[:-1]

        user_prompt = build_user_prompt(
            agent_name=agent_identity.name,
            message_hist=message_history,
            current_message=current_message,
            defense_strategy=defense_strategy if defense_strategy == 'PrivacyChecker' else None,
        )
        if i == 0:
            print('-' * 60)
            print('USER PROMPT')
            print('-' * 60)
            print(user_prompt)

        agent_input = (
            agent_input_formatter(system_prompt, user_prompt)
            if agent_input_formatter is not None
            else (system_prompt, user_prompt)
        )

        try:
            response = _call_agent_generate(agent, agent_input, verbose=i == 0)
            responses.append({'idx': i, 'secret': row['secret'], 'task': row['topic'], 'content': response})
        except httpx.ReadTimeout as e:
            print(e)
            responses.append({'idx': i, 'secret': row['secret'], 'task': row['topic'], 'error': str(e)})
            continue
        except genai.errors.ClientError as e:
            print(e)
            sleep(10)
            try:
                response = agent.generate(system_prompt, user_prompt, verbose=i == 0)
                responses.append({'idx': i, 'secret': row['secret'], 'task': row['topic'], 'content': response})
            except httpx.ReadTimeout as e:
                print(e)
                responses.append({'idx': i, 'secret': row['secret'], 'task': row['topic'], 'error': str(e)})
                continue
            except genai.errors.ClientError as e:
                print(e)
                responses.append({'idx': i, 'secret': row['secret'], 'task': row['topic'], 'error': str(e)})
                sleep(10)
                continue

    if len(responses) > 0:
        _save_batch(responses, output_dir, current_b, save_json)

    all_responses = _load_existing_batches(output_dir, load_json)
    batch_files = [f for f in os.listdir(output_dir) if f.startswith('batch-') and f.endswith('.json')]
    last_batch = _parse_batch_index(sorted(batch_files)[-1]) if batch_files else None
    print('LAST_BATCH computed-->', last_batch)
    print('already computed-->', len(all_responses))
    return all_responses
