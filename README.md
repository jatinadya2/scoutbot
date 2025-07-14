# scoutbot

## Getting scouting reports from sports info solutions
Links in report_links.txt

###  Quick reality-check of the two pages
Both URLs are WordPress posts whose scouting content sits inside article .entry-content; everything above the title and below the footer is noise. 

The “Skill Grade” block is plain paragraphs (not an HTML table), so we’ll regex those lines into a dict.

Player bio lines (Name / College / Bio / DOB) follow a predictable “Field: value” pattern just after the grade block.

### Minimal-disruption micro-pipeline (for these two links)

