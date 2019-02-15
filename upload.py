#! /usr/bin/env python3

# Standard packages
import argparse
import json
import os
import re
import time

# Third-party packages
import requests


# Arguments
parser = argparse.ArgumentParser(
    description=("Upload Markdown documents to a Discourse installation")
)

parser.add_argument("--api-username", required=True)
parser.add_argument("--api-key", required=True)
parser.add_argument("--api-url", required=True)
parser.add_argument("--title-map", required=True)
parser.add_argument(
    "--category", required=True, help=("Category for created posts")
)

args = parser.parse_args()
base_url = args.api_url.rstrip("/")
errors = []


def update_created_topics(created_topics):
    """
    Update created-topics.json with a new dictionaty
    """

    with open("created-topics.json", "w") as created_topics_file:
        json.dump(
            created_topics, created_topics_file, indent=4, sort_keys=True
        )
        print("  > Saved to created-topics.json")


with open(args.title_map) as title_map_file:
    paths = json.load(title_map_file)


print("- Getting ID for category " + args.category)

category_info = requests.get(f"{base_url}/c/{args.category}/show.json")
category_id = category_info.json()["category"]["id"]

print("  > ID: " + str(category_id))

# Get created topics
created_topics = {}

if os.path.isfile("created-topics.json"):
    with open("created-topics.json") as created_posts_file:
        created_topics = json.load(created_posts_file)

for file_path, title in paths.items():
    with open(file_path) as post_content_file:
        post_content = post_content_file.read()

    if file_path in created_topics:
        topic_id = created_topics[file_path]["id"]
        print(f"- Topic {topic_id} already created from {file_path}")
    else:
        response = None

        while response is None or response.status_code == 429:
            if response is not None and response.status_code == 429:
                print(
                    f"  > 429 from API, waiting 5s "
                    f"('{response.json()['errors']}')"
                )
                time.sleep(5)
            print(f"- Trying to create topic from {file_path}")
            response = requests.post(
                base_url + "/posts.json",
                data={
                    "api_key": args.api_key,
                    "api_username": args.api_username,
                    "title": title,
                    "category": category_id,
                    "raw": post_content,
                },
            )

        if response.ok:
            data = response.json()

            print(
                f"  > Topic {data['topic_slug']} created from {file_path}, "
                f"topic ID {data['topic_id']}, post ID {data['id']}"
            )

            created_topics[file_path] = {
                "slug": data["topic_slug"],
                "id": data["topic_id"],
                "wiki": False,
                "links_updated": False,
            }
            update_created_topics(created_topics)
        else:
            error_message = (
                f"Error {response.status_code} creating topic "
                f"from {file_path}: {response.json()['errors']}"
            )
            print(f"  > {error_message}")
            errors.append(error_message)

    if file_path in created_topics:
        topic_id = created_topics[file_path]["id"]

        if created_topics[file_path]["wiki"]:
            print(f"  > Topic {topic_id} already converted to wiki")
        else:
            wiki_response = None

            while wiki_response is None or wiki_response.status_code == 429:
                if (
                    wiki_response is not None
                    and wiki_response.status_code == 429
                ):
                    print(
                        f"  > 429 from API, waiting 5s "
                        f"('{wiki_response.json()['errors']}')"
                    )
                    time.sleep(5)
                print(f"  > Trying to convert topic {topic_id} to Wiki")
                wiki_response = requests.put(
                    f"{base_url}/posts/{topic_id}/wiki",
                    data={
                        "api_key": args.api_key,
                        "api_username": args.api_username,
                        "wiki": True,
                    },
                )

            if wiki_response.ok:
                print("  > Successfully converted")
                created_topics[file_path]["wiki"] = True
                update_created_topics(created_topics)
            else:
                error_message = (
                    f"Error {wiki_response.status_code} converting "
                    f"topic {topic_id} to wiki: "
                    f"{wiki_response.json()['errors']}"
                )
                print(f"  > {error_message}")
                errors.append(error_message)


for file_path, topic_info in created_topics.items():
    topic_url = f"/t/{topic_info['slug']}/{topic_info['id']}"

    if created_topics[file_path]["links_updated"]:
        print(f"- {topic_url} already updated")
        continue

    print(f"- Updating links in {topic_url}")
    get_response = requests.get(f"{base_url}{topic_url}.json?include_raw=1")
    post = get_response.json()["post_stream"]["posts"][0]
    post_content = post["raw"]
    post_id = post["id"]
    print(f"  > Found post ID: {post_id}")

    # Iterate through all created posts again, to replace links
    for nested_file_path, nested_topic_info in created_topics.items():
        nested_topic_url = (
            f"/t/{nested_topic_info['slug']}/{nested_topic_info['id']}"
        )
        post_content = re.sub(
            f"[./]*{nested_file_path}", nested_topic_url, post_content
        )

    post_response = None

    while post_response is None or post_response.status_code == 429:
        if post_response is not None and post_response.status_code == 429:
            print(
                f"  > 429 from API, waiting 5s "
                f"('{post_response.json()['errors']}')"
            )
            time.sleep(5)
        print(f"  > Trying to update post {post_id}")
        post_response = requests.put(
            f"{base_url}/posts/{post_id}.json",
            data={
                "api_key": args.api_key,
                "api_username": args.api_username,
                "post[raw]": post_content,
            },
        )

    if post_response.ok:
        print("  > Successfully updated links")
        created_topics[file_path]["links_updated"] = True
        update_created_topics(created_topics)
    else:
        error_message = (
            f"Error {post_response.status_code} updating links in "
            f"{topic_url}: {post_response.json()['errors']}"
        )
        print(f"  > {error_message}")
        errors.append(error_message)

if errors:
    print("Errors:")
    for error in errors:
        print(error)
