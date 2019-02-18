#! /bin/bash
set -exuo pipefail

# Get the right codebase
# git clone https://github.com/juju/docs ~/git/juju-docs
cd ~/git/juju-docs/src/en
git checkout devel
git checkout .
git pull

# Remove files we don't want to include in Discourse
rm commands.md test.md index.md

# Apply discoursifier conversions
~/git/discoursifier/convert.py

# Reformat with pandoc to remove newlines
find . -name '*.md' -exec pandoc --atx-headers -f markdown_mmd+backtick_code_blocks -t markdown_mmd+hard_line_breaks+backtick_code_blocks+shortcut_reference_links {} -o {} \;

# Unescape characters espaced by pandoc
find . -name '*.md' -exec sed -i -E 's!\\(\[|\*|\^|`|_|[(]|[)]|\$|\]|#|~)!\1!g' {} \;

# Fix notification blocks
find . -name '*.md' -exec sed -i -E 's!(\[note[^]]*\]) !\1\n!g' {} \;
find . -name '*.md' -exec sed -i -E 's! \[/note\]!\n[/note]!g' {} \;

# Replace "bash" and "no-highlight" code blocks with "text" code blocks
find . -name '*.md' -exec sed -i -E 's!``` (bash|no-highlight)!``` text!g' {} \;

echo "Enter the API key:"
read api_key

# Uploading
~/git/discoursifier/upload.py --api-key=${api_key} --api-username=system --api-url=https://discourse.jujucharms.com/ --title-map=title-map.json --category=docs-import

# Go back to the original directory
cd -
