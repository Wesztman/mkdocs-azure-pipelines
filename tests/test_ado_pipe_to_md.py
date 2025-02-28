import os

from mkdocs_azure_pipelines.ado_pipe_to_md import (
    END_TAG_PATTERN,
    START_TAG_PATTERN,
    extract_code,
    extract_parameters,
    extract_pool,
    extract_section_content,
    extract_trigger,
    extract_variables,
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
    content = """#:::title-start:::
# Title
#:::title-end:::
#:::example-start:::
# Example content
#:::example-end:::
"""
    assert extract_section_content(content, "title") == "Title"
    assert (
        extract_section_content(content, "example") == "```yaml\nExample content\n```"
    )
    content = "No sections here"
    assert extract_section_content(content, "title") is None
    content = """#:::title-start:::
# Title
#:::title-end:::
#:::example-start:::
steps:
  - task: UsePythonVersion@0
    inputs:
      versionSpec: ${{ parameters.python_version }}
      addToPath: true
      architecture: "x64"
  - bash: |
      python -m pip install --upgrade pip
      pip install -r requirements.txt
    displayName: "Install dependencies"
  - bash: |
      pip install pytest pytest-azurepipelines
      pytest
    displayName: "Run pytest"
  - bash: |
      echo "##vso[task.setvariable variable=encouraging_message, isOutput=true]${{ parameters.encouraging_message }}"
    displayName: "Output encouraging message"
    name: output_encouraging_message
#:::example-end:::
"""
    expected_example = '```yaml\nsteps:\n  - task: UsePythonVersion@0\n    inputs:\n      versionSpec: ${{ parameters.python_version }}\n      addToPath: true\n      architecture: "x64"\n  - bash: |\n      python -m pip install --upgrade pip\n      pip install -r requirements.txt\n    displayName: "Install dependencies"\n  - bash: |\n      pip install pytest pytest-azurepipelines\n      pytest\n    displayName: "Run pytest"\n  - bash: |\n      echo "##vso[task.setvariable variable=encouraging_message, isOutput=true]${{ parameters.encouraging_message }}"\n    displayName: "Output encouraging message"\n    name: output_encouraging_message\n```'
    assert extract_section_content(content, "example") == expected_example


def test_process_pipeline_file(tmp_path):
    content = """#:::title-start:::
# Title
#:::title-end:::
#:::about-start:::
# About
#:::about-end:::
"""
    file = tmp_path / "pipeline.yml"
    file.write_text(content)
    expected_output = "# Title\n\n## About\n\nAbout\n\n"
    assert process_pipeline_file(str(file)) == expected_output

    content = """#:::title-start:::
# Title
#:::title-end:::
#:::invalid-start:::
# Invalid
#:::invalid-end:::
"""
    file.write_text(content)
    assert process_pipeline_file(str(file)) is None

    content = """#:::title-start:::
# Title
#:::title-end:::
#:::about-start:::
# About
#:::about-end:::
#:::title-start:::
"""
    file.write_text(content)
    assert process_pipeline_file(str(file)) is None


def test_process_full_pipeline_file(tmp_path):
    # Determine paths to test resources
    test_dir = os.path.dirname(os.path.abspath(__file__))
    resources_path = os.path.join(test_dir, "resources")
    input_file = os.path.join(
        resources_path,
        "folder_with_pipelines/folder_in_folder_with_pipelines/full-pipeline.yml",
    )

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
    assert "# Full pipeline" in result
    assert "## About" in result
    assert "## Outputs" in result
    assert "## Example" in result
    assert "## Triggers" in result
    assert "## Pool" in result
    assert "## Variables" in result
    assert "## Parameters" in result
    assert "## Code" in result


def test_extract_trigger():
    content = """trigger:
  branches:
    include:
      - main # Change this to the branch you want to trigger on
    exclude:
      - feature_branches
"""
    expected_trigger = "```yaml\ntrigger:\n  branches:\n    include:\n      - main # Change this to the branch you want to trigger on\n    exclude:\n      - feature_branches\n```"

    assert extract_trigger(content) == expected_trigger


def test_extract_pool():
    content = """pool:
  vmImage: "ubuntu-latest"
"""
    expected_pool = '```yaml\npool:\n  vmImage: "ubuntu-latest"\n```'
    assert extract_pool(content) == expected_pool


def test_extract_variables():
    content = """variables:
  - name: tag
    value: "$(Build.BuildNumber)"
  - name: ImageName
    value: "demo Image"
  - name: python.version
    value: "3.8"
"""
    expected_variables = '```yaml\nvariables:\n  - name: tag\n    value: "$(Build.BuildNumber)"\n  - name: ImageName\n    value: "demo Image"\n  - name: python.version\n    value: "3.8"\n```'
    assert extract_variables(content) == expected_variables


def test_extract_parameters():
    content = """parameters:
  - name: python_version
    value: "3.8"
  - name: encouraging_message
    value: "You did great!"
"""
    expected_parameters = '```yaml\nparameters:\n  - name: python_version\n    value: "3.8"\n  - name: encouraging_message\n    value: "You did great!"\n```'
    assert extract_parameters(content) == expected_parameters


def test_extract_code():
    content = """steps:
  - task: UsePythonVersion@0
    inputs:
      versionSpec: ${{ parameters.python_version }}
      addToPath: true
      architecture: "x64"
  - bash: |
      python -m pip install --upgrade pip
      pip install -r requirements.txt
    displayName: "Install dependencies"
  - bash: |
      pip install pytest pytest-azurepipelines
      pytest
    displayName: "Run pytest"
  - bash: |
      echo "##vso[task.setvariable variable=encouraging_message, isOutput=true]${{ parameters.encouraging_message }}"
    displayName: "Output encouraging message"
    name: output_encouraging_message
"""
    expected_code = '```yaml\nsteps:\n  - task: UsePythonVersion@0\n    inputs:\n      versionSpec: ${{ parameters.python_version }}\n      addToPath: true\n      architecture: "x64"\n  - bash: |\n      python -m pip install --upgrade pip\n      pip install -r requirements.txt\n    displayName: "Install dependencies"\n  - bash: |\n      pip install pytest pytest-azurepipelines\n      pytest\n    displayName: "Run pytest"\n  - bash: |\n      echo "##vso[task.setvariable variable=encouraging_message, isOutput=true]${{ parameters.encouraging_message }}"\n    displayName: "Output encouraging message"\n    name: output_encouraging_message\n```'
    assert extract_code(content) == expected_code


def test_process_pipeline_file_with_trigger_pool_variables(tmp_path):
    content = """#:::title-start:::
# Title
#:::title-end:::
#:::example-start:::
# Example content
#:::example-end:::
trigger:
  branches:
    include:
      - main
    exclude:
      - feature_branches
pool:
  vmImage: "ubuntu-latest"
variables:
  - name: tag
    value: "$(Build.BuildNumber)"
  - name: ImageName
    value: "demo Image"
  - name: python.version
    value: "3.8"
parameters:
  - name: python_version
    type: string
"""
    file = tmp_path / "pipeline.yml"
    file.write_text(content)
    expected_output = """# Title

## Example

```yaml
Example content
```

## Triggers

```yaml
trigger:
  branches:
    include:
      - main
    exclude:
      - feature_branches
```

## Pool

```yaml
pool:
  vmImage: "ubuntu-latest"
```

## Variables

```yaml
variables:
  - name: tag
    value: "$(Build.BuildNumber)"
  - name: ImageName
    value: "demo Image"
  - name: python.version
    value: "3.8"
```

## Parameters

```yaml
parameters:
  - name: python_version
    type: string
```

"""
    assert process_pipeline_file(str(file)) == expected_output


def test_process_pipeline_file_without_title(tmp_path):
    # Create a dummy YAML file content with no title section
    content = """#:::about-start:::
# About
#:::about-end:::
#:::example-start:::
# steps:
#   - script: echo "Hello, World!"
#     displayName: "Say Hello"
#:::example-end:::
"""

    # Write this content to a temporary file
    file_name = "example_pipeline.yml"
    file_path = tmp_path / file_name
    file_path.write_text(content)

    # Process the file
    result = process_pipeline_file(str(file_path))

    # Expect the title to be generated from the file name
    expected_title = "# Example pipeline\n\n"
    expected_output = (
        expected_title
        + "## About\n\nAbout\n\n"
        + "## Example\n\n"
        + '```yaml\nsteps:\n  - script: echo "Hello, World!"\n    displayName: "Say Hello"\n```\n\n'
    )
    print(result)
    # Assert that the generated markdown content matches the expected output
    assert result == expected_output
