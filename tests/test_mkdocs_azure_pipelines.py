import os

from src.mkdocs_azure_pipelines.ado_pipe_to_md import main


def test_main(tmp_path):
    # Determine paths to test resources
    test_dir = os.path.dirname(os.path.abspath(__file__))
    resources_path = os.path.join(test_dir, "resources")
    input_file = os.path.join(resources_path, "test-pipe.yml")

    # Run main with input file and output to a temporary file
    output_file = os.path.join(tmp_path, "test-pipe.md")
    main([input_file, "-o", output_file])

    # Read generated Markdown content
    with open(output_file) as f:
        result = f.read()

    # Assert specific content rather than entire files
    assert "# Pytest pipeline step template" in result
    assert "## Parameters" in result
    assert "## Outputs" in result
    assert "## Example" in result
    assert "## Code" in result
