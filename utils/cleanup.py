import re


def remove_thinking(response: str) -> str:
    response = re.sub(
        r"<think>.*?</think>",
        "",
        response,
        flags=re.DOTALL,
    )

    return response.strip()
