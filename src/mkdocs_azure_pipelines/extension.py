import re
from collections.abc import Callable, Iterable, Iterator
from typing import Any

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

from mkdocs_azure_pipelines import PipelineProcessingError, process_pipeline_file


class MkDocsAzurePipelinesException(Exception):
    """
    Generic exception class for mkdocs-azure-pipelines errors.
    """


def replace_blocks(
    lines: Iterable[str], title: str, replace: Callable[..., Iterable[str]]
) -> Iterator[str]:
    """
    Find blocks of lines in the form of:

    ::: <title>
        :<key1>: <value>
        :<key2>:
        ...

    And replace them with the lines returned by `replace(key1="<value1>", key2="", ...)`
    """

    options = {}
    in_block_section = False

    for line in lines:
        if in_block_section:
            match = re.search(r"^\s+:(?P<key>.+):(?:\s+(?P<value>\S+))?", line)
            if match is not None:
                # New ':key:' or ':key: value' line, ingest it.
                key = match.group("key")
                value = match.group("value") or ""
                options[key] = value
                continue

            # Block is finished, flush it.
            in_block_section = False
            yield from replace(**options)
            yield line
            continue

        match = re.search(rf"^::: {title}", line)
        if match is not None:
            # Block header, ingest it.
            in_block_section = True
            options = {}
        else:
            yield line


def replace_pipeline_docs(**options: Any) -> Iterator[str]:
    for option in "file":
        if option not in options:
            raise MkDocsAzurePipelinesException(f"Option {option!r} is required")

    file = options["file"]

    lines: str = ""

    try:
        lines = process_pipeline_file(input_file=file)
    except PipelineProcessingError as e:
        raise MkDocsAzurePipelinesException(
            f"Error processing pipeline file {file!r}: {e}"
        ) from e

    yield from lines.splitlines()


class MdAzurePipelinesProcessor(Preprocessor):
    def run(self, lines: list[str]) -> list[str]:
        return list(
            replace_blocks(
                lines,
                title="mkdocs-azure-pipelines",
                replace=lambda **options: replace_pipeline_docs(**options),
            )
        )


class MdAzurePipelinesExtension(Extension):
    """
    Replace blocks like the following:

    ::: mkdocs-click
        :module: example.main
        :command: cli

    by Markdown documentation generated from the specified Click application.
    """

    def extendMarkdown(self, md: Any) -> None:
        md.registerExtension(self)
        processor = MdAzurePipelinesProcessor(md)
        md.preprocessors.register(processor, "md_ado_pipe", 143)
