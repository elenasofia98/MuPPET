from dataclasses import dataclass, asdict
from typing import List, Dict
from datetime import datetime
from .utils import process_markdown

@dataclass
class AgentIdentity:
    name: str
    role: str


@dataclass
class UserMemory:
    name: str
    memories: List[str]

@dataclass
class UserDescription:
    name: str
    description: str



@dataclass
class SystemPrompt:
    agent_identity: str
    owner_user: str
    group_member_list: str
    shared_group_memory: str
    user_memory_block: str


@dataclass
class ChatMessage:
    speaker: str
    content: str


@dataclass
class UserMessage:
    message_hist: str
    current_message: str



def render_agent_identity(agent:AgentIdentity, input_template='./prompts/agent_identity.md'):
    variables = asdict(agent)
    agent_identity = process_markdown(
        input_path=input_template,
        variables=variables,
        use_env=False,
        fail_on_missing=True
    )

    return agent_identity


def render_users_memories(users: List[UserMemory], input_template='./prompts/user_memory.md') -> str:
    rendered = []

    for user in users:
        memories = "\n".join(f"- {m}" for m in user.memories)
        variables = asdict(user)
        variables['memories'] = memories
        
        user_memory_block = process_markdown(
            input_path=input_template,
            variables=variables,
            use_env=False,
            fail_on_missing=True
        )
        rendered.append(user_memory_block)

    return "\n".join(rendered)

def render_user_memory(user: UserMemory, input_template='./prompts/user_memory.md') -> str:
    memories = "\n".join(f"- {m}" for m in user.memories)
    variables = asdict(user)
    variables['memories'] = memories
    
    user_memory_block = process_markdown(
        input_path=input_template,
        variables=variables,
        use_env=False,
        fail_on_missing=True
    )

    return user_memory_block


def render_users_descriptions(users: List[UserDescription], input_template='./prompts/user_description.md') -> str:
    rendered = []

    for user in users:
        variables = asdict(user)
        
        user_description_block = process_markdown(
            input_path=input_template,
            variables=variables,
            use_env=False,
            fail_on_missing=True
        )
        rendered.append(user_description_block)

    return "\n".join(rendered)


def build_system_prompt(
    agent: AgentIdentity,
    owner_user: str,
    user_memory: UserMemory,
    users_descriptions: List[UserDescription],
    shared_memory: List[str] = None,
    shared_memory_preformatted: str = None,
    private_chat_user=None,
    defense_strategy=None
) -> str:

    agent_identity = render_agent_identity(agent)
    group_member_list = render_users_descriptions(users_descriptions)

    if shared_memory is not None:
        shared_memory_block = "\n".join(
            f"- {m}" for m in shared_memory
        )
    if shared_memory_preformatted is not None:
        shared_memory_block = shared_memory_preformatted

    user_memory_block = render_user_memory(user_memory)



    system_prompt = SystemPrompt(
        agent_identity=agent_identity,
        owner_user=owner_user,
        group_member_list=group_member_list,
        shared_group_memory=shared_memory_block,
        user_memory_block=user_memory_block)
    variables= asdict(system_prompt)
    variables['private_chat_user']=private_chat_user
    system_prompt = process_markdown(
            input_path='./prompts/system_1o1.md' if defense_strategy is None else  f'./prompts/defense-prompts/system-{defense_strategy}.md',
            variables=variables,
            use_env=False,
            fail_on_missing=True
        )
    
    return system_prompt


def render_message(msg: ChatMessage,  input_template='./prompts/message.md'):
    variables = asdict(msg)
    message_block = process_markdown(
        input_path=input_template,
        variables=variables,
        use_env=False,
        fail_on_missing=True
    )
    return message_block



def render_message_hist(message_hist: List[ChatMessage], input_template="./prompts/history.md") -> str:
    message_hist = []
    for msg in message_hist:
        message_block = render_message(msg)
        message_hist.append(message_block)

    message_hist_block = "\n".join(message_hist)
    
    return message_hist_block



def build_user_prompt(
    agent_name:str,
    owner_user:str,
    message_hist: List[ChatMessage],
    current_message: ChatMessage,
    private_chat_user:str,
    defense_strategy=None
) -> str:
    
    message_hist_block = []
    for msg in message_hist:
        message_block = render_message(msg)
        message_hist_block.append(message_block)
    message_hist_block = "\n\n".join(message_hist_block)
    
    current_message = render_message(current_message)

    user_message = UserMessage(
        message_hist=message_hist_block,
        current_message=current_message
    )
    variables = asdict(user_message)
    variables['agent_name'] = agent_name
    variables['owner_user'] = owner_user
    variables['private_chat_user']=private_chat_user
    message_prompt = process_markdown(
            input_path='./prompts/user_message_1o1.md' if defense_strategy is None else f'./prompts/defense-prompts/user_message-{defense_strategy}.md',
            variables=variables,
            use_env=False,
            fail_on_missing=True
        )
    
    return message_prompt
