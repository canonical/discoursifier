#! /usr/bin/env python3

import yaml
import json


def generate_nav_markdown(sections, topics):
    """
    Given a tree of navigation sections and
    a dictionary of created Discourse topics,
    generate nav markdown to link to those topics
    """

    nav_markdown = ""

    for section in sections:
        if "location" in section:
            path = section["location"]

            if path in topics:
                topic = topics[path]
                path = f"/t/{topic['slug']}/{topic['id']}"

            nav_markdown += f"## [{section['title']}]({path})\n\n"
        else:
            nav_markdown += f"## {section['title']}\n\n"

        if "children" in section:
            for item in section["children"]:
                if 'location' in item:
                    path = item["location"]

                    if path in topics:
                        topic = topics[path]
                        path = f"/t/{topic['slug']}/{topic['id']}"

                    nav_markdown += f"- [{item['title']}]({path})\n"
                else:
                    nav_markdown += f"- {item['title']}"

            nav_markdown += "\n"

    return nav_markdown


with open("created-topics.json") as topics_file:
    topics = json.load(topics_file)

with open("metadata.yaml") as data_file:
    meta = yaml.load(data_file)


nav_markdown = generate_nav_markdown(
    sections=meta["navigation"], topics=topics
)


print(nav_markdown)
