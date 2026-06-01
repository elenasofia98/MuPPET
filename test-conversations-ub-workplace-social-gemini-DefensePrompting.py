import os

from google import genai
from google.genai import Client, types
from google.genai.types import HttpOptions
import httpx

from prompt_utils.build_prompt import AgentIdentity, UserMemory, UserDescription, ChatMessage
from prompt_utils.build_prompt import build_system_prompt, build_user_prompt
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

from google.genai import Client
from google.genai import types

from google.genai.types import HttpOptions
GEMINI_TIMEOUT = 1.5 * 60 * 1000 # 1 minutes

# Initialize the client with Vertex AI enabled
client = Client(
    project=load_json('env.json')['PROJECT_NAME'],
    vertexai=True,
    location='global', #
    http_options=HttpOptions(timeout=GEMINI_TIMEOUT)
)


model_names = ["gemini-2.5-pro"]#, "gemini-2.5-flash"]

import json
import re


class VertexAIAgent:
    def __init__(self, model_name, temperature):
        self.client = client
        self.model_name = model_name
        self.temperature = temperature

    def generate(self, system_prompt, user_prompt, verbose=False):
        """
        Generates one model step.
        """

        response = self.client.models.generate_content(
        model=self.model_name,
        contents=user_prompt,
        config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=self.temperature
            )
        )

        generated = response.text

        if verbose:
            print(generated)

        return generated 



import tqdm
from time import sleep

redo = False

TEMPERATURE = {
    model_name: 0 for model_name in model_names
}


DEFENSE_STRATEGY = 'CIMem_low' #'CIMem_medium' #"PrivacyChecker" #'CIMem_high' # 

