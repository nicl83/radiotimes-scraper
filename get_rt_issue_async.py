# NL 2022-10-03

import logging
import requests
import glob
import os
import re
import asyncio
import aiohttp

import argparse

from PIL import Image
from pathlib import Path

# Init temp and output folders
Path("tmp").mkdir(exist_ok=True)
Path("out").mkdir(exist_ok=True)

# Configure logging
log_level = logging.INFO

logger = logging.getLogger()
logger.setLevel(log_level)

log_console = logging.StreamHandler()
log_console.setLevel(log_level)

log_formatter = logging.Formatter("[%(asctime)s %(levelname)s] %(message)s")
log_console.setFormatter(log_formatter)

logger.addHandler(log_console)

# Configure argument parser
parser = argparse.ArgumentParser(description="Scrape Radio Times issue from Genome into a PDF")

subparser = parser.add_subparsers(help="Scraper mode", dest="mode")
single_mode = subparser.add_parser(name="single", help="single-issue download mode")
batch_mode = subparser.add_parser(name="batch", help="batch download mode")

parser.add_argument(
    "--region",
    help = "Radio Times region, defaults to London (l)",
    default="l",
    type=str
)

single_mode.add_argument(
    "--year",
    help="Year of Radio Times issue - decade will be automatically guessed",
    required=True,
    type=int
)
single_mode.add_argument(
    "--issue",
    dest="issue_number",
    help = "Radio Times issue number",
    required=True,
    type=int
)

batch_mode.add_argument(
    "--year",
    help="Year of Radio Times issues - decade will be automatically guessed",
    required=True,
    type=int
)
batch_mode.add_argument(
    "--from",
    dest = "start_issue",
    help="Starting issue number",
    required=True,
    type=int
)
batch_mode.add_argument(
    "--to",
    dest = "end_issue",
    help="Ending issue number",
    required=True,
    type=int
)

args = parser.parse_args()
 
rt_year = args.year
rt_decade = round(rt_year, -1) # if there's RT issues in the year 10,000, may God help us all

# extract_page_number = lambda x: int(re.search(r"_(\d*)\.jpg", x).group(1))
page_number_regex = re.compile(r"_(\d*)\.jpg")
def extract_page_number(filename):
    page_number_str = page_number_regex.search(filename).group(1)
    page_number = int(page_number_str)
    return page_number

async def get_rt_issue_pages(decade,year,issue,session: aiohttp.ClientSession):
    logging.info(f"Downloading issue {issue}...")
    root_path = f"https://genome.ch.bbc.co.uk/i/asset/{decade}/{year}/{issue}/{issue}/"
    page_number = 1
    
    while True:
        page_response = await session.get(root_path + f"{page_number}.jpg")
        
        if page_response.status != 200:
            if page_number == 1:
                logging.warning(f"No pages for issue {issue}, check issue number!")
            else:
                logging.info(f"Issue {issue} has {page_number - 1} pages")
            break
        
        with open(f"tmp/{issue}_{page_number}.jpg", "wb") as page_save:
            page_content = await page_response.content.read()
            page_save.write(page_content)
        
        logging.debug(f"saved page {page_number} for issue {issue}")
        page_number += 1

def build_rt_pdf(issue):
    filenames = glob.glob(f"tmp/{issue}_*.jpg")
    # fix page order
    filenames.sort(key=extract_page_number)

    image_objects = [
        Image.open(f) for f in filenames
    ]
    
    if len(image_objects) == 0:
        logging.warning(f"No images DL'd for issue {issue} - check issue number!")
        return
    
    pdf_path = f"out/{issue}.pdf"
    image_objects[0].save(
        pdf_path,
        format="PDF",
        resolution=100.0,
        save_all=True,
        append_images=image_objects[1:]
    )

    logging.info(f"saved {len(image_objects)} pages for issue {issue} to {pdf_path}")

def cleanup(issue):
    cleanup_files = glob.glob(f"tmp/{issue}_*.jpg")
    for file in cleanup_files:
        logging.debug(f"cleanup: deleting {file}")
        os.remove(file)

async def async_get_rt_issue(rt_decade,rt_year,rt_issue):
    async with aiohttp.ClientSession() as aio_session:
        await get_rt_issue_pages(rt_decade, rt_year, rt_issue, aio_session)
    build_rt_pdf(rt_issue)
    cleanup(rt_issue)

async def main():
    if args.mode == "single":
        logging.info("Running in single-issue mode")

        rt_issue = f"{args.issue_number}{args.region}"
        await async_get_rt_issue(rt_decade,rt_year,rt_issue)

    elif args.mode == "batch":        
        logging.info("Running in batch mode")
        logging.info(f"{(args.end_issue - args.start_issue) + 1} issues will be downloaded")
        tasks = []
        for issue_number in range(args.start_issue, args.end_issue+1):
                rt_issue = f"{issue_number}{args.region}"
                tasks.append(asyncio.create_task(async_get_rt_issue(rt_decade,rt_year,rt_issue)))
        
        await asyncio.gather(*tasks)

    else:
        logging.fatal(
        "How did we get here?? "
        "Script is running in a mode we didn't expect. "
        f"Argparse should've caught this - mode is {args.mode}")

if __name__ == "__main__":
    asyncio.run(main())