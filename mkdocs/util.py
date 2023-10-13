from __future__ import annotations

import os.path

TESTING_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_resource_path(path):
    return str(os.path.join(TESTING_DIR, "tests/resources", path))
