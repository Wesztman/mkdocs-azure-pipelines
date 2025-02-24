<p align="center">
  <img src="https://github.com/Wesztman/mkdocs-azure-pipelines/assets/54413402/5d0e50ea-843a-4e63-8660-785371fd63d0" width="250">
</p>

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
![GitHub License](https://img.shields.io/github/license/wesztman/mkdocs-azure-pipelines)
[![Workflow](https://github.com/Wesztman/mkdocs-azure-pipelines/actions/workflows/ci.yml/badge.svg)](https://github.com/Wesztman/mkdocs-azure-pipelines/actions/workflows/ci.yml)
![Python - Version](https://img.shields.io/badge/Python-3.10_|_3.11_|_3.12-blue)
[![PyPI - Version](https://img.shields.io/pypi/v/mkdocs-azure-pipelines)](https://pypi.org/project/mkdocs-azure-pipelines/)
![Tested on OS](https://img.shields.io/badge/Tested_on_OS-Linux_|_Win_|_Mac-blue)

# About

> [!NOTE]
> This project is still in the early stages of development, while it works there might be
> bugs and missing features. There might also be breaking changes between versions, please
> pin the version of the plugin to avoid issues.
> I've not yet tried running it on a pipeline >with jinja style template expressions. 

Generate mkdocs documentation from Azure Pipelines yaml files.

-"But why?"

When managing a large repository of pipeline template files, it can be difficult to keep track of what each template does and how to use it. This plugin aims to make it easier to document pipeline templates by generating markdown documentation from the template files themselves and adding it to a mkdocs site.

## How to use

Install the plugin:

```bash
pip install mkdocs-azure-pipelines
```
or
```bash
uv add mkdocs-azure-pipelines
```


Add the plugin to your `mkdocs.yml`, you can choose input files and directories to process.

**Note**, for now you can only specify a single output directory where all the generated markdowns will go.

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

The output dir is relative to the root of your documentation.

![image](https://github.com/user-attachments/assets/703a50ec-3555-466a-9534-1d7d4d9de934)

> [!TIP]
> The plugin will alter the files to watch when using `mkdocs serve` to include your input
> files and directories, hot reloading any changes you make to the yaml files.

### Parsing YAML

The plugin will parse the yaml files and extract the following information:

- Trigger
- Pool
- Variables
- Parameters
- Code (the first of _steps_, _jobs_ or _stages_ key found at top level, then all code under that key)

These will be added to the generated markdown file with the key as level 2 headers and the value as a code block, retaining the original, including comments.

### Adding Extra Content

To add extra content to your generated markdown you can use the **title**, **about**, **example** and **outputs** start and end-tags in the following syntax `#:::<tag>-start:::` and `#:::<tag>-end:::`.

```yaml
#:::title-start:::
# Pip cache step template
#:::title-end:::

#:::about-start:::
# This pipeline template is used to install pip deps and cache them.
#:::about-end:::

#:::example-start:::
# steps:
# - template: pip-install-and-cache-step.yml@templates
#   parameters:
#     python_version: '3.6'
#:::example-end:::

#:::outputs-start:::
# **encouraging_message**: A message to encourage the user.
#:::outputs-end:::

Pipeline/template code starts here...
```

These generate the following markdown:

````markdown
# Pip cache step template

## About

This pipeline template is used to install pip deps and cache them.

## Outputs

**encouraging_message**: A message to encourage the user.

## Example

    ```yaml
    steps:
    - template: pip-install-and-cache-step.yml@templates
      parameters:
        python_version: '3.6'
    ```

Pipeline/template code starts here...
````

### Debugging

If you are having issues with the plugin, you can run `mkdocs build` and `mkdocs serve` with the `--verbose` flag to get more information about what the plugin is doing. All logs from the plugin should be prefixed with `mkdocs-azure-pipelines: `.

## Contributing

Contributions are welcome! If you find any bugs or have a feature request, please open an issue or even better, a pull request 🥳

### Development

Development is done using [uv](https://docs.astral.sh/uv/). Python 3.10 or higher is required.

#### 1. Install UV

See the [uv repository](https://github.com/astral-sh/uv) for the latest and greatest in installation instructions.

#### 2. Install dependencies

```bash
uv sync
```

#### 3. Run tests

```bash
uv run pytest
```

#### 4. Install the pre-commit hooks

If you want to be sure that your code is properly formatted and linted before committing, you can install the pre-commit hooks.

```bash
uv run pre-commit install
```

This will stop you from committing if the code is not properly formatted or linted.

#### 5. Run pre-commit manually

You can run pre-commit manually on all files using:

```bash
uv run pre-commit run --all-files
```

## Project Goals

### Phase 1: Templates with parameters

- [x] Establish a syntax for title, about, example, outputs etc.
- [x] Create a Python script which can process a pipeline **template** and output a markdown file.
- [x] Convert to a real installable mkdocs plugin.

### Phase 2: Automatic parameter and code parsing

- [x] Make the plugin document parameters based on the actual pipeline code, no need to use parameters/code-start and -end tags.

### Phase 3: Any Azure Pipeline

- [x] Make the plugin work with any Azure Pipeline yaml file, not just templates. This means parsing variables, pool, trigger, resources etc.

### Phase 4: Automatic outputs parsing

- [ ] Make the plugin document outputs based on the actual pipeline code, no need to use outputs-start and outputs-end tags/section.

### Phase 5: Mermaid diagrams

- [ ] Generate mermaid diagrams for the template which take conditions and expressions into consideration.
