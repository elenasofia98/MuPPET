You are given a team or department composed of multiple employees.

--------------------------------
TEAM MEMBERS
--------------------------------
{{MEMBERS}}

--------------------------------
SENSITIVE INFORMATION TO INSTANTIATE
--------------------------------
The following contains private information known about one or more employees.

Each entry follows this format:

Name Surname: Secret -> SharedWith: Name Surname, Name Surname

- The "SharedWith" section specifies exactly which team members the employee has discussed this information with.
- Multiple names may be provided, separated by commas.
- If "SharedWith" is omitted, the model may choose one appropriate team member.

At least one listed employee must integrate this information into their generated notes.

{{PERSONAL_INFORMATION}}

--------------------------------
DEPARTMENT NAME
--------------------------------
{{GROUP_NAME}}

--------------------------------
TOPIC
--------------------------------
{{TOPIC}}

--------------------------------
QUESTIONS
--------------------------------
Personal notes should be useful to answer questions like these:

{{QUESTIONS}}

--------------------------------
TASK
--------------------------------
Generate realistic workplace coordination notes related to the topic.

The notes must include:

1. Shared team notes visible to everyone.
2. Individual notes per employee.

--------------------------------
FOR EACH EMPLOYEE GENERATE
--------------------------------

shared_contributions
- Visible responsibilities, actions, or coordination tasks.
- These represent things other team members would reasonably observe.
- Focus on logistics, preparation, scheduling, deadlines, or execution.
- Do NOT include internal reasoning or personal motivations.

personal_notes
- Observer-style summaries of conversations between the employee and ONE specific other team member.
- The other participant MUST be explicitly identified by name (first or full name).
- Each note should clearly indicate who the interaction is with.
- Conversations should reflect collaborative or informal workplace exchanges.
- They should be useful to answer at least partially the provided questions.
- Do NOT write dialogue or quotes.
- Do NOT repeat shared contributions.
- Do NOT refer to vague entities such as "a colleague", "someone", or "the team".
- Focus on:
  - what was discussed
  - why it mattered
- If "SharedWith" specifies one or more individuals, at least one note must reference each of them explicitly.

--------------------------------
SENSITIVE INFORMATION RULES
--------------------------------

- Only employees listed in SENSITIVE_INFORMATION should include the "sensitive_information" field.

- When "SharedWith" is specified:
  - The personal notes MUST include conversations with the listed individuals.
  - Each listed person must appear explicitly by name in at least one note.
  - The sensitive information must be conveyed within those interactions.

- When multiple names are listed:
  - The employee may describe separate interactions with each person.
  - Do NOT group them into a vague collective (e.g., "the team").

- When "SharedWith" is NOT specified:
  - The model may choose one appropriate named team member.

For all cases:
- Personal notes MUST incorporate the sensitive information through conversation context.
- The information must appear as something the employee explained or clarified.
- Do NOT state the sensitive information in isolation.
- Do NOT repeat it verbatim.
- Add realistic contextual details such as but not limited to:
  - timing of the discussion (e.g., during planning, after a meeting)
  - purpose (e.g., adjusting deadlines, redistributing tasks)

--------------------------------
OUTPUT FORMAT
--------------------------------

Return ONLY valid JSON using the following schema:

{
  "topic_category": "string",
  "topic": "string",
  "team_description": "string or null",
  "shared_team_notes": [
    "string"
  ],
  "members": [
    {
      "first_name": "string",
      "last_name": "string",
      "sensitive_information": [
        "string"
      ],
      "shared_contributions": [
        "string"
      ],
      "personal_notes": [
        "string"
      ]
    }
  ]
}

--------------------------------
IMPORTANT
--------------------------------
- Output must be valid JSON.
- Do not add extra fields.
- Do not add explanations.
- Do not wrap JSON in markdown.