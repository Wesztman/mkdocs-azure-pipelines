import re
from io import StringIO
from pathlib import Path

from ruamel.yaml import YAML

START_TAG_PATTERN = r"#:::(\w+)-start:::"
END_TAG_PATTERN = r"#:::(\w+)-end:::"

ALLOWED_TAGS = [
    "title",
    "about",
    "outputs",
    "example",
]


def get_yaml_instance() -> YAML:
    """
    Create and return a YAML instance with common configuration.
    """
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.width = 1000
    yaml.indent(mapping=2, sequence=4, offset=2)
    return yaml


def find_tags(pattern: str, text: str) -> list:
    """
    Find all tags in text matching the given regex pattern.
    """
    return re.findall(pattern, text)


def extract_section_content(content: str, section_name: str) -> str | None:
    """
    Extract content between start and end tags for a given section.
    If section_name is "example", wraps the content in a YAML code block.
    Removes only the initial "# " from each line while preserving additional spaces.
    """
    pattern = rf"#:::{section_name}-start:::(.*?)#:::{section_name}-end:::"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        section_text = match.group(1).lstrip("\n").rstrip("\n")
        # Remove only the first occurrence of "# " from each line.
        section_text = re.sub(r"^(\s*)#\s", r"\1", section_text, flags=re.MULTILINE)
        if section_name == "example":
            return f"```yaml\n{section_text}\n```"
        return section_text
    return None


def extract_yaml_section(content: str, fields: list[str]) -> str | None:
    """
    Extract the first found field from a list of possible fields in the YAML content.
    Returns the content in a YAML code block.
    """
    try:
        yaml = get_yaml_instance()
        data = yaml.load(content)
        if not data:
            return None
        for field in fields:
            if field in data:
                stream = StringIO()
                yaml.dump({field: data[field]}, stream)
                return f"```yaml\n{stream.getvalue().strip()}\n```"
        return None
    except Exception as e:
        print(f"Error parsing YAML for '{fields}': {e}")
        return None


def process_pipeline_file(input_file: str) -> str | None:
    """
    Process a pipeline file to generate Markdown documentation.
    Validates tag usage and extracts various sections and YAML blocks.
    """
    with open(input_file, encoding="utf-8") as f:
        content = f.read()

    start_tags = find_tags(START_TAG_PATTERN, content)
    end_tags = find_tags(END_TAG_PATTERN, content)

    # Validate tags
    if any(tag not in ALLOWED_TAGS for tag in start_tags):
        print("Found misspelled start tags.")
        print("Allowed tags are:", ", ".join(ALLOWED_TAGS))
        return None
    if any(tag not in ALLOWED_TAGS for tag in end_tags):
        print("Found misspelled end tags.")
        print("Allowed tags are:", ", ".join(ALLOWED_TAGS))
        return None
    if len(start_tags) != len(end_tags) or set(start_tags) != set(end_tags):
        print("Tag mismatch error.")
        print("Start tags:", start_tags)
        print("End tags:", end_tags)
        return None

    markdown_content = ""

    # Extract and add title
    title = extract_section_content(content, "title")
    if title is not None:
        markdown_content += f"# {title}\n\n"
    else:
        processed_filename = (
            Path(input_file)
            .stem.capitalize()
            .replace("_", " ")
            .replace("-", " ")
            .replace(".", " ")
            .strip()
        )
        markdown_content += f"# {processed_filename}\n\n"

    # Extract and add allowed sections (excluding title)
    for section_name in ALLOWED_TAGS[1:]:
        section_content = extract_section_content(content, section_name)
        if section_content is not None:
            markdown_content += (
                f"## {section_name.capitalize()}\n\n{section_content}\n\n"
            )

    # Extract and add additional YAML fields
    for fields, header in [
        (["trigger"], "Triggers"),
        (["resources"], "Resources"),
        (["pool"], "Pool"),
        (["variables"], "Variables"),
        (["parameters"], "Parameters"),
        (["steps", "jobs", "stages"], "Code"),
    ]:
        result = extract_yaml_section(content, fields)
        if result is not None:
            markdown_content += f"## {header}\n\n{result}\n\n"

    return markdown_content
