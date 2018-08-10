#! /usr/bin/env python3

from glob import glob
import markdown
import re

filepaths = glob('**/*.md', recursive=True)


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
        '!!! (Note|Warning|Positive|Negative)'
        '(?: "([^:]+)")?: *\n((?:    [^\n]+\n)+)'
    )

    for match in re.finditer(notification_match, content):
        matched_text = match.group(0)
        note_type = match.group(1)
        title = match.group(2)
        body = match.group(3).strip()

        if note_type and body:
            body = re.sub('^    ', '', body).replace('\n    ', '\n')

            replacement = ""

            if title:
                replacement = f'[{note_type}="{title}"]\n{body}\n[/{note_type}]'
            else:
                replacement = f'[{note_type}]\n{body}\n[/{note_type}]'

            content = content.replace(matched_text, replacement)

    return content


def convert_metadata(content):
    """
    Convert Markdown metadata (https://python-markdown.github.io/extensions/meta_data/).

    "Title" will be added as a <h1>, if there isn't one already
    "TODO" will be preserved in `<!-- -->` HTML comments
    anything else will be ignored
    """

    parser = markdown.Markdown(extensions=['markdown.extensions.meta'])

    parser.convert(content)
    title = parser.Meta.get('title', [])[0]
    todo = "\n- ".join(parser.Meta.get('todo', []))
    content = re.sub('^( *\w.*\n)*', '', content).lstrip()

    if title and not content.startswith('# '):
        content = f'# {title}\n\n' + content

    if todo:
        content = f"<!--\nTodo:\n- {todo}\n-->\n\n" + content

    return content


for path in filepaths:
    with open(path) as file_handle:
        content = file_handle.read()

    content = convert_notifications(content)
    content = convert_metadata(content)

    with open(path, 'w') as file_handle:
        file_handle.write(content)
