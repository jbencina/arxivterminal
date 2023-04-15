import logging
from datetime import datetime, timedelta, timezone
from typing import List

from arxiv import Search, SortCriterion, SortOrder

from arxivterminal.models import ArxivPaper


def download_papers(
    category: str, num_days: int, max_results: int = -1
) -> List[ArxivPaper]:
    """
    Download Arxiv papers from a specified category within the last `num_days`.

    Parameters
    ----------
    category : str
        The category to download papers from, e.g., 'cs.AI' for Artificial Intelligence.
    num_days : int
        The number of days to look back for downloading papers.
    max_results : int, optional, default=-1
        The maximum number of results to return. If -1, return all results.

    Returns
    -------
    List[ArxivPaper]
        A list of ArxivPaper objects representing the downloaded papers.
    """
    current_date = datetime.now(timezone.utc).date()

    start_date = datetime.combine(current_date, datetime.min.time()).replace(
        tzinfo=timezone.utc
    ) - timedelta(days=num_days - 1)
    end_date = datetime.combine(current_date, datetime.max.time()).replace(
        tzinfo=timezone.utc
    )
    logging.info(f"Query from {start_date} to {end_date}")

    search = Search(
        query=f"cat:{category}",
        sort_by=SortCriterion.SubmittedDate,
        sort_order=SortOrder.Descending,
    )

    papers = []

    for i, result in enumerate(search.results()):
        if max_results > 0 and i >= max_results:
            logging.info(f"Reached max results {max_results}")
            break

        paper = ArxivPaper(
            entry_id=result.entry_id,
            updated=result.updated,
            published=result.published,
            title=result.title,
            summary=result.summary,
            authors=[a.name for a in result.authors],
            categories=result.categories,
        )
        if paper.published >= start_date and paper.published <= end_date:
            papers.append(paper)
        elif paper.published < start_date:
            logging.info(f"Reached start date {start_date}")
            break

    logging.info(f"Found {len(papers)} papers")

    return papers
