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
def ensure_directories():
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

def extract_title(file, file_content) -> str:
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
    lines = file_content.split("\n")
    file_title = file.stem.replace("-", " ").replace("_", " ").title()
    for line in lines:
        if line.startswith("# "):
            file_title = line[2:].strip()
            break
    return file_title


def extract_modified_time(file) -> datetime:
    """
    Extracts the last modified time of a file.

    Args:
        file (os.PathLike or pathlib.Path): The file object whose modified time is to be extracted.

    Returns:
        datetime: The datetime object representing the last modified time of the file.
    """
    modified = datetime.fromtimestamp(file.stat().st_mtime)
    return modified


def list_of_notes_to_convert() -> list:
    """
    Generates a list of Markdown (.md) files in the specified notes directory.
    Returns:
        list: A list of Path objects representing Markdown files found in NOTES_DIRECTORY.
    """
    # making a list of .md files in given directory so it can be iterated over
    md_files = list(NOTES_DIRECTORY.glob("*.md"))
    md_files_in_dir = []
    for file in md_files:
        if file.is_file():
            md_files_in_dir.append(file)

    return md_files_in_dir

# iterating over all .md files in notes directory
def convert_md_to_html(md_files_in_dir) -> tuple[dict, dict]:
    # creating map for file - title pairs
    html_titles = {}
    # creating map for file - modified date pairs
    modified_dates = {}

    for file in md_files_in_dir:
        if file.is_file() and file.suffix.lower() == ".md":
            # create output .html file path directly from stem to cover .MD and .md extensions
            file_out = OUTPUT_DIRECTORY / f"{file.stem}.html"
            md = markdown.Markdown(extensions=md_extensions)

            with file.open("r", encoding="utf-8") as f:
                # loading the file using frontmatter
                md_content = frontmatter.load(f)
                # using frontmatter to return file contents without redundant metadata using .content method
                md_content = md_content.content

                # actual conversion using markdown instance
                html_note = md.convert(md_content)

            # building the .html file
            with file_out.open("w", encoding="utf-8") as f:
                # assigning title for the page
                title = extract_title(file, md_content)
                # mapping .md title to the actual file
                html_titles[file_out.name] = title

                # extracting modified date from file
                modified = extract_modified_time(file)
                # mapping modified date to the actual file
                modified_dates[file_out.name] = modified

                # injecting data into html
                # adding return to notes button
                html_page = f"""<!DOCTYPE html>
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


def generate_index_file(html_titles, modified_dates):
    # string comprehension to generate list of html_notes excluding index.html file itself
    html_notes = [n for n in OUTPUT_DIRECTORY.glob("*.html") if n.is_file() and n.name != "index.html"]

    # create empty dictionary for notes
    dict_of_html_notes = {}

    # generate links to pages that will be injected into index.html
    for note in html_notes:
        # unwrapping html_titles and matching on html_titles
        # unwrapping modified_dates and matching on html_titles
        if note.name in html_titles:
            html_title = html_titles[note.name]
            modified = modified_dates[note.name]
        else:
            html_title = note.stem.replace("-", " ").replace("_", " ").title()
            modified = datetime.fromtimestamp(note.stat().st_mtime)

        note_item = f"""<div class="note-item">
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
    dict_of_html_notes = " ".join(dict_of_html_notes.values())

    # index.html template creation
    index_page = f"""<!DOCTYPE html>
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
                {dict_of_html_notes}
            </div>
            <div id="no-results" style="display:none; margin-top:1rem;">No notes found.</div>
        </div>
        {SEARCH_SCRIPT}
    </body>
    </html>"""

    # crating/saving index.html
    index_file = OUTPUT_DIRECTORY / "index.html"
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(index_page)


def find_all_live_md_files() -> list:
    live_md_files = list(NOTES_DIRECTORY.glob("*.md"))
    live_md_files_in_dir = []
    for file in live_md_files:
        if file.is_file():
            live_md_files_in_dir.append(file.stem)

    return live_md_files_in_dir


def find_all_live_html_files() -> list:
    live_html_files = list(OUTPUT_DIRECTORY.glob("*.html"))
    live_html_files_in_dir = []
    for file in live_html_files:
        if file.is_file():
            live_html_files_in_dir.append(file.stem)

    return live_html_files_in_dir


def remove_unnecessary_html_files():
    live_md_files_in_dir = find_all_live_md_files()
    live_html_files_in_dir = find_all_live_html_files()

    # generate a list of redundant html files (their .md were deleted)
    redundant_files = set(live_html_files_in_dir) - set(live_md_files_in_dir)

    # remove all redundant html files protecting index.html
    for file in redundant_files:
        if file != "index":
            filename = file + ".html"
            file_path = OUTPUT_DIRECTORY / filename

            if file_path.exists():
                try:
                    file_path.unlink()
                    print(f"Deleted: {file_path}")
                except PermissionError:
                    print(f"Permission denied when deleting {file_path}")
                except OSError as e:
                    print(f"Error deleting {file_path}: {e}")


def build_notes():
    ensure_directories()
    md_files_in_dir = list_of_notes_to_convert()
    html_titles, modified = convert_md_to_html(md_files_in_dir)
    remove_unnecessary_html_files()
    generate_index_file(html_titles, modified)


if __name__ == "__main__":
    build_notes()