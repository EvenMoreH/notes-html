from pathlib import Path
import markdown
from datetime import datetime
from templates.css import TEMPLATE_CSS
from templates.search import SEARCH_SCRIPT
import frontmatter


# list of extensions to be used by markdown converter
md_extensions = [
    "extra",
    "toc",
    "codehilite",
    "smarty",
    "sane_lists",
    "nl2br",
]

# directories
NOTES_DIRECTORY = Path("notes")
OUTPUT_DIRECTORY = Path("output")

# checks if directories exist, if not creates them
def ensure_directories() -> None:
    """
    Creates the notes and output directories if they do not already exist.

    This function ensures that both NOTES_DIRECTORY and OUTPUT_DIRECTORY are present
    in the filesystem by creating them if necessary. If the directories already exist,
    no changes are made.

    Raises:
        OSError: If the directories cannot be created due to a system error.
    """
    NOTES_DIRECTORY.mkdir(exist_ok=True)
    OUTPUT_DIRECTORY.mkdir(exist_ok=True)

def extract_title(file: Path, file_content: str) -> str:
    """
    Extracts the title from a Markdown (.md) file's content.

    If the content contains a line starting with '# ', that line (without the '# ') is used as the title.
    Otherwise, the file's stem is converted to title case, with hyphens and underscores replaced by spaces.

    Args:
        file: A pathlib.Path-like object representing the file.
        file_content (str): The content of the Markdown file as a string.

    Returns:
        str: The extracted or generated title of the file.
    """
    # extracting title from .md file
    lines: list[str] = file_content.split("\n")
    file_title: str = file.stem.replace("-", " ").replace("_", " ").title()
    for line in lines:
        if line.startswith("# "):
            file_title = line[2:].strip()
            break
    return file_title


def extract_modified_time(file: Path) -> datetime:
    """
    Extracts the last modified time of a file.

    Args:
        file (Path): The file object whose modified time is to be extracted.

    Returns:
        datetime: The datetime object representing the last modified time of the file.
    """
    modified: datetime = datetime.fromtimestamp(file.stat().st_mtime)
    return modified


def list_of_notes_to_convert() -> list[Path]:
    """
    Generates a list of Markdown (.md) files in the specified notes directory.
    Returns:
        list[Path]: A list of Path objects representing Markdown files found in NOTES_DIRECTORY.
    """
    # making a list of .md files in given directory so it can be iterated over
    md_files: list[Path] = list(NOTES_DIRECTORY.glob("*.md"))
    md_files_in_dir: list[Path] = []
    for file in md_files:
        if file.is_file():
            md_files_in_dir.append(file)

    return md_files_in_dir

# iterating over all .md files in notes directory
def convert_md_to_html(md_files_in_dir: list[Path]) -> tuple[dict[str, str], dict[str, datetime]]:
    """
    Converts a list of Markdown files to HTML files, extracting titles and modification dates.
    For each Markdown file in the provided directory:
    - Converts the file content to HTML using the specified Markdown extensions.
    - Extracts the title from the file content.
    - Extracts the last modified date from the file.
    - Writes the converted HTML to an output file, including a back-link and custom CSS.
    - Maps the output HTML filename to its title and modification date.
    Args:
        md_files_in_dir (list[Path]): A list of Path objects representing Markdown files.
    Returns:
        tuple[dict[str, str], dict[str, datetime]]:
            - A dictionary mapping HTML filenames to their extracted titles.
            - A dictionary mapping HTML filenames to their last modified dates.
    """
    # creating map for file - title pairs
    html_titles: dict[str, str] = {}
    # creating map for file - modified date pairs
    modified_dates: dict[str, datetime] = {}

    for file in md_files_in_dir:
        if file.is_file() and file.suffix.lower() == ".md":
            # create output .html file path directly from stem to cover .MD and .md extensions
            file_out: Path = OUTPUT_DIRECTORY / f"{file.stem}.html"
            md: markdown.Markdown = markdown.Markdown(extensions=md_extensions)

            with file.open("r", encoding="utf-8") as f:
                # loading the file using frontmatter
                md_content: frontmatter.Post = frontmatter.load(f)
                # using frontmatter to return file contents without redundant metadata using .content method
                md_content_parsed: str = md_content.content

                # actual conversion using markdown instance
                html_note: str = md.convert(md_content_parsed)

            # building the .html file
            with file_out.open("w", encoding="utf-8") as f:
                # assigning title for the page
                title: str = extract_title(file, md_content_parsed)
                # mapping .md title to the actual file
                html_titles[file_out.name] = title

                # extracting modified date from file
                modified: datetime = extract_modified_time(file)
                # mapping modified date to the actual file
                modified_dates[file_out.name] = modified

                # injecting data into html
                # adding return to notes button
                html_page: str = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title}</title>
    <style>{TEMPLATE_CSS}</style>
