import pytest
from main import *

@pytest.mark.dir
def test_ensure_directories(tmp_path, monkeypatch):
    """
    Test the ensure_directories function's ability to create necessary directories.
    This test verifies that the ensure_directories function properly creates the
    notes and output directories if they don't exist.
    Args:
        tmp_path (Path): Pytest fixture built in that provides a temporary directory.
        monkeypatch (MonkeyPatch): Pytest built in fixture that allows patching objects.
    Returns:
        None
    """
    test_notes = tmp_path / "notes"
    test_output = tmp_path / "output"

    monkeypatch.setattr("main.NOTES_DIRECTORY", test_notes)
    monkeypatch.setattr("main.OUTPUT_DIRECTORY", test_output)

    ensure_directories()

    assert test_notes.exists() and test_notes.is_file()
    assert test_output.exists() and test_output.is_dir()

def test_extract_title():
    pass


def test_extract_modified_time():
    pass


def test_list_of_notes_to_convert():
    pass


def test_convert_md_to_html():
    pass


def test_generate_index_file():
    pass


def test_find_all_live_md_files():
    pass


def test_find_all_live_html_files():
    pass


def test_remove_unnecessary_html_files():
    pass


def test_build_notes():
    pass