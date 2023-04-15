import pytest

from arxivterminal.db import ArxivStats
from arxivterminal.output import print_stats


@pytest.fixture
def test_stats():
    return [
        ArxivStats(date="2023-01-01", count=5),
        ArxivStats(date="2023-01-02", count=3),
        ArxivStats(date="2023-01-03", count=2),
    ]


def test_print_stats(capsys, test_stats):
    print_stats(test_stats)

    captured = capsys.readouterr()
    output = captured.out.splitlines()

    assert output[0] == "Date       | Count"
    assert output[1] == "-------------------"
    assert output[2] == "2023-01-01 | 5"
    assert output[3] == "2023-01-02 | 3"
    assert output[4] == "2023-01-03 | 2"
    assert output[5] == "-------------------"
    assert output[6] == "Total count: 10"
