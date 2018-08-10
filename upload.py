#! /usr/bin/env python3

import argparse

# Arguments
parser = argparse.ArgumentParser(
    description=("Upload Markdown documents to a Discourse installation")
)

parser.add_argument('files', nargs="+", help=("Markdown files to upload"))
parser.add_argument('--api-username', required=True)
parser.add_argument('--api-key', required=True)
parser.add_argument('--api-url', required=True)
parser.add_argument(
    '--category',
    default="documentation",
    help=("Category for created posts (default: 'documentation')")
)

args = parser.parse_args()

print(str(args))
