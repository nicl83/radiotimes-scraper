# radiotimes-scraper
Scrape issue(s) of the Radio Times (UK) from a public archive

This script takes a year, an issue number, and an optional region (defaults to London) and saves it to `out/(issue_number).pdf`.

## Dependencies
This script requires `asyncio`, `aiohttp`, and `Pillow`.

## Usage
You can either download a single issue or a range of issues.

In either mode, you can override the region suffix (defaults to `l` for London) by using `get_rt_issue_async.py --region xx ...`.
If you are trying to download early issues that do not have a region, use the `--no-region` argument (same position as `--region`.)

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

## Examples
> `get_rt_issue_async.py --region tv single --year 1952 --issue 1475`

Download the "Television edition" of Radio Times issue 1475

> `get_rt_issue_async.py single --year 2002 --issue 4097`

Download the 4097th issue of Radio Times, using the default London region

> `get_rt_issue_async.py batch --year 2002 --from 4092 --to 4097`

Download issues 4092, 4093, 4094, 4095, 4096 and 4097, again using the default London region.
