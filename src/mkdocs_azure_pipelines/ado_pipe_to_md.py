import re
from io import StringIO

from ruamel.yaml import YAML

START_TAG_PATTERN = r"#:::(\w+)-start:::"
END_TAG_PATTERN = r"#:::(\w+)-end:::"

ALLOWED_TAGS = [
    "title",
    "about",
    "outputs",
    "example",
]

yaml = YAML()


def find_tags(expression: str, string: str) -> list:
    return re.findall(expression, string)


def extract_section_content(content: str, section_name: str) -> str | None:
    pattern = rf"#:::{section_name}-start:::(.*?)#:::{section_name}-end:::"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        section_text = match.group(1).strip()
        section_text = re.sub(r"^# ", "", section_text, flags=re.MULTILINE)
        # Wrap the example section in a code block
        if section_name == "example":
            return f"```yaml\n{section_text}\n```"
        return section_text.strip()
    return None


def extract_parameters(content: str) -> str | None:
    try:
        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.width = 1000
        yaml.indent(mapping=2, sequence=4, offset=2)
        yaml_content = yaml.load(content)
        if yaml_content is None or "parameters" not in yaml_content:
            return None
        stream = StringIO()
        yaml.dump({"parameters": yaml_content["parameters"]}, stream)
        parameters_content = stream.getvalue().strip()
        return f"```yaml\n{parameters_content}\n```"
    except Exception as e:
        print(f"Error parsing YAML: {e}")
        return None


def extract_code(content: str) -> str | None:
    try:
        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.width = 1000
        yaml.indent(mapping=2, sequence=4, offset=2)
        yaml_content = yaml.load(content)
        if yaml_content is None:
            return None
        for key in ["steps", "jobs", "stages"]:
            if key in yaml_content:
                stream = StringIO()
                yaml.dump({key: yaml_content[key]}, stream)
                code_content = stream.getvalue().strip()
                return f"```yaml\n{code_content}\n```"
    except Exception as e:
        print(f"Error parsing YAML: {e}")
        return None


def extract_trigger(content: str) -> str | None:
    try:
        yaml = YAML()
        yaml.preserve_quotes = True  # Keeps quotes as in the original YAML
        yaml.width = 1000  # Prevents line wrapping
        yaml.indent(mapping=2, sequence=4, offset=2)  # Ensure correct list indentation

        yaml_content = yaml.load(content)

        if yaml_content is None or "trigger" not in yaml_content:
            return None

        stream = StringIO()
        yaml.dump({"trigger": yaml_content["trigger"]}, stream)  # Preserves comments
        trigger_content = stream.getvalue().strip()

        return f"```yaml\n{trigger_content}\n```"

    except Exception as e:
        print(f"Error parsing YAML: {e}")
        return None


def extract_pool(content: str) -> str | None:
    try:
        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.width = 1000
        yaml.indent(mapping=2, sequence=4, offset=2)
        yaml_content = yaml.load(content)
        if yaml_content is None or "pool" not in yaml_content:
            return None
        stream = StringIO()
        yaml.dump({"pool": yaml_content["pool"]}, stream)
        pool_content = stream.getvalue().strip()
        return f"```yaml\n{pool_content}\n```"
    except Exception as e:
        print(f"Error parsing YAML: {e}")
        return None


def extract_variables(content: str) -> str | None:
    try:
        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.width = 1000
        yaml.indent(mapping=2, sequence=4, offset=2)
        yaml_content = yaml.load(content)
        if yaml_content is None or "variables" not in yaml_content:
            return None
        stream = StringIO()
        yaml.dump({"variables": yaml_content["variables"]}, stream)
        variables_content = stream.getvalue().strip()
        return f"```yaml\n{variables_content}\n```"
    except Exception as e:
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
    # Extract and add other sections
    for section_name in ALLOWED_TAGS[1:]:  # Exclude title
        section_content = extract_section_content(content, section_name)
        if section_content is not None:
            markdown_content += f"## {section_name.capitalize()}\n\n"
            markdown_content += f"{section_content}\n\n"
    # Extract and add trigger
    trigger = extract_trigger(content)
    if trigger is not None:
        markdown_content += "## Triggers\n\n"
        markdown_content += f"{trigger}\n\n"
    # Extract and add pool
    pool = extract_pool(content)
    if pool is not None:
        markdown_content += "## Pool\n\n"
        markdown_content += f"{pool}\n\n"
    # Extract and add variables
    variables = extract_variables(content)
    if variables is not None:
        markdown_content += "## Variables\n\n"
        markdown_content += f"{variables}\n\n"
    # Extract and add parameters
    parameters = extract_parameters(content)
    if parameters is not None:
        markdown_content += "## Parameters\n\n"
        markdown_content += f"{parameters}\n\n"
    # Extract and add code
    code = extract_code(content)
    if code is not None:
        markdown_content += "## Code\n\n"
        markdown_content += f"{code}\n\n"
    return markdown_content
