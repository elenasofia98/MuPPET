import re
import os
from pathlib import Path
from typing import Dict, Optional


VARIABLE_PATTERN = re.compile(r"\{\{(.*?)\}\}")


def load_markdown(file_path: str) -> str:
    """Load markdown file content."""
    return Path(file_path).read_text(encoding="utf-8")


def save_markdown(file_path: str, content: str) -> None:
    """Save updated markdown content."""
    Path(file_path).write_text(content, encoding="utf-8")


def replace_variables(
    content: str,
    variables: Optional[Dict[str, str]] = None,
    use_env: bool = False,
    fail_on_missing: bool = False,
) -> str:
    """
    Replace {{variables}} in markdown content.

    Args:
        content: Original markdown content
        variables: Dictionary of replacement values
        use_env: If True, fallback to environment variables
        fail_on_missing: If True, raise error if variable not found
    """

    variables = variables or {}

    def replacer(match):
        key = match.group(1).strip()

        if key in variables:
            return str(variables[key])

        if use_env and key in os.environ:
            return os.environ[key]

        if fail_on_missing:
            raise ValueError(f"Missing value for variable: {key}")

        return match.group(0)  # Leave unchanged if not found

    return VARIABLE_PATTERN.sub(replacer, content)


def process_markdown(
    input_path: str,
    variables: Optional[Dict[str, str]] = None,
    use_env: bool = False,
    fail_on_missing: bool = False,
) -> None:
    """
    Load, process, and save markdown file.
    """
    content = load_markdown(input_path)
    updated_content = replace_variables(
        content,
        variables=variables,
        use_env=use_env,
        fail_on_missing=fail_on_missing,
    )

    #save_path = output_path or input_path
    return updated_content
    



####
def test(output_path=None):
    variables = {
       "conversation_history": "this is con history",
        "current_user_name": "Alice",
        "current_user_id": "00",
        "current_message" : "Hello!",
        "agent_name": "Andy"
    }
    
    updated_content = process_markdown(
        input_path="prompts/user_message.md",
        variables=variables,
        use_env=False,
        fail_on_missing=True,
    )
    print("Markdown processed successfully.")
    
    if output_path:
        save_markdown(output_path, updated_content)
    
    return updated_content