from __future__ import annotations

import argparse
import re
from typing import Sequence


START_TAG_PATTERN = r"#:::(\w+)-start:::"
END_TAG_PATTERN = r"#:::(\w+)-end:::"

ALLOWED_TAGS = [
    "title",
    "about",
    "parameters",
    "outputs",
    "example",
    "code",
]


def findtags(expression: str, string: str) -> list:
    return re.findall(expression, string)


def process_pipeline_file(input_file):
    # Read the input pipeline file
    with open(input_file, encoding="utf-8") as f:
        content = f.read()

    start_tags = re.findall(START_TAG_PATTERN, content)
    for tag in start_tags:
        if tag not in ALLOWED_TAGS:
            print(f"Found misspelled start tag: #:::{tag}-start:::")
            print("Allowed tags are:", ", ".join(ALLOWED_TAGS))
            return

    end_tags = re.findall(END_TAG_PATTERN, content)
    for tag in end_tags:
        if tag not in ALLOWED_TAGS:
            print(f"Found misspelled end tag: #:::{tag}-end:::")
            print("Allowed tags are:", ", ".join(ALLOWED_TAGS))
            return

    # Check for tag mismatches
    if len(start_tags) != len(end_tags):
        print(
            "Tag mismatch error: Number of start tags does not match the number of \
            end tags.",
        )
        print(f"Start tags: {start_tags}")
        print(f"End tags: {end_tags}")
        return

    for start_tag, end_tag in zip(start_tags, end_tags):
        if start_tag != end_tag:
            print(
                f"Tag mismatch error: Start tag #{start_tag} does not match end tag \
                #{end_tag}.",
            )
            return

    # Extract content between markers and remove leading '#' characters
    title = re.search(
        r"#:::title-start:::(.*?)#:::title-end:::",
        content,
        re.DOTALL,
    )
    about = re.search(
        r"#:::about-start:::(.*?)#:::about-end:::",
        content,
        re.DOTALL,
    )
    parameters = re.search(
        r"#:::parameters-start:::(.*?)#:::parameters-end:::",
        content,
        re.DOTALL,
    )
    outputs = re.search(
        r"#:::outputs-start:::(.*?)#:::outputs-end:::",
        content,
        re.DOTALL,
    )
    example = re.search(
        r"#:::example-start:::(.*?)#:::example-end:::",
        content,
        re.DOTALL,
    )
    code = re.search(
        r"#:::code-start:::(.*?)#:::code-end:::",
        content,
        re.DOTALL,
    )

    # Create Markdown documentation
    markdown_content = ""

    # Add title section
    if title:
        title_text = title.group(1).strip()
        title_text = re.sub(r"^# ", "", title_text)
        markdown_content += f"# {title_text}\n\n"

    # Add about section
    if about:
        about_text = about.group(1).strip()
        about_text = re.sub(r"^# ", "", about_text)
        markdown_content += f"{about_text}\n\n"

    # Add parameters section
    if parameters:
        markdown_content += "## Parameters\n\n```yaml\n"
        markdown_content += parameters.group(1) + "\n```\n\n"

    # Add outputs section
    if outputs:
        outputs_text = outputs.group(1).strip()
        outputs_text = re.sub(r"^# ", "", outputs_text, flags=re.MULTILINE)
        outputs_text = re.sub(r"^\s*#", "", outputs_text, flags=re.MULTILINE)
        markdown_content += "## Outputs\n\n"
        markdown_content += outputs_text + "\n\n"

    # Add example section
    if example:
        example_text = example.group(1).strip()
        example_text = re.sub(r"^# ", "", example_text, flags=re.MULTILINE)
        markdown_content += "## Example\n\n```yaml\n"
        markdown_content += example_text + "\n```\n\n"

    # Add code section
    if code:
        code_text = code.group(1).strip()
        code_text = re.sub(r"^# ", "", code_text, flags=re.MULTILINE)
        markdown_content += "## Code\n\n```yaml\n"
        markdown_content += code_text + "\n```\n\n"

    return markdown_content


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    parser.add_argument("-o", "--output", help="output file")
    args = parser.parse_args(argv)

    md = process_pipeline_file(args.filename)
    # Write the Markdown content to the output file
    if args.output:
        with open(args.output, "w") as output_file:
            output_file.write(md)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
