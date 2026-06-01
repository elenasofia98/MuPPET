# MuPPET

LLM agents are increasingly deployed in multi-party environments, handling sensitive personal data on behalf of individual users, for instance in group chats. When such an agent discloses private information, it reaches every group member at once. This risk is structurally harder to control than in one-to-one settings, as every piece of private information must be appropriate for every recipient in the group. Yet all existing contextual privacy benchmarks consider only single-interlocutor settings, leaving multi-party privacy risks unmeasured. 

We introduce **MuPPET** (**Mu**lti-**P**arty **P**rivacy **E**xposure **T**esting), a benchmark for contextual privacy in multi-party conversations. Our experiments show that models leak substantially more in multi-party settings than one-to-one evaluations suggest. Frontier models are vulnerable, and smaller open-weights models, often preferred for local deployment with sensitive data, even more so. Existing contextual privacy defences offer only partial protection, degrade utility, and do not resolve the underlying party-tracking problem.

## Data



## Replicate


### Enviroment variables

In a file in the main directory ``env.json`` insert the OpenAI API key, ``HF_TOKEN`` and project name for the Google Cloud project.

### Set up a local enviroment
Create a local enviroment, e.g. ``python -m venv ./muppet-bench`` and activate it ``.\muppet-bench\Scripts\activate``.

Then install the requirements: ```pip install -r .\requirements.txt```

## Load data