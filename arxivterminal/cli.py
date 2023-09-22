import logging
import sys
from datetime import datetime, timedelta

import click

from arxivterminal.constants import DATABASE_PATH, LOG_PATH
from arxivterminal.db import ArxivDatabase
from arxivterminal.fetch import download_papers
from arxivterminal.output import ExitAppException, print_papers, print_stats


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
    default="cs.AI,cs.LG",  # AI and Machine Learning categories
    help="Comma-separated list of categories to fetch papers.",
)
def fetch(num_days, categories):
    """
    Fetch papers from the specified categories and store them in the database.
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


@click.command()
@click.option("--days-ago", default=7, help="Number of days ago to fetch papers.")
def show(days_ago):
    """
    Show papers fetched from the specified number of days ago.
    """
    published_after = datetime.now() - timedelta(days=days_ago)
    db = ArxivDatabase(DATABASE_PATH)
    papers = db.get_papers(published_after)

    try:
        print_papers(papers)
    except ExitAppException:
        sys.exit(0)


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
@click.option(
    "-l", "--limit", default=10, help="The maximum number of results to return"
)
def search(query, limit):
    """
    Search papers in the database based on a query.
    """
    db = ArxivDatabase(DATABASE_PATH)
    search_results = db.search_papers(query)[:limit]

    try:
        print_papers(search_results, show_dates=True)
    except ExitAppException:
        sys.exit(0)


for cmd in [delete_all, fetch, search, show, stats]:
    cli.add_command(cmd)

if __name__ == "__main__":
    cli()
