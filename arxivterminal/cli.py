import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

import click
from appdirs import user_data_dir, user_log_dir

from arxivterminal.db import ArxivDatabase
from arxivterminal.fetch import download_papers
from arxivterminal.output import print_papers, print_stats

APP_NAME = "arxivterminal"
DATABASE_PATH = Path(user_data_dir(APP_NAME)) / "papers.db"
LOG_PATH = Path(user_log_dir(APP_NAME)) / f"{APP_NAME}.log"


@click.group()
def cli():
    """
    Main CLI entry point.
    """
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.INFO, filename=LOG_PATH)
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


@click.command()
@click.option("--num-days", default=7, help="Number of days to fetch papers.")
@click.option(
    "--categories",
    default="cs.AI",
    help="Comma-separated list of categories to fetch papers.",
)
def fetch(num_days, categories):
    """
    Fetch papers from the specified categories and store them in the database.

    Parameters
    ----------
    num_days : int
        Number of days to fetch papers.
    categories : str
        Comma-separated list of categories to fetch papers.
    """
    categories = categories.split(",")
    db = ArxivDatabase(DATABASE_PATH)
    for category in categories:
        papers = download_papers(category, num_days=num_days)
        db.save_papers(papers)
        logging.info(f"Fetched papers from {category}")


@click.command()
def delete_all():
    """
    Delete all papers from the database.
    """
    db = ArxivDatabase(DATABASE_PATH)
    db.delete_papers()
    logging.info("Deleted all papers from the database")


@click.command()
@click.option("--days-ago", default=7, help="Number of days ago to fetch papers.")
def show(days_ago):
    """
    Show papers fetched from the specified number of days ago.

    Parameters
    ----------
    days_ago : int
        Number of days ago to fetch papers.
    """
    published_after = datetime.now() - timedelta(days=days_ago)
    db = ArxivDatabase(DATABASE_PATH)
    papers = db.get_papers(published_after)
    print_papers(papers)


@click.command()
def stats():
    """
    Show statistics of the papers stored in the database.
    """
    db = ArxivDatabase(DATABASE_PATH)
    stats = db.get_stats()
    print_stats(stats)
    print(f"Log path: {LOG_PATH}")
    print(f"Data path: {DATABASE_PATH}")


@click.command()
@click.argument("query")
def search(query):
    """
    Search papers in the database based on a query.

    Parameters
    ----------
    query : str
        Search query for the papers.
    """
    db = ArxivDatabase(DATABASE_PATH)
    papers = db.search_papers(query)
    print_papers(papers)


for cmd in [delete_all, fetch, search, show, stats]:
    cli.add_command(cmd)

if __name__ == "__main__":
    cli()
