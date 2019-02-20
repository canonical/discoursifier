#! /usr/bin/env python3

import json
import os
import re
from glob import glob


filepaths = glob("**/*.md", recursive=True)

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
            "[^\w-]", "", old_heading_slug
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

with open("heading-slugs.json", "w") as heading_slugs_handle:
    json.dump(heading_slugs, heading_slugs_handle, indent=4, sort_keys=True)
