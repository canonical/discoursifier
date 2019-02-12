#! /usr/bin/env python3

# Standard packages
import argparse
import json
import re

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
parser.add_argument("--category", required=True, help=("Category for created posts"))

args = parser.parse_args()
base_url = args.api_url.rstrip('/')


with open(args.title_map) as title_map_file:
    paths = json.load(title_map_file)


print("- Getting ID for category " + args.category)

category_info = requests.get(f"{base_url}/c/{args.category}/show.json")
category_id = category_info.json()['category']['id']

print("  > ID: " + str(category_id))

created_posts = {}

for file_path, title in paths.items():
    with open(file_path) as post_content_file:
        post_content = post_content_file.read()

    print("- Uploading " + file_path)

    response = requests.post(
        base_url + '/posts.json',
        data={
            'api_key': args.api_key,
            'api_username': args.api_username,
            'title': title,
            'category': category_id,
            'raw': post_content
        }
    )

    if response.ok:
        data = response.json()
        created_posts[file_path] = f"/t/{data['topic_slug']}/{data['topic_id']}"

        print(f"  > Topic created, post ID: {data['id']}")

        print("  > Converting to Wiki")
        wiki_response = requests.put(
            f"{base_url}/posts/{data['id']}/wiki",
            data={
                'api_key': args.api_key,
                'api_username': args.api_username,
                'wiki': True,
            }
        )

        if wiki_response.ok:
            print("  > Success")
        else:
            print(f"  > Error {wiki_response.status_code}: {wiki_response.json()['errors']}")
    else:
        print(f"  > Error {response.status_code}: {response.json()['errors']}")


for file_path, topic_url in created_posts.items():
    print(f"- Updating links in {topic_url}")
    get_response = requests.get(f"{base_url}{topic_url}.json?include_raw=1")
    post = get_response.json()['post_stream']['posts'][0]
    post_content = post['raw']
    post_id = post['id']
    print(f"  > Found post ID: {post_id}")

    # Iterate through all created posts again, to replace links
    for file_path, topic_url in created_posts.items():
        post_content = re.sub(f"[./]*{file_path}", topic_url, post_content)

    post_response = requests.put(
        f"{base_url}/posts/{post_id}.json",
        data={
            'api_key': args.api_key,
            'api_username': args.api_username,
            'post[raw]': post_content
        }
    )
    print("  > Updated links")

with open('created-posts.json', 'w') as created_posts_file:
    json.dump(created_posts, created_posts_file)
    print("- Created posts mapping saved to created-posts.json")
