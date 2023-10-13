<p align="center">
  <img src="https://github.com/Wesztman/mkdocs-azure-pipelines/assets/54413402/5d0e50ea-843a-4e63-8660-785371fd63d0" width="250">
</p>

[![tox](https://github.com/Wesztman/mkdocs-azure-pipelines/actions/workflows/tox.yml/badge.svg)](https://github.com/Wesztman/mkdocs-azure-pipelines/actions/workflows/tox.yml)
![](https://img.shields.io/badge/Python-%3E=3.10-blue)
![](https://img.shields.io/badge/Under%20Development%20-fc2803)

# mkdocs-azure-pipelines
Generate mkdocs documentation from Azure Pipelines yaml files.

## Why

When managing a large repository of pipeline template files, it can be difficult to keep track of what each template does and how to use it. This plugin aims to make it easier to document pipeline templates by generating markdown documentation from the template files themselves and adding it to a mkdocs site.

## Project Goals

### Phase 1: Templates with parameters
- [x] Establish a syntax for title, about, example, outputs etc.
- [x] Create a Python script which can process a pipeline **template** and output a markdown file.
- [ ] **In Progress**: Convert to a real installable mkdocs plugin and publish to PyPi.

### Phase 2: Puml

- [ ] Generate puml diagrams for the template which take conditions and expressions into consideration.

### Phase 3: Automatic parameter parsing

- [ ] Make the plugin document parameters based on the actual pipeline code, no need to use parameters-start and parameters-end tags.

### Phase 4: Automatic outputs parsing

- [ ] Make the plugin document outputs based on the actual pipeline code, no need to use outputs-start and outputs-end tags/section.

### Phase 5: Robustness and extras

- [ ] Support different syntaxes for parameters i.e both with and without "name" and "type" keys.
- [ ] Handle syntax errors gracefully with clear error messages.

### Phase 6: Any Azure Pipeline

- [ ] Make the plugin work with any Azure Pipeline yaml file, not just templates. This means parsing variables, pool, trigger, resources etc.

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
  default: 'You look great today!'
#:::parameters-end:::

#:::code-start:::
steps:
  - task: UsePythonVersion@0
    inputs:
      versionSpec: ${{ parameters.python_version }}
      addToPath: true
      architecture: 'x64'

  - bash: |
      python -m pip install --upgrade pip
      pip install -r requirements.txt
    displayName: 'Install dependencies'

  - bash: |
      pip install pytest pytest-azurepipelines
      pytest
    displayName: 'Run pytest'

  - bash: |
      echo "##vso[task.setvariable variable=encouraging_message, isOutput=true]${{ parameters.encouraging_message }}"
    displayName: 'Output encouraging message'
    name: output_encouraging_message
#:::code-end:::
```

Would result in the following markdown when processed by the plugin:

``````markdown
# Pytest pipeline step template

This pipeline template is used to run pytest.

## Parameters

```yaml
parameters:
- name: python_version # The version of Python to use.
  type: string
- name: encouraging_message # The message to output.
  type: string
  default: 'You look great today!'
```

## Outputs

**encouraging_message**: A message to encourage the user.

## Example

```yaml
steps:
- template: pip-build-and-publish-step.yml@templates
parameters:
    python_version: '3.6'
```

## Code

```yaml
steps:
  - task: UsePythonVersion@0
    inputs:
      versionSpec: ${{ parameters.python_version }}
      addToPath: true
      architecture: 'x64'

  - bash: |
      python -m pip install --upgrade pip
      pip install -r requirements.txt
    displayName: 'Install dependencies'

  - bash: |
      pip install pytest pytest-azurepipelines
      pytest
    displayName: 'Run pytest'

  - bash: |
      echo "##vso[task.setvariable variable=encouraging_message, isOutput=true]You look great today!"
    displayName: 'Output encouraging message'
    name: output_encouraging_message
```
``````

Which would result in the following when built

![image](https://github.com/Wesztman/mkdocs-azure-pipelines/assets/54413402/b130cde2-4b53-4510-8ad6-5a46850eeae9)


## Contributing

### Development

<span style="color: lightgreen"> 🔔 Make sure that you have [pipx](https://pypa.github.io/pipx/installation/) installed on your environment.</span>

```bash
pipx install pre-commit
pipx install tox
```

### Testing
Linting and formatting are handled by [pre-commit](https://pre-commit.com/). Tests and resources are in the tests directory written with [pytest](https://docs.pytest.org/en/latest/). Use [tox](https://tox.wiki/en/4.11.3/index.html) to run both of them:

```bash
tox
```
