# boostnote2typora

Migration boostnote to typora

## Usages

1. Edit `boostnote_path` in main function
2. Run
3. `typora` directory will be created at `boostnote_path`

## Notes

#### note, images and attachment

- each note copied to *title*.md file
- attachments are copied to *title*.assets directory
- this is to mimic `Copy image to .${filename}.assets` setting in `Images Insert`

#### snippet

- a snippet that have multiple code converted to a md file
- each code will be converted to code block (\`\`\` .. \`\`\`)

#### UML

- it also handle flowchart and latex, but you have to check result
- it does not support inline math and plantuml. you have to translate content manually
- in these two case, script print log message

## Reference

- https://github.com/silverben10/Boostnote-to-Markdown