</head>
<body>
    <div>
        <a href="index.html" class="back-link">← Back to Notes</a>
    </div>
    <div>{html_note}</div>
</body>
</html>"""
                # write full output to file
                f.write(html_page)

    # returning dictionaries of html titles and dates of modification mapped to filenames
    return html_titles, modified_dates


def generate_index_file(html_titles: dict[str, str], modified_dates: dict[str, datetime]) -> None:
    """
    Generates an index.html file listing all HTML note files in the OUTPUT_DIRECTORY, excluding index.html itself.
    Each note is displayed with its title (from html_titles if available, otherwise derived from the filename)
    and its last modified date (from modified_dates if available, otherwise from the file's metadata).
    The notes are sorted alphabetically by title and rendered as HTML blocks within the index page.
    Also injects a search input and supporting CSS/JS for filtering notes.
    Args:
        html_titles (dict[str, str]): A dictionary mapping HTML filenames to their respective titles.
        modified_dates (dict[str, datetime]): A dictionary mapping HTML filenames to their last modified datetime objects.
    Returns:
        None. Writes the generated index.html file to OUTPUT_DIRECTORY.
    """
    # string comprehension to generate list of html_notes excluding index.html file itself
    html_notes: list[Path] = [n for n in OUTPUT_DIRECTORY.glob("*.html") if n.is_file() and n.name != "index.html"]

    # create empty dictionary for notes
    dict_of_html_notes: dict[str, str] = {}

    # generate links to pages that will be injected into index.html
    for note in html_notes:
        # unwrapping html_titles and matching on html_titles
        # unwrapping modified_dates and matching on html_titles
        html_title: str
        modified: datetime
        if note.name in html_titles:
            html_title = html_titles[note.name]
            modified = modified_dates[note.name]
        else:
            html_title = note.stem.replace("-", " ").replace("_", " ").title()
            modified = datetime.fromtimestamp(note.stat().st_mtime)

        note_item: str = f"""<div class="note-item">
                    <div class="note-title">
                        <a href="{note.name}">{html_title}</a>
                    </div>
                    <div class="note-date">
                        {modified.strftime("%B %d, %Y")}
                    </div>
                </div>"""

        # building dictionary of title - note pairs
        dict_of_html_notes[f"{html_title}"] = note_item
    # sorting dictionary alphabetically by key == title
    dict_of_html_notes = {key: dict_of_html_notes[key] for key in sorted(dict_of_html_notes.keys())}

    # joining dictionary values into a string to inject is as a whole html block into index file
    string_of_all_html_notes: str = " ".join(dict_of_html_notes.values())

    # index.html template creation
    index_page: str = f"""<!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>My Notes</title>
        <style>{TEMPLATE_CSS}</style>
    </head>
    <body>
        <div>
            <h1>My Notes</h1>
            <input id="search" type="search" placeholder="Search notes..." aria-label="Search notes" />
            <div id="results" class="note-list">
                {string_of_all_html_notes}
            </div>
            <div id="no-results" style="display:none; margin-top:1rem;">No notes found.</div>
        </div>
        {SEARCH_SCRIPT}
    </body>
    </html>"""

    # crating/saving index.html
    index_file: Path = OUTPUT_DIRECTORY / "index.html"
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(index_page)


def find_all_live_md_files() -> list[str]:
    """
    Finds all Markdown (.md) files in the NOTES_DIRECTORY.
    Returns:
        list[str]: A list of stem names (filenames without extension) for all Markdown files found in NOTES_DIRECTORY.
    """
    live_md_files: list[Path] = list(NOTES_DIRECTORY.glob("*.md"))
    live_md_files_in_dir: list[str] = []
    for file in live_md_files:
        if file.is_file():
            live_md_files_in_dir.append(file.stem)

    return live_md_files_in_dir


def find_all_live_html_files() -> list[str]:
    """
    Finds all live HTML files in the OUTPUT_DIRECTORY.
    Returns:
        list[str]: A list of stem names (filenames without extension) for all HTML files found in OUTPUT_DIRECTORY.
    """
    live_html_files: list[Path] = list(OUTPUT_DIRECTORY.glob("*.html"))
    live_html_files_in_dir: list[str] = []
    for file in live_html_files:
        if file.is_file():
            live_html_files_in_dir.append(file.stem)

    return live_html_files_in_dir


def remove_unnecessary_html_files() -> None:
    """
    Removes HTML files from OUTPUT_DIRECTORY that do not have corresponding Markdown files.

    This function compares the stems of Markdown files in NOTES_DIRECTORY with HTML files
    in OUTPUT_DIRECTORY. Any HTML file whose stem does not match a Markdown file is considered
    redundant and is deleted, except for index.html.

    Extended Description:
        - Finds all Markdown and HTML files in their respective directories.
        - Identifies HTML files without corresponding Markdown files.
        - Deletes redundant HTML files, skipping index.html.
        - Prints status messages for deleted files and errors.

    Assertions:
        - Only HTML files with corresponding Markdown files remain after execution.
        - index.html is never deleted.
        - Permission errors and OS errors are handled gracefully.

    Returns:
        None
    """
    live_md_files_in_dir: list[str] = find_all_live_md_files()
    live_html_files_in_dir: list[str] = find_all_live_html_files()

    # generate a list of redundant html files (their .md were deleted)
    redundant_files: set[str] = set(live_html_files_in_dir) - set(live_md_files_in_dir)

    # remove all redundant html files protecting index.html
    for file in redundant_files:
        if file != "index":
            filename: str = file + ".html"
            file_path: Path = OUTPUT_DIRECTORY / filename

            if file_path.exists():
                try:
                    file_path.unlink()
                    print(f"Deleted: {file_path}")
                except PermissionError:
                    print(f"Permission denied when deleting {file_path}")
                except OSError as e:
                    print(f"Error deleting {file_path}: {e}")


def build_notes() -> None:
    """
    Builds HTML notes from Markdown files and generates an index file.

    This function ensures required directories exist, converts Markdown files to HTML,
    removes unnecessary HTML files, and generates an index file with titles and
    modification timestamps.

    Extended Description:
        - Ensures output and source directories are present.
        - Finds Markdown files to convert.
        - Converts Markdown files to HTML, collecting titles and modification times.
        - Removes HTML files that are no longer needed.
        - Generates an index HTML file listing all notes.

    Assertions:
        - Output directory exists after execution.
        - Index file is generated and contains all converted notes.
        - No unnecessary HTML files remain in the output directory.

    Returns:
        None
    """
    ensure_directories()
    md_files_in_dir: list[Path] = list_of_notes_to_convert()
    html_titles: dict[str, str]
    modified: dict[str, datetime]
    html_titles, modified = convert_md_to_html(md_files_in_dir)
    remove_unnecessary_html_files()
    generate_index_file(html_titles, modified)


if __name__ == "__main__":
    build_notes()