import json

def json_to_llm_text(data, indent=0, mode="pretty"):
    """
    Convert JSON-like Python data into a structured text for LLMs.

    mode="pretty" -> readable indented format
    mode="compact" -> single-line CSV-like format
    """
    if mode == "compact":
        if isinstance(data, list):
            if all(isinstance(item, dict) for item in data):
                # Extract headers
                headers = sorted({key for obj in data for key in obj.keys()})
                lines = [", ".join(headers)]
                for obj in data:
                    row = [str(obj.get(h, "")) for h in headers]
                    lines.append(", ".join(row))
                return "\n".join(lines)
            else:
                return ", ".join(map(str, data))
        elif isinstance(data, dict):
            return ", ".join(f"{k}={v}" for k, v in data.items())
        else:
            return str(data)

    # Pretty mode (indented)
    text_lines = []
    prefix = "  " * indent

    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                text_lines.append(f"{prefix}{key}:")
                text_lines.append(json_to_llm_text(value, indent + 1, mode))
            else:
                text_lines.append(f"{prefix}{key}: {value}")

    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                text_lines.append(f"{prefix}- {json_to_llm_text(item, indent + 1, mode).strip()}")
            else:
                text_lines.append(f"{prefix}- {item}")

    else:
        text_lines.append(f"{prefix}{data}")

    return "\n".join(text_lines)

if __name__ == "__main__":
    # Example JSON input
    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    llm_text = json_to_llm_text(data, mode="pretty")
    with open("output_compact.txt", "w", encoding="utf-8") as f:
        f.write(llm_text)
