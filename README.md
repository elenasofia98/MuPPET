# MuPPET

LLM agents are increasingly deployed in multi-party environments, handling sensitive personal data on behalf of individual users, for instance in group chats. When such an agent discloses private information, it reaches every group member at once. This risk is structurally harder to control than in one-to-one settings, as every piece of private information must be appropriate for every recipient in the group. Yet all existing contextual privacy benchmarks consider only single-interlocutor settings, leaving multi-party privacy risks unmeasured. 

We introduce **MuPPET** (**Mu**lti-**P**arty **P**rivacy **E**xposure **T**esting), a benchmark for contextual privacy in multi-party conversations. Our experiments show that models leak substantially more in multi-party settings than one-to-one evaluations suggest. Frontier models are vulnerable, and smaller open-weights models, often preferred for local deployment with sensitive data, even more so. Existing contextual privacy defences offer only partial protection, degrade utility, and do not resolve the underlying party-tracking problem.

## Data



## Replicate


### Enviroment variables

In a file in the main directory ``env.json`` insert the OpenAI API key, ``HF_TOKEN`` and project name for the Google Cloud project.

### Set up a local enviroment
Create a local enviroment, e.g. ``python -m venv ./muppet-bench`` and activate it ``source muppet-bench/bin/activate`` (or ``.\muppet-bench\Scripts\activate``).

Then install the requirements: ```pip install -r .\requirements.txt```

## Load data

The dataset logic is implemented in `dataset.py` via the `Dataset` class. It loads:

- users metadata from `MuPPET_data/users_large20_workplace.json`
- task definitions from `MuPPET_data/seeds/workplace-social/basic_tasks.json`
- privacy-sensitive task mappings from `MuPPET_data/seeds/workplace-social/ai_on_user_behalf.json`
- precomputed memories from `MuPPET_data/memories/large20_workplace<modality>` batches
- conversations from `MuPPET_data/conversations<config>/large20_workplace<modality>-social` batches
- the main conversation dataframe from `MuPPET_data/conversations-ub/large20_workplace<modality>-social_memories_and_secrets.csv`

The loader performs these steps:

1. instantiate `Dataset(group_type, config, modality)`
2. call `dataset.load_dataset()`
3. the result is `data, conversations, filtered_memories`

The returned `data` frame includes additional columns for:

- `secret` — the private item for the current row
- `secret_holder` — the user holding the secret
- `agent_task` — the defense-task mapping used for that row

The benchmark scripts use this shared data loading pipeline to build prompts and evaluate model responses.

## Benchmark scripts

The repository includes a set of ``test-conversations-*.py`` scripts that run the MuPPET benchmark against different model backends:

- ``test-conversations-ub-workplace-social-gemini.py`` and ``test-conversations-ub-workplace-social-gemini-DefensePrompting.py`` for Vertex AI / Gemini models.
- ``test-conversations-ub-workplace-social-openai.py`` and ``test-conversations-ub-workplace-social-openai-DefensePrompting.py`` for OpenAI models.
- ``test-conversations-ub-workplace-social-hf.py`` and ``test-conversations-ub-workplace-social-hf-DefensePrompting.py`` for Hugging Face models.

These scripts use the shared ``conversation_runner.py`` pipeline and centralized agent logic in ``agents.py`` to build prompts, generate responses, and save batch outputs.

