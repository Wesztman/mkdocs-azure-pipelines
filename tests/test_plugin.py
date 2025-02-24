from unittest.mock import Mock

import pytest
from mkdocs.structure.files import Files

from mkdocs_azure_pipelines.plugin import (
    AzurePipelinesPlugin,
    ConfigurationError,
    PluginConfig,
    get_all_files,
)


def test_get_all_files(tmp_path):
    # Create temporary files and directories
    file1 = tmp_path / "file1.yml"
    file1.write_text("content")
    file2 = tmp_path / "file2.yml"
    file2.write_text("content")
    dir1 = tmp_path / "dir1"
    dir1.mkdir()
    file3 = dir1 / "file3.yml"
    file3.write_text("content")

    input_files = [str(file1), str(file2)]
    input_dirs = [str(dir1)]

    all_files = get_all_files(tuple(input_files), tuple(input_dirs))
    assert set(all_files) == {str(file1), str(file2), str(file3)}


def test_azure_pipelines_plugin_on_files(tmp_path):
    # Create a temporary pipeline file
    content = """#:::title-start:::\n# Title\n#:::title-end:::\n#:::about-start:::\n# About\n#:::about-end:::"""
    pipeline_file = tmp_path / "pipeline.yml"
    pipeline_file.write_text(content)

    # Mock the plugin config
    plugin_config = PluginConfig()
    plugin_config["input_files"] = [str(pipeline_file)]
    plugin_config["input_dirs"] = []
    plugin_config["output_dir"] = str(tmp_path)

    # Create the plugin instance
    plugin = AzurePipelinesPlugin()
    plugin.config = plugin_config  # pyright: ignore

    # Mock the Files object
    files = Files([])

    # Call the on_files method
    updated_files = plugin.on_files(files, config=Mock())

    # Check that the new markdown file is added
    assert any(f.src_uri.endswith(".md") for f in updated_files)


def test_azure_pipelines_plugin_on_serve(tmp_path):
    # Create a temporary pipeline file
    content = """#:::title-start:::\n# Title\n#:::title-end:::\n#:::about-start:::\n# About\n#:::about-end:::"""
    pipeline_file = tmp_path / "pipeline.yml"
    pipeline_file.write_text(content)

    # Mock the plugin config
    plugin_config = PluginConfig()
    plugin_config["input_files"] = [str(pipeline_file)]
    plugin_config["input_dirs"] = []
    plugin_config["output_dir"] = str(tmp_path)

    # Create the plugin instance
    plugin = AzurePipelinesPlugin()
    plugin.config = plugin_config  # pyright: ignore

    # Mock the LiveReloadServer object
    server = Mock()

    # Call the on_serve method
    plugin.on_serve(server, config=Mock(), builder=Mock())

    # Check that the file is being watched
    server.watch.assert_called_with(str(pipeline_file))


def test_azure_pipelines_plugin_on_config_raises_exception():
    plugin = AzurePipelinesPlugin()
    plugin.config = PluginConfig()  # type: ignore
    with pytest.raises(
        ConfigurationError,
        match="At least one input_files or input_dirs must be specified.",
    ):
        plugin.on_config(Mock())
