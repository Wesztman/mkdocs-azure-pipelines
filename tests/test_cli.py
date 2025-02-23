import os
import tempfile

from mkdocs_azure_pipelines.cli import main


def test_example():
    # Add your test cases here
    assert True


def test_main_valid_input_output():
    content = """#:::title-start:::
# Title
#:::title-end:::
#:::about-start:::
# About
#:::about-end:::
"""
    with tempfile.NamedTemporaryFile(delete=False) as input_file:
        input_file.write(content.encode())
        input_file_name = input_file.name

    with tempfile.NamedTemporaryFile(delete=False) as output_file:
        output_file_name = output_file.name

    argv = [input_file_name, "-o", output_file_name]
    assert main(argv) == 0

    with open(output_file_name) as f:
        output_content = f.read()
        expected_output = "# Title\n\n## About\n\nAbout\n\n"
        assert output_content == expected_output

    os.remove(input_file_name)
    os.remove(output_file_name)


def test_main_valid_input_no_output():
    content = """#:::title-start:::\n# Title\n#:::title-end:::\n#:::about-start:::\n# About\n#:::about-end:::"""
    with tempfile.NamedTemporaryFile(delete=False) as input_file:
        input_file.write(content.encode())
        input_file_name = input_file.name

    argv = [input_file_name]
    assert main(argv) == 0

    os.remove(input_file_name)


def test_main_invalid_input():
    argv = ["non_existent_file.yml"]
    assert main(argv) == 1  # Expecting the function to return 1 when file is not found
