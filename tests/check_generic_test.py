from __future__ import annotations

import pytest

from mkdocs.ado_pipe_to_md import main
from mkdocs.util import get_resource_path


@pytest.mark.parametrize(
    "filename, expected_retval",
    [("test-pipe.yml", 0)],
)
def test_main(capsys, filename, expected_retval):
    ret = main([get_resource_path(filename)])
    assert ret == expected_retval
    if expected_retval == 1:
        stdout, _ = capsys.readouterr()
        assert filename in stdout
