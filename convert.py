#! /usr/bin/env python3

from glob import glob
import markdown
import os
import re
import json
import subprocess

filepaths = glob("**/*.md", recursive=True)


def convert_foldouts(content):
    links = ""
    body_links = content.split("\n\n<!-- LINKS -->")

    if len(body_links) > 1:
        content = body_links[0]
        links = "\n\n<!-- LINKS -->" + body_links[1]

    sections = re.split("(?:^|\n)\^# ", content)

    new_content = ""

    for index, section in enumerate(sections):
        if index == 0:
            new_content = section
            continue

        foldout_match = re.match(
            "^(\w.*)\n((?: +.*\n|\n)+)((?:.|\n)*$)", section
        )

        summary = foldout_match.groups()[0]
        foldout_body = foldout_match.groups()[1]
        remainder = foldout_match.groups()[2]

        foldout_html = markdown.markdown(foldout_body + links)

        new_content += (
            f"\n<details>\n<summary>{summary}</summary>"
            f"\n{foldout_html}\n</details>\n{remainder}"
        )

    return new_content + links


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
                options = f' type="{note_type}"'

            if title:
                options = f'{options} status="{title}"'

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

    head, body = content.split("\n\n", 1)

    body = body.strip()

    parser = markdown.Markdown(extensions=["markdown.extensions.meta"])
    parser.convert(head)
    title = parser.Meta.get("title", [None])[0]
    todo = "\n- ".join(parser.Meta.get("todo", []))
    title_match = re.match("^# ([^\n]+)(.*)$", body, re.DOTALL)

    if title_match:
        # Prefer the longer tile
        if title and len(title_match.groups()[0]) > len(title):
            title = title_match.groups()[0]
        body = title_match.groups()[1].strip()

    if todo:
        body = f"<!--\nTodo:\n- {todo}\n-->\n\n" + body

    return title, body


title_map = {}

with open('uploaded-media.json') as media_json:
    images_map = json.load(media_json)

# Convert markdown
# ===

print("\n# Converting Markdown content")

for path in filepaths:
    print(f"- Converting {path}")

    with open(path) as file_handle:
        content = file_handle.read()

    # Remove <style> tags
    content = re.sub("<style[^>]*>[^<]*</style>", "", content, flags=re.DOTALL)

    content = convert_notifications(content)
    title, content = convert_metadata(content)
    content = convert_foldouts(content)

    # Replace image URLs
    for media in images_map:
        relative_path = os.path.relpath(media['local_filepath'])
        content = content.replace(f"({relative_path})", f"({media['url']})")
        content = content.replace(f'"{relative_path}"', f'"{media["url"]}"')
        content = content.replace(f' {relative_path}', f' {media["url"]}')

    title_map[path] = title

    with open(path, "w") as file_handle:
        file_handle.write(content)

print("\n> Writing to title-map.json")

# Write title mapping to file
with open("title-map.json", "w") as title_map_file:
    json.dump(title_map, title_map_file, indent=4, sort_keys=True)

print("\n> Running pandoc transformations")

for path in filepaths:
    # Reformat file to remove newlines
    subprocess.check_call(
        [
            "pandoc",
            "--atx-headers",
            "-f",
            "markdown_mmd+backtick_code_blocks",
            "-t",
            (
                "markdown_mmd+hard_line_breaks+"
                "backtick_code_blocks+shortcut_reference_links"
            ),
            path,
            "-o",
            path,
        ]
    )

    # Unescape characters escaped by Pandoc
    subprocess.check_call(
        [
            "sed",
            "-i",
            "-E",
            r"s!\\(\[|\*|\^|`|_|[(]|[)]|\$|\]|#|~)!\1!g",
            path,
        ]
    )

    # Add notifications around notification blocks
    subprocess.check_call(
        ["sed", "-i", "-E", r"s!(\[note[^]]*\]) !\1\n!g", path]
    )

# Add header IDs
# ===

print("\n> Adding heading markup")

heading_slugs = {}

if os.path.isfile("heading-slugs.json"):
    with open("heading-slugs.json") as heading_slugs_handle:
        heading_slugs = json.load(heading_slugs_handle)

for path in filepaths:
    with open(path) as read_handle:
        content = read_handle.read()

    headings = re.findall("(^#{2,4} .*)", content, flags=re.MULTILINE)

    for heading in headings:
        elem = None
        heading_body = ""

        if heading[:3] == "## ":
            elem = "h2"
            heading_body = heading[3:]
        elif heading[:4] == "### ":
            elem = "h3"
            heading_body = heading[4:]
        elif heading[:5] == "#### ":
            elem = "h4"
            heading_body = heading[5:]

        old_heading_slug = (
            heading_body.replace(" ", "-").replace("`", "").lower()
        )
        new_heading_slug = "heading--" + re.sub(
            r"[^\w-]", "", old_heading_slug
        ).strip("-")

        heading_slugs[old_heading_slug] = new_heading_slug

        heading_html = (
            f'<{elem} id="{new_heading_slug}">{heading_body}</{elem}>'
        )
        content = re.sub(
            f"^{re.escape(heading)}$",
            heading_html,
            content,
            flags=re.MULTILINE,
        )

    with open(path, "w") as write_handle:
        write_handle.write(content)

# Now update the heading links
for path in filepaths:
    for old_heading_slug, new_heading_slug in heading_slugs.items():
        with open(path) as read_handle:
            content = read_handle.read()

        content = re.sub(
            "#" + re.escape(old_heading_slug) + r"([\]\)$])",
            "#" + new_heading_slug + r"\1",
            content,
        )

        with open(path, "w") as write_handle:
            write_handle.write(content)

print("\n> Writing to heading-slugs.json")

with open("heading-slugs.json", "w") as heading_slugs_handle:
    json.dump(heading_slugs, heading_slugs_handle, indent=4, sort_keys=True)