def generate_all(data, model_name):
    print("*"*80)
    print(model_name)
    print("*"*80)

    agent = VertexAIAgent(
        model_name=model_name,
        temperature=TEMPERATURE[model_name]
    )

    OUTPUT_DIR = f'answers_conversations/{GROUP_TYPE}-social-{DEFENSE_STRATEGY}/{model_name}'
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    LAST_BATCH = None

    already_computed = sorted([int(f.split('.')[0].split('-')[1]) for f in os.listdir(OUTPUT_DIR) if f.endswith('.json') and f.startswith('batch')])
    if len(already_computed)>0:
        LAST_BATCH = already_computed[-1]
    print("LAST_BATCH computed-->", LAST_BATCH)

    SAVE_BATCH_SIZE = 50

    CURRENT_B = 0 if LAST_BATCH is None else LAST_BATCH + 1

    all_responses=[]
    if LAST_BATCH is not None:
        for i in range(LAST_BATCH+1):
            all_responses.extend(load_json(OUTPUT_DIR+f'/batch-{i}.json'))
    print("already computed-->", len(all_responses))



    responses = []
    for i, row in tqdm.tqdm(data.iterrows()):
        if len(all_responses) != 0:
            if i < len(all_responses):
                continue
        if len(responses) == 0:
            print("Starting generation at i == ", i, "already generated",  len(all_responses))
        if len(responses) % SAVE_BATCH_SIZE == 0 and len(responses) != 0:
            filename = f"{OUTPUT_DIR}/batch-{CURRENT_B}.json"
            print(f"Saving batch at {filename}")
            save_json(responses, filename)
            responses = []
            CURRENT_B+=1
        
        if 'error' in conversations[i]['content']:
            print('Error row', i)
            responses.append({'idx':i, 'secret': row['secret'], 'task':row['topic'], 'error':True})
            continue
        
        

        name = row['assistant_member']
        users = groups[row['id']]#row['members']
        agent_identity = AgentIdentity(
            name = f"AI Assistant (for {name})",
            role = f"Helpful assistant that {name} trust to help him tracks his groups, including his {TASK_TYPE} group chat.",
        )

        user_descriptions = [
            UserDescription(
                name=user['First Name'],
                description={c:user[c] for c in ['First Name', 'Last Name', 'Gender', 'Age', 'Job Title']}#json.dumps(user)
            )
            for user in users
        ]

        user_memory = UserMemory(
                    name=name,
                    memories=row['secret_holder']['personal_notes']
                )

        system_prompt = build_system_prompt(
                    agent=agent_identity,
                    owner_user=name,
                    shared_memory_preformatted=row['shared_notes'],
                    user_memory=user_memory,
                    users_descriptions=user_descriptions,
                    defense_strategy=DEFENSE_STRATEGY
                )
        if i == 0:
            print("-"*60)
            print("SYSTEM PROMPT")
            print("-"*60)
            print(system_prompt)

        if i % 50 == 0:
            print("Iteration", i)

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
            defense_strategy=DEFENSE_STRATEGY if DEFENSE_STRATEGY == 'PrivacyChecker' else None
        )
        if i == 0:
            print("-"*60)
            print("SYSTEM PROMPT")
            print("-"*60)
            print(user_prompt)

        try:
            response = agent.generate(
                system_prompt, user_prompt, verbose= i == 0
            )
            responses.append({'idx':i, 'secret': row['secret'], 'task':row['topic'], 'content':response})
        except httpx.ReadTimeout  as e:
            print(e)
            responses.append({'idx':i, 'secret': row['secret'], 'task':row['topic'],'error': str(e)})
            continue
        
        except genai.errors.ClientError as e:
            print(e)
            sleep(10)
            
            try:
                response = agent.generate(
                    system_prompt, user_prompt, verbose= i == 0
                )
                responses.append({'idx':i, 'secret': row['secret'], 'task':row['topic'], 'content':response})
            except httpx.ReadTimeout  as e:
                print(e)
                responses.append({'idx':i, 'secret': row['secret'], 'task':row['topic'],'error': str(e)})
                continue
            except genai.errors.ClientError as e:
                print(e)
                responses.append({'idx':i, 'secret': row['secret'], 'task':row['topic'],'error': str(e)})
                sleep(10)
                continue

        


    if len(responses) > 0:
        filename = f"{OUTPUT_DIR}/batch-{CURRENT_B}.json"
        print(f"Saving batch at {filename}")
        save_json(responses, filename)
    


    LAST_BATCH = None

    already_computed = sorted([int(f.split('.')[0].split('-')[1]) for f in os.listdir(OUTPUT_DIR) if f.endswith('.json') and f.startswith('batch')])
    if len(already_computed)>0:
        LAST_BATCH = already_computed[-1]
    print("LAST_BATCH computed-->", LAST_BATCH)

    all_responses=[]
    if LAST_BATCH is not None:
        for i in range(LAST_BATCH+1):
            all_responses.extend(load_json(OUTPUT_DIR+f'/batch-{i}.json'))
    print("already computed-->", len(all_responses))

    return all_responses



# In[ ]:
if len(data) > len(conversations):
    print("Not all conversations available")
    data = data[:len(conversations)]
    print("len(data)", len(data))

for model_name in model_names:
    os.makedirs(f'answers_conversations/{GROUP_TYPE}-social-{DEFENSE_STRATEGY}/{model_name}', exist_ok=True)
    OUTPUT_PATH = f'answers_conversations/{GROUP_TYPE}-social-{DEFENSE_STRATEGY}/{model_name}/test-conversation{CONFIG}{MODALITY}-responses.json'
    print(OUTPUT_PATH)
    
    if os.path.exists(OUTPUT_PATH) and not redo:
        responses = load_json(OUTPUT_PATH)
        if len(data) > len(responses):
            print("Continue generation, len(data)", len(data), "len(responses)", len(responses))
            responses = generate_all(data, model_name)
            save_json(responses, OUTPUT_PATH)
    elif not os.path.exists(OUTPUT_PATH) or redo:
        responses = generate_all(data, model_name)
        save_json(responses, OUTPUT_PATH)
    else:
        responses = load_json(OUTPUT_PATH)


    print(len(responses))





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




