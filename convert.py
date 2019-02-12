#! /usr/bin/env python3

from glob import glob
import markdown
import re
import json

filepaths = glob("**/*.md", recursive=True)


def convert_notifications(content):
    """
    Convert old-style notifications:

        !!! Note "title":
            this is some note contents
    
    Into new style:

        [note="title"]
        this is some note contents
        [/note]
    """

    notification_match = (
        "!!! (Note|Warning|Positive|Negative|Important|Tip|Information)"
        '(?: "([^"]*)")?:?(.*\n(?:    .+\n)*)'
    )

    for match in re.finditer(notification_match, content):
        matched_text = match.group(0)
        note_type = match.group(1).lower()
        title = match.group(2)
        body = match.group(3).strip()

        if note_type in ["warning", "important"]:
            note_type = "caution"

        if note_type == "tip":
            note_type = "note"

        if note_type and body:
            body = re.sub("^    ", "", body).replace("\n    ", "\n")

            options = ""

            if note_type != "note":
                options = f"={note_type}"

            if title:
                options = f'{options} title="{title}"'

            replacement = f"[note{options}]\n{body}\n[/note]\n"

            content = content.replace(matched_text, replacement)

    return content


def convert_metadata(content):
    """
    Convert Markdown metadata
    (See https://python-markdown.github.io/extensions/meta_data/)

    "Title" will be added as a <h1>, if there isn't one already
    "TODO" will be preserved in `<!-- -->` HTML comments
    anything else will be ignored
    """

    parser = markdown.Markdown(extensions=["markdown.extensions.meta"])

    parser.convert(content)
    title = parser.Meta.get("title", [None])[0]
    todo = "\n- ".join(parser.Meta.get("todo", []))
    content = re.sub("^( *\w.*\n)*", "", content).lstrip()

    title_match = re.match("^# ([^\n]+)(.*)$", content, re.DOTALL)

    if title_match and len(title_match) > len(title):
        # Prefer the <h1> value to the metadata
        title = title_match.groups()[0]
        content = title_match.groups()[1].strip()

    if todo:
        content = f"<!--\nTodo:\n- {todo}\n-->\n\n" + content

    return title, content


title_map = {}

# Convert markdown
for path in filepaths:
    with open(path) as file_handle:
        content = file_handle.read()

    content = convert_notifications(content)
    title, content = convert_metadata(content)

    title_map[path] = title

    with open(path, "w") as file_handle:
        file_handle.write(content)

# Write title mapping to file
with open("title-map.json", "w") as title_map_file:
    json.dump(title_map, title_map_file)
