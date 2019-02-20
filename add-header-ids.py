#! /usr/bin/env python3

import re
from glob import glob


filepaths = glob("**/*.md", recursive=True)


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

        heading_slug = heading_body.replace(" ", "-").replace("`", "").lower()
        heading_html = f'<{elem} id="{heading_slug}">{heading_body}</{elem}>'
        content = re.sub(
            f"^{re.escape(heading)}$",
            heading_html,
            content,
            flags=re.MULTILINE,
        )

    with open(path, "w") as write_handle:
        write_handle.write(content)
