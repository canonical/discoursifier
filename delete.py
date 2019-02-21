#! /usr/bin/env python3

# Standard packages
import argparse

# Local imports
from discourse_api import DiscourseAPI

# Arguments
parser = argparse.ArgumentParser(
    description=("Upload Markdown documents to a Discourse installation")
)

parser.add_argument("--api-username", required=True)
parser.add_argument("--api-key", required=True)
parser.add_argument("--api-url", required=True)
parser.add_argument(
    "--category", required=True, help=("Category for created posts")
)

args = parser.parse_args()

api = DiscourseAPI(
    url=args.api_url.rstrip("/"),
    username=args.api_username,
    key=args.api_key,
    category_name=args.category,
)

category_topics = api.get_category_topics()

while len(category_topics) > 1:
    print(f"- Deleting {len(category_topics)}")

    for topic in category_topics:
        api.delete_topic(topic["id"])

    print("- Getting topics again, to check we deleted them all")
    category_topics = api.get_category_topics()

api.print_errors()
