# radiotimes-scraper
Scrape issue(s) of the Radio Times (UK) from a public archive

This script takes a year, an issue number, and an optional region (defaults to London) and saves it to `out/(issue_number).pdf`.

## Usage
You can either download a single issue or a range of issues.

In either mode, you can override the region suffix (defaults to `l` for London) by using `get_rt_issue_async.py --region xx ...`

### Single-issue mode
`get_rt_issue_async.py single --year 2002 --issue 4097`

Required arguments:
- `--year` - the year in which the issue was published
- `--issue` - the issue number to be downloaded

### Batch mode
`get_rt_issue_async.py batch --year 2002 --from 4087 --to 4097`

Required arguments:
- `--year` - same as above, the year in which the issues were published
- - This script cannot download issues from multiple years at once, sorry.
- `--from` - the issue to start downloading from
- `--to` - the issue to download to (inclusive)
