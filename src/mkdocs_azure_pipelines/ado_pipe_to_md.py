import argparse
import re
from collections.abc import Sequence


class PipelineProcessingError(Exception):
    """
    Generic exception class for pipeline processing errors.
    """


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


def _find_tags(expression: str, string: str) -> list:
    return re.findall(expression, string)


def _extract_section_content(content: str, section_name: str) -> str | None:
    pattern = rf"#:::{section_name}-start:::(.*?)#:::{section_name}-end:::"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        section_text = match.group(1).strip()
        section_text = re.sub(r"^# ", "", section_text, flags=re.MULTILINE)
        return section_text
    return None


def process_pipeline_file(input_file: str) -> str:
    # Read the input pipeline file
    with open(input_file, encoding="utf-8") as f:
        content = f.read()

    start_tags = _find_tags(START_TAG_PATTERN, content)
    end_tags = _find_tags(END_TAG_PATTERN, content)

    # Check for misspelled tags or tag mismatches
    if any(tag not in ALLOWED_TAGS for tag in start_tags):
        raise PipelineProcessingError(
            "Found misspelled start tags. "
            f"Allowed tags are: {', '.join(ALLOWED_TAGS)}"
        )

    if any(tag not in ALLOWED_TAGS for tag in end_tags):
        raise PipelineProcessingError(
            "Found misspelled end tags. " f"Allowed tags are: {', '.join(ALLOWED_TAGS)}"
        )

    if len(start_tags) != len(end_tags) or set(start_tags) != set(end_tags):
        raise PipelineProcessingError(
            "Tag mismatch error. " f"Start tags: {start_tags}, End tags: {end_tags}"
        )

    # Create Markdown documentation
    markdown_content = ""

    # Extract and add title
    title = _extract_section_content(content, "title")
    if title is not None:
        markdown_content += f"# {title}\n\n"

    # Extract and add other sections
    for section_name in ALLOWED_TAGS[1:]:  # Exclude title
        section_content = _extract_section_content(content, section_name)
        if section_content is not None:
            markdown_content += f"## {section_name.capitalize()}\n\n"
            markdown_content += f"{section_content}\n\n"

    return markdown_content


def cli(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    parser.add_argument("-o", "--output", help="output file")
    args = parser.parse_args(argv)

    # Process the pipeline file
    md = process_pipeline_file(args.filename)

    # Write the Markdown content to the output file
    if args.output and md is not None:
        with open(args.output, "w") as output_file:
            output_file.write(md)

    return 0


if __name__ == "__main__":
    raise SystemExit(cli())
