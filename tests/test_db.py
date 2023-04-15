from datetime import datetime, timedelta

import pytest

from arxivterminal.db import ArxivDatabase
from arxivterminal.models import ArxivPaper


@pytest.fixture
def test_db(tmp_path):
    db_path = tmp_path / "test.db"
    return ArxivDatabase(str(db_path))


@pytest.fixture
def test_papers():
    return [
        ArxivPaper(
            entry_id="2",
            updated=datetime.now(),
            published=datetime.now() - timedelta(days=2),
            title="Test Paper 2",
            summary="This is another test paper.",
            authors=["John Doe", "Jane Smith"],
            categories=["cs.AI", "cs.CL"],
        ),
        ArxivPaper(
            entry_id="1",
            updated=datetime.now(),
            published=datetime.now() - timedelta(days=1),
            title="Test Paper 1",
            summary="This is a test paper.",
            authors=["John Doe", "Jane Smith"],
            categories=["cs.AI"],
        ),
    ]


def test_save_and_get_papers(test_db, test_papers):
    test_db.save_papers(test_papers)

    papers = test_db.get_papers(published_after=datetime.now() - timedelta(days=10))
    assert len(papers) == 2

    for idx, paper in enumerate(papers):
        assert paper.entry_id == test_papers[idx].entry_id
        assert paper.title == test_papers[idx].title
        assert paper.summary == test_papers[idx].summary
        assert paper.authors == test_papers[idx].authors
        assert paper.categories == test_papers[idx].categories


def test_delete_papers(test_db, test_papers):
    test_db.save_papers(test_papers)
    test_db.delete_papers()
    papers = test_db.get_papers(published_after=datetime.now() - timedelta(days=10))
    assert len(papers) == 0


def test_search_papers(test_db, test_papers):
    test_db.save_papers(test_papers)
    search_result = test_db.search_papers("another")
    assert len(search_result) == 1
    assert search_result[0].entry_id == "2"


def test_get_stats(test_db, test_papers):
    test_db.save_papers(test_papers)
    stats = test_db.get_stats()
    assert len(stats) == 2
    assert stats[0].count == 1
    assert stats[1].count == 1
