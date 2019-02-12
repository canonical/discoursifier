# Discoursifier

Scripts for converting Markdown files from [documentation-builder](https://github.com/canonical-webteam/documentation-builder) format.

## Usage

Example:

``` bash
cd juju-docs/src/en  # Where all the .md files are
~/git/discoursifier/convert.py  # Convert all .md files, create "title-map.json"
~/git/discoursifier/upload.py --api-url https://discourse.jujucharms.com --api-key xxxxx --api-username robin --category docs --title-map title-map.json
```

This should upload all items to the API.

You can also delete all items in a topic with:

``` bash
~/git/discoursifier/delete.py --api-url https://discourse.jujucharms.com --api-key xxxxx --api-username robin --category docs
```
