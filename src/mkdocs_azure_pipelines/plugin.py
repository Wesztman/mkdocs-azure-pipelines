import hashlib
import logging
from collections.abc import Callable
from functools import cache
from pathlib import Path

from mkdocs.config import config_options
from mkdocs.config.base import Config
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.livereload import LiveReloadServer
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import File, Files

from .ado_pipe_to_md import process_pipeline_file

log = logging.getLogger(f"mkdocs.plugins.{__name__}")


class PluginConfig(Config):
    input_files = config_options.ListOfItems(config_options.File(exists=True))
    input_dirs = config_options.ListOfItems(config_options.Dir(exists=True))
    output_dir = config_options.Type(str, default="pipelines")


@cache
def get_all_files(input_files: tuple[str], input_dirs: tuple[str]) -> list:
    """
    Get all files to be processed from input_files and input_dirs
    Cache the result to avoid reprocessing the same files multiple times.
    Convert the input arguments to tuples to make them hashable.
    """
    files_to_process = []

    # Add files from input_files
    for file in input_files:
        files_to_process.append(file)

    # Add files from input_dirs (looking for *.yml files)
    for dir in input_dirs:
        log.info(f"Processing directory: {dir}")
        for file in Path(dir).rglob("*.yml"):
            files_to_process.append(str(file))

    return files_to_process


class AzurePipelinesPlugin(BasePlugin[PluginConfig]):
    def on_files(self, files: Files, /, *, config: MkDocsConfig) -> Files:
        log.info("Now in on_files")
        log.info(f"Output dir: {self.config.output_dir}")

        def unique_filename(file_path: str) -> str:
            path = Path(file_path)
            hashed_name = hashlib.sha1(file_path.encode()).hexdigest()[
                :10
            ]  # Short hash
            return f"{path.stem}-{hashed_name}{path.suffix}"

        def process_and_add_file(file_path: str):
            log.info(f"Processing file: {file_path}")
            md_content = process_pipeline_file(file_path)
            md_file_path = (
                f"{self.config.output_dir}/{unique_filename(file_path)}".replace(
                    ".yml", ".md"
                )
            )
            if md_content:
                new_md_file = File.generated(
                    config=config,
                    src_uri=md_file_path,
                    content=md_content,
                )
                files.append(new_md_file)
                log.info(f"New md file generated: {md_file_path}")
            else:
                log.info(f"No content generated for file: {file_path}")

        # Get all files to be processed using cached result
        all_files = get_all_files(
            tuple(self.config.input_files), tuple(self.config.input_dirs)
        )

        # Process each file in the list
        for file in all_files:
            process_and_add_file(file)

        return files

    def on_serve(
        self, server: LiveReloadServer, /, *, config: MkDocsConfig, builder: Callable
    ) -> LiveReloadServer:
        log.info("Now in on_serve")

        # Get the list of files to watch from get_all_files
        all_files = get_all_files(
            tuple(self.config.input_files), tuple(self.config.input_dirs)
        )

        # Watch each file returned from get_all_files
        for file_path in all_files:
            server.watch(file_path)  # Watch the file directly
            log.info(f"Watching file: {file_path}")

        return server
