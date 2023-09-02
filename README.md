![](https://img.shields.io/badge/Under%20Development%20-fc2803)

# mkdocs-azure-pipelines
Generate mkdocs documentation from Azure Pipelines yaml files.

## Project Goals

### Phase 1: Step templates with parameters
- [x] Establish a syntax for title, about, example, outputs etc.
- [ ] **In Progress**: Create a Python script which can process a pipeline **step template** and output a markdown file.
- [ ] Convert to a real installable mkdocs plugin and publish to PyPi.

### Phase 1.5: Job templates and variables
- [ ] Make the script work for job templates also.
- [ ] Parse variable sections

### Phase 2: Configuration and output parsing
- [ ] Make plugin configuration options available to the user.
- [ ] Make the plugin document outputs based on the actual pipeline code.

### Phase 3: Puml 
- [ ] Generate puml diagrams for the template which take conditions and expressions into consideration.

### Phase 4: Robustness
- [ ] Support different syntaxes for parameters and variables.
- [ ] Handle syntax errors gracefully with clear error messages.


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
# - encouraging_message: A message to encourage the user.
#:::outputs-end:::

parameters:
- name: python_version # The version of Python to use.
  type: string

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

Would result in the following markdown when processed by the plugin:

``````markdown
# Pytest pipeline step template

This pipeline template is used to run pytest.

## Example

```yaml
steps:
- template: pip-build-and-publish-step.yml@templates
parameters:
    python_version: '3.6'
```

## Parameters

- python_version: The version of Python to use.

## Outputs

- encouraging_message: A message to encourage the user.

## Code

```yaml
parameters:
- name: python_version
  type: string

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
