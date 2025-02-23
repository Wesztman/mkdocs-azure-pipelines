import re

import yaml

START_TAG_PATTERN = r"#:::(\w+)-start:::"
END_TAG_PATTERN = r"#:::(\w+)-end:::"
CODE_BLOCK_TAG = "#:::code-block:::"

ALLOWED_TAGS = [
    "title",
    "about",
    "outputs",
    "example",
    "code",
]


def find_tags(expression: str, string: str) -> list:
    return re.findall(expression, string)


def extract_section_content(content: str, section_name: str) -> str | None:
    pattern = rf"#:::{section_name}-start:::(.*?)#:::{section_name}-end:::"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        section_text = match.group(1).strip()
        section_text = re.sub(r"^# ", "", section_text, flags=re.MULTILINE)
        # Handle code blocks
        if CODE_BLOCK_TAG in section_text:
            section_text = section_text.replace(CODE_BLOCK_TAG, "")
            return f"```yaml\n{section_text.strip()}\n```"

        return section_text.strip()
    return None


def extract_parameters(content: str) -> str | None:
    try:
        yaml_content = yaml.safe_load(content)
        if yaml_content is None:
            return None
        for key, value in yaml_content.items():
            if key == "parameters":
                return f"```yaml\n{
                    yaml.dump({key: value}, default_flow_style=False).strip()
                }\n```"
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}")
    return None


def process_pipeline_file(input_file: str) -> str | None:
    # Read the input pipeline file
    with open(input_file, encoding="utf-8") as f:
        content = f.read()

    start_tags = find_tags(START_TAG_PATTERN, content)
    end_tags = find_tags(END_TAG_PATTERN, content)

    # Check for misspelled tags or tag mismatches
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

    # Create Markdown documentation
    markdown_content = ""

    # Extract and add title
    title = extract_section_content(content, "title")
    if title is not None:
        markdown_content += f"# {title}\n\n"

    # Extract and add parameters
    parameters = extract_parameters(content)
    if parameters is not None:
        markdown_content += "## Parameters\n\n"
        markdown_content += f"{parameters}\n\n"

    # Extract and add other sections
    for section_name in ALLOWED_TAGS[1:]:  # Exclude title
        section_content = extract_section_content(content, section_name)
        if section_content is not None:
            markdown_content += f"## {section_name.capitalize()}\n\n"
            markdown_content += f"{section_content}\n\n"

    return markdown_content
