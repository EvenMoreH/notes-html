import pytest
from main import *

@pytest.fixture
def setup_test_directories(tmp_path, monkeypatch):
    """
    Sets up temporary test directories for notes and output, and patches the main module's
    NOTES_DIRECTORY and OUTPUT_DIRECTORY variables to use these temporary directories.
    Args:
        tmp_path (pathlib.Path): pytest fixture providing a temporary directory unique to the test invocation.
        monkeypatch (pytest.MonkeyPatch): pytest fixture for safely patching and restoring attributes.
    Side Effects:
        - Creates 'notes' and 'output' directories inside the temporary path.
        - Patches 'main.NOTES_DIRECTORY' and 'main.OUTPUT_DIRECTORY' to point to the created directories.
    """
    test_notes_dir = tmp_path / "notes"
    test_output_dir = tmp_path / "output"
    test_notes_dir.mkdir()
    test_output_dir.mkdir()

    monkeypatch.setattr("main.NOTES_DIRECTORY", test_notes_dir)
    monkeypatch.setattr("main.OUTPUT_DIRECTORY", test_output_dir)

    return test_notes_dir, test_output_dir