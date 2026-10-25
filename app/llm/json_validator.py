import json
from typing import Any


def parse_json(text: str) -> Any:
    """Parse strict JSON and provide a useful error when model output is invalid."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        preview = cleaned[:240].replace("\n", " ")
        raise ValueError(
            f"Ollama returned invalid or incomplete JSON at line {exc.lineno}, "
            f"column {exc.colno}: {exc.msg}. Output preview: {preview!r}"
        ) from exc
