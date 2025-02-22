import os

from mkdocs_azure_pipelines.ado_pipe_to_md import (
    END_TAG_PATTERN,
    START_TAG_PATTERN,
    extract_section_content,
    find_tags,
    process_pipeline_file,
)


def test_find_tags():
    string = "#:::title-start:::\n#:::title-end:::"
    assert find_tags(START_TAG_PATTERN, string) == ["title"]
    assert find_tags(END_TAG_PATTERN, string) == ["title"]

    string = "No tags here"
    assert find_tags(START_TAG_PATTERN, string) == []
    assert find_tags(END_TAG_PATTERN, string) == []


def test_extract_section_content():
    content = """#:::title-start:::\n# Title\n#:::title-end:::"""
    assert extract_section_content(content, "title") == "Title"

    content = "No sections here"
    assert extract_section_content(content, "title") is None

    content = """#:::code-start:::\n#:::code-block:::\n# Code\n#:::code-end:::"""
    assert extract_section_content(content, "code") == "```yaml\nCode\n```"


def test_process_pipeline_file(tmp_path):
    content = """#:::title-start:::\n# Title\n#:::title-end:::\n#:::about-start:::\n# About\n#:::about-end:::"""
    file = tmp_path / "pipeline.yml"
    file.write_text(content)
    expected_output = "# Title\n\n## About\n\nAbout\n\n"
    assert process_pipeline_file(str(file)) == expected_output

    content = """#:::title-start:::\n# Title\n#:::title-end:::\n#:::invalid-start:::\n# Invalid\n#:::invalid-end:::"""
    file.write_text(content)
    assert process_pipeline_file(str(file)) is None

    content = """#:::title-start:::\n# Title\n#:::title-end:::\n#:::about-start:::\n# About\n#:::about-end:::\n#:::title-start:::"""
    file.write_text(content)
    assert process_pipeline_file(str(file)) is None


def test_process_pipeline_file_with_resources(tmp_path):
    # Determine paths to test resources
    test_dir = os.path.dirname(os.path.abspath(__file__))
    resources_path = os.path.join(test_dir, "resources")
    input_file = os.path.join(resources_path, "test-pipe.yml")

    # Run process_pipeline_file with input file and output to a temporary file
    output_file = os.path.join(tmp_path, "test-pipe.md")
    md_content = process_pipeline_file(input_file)
    if md_content is not None:
        with open(output_file, "w") as f:
            f.write(md_content)

    # Read generated Markdown content
    with open(output_file) as f:
        result = f.read()

    # Assert specific content rather than entire files
    assert "# Pytest pipeline step template" in result
    assert "## Parameters" in result
    assert "## Outputs" in result
    assert "## Example" in result
    assert "## Code" in result
