import logging
from pathlib import Path

import arxiv

from arxivterminal.models import ArxivPaper


def download_paper(paper: ArxivPaper, paper_dir: str = "./arxiv_papers"):
    """
    Downloads an Arxiv paper as PDF to the specified directory.

    Parameters
    ----------
    paper: ArxivPaper
        The paper to be downloaded.
    paper_dir: str
        The path where the paper will be saved. Defaults to ./arxiv_papers
        which means the PDFs will be stored relative to the current
        directory of the script.
    """
    id = paper.entry_id.split("/")[-1]
    file_name = f"{id}.pdf"
    paper_location = Path(paper_dir) / file_name

    if paper_location.exists():
        logging.info(f"Paper is already downloaded at {str(paper_location)}")
        raise FileExistsError
    else:
        paper_location.parent.mkdir(parents=True, exist_ok=True)

    result = next(arxiv.Search(id_list=[id]).results())
    result.download_pdf(dirpath=paper_dir, filename=file_name)
    logging.info(f"Saved paper to {str(paper_location)}")
