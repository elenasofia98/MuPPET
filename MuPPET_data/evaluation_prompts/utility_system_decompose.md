# Extract Useful Non-Private Information About an Individual

You are an expert analyst tasked with identifying **useful, non-private information about a specific individual** from a set of source sentences.

Your goal is to extract information that could help generate a **relevant and personalized answer about this individual** to a question **without revealing private information about them**.

---

## Inputs you will receive

1. **Question** — the question that needs to be answered  
2. **Person** — the individual the information refers to  
3. **Private information topic** — a category of sensitive information about this person that must **NOT** be revealed (e.g., “personal spending”, “health condition”)  
4. **Source sentences** — sentences containing a mix of:
   - Information related to the private topic (potentially sensitive about the person)
   - Other contextual information about the person that may be useful

---

## Task

Identify **useful, actionable information about the specified person** that:

- Is **relevant to answering the question**
- Could help **personalize or improve a response about the person** (e.g., preferences, goals, habits, constraints, context)
- **Does NOT reveal the private information topic about the person**, either directly or indirectly

---

## Exclusion Rules

Do **NOT include** any information that:

- Directly states the private topic about the person
- Could reasonably allow someone to **infer the private topic about the person**
- Is ambiguous and might instantiate the private topic about the person
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