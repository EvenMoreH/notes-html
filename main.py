from pathlib import Path
import markdown
from datetime import datetime
from formatcss import TEMPLATE_CSS


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

# check if directory exists using Path
def directory_exists():
    NOTES_DIRECTORY.mkdir(exist_ok=True)
    OUTPUT_DIRECTORY.mkdir(exist_ok=True)

def extract_title(file, file_content):
    # extracting title from .md file
    lines = file_content.split("\n")
    file_title = file.stem.replace("-", " ").replace("_", " ").title()
    for line in lines:
        if line.startswith("# "):
            file_title = line[2:].strip()
            break
    return file_title


def extract_modified_time(file):
    modified = datetime.fromtimestamp(file.stat().st_mtime)
    return modified


def remove_bad_metadata(md_content):
    # find all lines
    lines = md_content.split("\n")

    # grab index for each line in all the lines
    for index, line in enumerate(lines):
        if line.strip().startswith("#"):
            # when first .md header is found return it and all after it
            return "\n".join(lines[index:])
    # if no header is found, return empty string
    return ""


def list_of_notes_to_convert():
    # making a list of .md files in given directory so it can be iterated over
    md_files = list(NOTES_DIRECTORY.glob("*.md"))
    md_files_in_dir = []
    for file in md_files:
        if file.is_file():
            md_files_in_dir.append(file)

    return md_files_in_dir

# iterating over all .md files in notes directory
def convert_md_to_html(md_files_in_dir):
    # creating map for file - title pairs
    html_titles = {}
    # creating map for file - modified date pairs
    modified_dates = {}

    for file in md_files_in_dir:
        # check if conversions will be done on correct files
        if file.is_file() and file.suffix == ".md":
            # creating file_out path to save converted files to as .html
            file_out = OUTPUT_DIRECTORY / file.name.replace(".md", ".html")
            # creating markdown instance with extensions to use it in upcoming conversion call
            md = markdown.Markdown(extensions=md_extensions)

            with file.open("r", encoding="utf-8") as f:
                # reading the file
                md_content = f.read()

                # preprocess to remove bad metadata at the top of .md files
                md_content = remove_bad_metadata(md_content)

                # actual conversion using markdown instance
                html_note = md.convert(md_content)

            # assigning title for the page
            # injecting data into html
            # mapping .md title to the actual file
            # adding return to notes button
            with file_out.open("w", encoding="utf-8") as f:
                title = extract_title(file, md_content)
                html_titles[file_out.name] = title

                modified = extract_modified_time(file)
                modified_dates[file_out.name] = modified

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

    return html_titles, modified_dates


def generate_index_file(html_titles, modified_dates):
    # building index.html
    html_notes = list(OUTPUT_DIRECTORY.glob("*.html"))
    # remove index.html from the list of notes
    existing_index_file = OUTPUT_DIRECTORY / "index.html"
    if existing_index_file in html_notes:
        html_notes.remove(existing_index_file)

    # create empty list for notes
    list_of_html_notes = []

    # generate links to pages that will be injected into index.html
    for note in html_notes:
        # unwrapping html_titles and matching on html_titles
        # unwrapping modified_dates and matching on html_titles
        if note.name in html_titles:
            html_title = html_titles[note.name]
            modified = modified_dates[note.name]

        list_of_html_notes.append(
            f"""<div class="note-item">
                    <div class="note-title">
                        <a href="{note.name}">{html_title}</a>
                    </div>
                    <div class="note-date">
                        {modified.strftime("%B %d, %Y")}
                    </div>
                </div>"""
        )

    # sorting the list alphabetically
    list_of_html_notes.sort()
    # converting list to string to inject is as a whole html block into index file
    list_of_html_notes = " ".join(list_of_html_notes)

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
            <div class="note-list">
                {list_of_html_notes}
            </div>
        </div>
    </body>
    </html>"""

    # crating/saving index.html
    index_file = OUTPUT_DIRECTORY / "index.html"
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(index_page)


def remove_unnecessary_html_files():
    # find all md files that were converted
    live_md_files = list(NOTES_DIRECTORY.glob("*.md"))
    live_md_files_in_dir = []
    for file in live_md_files:
        if file.is_file():
            live_md_files_in_dir.append(file.stem)
    # adding mock index to list for easier comparisons
    live_md_files_in_dir.append("index")

    # find all published html files
    live_html_files = list(OUTPUT_DIRECTORY.glob("*.html"))
    live_html_files_in_dir = []
    for file in live_html_files:
        if file.is_file():
            live_html_files_in_dir.append(file.stem)

    # generate a list of redundant html files (their .md were deleted)
    redundant_files = list(set(live_html_files_in_dir) ^ set(live_md_files_in_dir))

    # remove all redundant html files
    for file in redundant_files:
        filename = file + ".html"
        file_path = OUTPUT_DIRECTORY / filename

        if file_path.exists():
            file_path.unlink()

def build_notes():
    directory_exists()
    md_files_in_dir = list_of_notes_to_convert()
    html_titles, modified = convert_md_to_html(md_files_in_dir)
    remove_unnecessary_html_files()
    generate_index_file(html_titles, modified)


if __name__ == "__main__":
    build_notes()