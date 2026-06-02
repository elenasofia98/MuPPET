import json
import os
from ast import literal_eval

import pandas as pd
import numpy as np

class Dataset:
    def __init__(self, group_type, config='-ub', modality='-bc'):
        self.group_type = group_type
        self.config = config
        self.modality = modality
        self.task_type = group_type.split('_')[1] if '_' in group_type else group_type

        self.groups = self.load_json(f'MuPPET_data/users_{group_type}.json')
        self.sensitive_tasks = self.load_json(f'MuPPET_data/seeds/{self.task_type}-social/basic_tasks.json')
        self.sensitive_tasks_social = self.load_json(f'MuPPET_data/seeds/{self.task_type}-social/ai_on_user_behalf.json')
        self.users_distr = self.load_json(f"./MuPPET_data/users/{self.group_type}{self.modality}/user_names.json")

        self.mapping_social_tasks = self._build_mapping_social_tasks()

    @staticmethod
    def load_json(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def save_json(data, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    @staticmethod
    def _list_batch_indices(folder):
        return sorted(
            int(f.split('.')[0].split('-')[1])
            for f in os.listdir(folder)
            if f.endswith('.json') and f.startswith('batch-')
        )

    def _build_mapping_social_tasks(self):
        return {
            task: {
                secret: {
                    self.sensitive_tasks[task][secret][i]: self.sensitive_tasks_social[task][secret][i]
                    for i in range(len(self.sensitive_tasks[task][secret]))
                }
                for secret in self.sensitive_tasks[task]
            }
            for task in self.sensitive_tasks
        }

    def load_memories(self):
        folder = f'MuPPET_data/memories/{self.group_type}{self.modality}'
        return [
            entry
            for batch_index in self._list_batch_indices(folder)
            for entry in self.load_json(os.path.join(folder, f'batch-{batch_index}.json'))
        ]

    def load_conversations(self):
        folder = f'MuPPET_data/conversations{self.config}/{self.group_type}{self.modality}-social'
        return [
            entry
            for batch_index in self._list_batch_indices(folder)
            for entry in self.load_json(os.path.join(folder, f'batch-{batch_index}.json'))
        ]

    def filter_memories(self, memories):
        filtered = []
        secret_holders = []
        
        for memory in memories:
            if 'error' in memory or 'error' in memory.get('content', {}):
                continue
            
            shc = []
            found_correct_formatting = False
            for member in memory['content'].get('members', []):
                if member.get('sensitive_information'):
                    member_correct_formatting = (
                        member['first_name'] + member['last_name']
                        == memory['user_with_secret']['First Name'] + memory['user_with_secret']['Last Name']
                    )
                    if member_correct_formatting:
                        shc.append(member)
                        found_correct_formatting = True

            if found_correct_formatting:
                filtered.append(memory)
                secret_holders.append(shc[0])
        self.users_distr = [x for i,x in enumerate(self.users_distr) if i in filtered]
        return filtered, secret_holders

    def load_data_frame(self):
        csv_path = f'MuPPET_data/conversations-ub/{self.group_type}{self.modality}-social_memories_and_secrets.csv'
        data = pd.read_csv(csv_path)
        for column in ['members', 'member_notes']:
            data[column] = data[column].apply(literal_eval)
        return data

    def load_dataset(self, add_user_distr=None):
        memories = self.load_memories()
        conversations = self.load_conversations()
        filtered_memories, secret_holders = self.filter_memories(memories)
        data = self.load_data_frame()

        data['secret'] = [memory['secret'] for memory in filtered_memories]
        data['secret_holder'] = secret_holders
        data['agent_task'] = [
            self.mapping_social_tasks[memory['topic']][memory['secret']][memory['agent_task']]
            for memory in filtered_memories
        ]

        if add_user_distr is not None:
            np.random.seed(42)
            user_subset = []
            for u in self.users_distr:
                s = {}
                s['know'] = np.random.choice(u['know'], add_user_distr, replace=False)
                s['not_know'] = np.random.choice(u['not_know'], add_user_distr, replace=False)
                user_subset.append(s)

            user_subset = pd.DataFrame(user_subset)
            data = pd.concat([data, user_subset], axis=1)

        return data, conversations, filtered_memories
