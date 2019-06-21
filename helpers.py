# Standard library
import json
import os


def get_created_topics():
    """
    Retrieve a dictionary from the created-topics.json file
    """

    created_topics = {}

    if os.path.isfile("created-topics.json"):
        with open("created-topics.json") as created_posts_file:
            created_topics = json.load(created_posts_file)

    return created_topics


def save_created_topics(created_topics):
    """
    Update created-topics.json with a new dictionary
    """

    with open("created-topics.json", "w") as created_topics_file:
        json.dump(
            created_topics, created_topics_file, indent=4, sort_keys=True
        )
        print("  > Saved to created-topics.json")


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
