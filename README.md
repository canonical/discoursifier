# Discoursifier

Scripts for converting Markdown files from [documentation-builder](https://github.com/canonical-webteam/documentation-builder) format.

## Usage

Example:

``` bash
# First, set up a python environment and install dependencies
python3 -m venv env3
source env3/bin/activate
pip3 install -r ~/git/discoursifier/requirements.txt

# Now get to the documents you want to convert and upload
cd ~/Projects/juju-docs/src/en  # Where all the .md files are
git checkout master  # Check we're on the right branch
git pull             # Check we're up to date

# Upload assets to the assets server, create "uploaded-media.json"
upload-assets --api-token XXX ../media/ > uploaded-media.json
# Now open up uploaded-media.json and fix its JSON format

# Now convert all .md files, create "title-map.json", "heading-slugs.json"
~/Projects/discoursifier/convert.py

# And upload to the Discourse, create "created-topics.json"
~/Projects/discoursifier/upload.py --api-url https://discourse.jujucharms.com --api-key xxxxx
```

This should upload all items to the API, and replace all links as appropriate.

Now you can generate the navigation markdown, which you should place in the index topic under a `# Navigation` heading:

``` bash
~/Projects/discoursifier/generate-nav-markdown.md  # Read metadata.yaml and generate nav markdown from it
```

You can also delete all items in a topic with:

``` bash
~/Projects/discoursifier/delete.py --api-url https://discourse.jujucharms.com --api-key xxxxx
```
