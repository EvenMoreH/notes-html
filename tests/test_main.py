import pytest
from pytest import MonkeyPatch
from main import *
from pathlib import Path
from datetime import datetime
import os
from conftest import setup_test_directories


@pytest.mark.dir
def test_ensure_directories(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
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
def test_extract_title(content: str, file_name: str, expected_title: str) -> None:
    """
    Test the extract_title function for correct title extraction from Markdown content.
    This test uses parameterized inputs to verify:
    - Title is extracted from the first Markdown header if present.
    - If no header exists, title is derived from the file name.
    - Handles empty files and files with multiple headers.
    Args:
        content (str): Markdown content to extract title from.
        file_name (str): Name of the file to use for fallback title.
        expected_title (str): Expected title result for assertion.
    Assertions:
        - The extracted title matches the expected_title for each test case.
    """
    test_file = Path(file_name)
    title = extract_title(test_file, content)
    assert title == expected_title

@pytest.mark.mod_time
def test_extract_modified_time(tmp_path: Path) -> None:
    """
    Test the extract_modified_time function for correct file modification time extraction.
    This test:
    - Creates a temporary file in a pytest-provided directory.
    - Writes content to the file.
    - Gets the actual modification time using os.path.getmtime.
    - Calls extract_modified_time and compares its result to the actual time.
    Args:
        tmp_path (Path): Pytest fixture providing a temporary directory.
    Assertions:
        - The modification time returned by extract_modified_time matches the actual file mod time.
    """
    # test file setup
    test_file = tmp_path / "test_file.md"
    test_file.write_text("Test content")

    # fetch actual time
    actual_mod_time = datetime.fromtimestamp(os.path.getmtime(test_file))

    # fetch modified time from file
    function_mod_time = extract_modified_time(test_file)

    # checking if actual time matches modified time
    assert function_mod_time == actual_mod_time


@pytest.mark.input_files
def test_list_of_notes_to_convert(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """
    Test the list_of_notes_to_convert function for correct file filtering.
    This test:
    - Creates a temporary notes directory.
    - Adds valid Markdown files, invalid files, and a folder named with .md.
    - Monkeypatches NOTES_DIRECTORY to the test path.
    - Calls list_of_notes_to_convert and verifies:
        - Only valid Markdown files are included.
        - Invalid files and folders are excluded.
    Args:
        tmp_path (Path): Pytest fixture providing a temporary directory.
        monkeypatch (MonkeyPatch): Pytest fixture for patching global variables.
    Assertions:
        - Result contains only valid Markdown files.
        - Invalid files and folders are not present in the result.
    Extended Description:
        1. Create valid and invalid files in a temp directory.
        2. Create a folder named with .md extension.
        3. Patch NOTES_DIRECTORY and call list_of_notes_to_convert.
        4. Assert only valid files are returned.
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


@pytest.mark.conversion
def test_convert_md_to_html_basic(setup_test_directories: tuple[Path, Path]) -> None:
    """
    Test the convert_md_to_html function for basic Markdown to HTML conversion.
    This test:
    - Sets up test notes and output directories.
    - Creates multiple Markdown files with various content:
        - File with a title header.
        - File with multiple headers, lists, and code block.
        - File with no title header.
    - Calls convert_md_to_html and verifies:
        - All files are converted to HTML.
        - HTML files exist and contain expected structure.
        - Titles and metadata are extracted for each file.
        - HTML output contains required elements.
    Args:
        setup_test_directories: Pytest fixture that sets up temporary notes and output directories.
    Assertions:
        - Number of HTML titles and metadata matches number of test files.
        - HTML files exist for each Markdown file.
        - HTML output contains <!DOCTYPE html>, <html>, </html>, <title>, <style>, and "Back to Notes".
    """
    # assigning paths based on setup fixture
    test_notes_dir, test_output_dir = setup_test_directories
    # create test file contents
    test_files = {
        "basic": {
            "content": "# Test Title\nParagraph 1.\nParagraph 2.",
            "filename": "basic-file.md",
        },
        "complex": {
            "content": "# Test Title\n## Subtitle\n### Another Header\n\
            Paragraph\n* List item 1\n* List item 2\n```python\nprint('code block')\n```",
            "filename": "complex-file.md",
        },
        "no_title": {
            "content": "Paragraph 1.\nParagraph 2.",
            "filename": "no-title-file.md",
        },
    }
    number_of_test_files = len(test_files.keys())

    # creating empty list to store files in (such list would be an output of list_of_notes_to_convert())
    md_files_in_dir = []
    # create files and write content to them based on test_files dictionary
    for file in test_files.values():
        file_path = test_notes_dir / file["filename"]
        file_path.write_text(file["content"], encoding="utf-8")
        md_files_in_dir.append(file_path)

    # calling function in test
    html_titles, modified = convert_md_to_html(md_files_in_dir)

    # assert if correct amount of titles and metadata was extracted
    assert len(html_titles) == number_of_test_files
    assert len(modified) == number_of_test_files

    # checking if all files were correctly converted and created, and contain proper html
    for file in test_files.values():
        html_filename = f"{Path(file["filename"]).stem}.html"
        html_file_path = test_output_dir / html_filename

        assert html_file_path.exists()

        html_content = html_file_path.read_text(encoding="utf-8")
        assert "<!DOCTYPE html>" in html_content
        assert "<html>" in html_content
        assert "</html>" in html_content
        assert "<title>" in html_content
        assert "<style>" in html_content
        assert "Back to Notes" in html_content


@pytest.mark.conversion
def test_convert_md_to_html_metadata_file(setup_test_directories: tuple[Path, Path]) -> None:
    """
    Test the convert_md_to_html function to ensure that Markdown files containing metadata
    are correctly converted to HTML files with the following requirements:
    - The metadata block (YAML front matter) is excluded from the HTML output.
    - The HTML file is created in the output directory.
    - The HTML file's title matches the title heading in the Markdown content, not the metadata title.
    - The HTML output contains expected HTML structure and content, including:
        - <!DOCTYPE html>, <html>, </html>, <title>, <style>, and "Back to Notes".
        - The Markdown headings and content are preserved.
    - None of the metadata fields or values appear in the HTML output.
    Args:
        setup_test_directories: Pytest fixture that sets up temporary notes and output directories.
    Asserts:
        - HTML file exists after conversion.
        - HTML title matches the title heading in the Markdown file.
        - Metadata is excluded from the HTML output.
        - File contents and expected HTML structure are present in the output.
    """
    # assigning paths based on setup fixture
    test_notes_dir, test_output_dir = setup_test_directories

    # creating test file with metadata
    doc_test_title = "Actual Title"
    metadata_content = f"""---
title: Metadata Title
tags: [test, markdown, metadata]
date: 01-01-2001
---
# {doc_test_title}
## Subtitle
File Contents"""

    test_file_name = "metadata-test-file.md"
    test_file_path = test_notes_dir / test_file_name
    test_file_path.write_text(metadata_content, encoding="utf-8")

    # calling function in test (creating list out of test_file_path)
    html_titles, _ = convert_md_to_html([test_file_path])

    html_filename = test_file_name.replace(".md", ".html")
    html_file_path = test_output_dir / html_filename

    # checking if name and title are correct after conversion
    assert html_file_path.exists()
    assert html_titles[html_filename] == doc_test_title

    # read converted file contents
    html_content = html_file_path.read_text(encoding="utf-8")

    # checking if metadata was excluded
    assert "---" not in html_content
    assert "title:" not in html_content
    assert "Metadata Title" not in html_content
    assert "tags:" not in html_content
    assert "test, markdown, metadata" not in html_content
    assert "date:" not in html_content
    assert "01-01-2001" not in html_content

    # checking if file contents were preserved
    assert "<!DOCTYPE html>" in html_content
    assert "<html>" in html_content
    assert f"<title>{doc_test_title}</title>" in html_content
    assert "Subtitle" in html_content
    assert "File Contents" in html_content
    assert "<style>" in html_content
    assert "Back to Notes" in html_content
    assert "</html>" in html_content


@pytest.mark.conversion
def test_convert_md_to_html_empty_file(setup_test_directories: tuple[Path, Path]) -> None:
    """
    Test the convert_md_to_html function for handling empty Markdown files.
    This test:
    - Sets up test notes and output directories.
    - Creates an empty Markdown file.
    - Calls convert_md_to_html with the empty file.
    Assertions:
        - HTML file is created for the empty Markdown file.
        - Title is derived from the file name.
        - HTML output contains expected structure and elements.
    """
    # assigning paths based on setup fixture
    test_notes_dir, test_output_dir = setup_test_directories

    # create empty markdown file
    test_file_name = "empty-file.md"
    test_file_path = test_notes_dir / test_file_name
    test_file_path.write_text("", encoding="utf-8")

    # calling function in test
    html_titles, _ = convert_md_to_html([test_file_path])

    html_filename = test_file_name.replace(".md", ".html")
    html_file_path = test_output_dir / html_filename

    # checking if file was converted correctly and uses filename as Title
    assert html_file_path.exists()
    assert html_titles[html_filename] == "Empty File"

    # checking if html file was created correctly despite being empty
    html_content = html_file_path.read_text(encoding="utf-8")

    assert "<!DOCTYPE html>" in html_content
    assert "<html>" in html_content
    assert "<title>Empty File</title>" in html_content
    assert "<style>" in html_content
    assert "Back to Notes" in html_content
    assert "</html>" in html_content


@pytest.mark.conversion
def test_convert_md_to_html_non_md_file(setup_test_directories: tuple[Path, Path]) -> None:
    """
    Test the convert_md_to_html function to ensure non-Markdown files are ignored.
    This test:
    - Sets up test notes and output directories.
    - Creates a valid Markdown file and a non-Markdown (.txt) file.
    - Calls convert_md_to_html with both files.
    Assertions:
        - Only the Markdown file is processed and converted to HTML.
        - The non-Markdown file is ignored and not converted.
        - The output directory contains only the expected HTML file.
    """
    # assigning paths based on setup fixture
    test_notes_dir, test_output_dir = setup_test_directories

    # create valid markdown file
    test_md_file_name = "valid-file.md"
    test_md_file_path = test_notes_dir / test_md_file_name
    test_md_file_path.write_text("# Valid Markdown", encoding="utf-8")

    # creating non-markdown file
    test_txt_file_name = "non-markdown.txt"
    test_txt_file_path = test_notes_dir / test_txt_file_name
    test_txt_file_path.write_text("Not Markdown", encoding="utf-8")

    # calling function in test with list of two test files as arg
    html_titles, modified = convert_md_to_html([test_md_file_path, test_txt_file_path])

    # checking if only .md file was processed
    assert len(html_titles) == 1
    assert len(modified) == 1
    assert "valid-file.html" in html_titles
    assert "non-markdown.html" not in html_titles

    # checking if correct file was created
    assert (test_output_dir / test_md_file_name.replace(".md", ".html")).exists()
    assert not (test_output_dir / test_txt_file_name.replace(".txt", ".html")).exists()


@pytest.mark.index
def test_generate_index_file_basic(setup_test_directories: tuple[Path, Path]) -> None:
    """
    Test the generate_index_file function for basic index generation with provided titles and dates.
    This test:
    - Creates mock HTML files in the output directory.
    - Provides html_titles and modified dictionaries with custom titles and dates.
    - Calls generate_index_file and verifies:
        - index.html is created and contains expected HTML structure.
        - All notes are listed with correct titles and modification dates.
        - Notes are sorted alphabetically by title.
        - Search functionality is present.
    Args:
        setup_test_directories: Pytest fixture providing temporary output directory.
    Assertions:
        - index.html is created and contains expected HTML structure.
        - All note files are listed with correct titles and dates.
        - Notes are sorted alphabetically by title.
        - Search input is present in the index.
    """
    # assigning paths based on setup fixture
    _, test_output_dir = setup_test_directories

    # creating mock HTML files in temp output directory (dictionary with title:content pairs)
    test_files = {
        "beta-note.html":"One content",
        "gamma-note.html":"Two content",
        "alfa-note.html":"Three content",
    }

    # writing content to files
    for filename, content in test_files.items():
        file_path = test_output_dir / filename
        file_path.write_text(content, encoding="utf-8")

    # creating mock html_titles dictionary
    html_titles = {
        "beta-note.html":"Beta Title",
        "gamma-note.html":"Gamma Title",
        "alfa-note.html":"Alfa Title",
    }

    # creating mock modified dates dictionary
    test_datetime = datetime(2001, 1, 11, 12, 0, 0)
    modified = {
        "beta-note.html":test_datetime,
        "gamma-note.html":test_datetime,
        "alfa-note.html":test_datetime,
    }

    # calling function in test
    generate_index_file(html_titles, modified)

    # checking if index file was generated
    index_path = test_output_dir / "index.html"
    assert index_path.exists()

    # checking if index.html contents were properly generated
    index_content = index_path.read_text(encoding="utf-8")

    # basic html structure
    assert "<!DOCTYPE html>" in index_content
    assert "<html>" in index_content
    assert "<title>My Notes</title>" in index_content
    assert "<style>" in index_content
    assert "</html>" in index_content

    # search functionality present
    assert '<input id="search" type="search"' in index_content
    assert 'Search notes...' in index_content

    # checking if all note files were added to index
    for filename, title in html_titles.items():
        assert f'<a href="{filename}"' in index_content
        assert f">{title}</a>" in index_content

    # checking date
    expected_date = test_datetime.strftime("%B %d, %Y")  # "January 11, 2001"
    assert expected_date in index_content

    # check if notes are sorted A-Z by title
    beta_note_position = index_content.find("Beta Title")
    gamma_note_position = index_content.find("Gamma Title")
    alfa_note_position = index_content.find("Alfa Title")

    assert 0 < alfa_note_position < beta_note_position < gamma_note_position


@pytest.mark.index
def test_generate_index_file_empty_directory(setup_test_directories: tuple[Path, Path]) -> None:
    # assigning paths based on setup fixture
    _, test_output_dir = setup_test_directories

    # creating mock html_titles dictionary
    html_titles = {}

    # creating mock modified dates dictionary
    modified = {}

    # calling function in test
    generate_index_file(html_titles, modified)

    # checking if index file was generated
    index_path = test_output_dir / "index.html"
    assert index_path.exists()

    # read and validate the content of the index file
    index_content = index_path.read_text(encoding="utf-8")

    # verify basic HTML structure
    assert "<!DOCTYPE html>" in index_content
    assert "<html>" in index_content
    assert "<title>My Notes</title>" in index_content
    assert "<style>" in index_content
    assert "</html>" in index_content

    # verify search functionality is still present
    assert '<input id="search" type="search"' in index_content
    assert 'Search notes...' in index_content

@pytest.mark.index
def test_generate_index_file_missing_metadata(setup_test_directories: tuple[Path, Path]) -> None:
    """
    Test the generate_index_file function when metadata is missing for HTML files.
    This test:
    - Creates mock HTML files in the output directory without metadata.
    - Calls generate_index_file with empty html_titles and modified dictionaries.
    - Verifies that index.html is generated and contains:
        - Basic HTML structure and search functionality.
        - Links to all HTML files, with titles derived from file names.
        - Modification date in "Month Day, Year" format.
        - Notes sorted alphabetically by derived title.
    Args:
        setup_test_directories: Pytest fixture providing temporary output directory.
    Assertions:
        - index.html is created and contains expected HTML structure.
        - All HTML files are listed in the index.
        - Titles are derived from file names when metadata is missing.
        - Modification date is present and correctly formatted.
        - Notes are sorted alphabetically by title.
    """
    # assigning paths based on setup fixture
    _, test_output_dir = setup_test_directories

    # creating mock HTML files in temp output directory (dictionary with title:content pairs)
    test_files = {
        "beta-note.html": "One content",
        "gamma-note.html": "Two content",
        "alfa-note.html": "Three content",
    }

    # writing content to files
    for filename, content in test_files.items():
        file_path = test_output_dir / filename
        file_path.write_text(content, encoding="utf-8")

    # getting modified datetime from one of created files
    test_modified_date = datetime.fromtimestamp(os.path.getmtime(test_output_dir / "alfa-note.html"))

    # creating mock html_titles dictionary
    html_titles = {}

    # creating mock modified dates dictionary
    modified = {}

    # calling function in test
    generate_index_file(html_titles, modified)

    # checking if index file was generated
    index_path = test_output_dir / "index.html"
    assert index_path.exists()

    # checking if index.html contents were properly generated
    index_content = index_path.read_text(encoding="utf-8")

    # basic html structure
    assert "<!DOCTYPE html>" in index_content
    assert "<html>" in index_content
    assert "<title>My Notes</title>" in index_content
    assert "<style>" in index_content
    assert "</html>" in index_content

    # search functionality present
    assert '<input id="search" type="search"' in index_content
    assert 'Search notes...' in index_content

    # checking if all note files were added to index based on test_files dictionary, not html_titles
    for filename in test_files.keys():
        assert f'<a href="{filename}"' in index_content

    # checking datetime of modification in "January 11, 2001" format
    assert test_modified_date.strftime("%B %d, %Y") in index_content

    # check if notes are sorted A-Z by title
    # titles are derived from file names if Title metadata is missing
    beta_note_position = index_content.find("Beta Note")
    gamma_note_position = index_content.find("Gamma Note")
    alfa_note_position = index_content.find("Alfa Note")

    assert 0 < alfa_note_position < beta_note_position < gamma_note_position


@pytest.mark.lookup
def test_find_all_live_md_files(setup_test_directories: tuple[Path, Path]) -> None:
    """
    Tests the find_all_live_md_files function to ensure it correctly identifies valid markdown files.
    Args:
        setup_test_directories: Pytest fixture that sets up test directories and returns their paths.
    Assertions:
        - Only valid markdown files (.md) are found in the directory.
        - Invalid files (.txt, .html, files without extension) are not included in results.
        - Folders named with .md extension are excluded from results.
    Extended Description:
        1. Sets up a test directory with valid and invalid files, and a folder named with .md extension.
        2. Writes sample content to each file.
        3. Calls find_all_live_md_files and checks:
            - The number of results matches the number of valid files.
            - Each valid file is present in results.
            - Each invalid file and folder are absent from results.
    """
    # test directory setup
    test_notes_dir, _ = setup_test_directories

    # list of valid markdown files
    test_valid_files = ["file1.md", "file-2.md", "file_3.md", "file four.md"]

    # list of invalid files
    test_invalid_files = ["badfile1.txt", "badfile-2.html", "badfile_3"]

    # invalid folder
    test_invalid_folder = test_notes_dir / "folder.md"
    test_invalid_folder.mkdir()

    # create and write to files
    for file in test_valid_files:
        (test_notes_dir / file).write_text("# Test Valid Title\nTest Valid Content", encoding="utf-8")

    for file in test_invalid_files:
        (test_notes_dir / file).write_text("# Test Invalid Title\nTest Invalid Content", encoding="utf-8")

    # calling function in test
    test_results = find_all_live_md_files()

    # checking if only valid files were found
    assert len(test_results) == len(test_valid_files)

    for file in test_valid_files:
        assert file.replace(".md", "") in test_results

    for file in test_invalid_files:
        assert file.replace(".md", "") not in test_results

    # checking if folders containing .md were excluded
    assert test_invalid_folder not in test_results


@pytest.mark.lookup
def test_find_all_live_html_files(setup_test_directories: tuple[Path, Path]) -> None:
    """
    Tests the find_all_live_html_files function to ensure it correctly identifies valid HTML files
    in a test output directory setup.
    The test performs the following checks:
    - Creates a set of valid HTML files (.html) and invalid files (non-.html extensions).
    - Creates a folder named with a .html extension to verify folders are excluded.
    - Writes sample content to each file.
    - Calls find_all_live_html_files and asserts:
        - Only valid HTML files are found.
        - Invalid files are not included in the results.
        - Folders with .html in name are excluded from the results.
    Assertions:
        - Only valid HTML files are present in the results.
        - Invalid files and folders are excluded.
    """
    # test directory setup
    _, test_output_dir = setup_test_directories

    # list of valid html files
    test_valid_files = ["file1.html", "file-2.html", "file_3.html", "file four.html"]

    # list of invalid files
    test_invalid_files = ["badfile1.txt", "badfile-2.md", "badfile_3"]

    # invalid folder
    test_invalid_folder = test_output_dir / "folder.html"
    test_invalid_folder.mkdir()

    # create and write to files
    for file in test_valid_files:
        (test_output_dir / file).write_text("# Test Valid Title\nTest Valid Content", encoding="utf-8")

    for file in test_invalid_files:
        (test_output_dir / file).write_text("# Test Invalid Title\nTest Invalid Content", encoding="utf-8")

    # calling function in test
    test_results = find_all_live_html_files()

    # checking if only valid files were found
    assert len(test_results) == len(test_valid_files)

    for file in test_valid_files:
        assert file.replace(".html", "") in test_results

    for file in test_invalid_files:
        assert file.replace(".html", "") not in test_results

    # checking if folders containing .md were excluded
    assert test_invalid_folder not in test_results


@pytest.mark.cleanup
def test_remove_unnecessary_html_files(setup_test_directories: tuple[Path, Path]) -> None:
    """Test removal of unnecessary HTML files from output directory.
    This test sets up a notes and output directory, creates markdown and HTML files,
    and ensures only HTML files corresponding to markdown files and index.html are
    preserved after calling remove_unnecessary_html_files(). Redundant HTML files
    are deleted.
    Extended Description:
        1. Create notes and output directories using fixture.
        2. Write three markdown files and five HTML files (three live, two redundant).
        3. Write index.html file.
        4. Call remove_unnecessary_html_files().
        5. Assert live HTML files and index.html exist.
        6. Assert redundant HTML files do not exist.
    Assertions:
        - Live HTML files remain in output directory.
        - Redundant HTML files are removed.
        - index.html is preserved.
    """
    # test directory setup
    test_notes_dir, test_output_dir = setup_test_directories

    # list of live .md files
    test_md_files = ["alfa.md", "beta.md", "gamma.md"]

    # list of live .html files
    test_html_files = ["alfa.html", "beta.html", "gamma.html"]

    # list of redundant .html files
    test_redundant_html_files = ["xray.html", "zulu.html"]

    # all html files
    test_all_html_files = test_html_files + test_redundant_html_files

    # mock index file
    test_index = test_output_dir / "index.html"
    test_index.write_text("My Test Index File", encoding="utf-8")

    # create and write to test files
    for file in test_md_files:
        (test_notes_dir / file).write_text("Test markdown file", encoding="utf-8")

    for file in test_all_html_files:
        (test_output_dir / file).write_text("Test html file", encoding="utf-8")

    # calling function in test
    remove_unnecessary_html_files()

    # checking if live files were preserved
    for file in test_html_files:
        assert (test_output_dir / file).exists()

    # checking if redundant files were removed
    for file in test_redundant_html_files:
        assert not (test_output_dir / file).exists()

    # checking if index.html was preserved
    assert test_index.exists()


@pytest.mark.integration
def test_build_notes(setup_test_directories: tuple[Path, Path], monkeypatch: MonkeyPatch) -> None:
    """
    Integration test for the build_notes function to verify end-to-end note conversion.
    This test performs the following steps:
    - Sets up temporary notes and output directories.
    - Creates multiple Markdown files with and without title headers.
    - Creates non-markdown files to ensure they are skipped.
    - Adds redundant HTML files to test cleanup.
    - Mocks CSS and search script to avoid external dependencies.
    - Calls build_notes and verifies:
        - All Markdown files are converted to HTML with correct titles.
        - Non-markdown files are not converted.
        - Redundant HTML files are removed.
        - The index.html file is created and contains links to converted notes.
        - Non-markdown files are not present in the index.
    Args:
        setup_test_directories: Pytest fixture providing temporary notes and output directories.
        monkeypatch: Pytest fixture for patching global variables.
    Assertions:
        - Converted HTML files exist for each Markdown file.
        - HTML titles match extracted or fallback titles.
        - Non-markdown files are not converted.
        - Redundant HTML files are deleted.
        - Index file exists and contains correct links.
        - Non-markdown files are not listed in the index.
    """
    # test directory setup
    test_notes_dir, test_output_dir = setup_test_directories

    # creating mock .md files
    md_files = {
        "file1.md":"# Title 1\nContent 1",
        "file2.md":"# Title 2\nContent 2",
        "file3.md":"No Title Content",
    }

    # creating a non-markdown file that should be skipped
    non_md_files = {
        "file4.txt": "Not Markdown",
        "file5.xml": "",
    }

    for filename, content in {**md_files, **non_md_files}.items():
        (test_notes_dir / filename).write_text(content, encoding="utf-8")

    # creating redundant .html files
    redundant_html_files = ["old.html", "bad_file.html"]
    for file in redundant_html_files:
        (test_output_dir / file).write_text("Old Content", encoding="utf-8")

    # mock css and search to avoid dependencies
    monkeypatch.setattr("main.TEMPLATE_CSS", "/* Mock CSS */")
    monkeypatch.setattr("main.SEARCH_SCRIPT", "<!-- Mock JS -->")

    # calling function in test
    build_notes()

    # checking if directories exists
    assert test_notes_dir.exists()
    assert test_output_dir.exists()

    # checking if files were converted
    for md_file, content in md_files.items():
        html_filename = f"{Path(md_file).stem}.html"
        html_file = test_output_dir / html_filename
        assert html_file.exists()

        # using main.py logic to get titles from mock files
        expected_title = None
        for line in content.split("\n"):
            if line.startswith("# "):
                expected_title = line[2:].strip()
                break

        # fallback to title derived from file name if no title header in file
        if not expected_title:
            expected_title = Path(md_file).stem.replace("-", " ").replace("_", " ").title()

        # checking if correct title is present in converted files
        html_content = html_file.read_text(encoding="utf-8")
        assert f"<title>{expected_title}</title>" in html_content

    # checking if non-markdown files were skipped
    for non_md_file in non_md_files:
        html_filename = f"{Path(non_md_file).stem}.html"
        html_file = test_output_dir / html_filename
        assert not html_file.exists()

    # checking if redundant files were removed
    for redundant_file in redundant_html_files:
        assert not (test_output_dir / redundant_file).exists()

    # checking if index.html was created, preserved and has proper content
    index_file = test_output_dir / "index.html"
    assert index_file.exists()

    index_content = index_file.read_text(encoding="utf-8")
    assert "<title>My Notes</title>" in index_content

    # checking if index contains links to converted files
    for md_file in md_files.keys():
        html_filename = f"{Path(md_file).stem}.html"
        assert f'href="{html_filename}"' in index_content

    # checking that non-markdown files are not in the index
    for non_md_file in non_md_files:
        html_filename = f"{Path(non_md_file).stem}.html"
        assert f'href="{html_filename}"' not in index_content