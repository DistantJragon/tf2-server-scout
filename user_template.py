import re
from collections.abc import Callable

# Define a type alias for the template function.
type TemplateFunction = Callable[[dict[str, str]], str]


# Compile the template into a callable "render" function.
def compile_template(template: str) -> TemplateFunction:
    # Match patterns like {name} - simple non-nested placeholders.
    pattern = re.compile(r"\{([^}]+)\}")
    parts: list[Callable[[dict[str, str]], str] | str] = []
    last_index = 0

    # Loop through all matches, capturing literal text and keys.
    for match in pattern.finditer(template):
        start, end = match.span()
        # Append the literal part before the placeholder.
        if start > last_index:
            parts.append(template[last_index:start])
        key = match.group(1)
        # For each placeholder, append a lambda that looks up the key.
        parts.append(lambda values, key=key: str(
            values.get(key, f"{{{key}}}")))
        last_index = end

    # Append any remaining literal text.
    if last_index < len(template):
        parts.append(template[last_index:])

    # Return a render function that accepts a dictionary.
    def render(values: dict[str, str]) -> str:
        # For each part, either use it directly (if string) or call it.
        return "".join(part(values) if callable(part) else part for part in parts)

    return render
