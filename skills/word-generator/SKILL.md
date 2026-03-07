---
name: word-generator
description: Generate Word documents (.docx) locally from plain text, Markdown, Markdown files, or Markdown templates with placeholders. Use when you need to create, export, or automate DOCX generation without external services, especially for reports, formatted notes, simple image/table documents, or reusable template-based documents.
---

# Word Generator

Generate a `.docx` file locally with the bundled Python script.

## Workflow

1. Choose one input mode:
   - plain text paragraphs
   - JSON paragraph array
   - Markdown string
   - Markdown file
   - template file with `{{placeholders}}`
2. Run `scripts/create_docx.py` with an output path.
3. Open the generated `.docx` in Word, WPS, or LibreOffice.

## Commands

Markdown file:

```bash
python3 skills/word-generator/scripts/create_docx.py \
  --markdown-file skills/word-generator/assets/examples/sample.md \
  --output ./out/sample.docx
```

Template fill:

```bash
python3 skills/word-generator/scripts/create_docx.py \
  --template-file skills/word-generator/assets/examples/report-template.md \
  --vars-file skills/word-generator/assets/examples/report-vars.json \
  --output ./out/report.docx
```

Plain text:

```bash
python3 skills/word-generator/scripts/create_docx.py \
  --title "Quick Note" \
  --text $'First paragraph\nSecond paragraph' \
  --output ./out/note.docx
```

## Supported Markdown

- `#`, `##`, `###` headings
- plain paragraphs
- unordered lists using `-`, `*`, `+`
- local images using `![alt](./image.png)`
- remote images using `![alt](https://example.com/image.png)`
- simple pipe tables
- inline `**bold**`, `*italic*`, and `` `code` ``

## Placeholder Syntax

Use placeholders like:

```text
{{title}}
{{owner}}
{{summary}}
```

Unknown placeholders are kept as-is.

## Runtime Notes

- Require `python3` and the `python-docx` package on the host.
- Resolve local image paths relative to the Markdown/template file.
- Download remote image URLs during generation.
- Replace missing images with `[missing image: ...]` in the document.
- Keep this skill self-contained under `skills/word-generator/` so it can be packaged as a `.skill` file for distribution.
