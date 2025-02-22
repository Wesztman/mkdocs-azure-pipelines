import logging
from pathlib import Path

from mkdocs.config import config_options
from mkdocs.config.base import Config
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import File, Files

from .ado_pipe_to_md import process_pipeline_file

log = logging.getLogger(f"mkdocs.plugins.{__name__}")


class PluginConfig(Config):
    input_files = config_options.ListOfItems(config_options.File(exists=True))
    input_dirs = config_options.ListOfItems(config_options.Dir(exists=True))
    output_dir = config_options.Type(str, default="pipelines")


class AzurePipelinesPlugin(BasePlugin[PluginConfig]):
    def on_files(self, files: Files, /, *, config: MkDocsConfig) -> Files:
        log.info("Now in on_files")
        log.info(f"Output dir: {self.config.output_dir}")

        for file in self.config.input_files:
            log.info(f"Processing pipeline: {file}")
            md_content = process_pipeline_file(file)
            if md_content:
                new_md_file = File.generated(
                    config=config,
                    src_uri=f"{self.config.output_dir}/test.md",
                    content=md_content,
                )

                files.append(new_md_file)
            else:
                log.info(f"No content generated for file: {file}")

        for dir in self.config.input_dirs:
            log.info(f"Processing directory: {dir}")

            dirs_path = Path(dir)
            for file in dirs_path.rglob("*.yml"):
                log.info(f"Processing pipeline from dir: {file}")
                md_content = process_pipeline_file(str(file))
                if md_content:
                    new_md_file = File.generated(
                        config=config,
                        src_uri=f"{self.config.output_dir}/test.md",
                        content=md_content,
                    )

                    files.append(new_md_file)
                else:
                    log.info(f"No content generated for file: {file}")

        return files
