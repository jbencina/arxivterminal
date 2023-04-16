import shutil
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from arxivterminal.download import download_paper
from arxivterminal.models import ArxivPaper


def test_download_paper_exception():
    paper_id = 1
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create an ArxivPaper object
        test_paper = ArxivPaper(
            entry_id=f"http://arxiv.org/abs/1",
            updated=datetime.now(),
            published=datetime.now(),
            title="Test Paper",
            summary="This is a test paper.",
            authors=["John Doe", "Jane Doe"],
            categories=["cs.AI", "cs.LG"],
            viewed=False,
        )

        path = Path(tmpdir) / f"{paper_id}.pdf"

        with open(path, "w"):
            # Create empty file
            pass

        # Check if an exception is raised when trying to download the same paper again
        with pytest.raises(FileExistsError):
            download_paper(test_paper, paper_dir=tmpdir)

        # Clean up the temporary directory
        shutil.rmtree(tmpdir)
