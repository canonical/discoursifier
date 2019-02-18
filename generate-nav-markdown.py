#! /usr/bin/env python3

import yaml
import json


def get_location(path):
    if path in topics:
        topic = topics[path]
        path = f"/t/{topic['slug']}/{topic['id']}"

    return path


with open('created-topics.json') as topics_file:
    topics = json.load(topics_file)

with open('metadata.yaml') as data_file:
    meta = yaml.load(data_file)


nav_sections = meta['navigation']

for section in nav_sections:
    if 'location' in section:
        path = get_location(item['location'])
        print(f"## [{section['title']}]({path})\n")
    else:
        print(f"## {section['title']}\n")

    if 'children' in section:
        for item in section['children']:
            path = get_location(item['location'])

            print(f"- [{item['title']}]({path})")
        
        print("\n")