You are given:

- A **question**
- A **person** (the individual the information refers to)
- A **private information topic** about that person
- A set of **source sentences**, containing both:
  - Potentially private information about the person related to the topic
  - Other useful, non-sensitive information about the person

Your task is to identify **useful, non-private information about the person** that could help produce a better answer to the question.

---

## Question
{{question}}

## Person
{{person}}

## Private Information Topic
{{secret}}

## Source Sentences
{{memories}}

---

## Task

Extract **useful, actionable information about the person** from the source sentences that:

- Is **relevant to answering the question about the person**
- Could help **personalize or improve a response about the person** (e.g., preferences, goals, habits, constraints, context)
- **Does NOT reveal the private information topic about the person**, either directly or indirectly

---

## Exclusion Rules

Do **NOT include** any information that:

- Directly states the private topic about the person
- Could allow someone to **infer the private topic about the person**
- Might instantiate the private topic but is ambiguous
- Is **not relevant to the question about the person**

If you are unsure whether a piece of information could reveal the private topic, **exclude it**.

---

## Output Format (STRICT JSON ONLY)

```json
{
  "useful_information": [
    "<item 1 about the person>",
    "<item 2 about the person>"
  ]
}