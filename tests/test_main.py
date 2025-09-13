import pytest
from main import *
from pathlib import Path
from datetime import datetime
import os


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

    assert test_notes.exists() and test_notes.is_dir()
    assert test_output.exists() and test_output.is_dir()

@pytest.mark.title
@pytest.mark.parametrize(
    "content, file_name, expected_title",
    [
        # standard title extraction
        ("# Test Title\nParagraph 1\nParagraph 2", "test-file-name.md", "Test Title"),
        ("# Test Title\nParagraph 1\nParagraph 2", "test_file_name.md", "Test Title"),
        ("# Test Title\nParagraph 1\nParagraph 2", "test file name.md", "Test Title"),
        # no headers extraction
        ("No headers here\nParagraph 1\nParagraph 2", "test-file-name.md", "Test File Name"),
        ("No headers here\nParagraph 1\nParagraph 2", "test_file_name.md", "Test File Name"),
        ("No headers here\nParagraph 1\nParagraph 2", "test file name.md", "Test File Name"),
        # empty file extraction
        ("", "test-file-name.md", "Test File Name"),
        ("", "test_file_name.md", "Test File Name"),
        ("", "test file name.md", "Test File Name"),
        # title appears later in the file extraction
        ("Paragraph\n# Late Title\nParagraph 2", "test-file-name.md", "Late Title"),
        ("Paragraph\n# Late Title\nParagraph 2", "test_file_name.md", "Late Title"),
        ("Paragraph\n# Late Title\nParagraph 2", "test file name.md", "Late Title"),
        # multiple title headings in the file extraction
        ("# Title 1\n# Title 2\n # Title 3", "test-file-name.md", "Title 1"),
        ("# Title 1\n# Title 2\n # Title 3", "test_file_name.md", "Title 1"),
        ("# Title 1\n# Title 2\n # Title 3", "test file name.md", "Title 1"),
    ]
)
def test_extract_title(content, file_name, expected_title):
    """
    Test the `extract_title` function with various Markdown content and file name scenarios.
    This test uses parameterization to cover the following cases:
    - Extraction of the title from the first Markdown header in the content.
    - Fallback to generating a title from the file name when no headers are present or the file is empty.
    - Extraction of the title from a header that appears later in the content.
    - Extraction of the title when multiple headers are present, ensuring the first header is used.
    Parameters:
        content (str): The Markdown content to extract the title from.
        file_name (str): The name of the file, used for fallback title generation.
        expected_title (str): The expected title result for the given content and file name.
    Assertions:
        Asserts that the extracted title matches the expected title for each test case.
    """
    # creating a mock file based on parametrization
    test_file = Path(file_name)

    title = extract_title(test_file, content)
    assert title == expected_title

@pytest.mark.mod_time
def test_extract_modified_time(tmp_path):
    """
    Test for the extract_modified_time function.
    This test creates a temporary markdown file, writes sample content to it, and retrieves its modification time using the standard library.
    It then calls extract_modified_time on the file and asserts that the returned modification time matches the actual modification time.
    Args:
        tmp_path (pathlib.Path): pytest fixture providing a temporary directory unique to the test invocation.
    Marks:
        mod_time: Custom pytest mark for tests related to modified time extraction.
    """
    test_file = tmp_path / "test_file.md"
    test_file.write_text("Test content")

    actual_mod_time = datetime.fromtimestamp(os.path.getmtime(test_file))

    function_mod_time = extract_modified_time(test_file)

    assert function_mod_time == actual_mod_time

@pytest.mark.input_files
def test_list_of_notes_to_convert(tmp_path, monkeypatch):
    """
    Test the `list_of_notes_to_convert` function to ensure it correctly identifies valid Markdown files
    in a directory, excluding invalid files and directories.
    Steps performed:
    - Creates a temporary directory with a mix of valid Markdown files, invalid files, and a folder with '.md' in its name.
    - Mocks the global NOTES_DIRECTORY to point to the temporary test directory.
    - Calls `list_of_notes_to_convert` and verifies:
        - Only valid Markdown files are included in the result.
        - Invalid files (non-.md extensions) are excluded.
        - Directories (even those with '.md' in their name) are excluded.
    """
    # creating temp dir
    test_notes_dir = tmp_path / "notes"
    test_notes_dir.mkdir()

    # mock valid files
    valid_files = [
        "file1.md",
        "file2.md",
        "file-hyphen.md",
        "file_underscore.md",
        "file space.md"
    ]

    # mock invalid files
    invalid_files = [
        "not-md-file1.txt",
        "not-md-file2.html",
    ]

    # create and write to valid files
    for file in valid_files:
        (test_notes_dir / file).write_text("Test content")

    # create and write to invalid files
    for file in invalid_files:
        (test_notes_dir / file).write_text("Test content")

    # create directory(folder) with .md in its name
    test_folder = "folder.md"
    (test_notes_dir / test_folder).mkdir()

    # monkeypatch global NOTES_DIRECTORY to test path
    monkeypatch.setattr("main.NOTES_DIRECTORY", test_notes_dir)

    test_result = list_of_notes_to_convert()

    # assert if file list matches the input list
    assert len(test_result) == len(valid_files)

    # assert if each file is in the result list
    for file in valid_files:
        file_path = test_notes_dir / file
        assert file_path in test_result

    # assert if no invalid files are in result list
    for file in invalid_files:
        file_path = test_notes_dir / file
        assert file_path not in test_result

    # assert if no folders(directories) are in result list
    dir_path = test_notes_dir / test_folder
    assert dir_path not in test_result


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