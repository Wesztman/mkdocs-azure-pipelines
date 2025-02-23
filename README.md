<p align="center">
  <img src="https://github.com/Wesztman/mkdocs-azure-pipelines/assets/54413402/5d0e50ea-843a-4e63-8660-785371fd63d0" width="250">
</p>

[![Workflow](https://github.com/Wesztman/mkdocs-azure-pipelines/actions/workflows/ci.yml/badge.svg)](https://github.com/Wesztman/mkdocs-azure-pipelines/actions/workflows/ci.yml)
![Python - Version](https://img.shields.io/badge/Python-3.10_|_3.11_|_3.12-blue)
![PyPI - Version](https://img.shields.io/pypi/v/mkdocs-azure-pipelines)
![Tested on OS](https://img.shields.io/badge/Tested_on_OS-Linux_|_Win_|_Mac-blue)

# About

Generate mkdocs documentation from Azure Pipelines yaml files.

Install the plugin:

```bash
pip install mkdocs-azure-pipelines
```

Add the plugin to your `mkdocs.yml`, you can choose input files and directories to process. For now you can only specify a single output directory.

```yaml
plugins:
  - mkdocs-azure-pipelines:
      input_files:
        - steps-template.yml
        - jobs-template.yml
      input_dirs:
        - folder_with_pipelines
      output_dir: "Pipelines"
```
The output dir is what will be showed in your documentation.

![image](https://github.com/user-attachments/assets/703a50ec-3555-466a-9534-1d7d4d9de934)

## Why

When managing a large repository of pipeline template files, it can be difficult to keep track of what each template does and how to use it. This plugin aims to make it easier to document pipeline templates by generating markdown documentation from the template files themselves and adding it to a mkdocs site.

## Project Goals

### Phase 1: Templates with parameters

- [x] Establish a syntax for title, about, example, outputs etc.
- [x] Create a Python script which can process a pipeline **template** and output a markdown file.
- [x] Convert to a real installable mkdocs plugin.

### Phase 2: Automatic parameter and code parsing

- [ ] Make the plugin document parameters based on the actual pipeline code, no need to use parameters/code-start and -end tags.

### Phase 3: Automatic outputs parsing

- [ ] Make the plugin document outputs based on the actual pipeline code, no need to use outputs-start and outputs-end tags/section.

### Phase 5: Any Azure Pipeline

- [ ] Make the plugin work with any Azure Pipeline yaml file, not just templates. This means parsing variables, pool, trigger, resources etc.

### Phase 6: Mermaid diagrams

- [ ] Generate mermaid diagrams for the template which take conditions and expressions into consideration.

## Syntax

The idea is to use some kind of syntax to indicate what should be documented. This syntax should be easy to read and write, and should be able to be used in a way that doesn't break the pipeline. For simplicity the "marker"/"tag" will have a start point, end point and an identifier. The identifier will be used to determine what to do with the text between the start and end points. All text between the start and end points will be treated as markdown.

### Example

The following example shows how the syntax could look to document a pipeline template and what the resulting markdown would look like.

```yaml
# pytest-step.yml

#:::title-start:::
# Pytest pipeline step template
#:::title-end:::

#:::about-start:::
# This pipeline template is used to run pytest.
#:::about-end:::

#:::example-start:::
# steps:
# - template: pip-build-and-publish-step.yml@templates
#   parameters:
#     python_version: '3.6'
#:::example-end:::

#:::outputs-start:::
# **encouraging_message**: A message to encourage the user.
#:::outputs-end:::

#:::parameters-start:::
parameters:
  - name: python_version # The version of Python to use.
    type: string
  - name: encouraging_message # The message to output.
    type: string
    default: "You look great today!"
#:::parameters-end:::

#:::code-start:::
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
#:::code-end:::
```

Would result in the following markdown when processed by the plugin:

````markdown
# Pytest pipeline step template

This pipeline template is used to run pytest.

## Parameters

```yaml
parameters:
  - name: python_version # The version of Python to use.
    type: string
  - name: encouraging_message # The message to output.
    type: string
    default: "You look great today!"
```

## Outputs

**encouraging_message**: A message to encourage the user.

## Example

```yaml
steps:
  - template: pip-build-and-publish-step.yml@templates
parameters:
  python_version: "3.6"
```

## Code

```yaml
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
      echo "##vso[task.setvariable variable=encouraging_message, isOutput=true]You look great today!"
    displayName: "Output encouraging message"
    name: output_encouraging_message
```
````

Which would result in the following when built

![image](https://github.com/Wesztman/mkdocs-azure-pipelines/assets/54413402/b130cde2-4b53-4510-8ad6-5a46850eeae9)

## Contributing

### Development

Development is done with [PDM](https://pdm.fming.dev/), using tox as a task runner for testing, formatting, linting and pre-commit hooks. Python 3.10 or higher is required.

#### 1. Install PDM

```bash
# Linux/MacOS
curl -sSL https://pdm-project.org/install-pdm.py | python3 -

# Windows
(Invoke-WebRequest -Uri https://pdm-project.org/install-pdm.py -UseBasicParsing).Content | py -
```

#### 2. Install dependencies

```bash
# clone the repository
# cd into the repository
pdm install
```

> Alternatively if you want to save some time and only intend to run tox you can
> install only the dev group of dependencies with `pdm install -G dev`.

#### 3. Run tests, linting and formatting checks, pre-commit hooks, type checking as well as building the package

```bash
pdm run tox
```

It's also possible to run the tasks in parallel using the `-p` flag, significantly reducing the time it takes to run the tasks.

```bash
pdm run tox -p
```

> If in VSCode, you can use the `Tasks: Run Build Task` (`Ctrl+Shift+B`) command from the command palette (`Ctrl+Shift+P`) to run tox in parallel mode.

#### 4. Install the pre-commit hooks

If you want to be sure that your code is properly formatted and linted before committing, you can install the pre-commit hooks.

```bash
pdm run pre-commit install
```

This will stop you from committing if the code is not properly formatted or linted.

#### Separate tasks

Alternatively you can run the tasks separately using the provided PDM scripts.

```bash
# Seperately
pdm run format
pdm run lint
pdm run typecheck
pdm run test

# Or all at once
pdm run all
```
