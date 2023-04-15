import logging
import sys
from datetime import datetime, timedelta

import click

from arxivterminal.constants import DATABASE_PATH, LOG_PATH, MODEL_PATH
from arxivterminal.db import ArxivDatabase
from arxivterminal.fetch import download_papers
from arxivterminal.ml import LsaDocumentSearch
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
    "-e", "--experimental", is_flag=True, help="Uses experimental LSA relevance search"
)
@click.option(
    "-f", "--force", is_flag=True, help="Forces a refresh of the experimental model"
)
@click.option(
    "-l", "--limit", default=10, help="The maximum number of results to return"
)
def search(query, experimental, limit, force):
    """
    Search papers in the database based on a query.

    Parameters
    ----------
    query : str
        Search query for the papers.
    experimental: bool
        If toggled, then documents will be matched using an LSA model rather than a simple string pattern
    limit: int
        The maximum number of results to display.
    force: bool
        If toggled, then forces a refresh of the underlying model before performing a search.
    """
    db = ArxivDatabase(DATABASE_PATH)

    if experimental:
        # TODO: Try better approaches :)
        lsa = LsaDocumentSearch(MODEL_PATH)
        search_results = lsa.search(db, query, limit=limit, force_refresh=force)
    else:
        search_results = db.search_papers(query)[:limit]

    try:
        print_papers(search_results, show_dates=(not experimental))
    except ExitAppException:
        sys.exit(0)


for cmd in [delete_all, fetch, search, show, stats]:
    cli.add_command(cmd)

if __name__ == "__main__":
    cli()
