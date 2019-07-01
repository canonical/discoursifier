#! /bin/bash
set -exuo pipefail

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
