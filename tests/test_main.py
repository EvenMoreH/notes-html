import pytest
from main import *
from pathlib import Path
from datetime import datetime
import os
from conftest import setup_test_directories


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
    Test the extract_modified_time function to ensure it returns the correct modification time for a file.
    This test creates a temporary markdown file, writes sample content to it, and compares the modification time
    returned by extract_modified_time with the actual modification time obtained from the filesystem.
    Args:
        tmp_path (pathlib.Path): pytest fixture providing a temporary directory unique to the test invocation.
    Asserts:
        The modification time returned by extract_modified_time matches the actual modification time of the file.
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


@pytest.mark.conversion
def test_convert_md_to_html_basic(setup_test_directories):
    """
    Test the convert_md_to_html function for basic Markdown to HTML conversion.
    This test:
    - Sets up test directories using setup_test_directories fixture.
    - Creates multiple Markdown files with varying content (basic, complex, and no title).
    - Writes the files to the test notes directory.
    - Calls convert_md_to_html with the list of created Markdown files.
    - Asserts that the correct number of HTML titles and metadata entries are returned.
    - Verifies that the corresponding HTML files are created in the output directory.
    - Checks that each HTML file contains essential HTML elements and expected content.
    Args:
        setup_test_directories: Pytest fixture that provides temporary test notes and output directories.
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
def test_convert_md_to_html_metadata_file(setup_test_directories):
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
def test_convert_md_to_html_empty_file(setup_test_directories):
    """
    Test that an empty Markdown file is correctly converted to an HTML file.
    This test verifies that:
    - An empty Markdown file is created and passed to the conversion function.
    - The resulting HTML file exists in the output directory.
    - The HTML file uses the filename (with formatting) as the title ("Empty File").
    - The HTML file contains the expected HTML structure and elements, including:
        - <!DOCTYPE html>
        - <html> and </html> tags
        - <title>Empty File</title>
        - <style> tag
        - "Back to Notes" link text
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
def test_convert_md_to_html_non_md_file(setup_test_directories):
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
def test_generate_index_file_basic(setup_test_directories):
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
def test_generate_index_file_empty_directory(setup_test_directories):
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
def test_generate_index_file_missing_metadata(setup_test_directories):
    """
    Test the generate_index_file function when HTML files are missing metadata.
    This test verifies that:
    - The index.html file is generated in the output directory.
    - The index.html contains the expected HTML structure and search functionality.
    - All note files present in the output directory are included in the index, even if their titles are missing from metadata.
    - The modification date of each note is displayed in "Month Day, Year" format.
    - Notes are sorted alphabetically by title, which is derived from the filename if metadata is missing.
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

def test_find_all_live_md_files():
    pass


def test_find_all_live_html_files():
    pass


def test_remove_unnecessary_html_files():
    pass


def test_build_notes():
    pass