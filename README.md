# boostnote2typora

Migration boostnote to typora

## Requirements

- Python3 and cson, pathlib, pathvalidate packages (install using pip)
- Make sure there is no empty note

## Usages

1. Edit `boostnote_path` in main function
2. Run
3. `typora` directory will be created at `boostnote_path`

## Notes

#### note, images and attachment

- Each note copied to *title*.md file
- Attachments are copied to *title*.assets directory
- This is to mimic `Copy image to .${filename}.assets` setting in `Images Insert`

#### snippet

- A snippet that have multiple code converted to a md file
- Each code will be converted to code block (\`\`\` .. \`\`\`)

#### UML

- It also handle flowchart and latex, but you have to check result
- It does not support inline math and plantuml. you have to translate content manually
- In these two case, script print log message

## Reference

- https://github.com/silverben10/Boostnote-to-Markdown
