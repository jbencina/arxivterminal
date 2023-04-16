from datetime import datetime

import numpy as np
import pytest

from arxivterminal.ml import LsaDocumentSearch, cosine_sim
from arxivterminal.models import ArxivPaper

# You can use sample ArxivPaper objects for testing.
sample_papers = [
    ArxivPaper(
        entry_id="1",
        title="Title 1",
        summary="Summary 1 and some text",
        updated=datetime(2022, 1, 1),
        published=datetime(2022, 1, 1),
        authors=["Author 1"],
        categories=["Category 1"],
        viewed=False,
    ),
    ArxivPaper(
        entry_id="2",
        title="Title 2",
        summary="Summary 2 and some text",
        updated=datetime(2022, 1, 2),
        published=datetime(2022, 1, 2),
        authors=["Author 2"],
        categories=["Category 2"],
        viewed=False,
    ),
    ArxivPaper(
        entry_id="3",
        title="Title 3",
        summary="Summary 3 and some text",
        updated=datetime(2022, 1, 3),
        published=datetime(2022, 1, 3),
        authors=["Author 3"],
        categories=["Category 3"],
        viewed=False,
    ),
    ArxivPaper(
        entry_id="4",
        title="Title 4",
        summary="Summary 4 and some text",
        updated=datetime(2022, 1, 4),
        published=datetime(2022, 1, 4),
        authors=["Author 4"],
        categories=["Category 4"],
        viewed=False,
    ),
    ArxivPaper(
        entry_id="5",
        title="Title 5",
        summary="Summary 5 and some text",
        updated=datetime(2022, 1, 5),
        published=datetime(2022, 1, 5),
        authors=["Author 5"],
        categories=["Category 5"],
        viewed=False,
    ),
]


@pytest.fixture
def lsa_document_search(tmp_path):
    model_path = tmp_path / "test_model.joblib"
    return LsaDocumentSearch(str(model_path))


def test_cosine_sim():
    a = np.array([1, 2, 3])
    b = np.array([2, 3, 4])

    result = cosine_sim(a, b)
    assert result == pytest.approx(0.992, rel=1e-3)


def test_fit(lsa_document_search):
    lsa_document_search.fit(
        sample_papers, force_overwrite=True, min_df=2, max_df=5, embedding_dim=2
    )
    assert lsa_document_search.is_trained
