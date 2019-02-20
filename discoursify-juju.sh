#! /bin/bash
set -exuo pipefail

# Get the right codebase
# git clone https://github.com/juju/docs ~/git/juju-docs
cd ~/git/juju-docs/src/en
git checkout devel
git reset --hard origin/devel
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

# Add IDs to headings
~/git/discoursifier/add-header-ids.py

# Replace "bash" and "no-highlight" code blocks with "text" code blocks
find . -name '*.md' -exec sed -i -E 's!``` (bash|no-highlight)!``` text!g' {} \;

if [ -z "${JUJU_DISCOURSE_API_KEY:-}" ]; then
    echo "Enter the API key:"
    read JUJU_DISCOURSE_API_KEY
fi

echo "Ready to upload? Y/n:"
read ready

# Uploading
if [ "${ready,,}" == "y" ]; then
    ~/git/discoursifier/upload.py --api-key=${JUJU_DISCOURSE_API_KEY} --api-username=system --api-url=https://discourse.jujucharms.com/ --title-map=title-map.json --category=docs-import
fi

# Go back to the original directory
cd -
