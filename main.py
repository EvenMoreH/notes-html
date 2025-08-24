from pathlib import Path
import markdown

from examplecss import TEMPLATE_CSS

md_extensions = [
    "extra",
    "toc",
    "codehilite",
    "smarty",
]

# directories
NOTES_DIRECTORY = Path("notes")
OUTPUT_DIRECTORY = Path("output")

# check if directory exists using Path
def directory_exists():
    NOTES_DIRECTORY.mkdir(exist_ok=True)
    OUTPUT_DIRECTORY.mkdir(exist_ok=True)

# making a list of .md files in given directory so it can be iterated over
md_files = list(NOTES_DIRECTORY.glob("*.md"))
files_in_dir = []
for file in md_files:
    if file.is_file():
        files_in_dir.append(file)

for file in files_in_dir:
    # creating file_out path to save converted files to
    file_out = OUTPUT_DIRECTORY / file.name.replace(".md", "")
    markdown.markdownFromFile(input=f"{file}", output=f"{file_out}.html", encoding="utf-8", extensions=md_extensions)