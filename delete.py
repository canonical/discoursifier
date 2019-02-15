#! /usr/bin/env python3

# Standard packages
import argparse
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
parser.add_argument("--category", required=True, help=("Category for created posts"))

args = parser.parse_args()
base_url = args.api_url.rstrip('/')
errors = []


def get_category_topics():
    category_info = requests.get(f"{base_url}/c/{args.category}/show.json")
    category_id = category_info.json()['category']['id']
    category_data = requests.get(f"{base_url}/c/{category_id}.json")
    return category_data.json()['topic_list']['topics']


category_topics = get_category_topics()

while len(category_topics) > 1:
    print(f"- Deleting {len(category_topics)}")

    for topic in category_topics:
        response = None

        while response is None or response.status_code == 429:
            if response is not None and response.status_code == 429:
                print(f"  > 429 from API, waiting 5s ('{response.json()['errors']}')")
                time.sleep(5)
            print(f"- Trying to delete topic: {topic['id']}")
            response = requests.delete(
                f"{base_url}/t/{topic['id']}.json",
                params={
                    'api_key': args.api_key,
                    'api_username': args.api_username,
                }
            )

        if response.ok:
            print(f"  > Deleted")
        else:
            error_message = f"Error {response.status_code} deleting topic {topic['id']}: {response.json()['errors']}"
            print(F"  > {error_message}")
            errors.append(error_message)

    print("- Getting topics again, to check we deleted them all")
    category_topics = get_category_topics()


if errors:
    print("Errors:")
    for error in errors:
        print(error)
