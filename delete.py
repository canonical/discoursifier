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

# Get category data
category_info = requests.get(f"{base_url}/c/{args.category}/show.json")
category_id = category_info.json()['category']['id']
category_data = requests.get(f"{base_url}/c/{category_id}.json")
category_topics = category_data.json()['topic_list']['topics']

for topic in category_topics:
    response = None

    while response is None or response.status_code == 429:
        if response is not None and response.status_code == 429:
            print(f"  > API says 'back-off': Waiting 1s for API to be ready")
            time.sleep(1)
        print(f"- Trying to delete topic: {topic['id']}")
        response = requests.delete(
            f"{base_url}/t/{topic['id']}.json",
            params={
                'api_key': args.api_key,
                'api_username': args.api_username,
            }
        )

    if response.ok:
        print(f"  > Deleted: {response.text}")
    else:
        error_message = f"  > Error {response.status_code}: {response.json()['errors']}"
        print(error_message)
        errors.append(error_message)

if errors:
    print("Errors:")
    for error in errors:
        print(error)
