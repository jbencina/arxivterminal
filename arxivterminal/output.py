from typing import List

from termcolor import colored

from arxivterminal.constants import DATABASE_PATH, MODEL_PATH
from arxivterminal.db import ArxivDatabase, ArxivStats
from arxivterminal.download import download_paper
from arxivterminal.fetch import ArxivPaper
from arxivterminal.ml import LsaDocumentSearch


class ExitAppException(Exception):
    pass


def print_papers(papers: List[ArxivPaper], show_dates: bool = True):
    """
    Print a list of Arxiv papers and their publication date in a formatted manner.

    Parameters
    ----------
    papers : List[ArxivPaper]
        A list of ArxivPaper objects to be printed.
    show_dates: bool
        If true, then the publish date of the paper is shown. Otherwise, date headers are
        omitted.
    """
    current_date = None
    total_papers = len(papers)

    def _format_categories(categories: List[str]) -> str:
        joined = ",".join(categories)
        return f"[{joined}]"

    def _format_authors(authors: List[str], max_len: int):
        author_list = ", ".join(authors[:max_len])

        if len(authors) > max_len:
            author_list += ", et al."

        return author_list

    while True:
        for i, paper in enumerate(papers):
            paper_date = paper.published.date()
            if (paper_date != current_date) and show_dates:
                print(colored(f"\n{paper_date}", "cyan"))
                print(colored("".join(["-"] * 10), "cyan"))
                current_date = paper_date
            inverted_line_number = total_papers - i

            if paper.viewed:
                print(
                    f"{colored(inverted_line_number, 'green')}. {colored(paper.title, 'green')}"
                )
            else:
                print(f"{colored(inverted_line_number, 'yellow')}. {paper.title}")

        # Get the line number from the user
        user_input = input(
            "\nEnter the line number to show the full abstract, 'b' to go back, or 'q' to quit: "
        )

        while user_input.lower() != "b":
            try:
                line_number = int(user_input)
                if 1 <= line_number <= total_papers:
                    selected_index = total_papers - line_number
                    selected_paper = papers[selected_index]
                    print(f"\n{colored(selected_paper.title, 'yellow')}")
                    print(f"{_format_authors(selected_paper.authors, 3)}")
                    print(f"\n{colored(selected_paper.entry_id, 'blue')}")
                    print(f"\n{colored('Abstract:', 'cyan')} {selected_paper.summary}")
                    print(
                        f"\nCategories: {_format_categories(selected_paper.categories)}\n"
                    )
                    db = ArxivDatabase(str(DATABASE_PATH))
                    db.mark_paper_viewed(selected_paper)
                    papers[selected_index].viewed = True
                else:
                    print("Invalid line number. Please try again.")
            except ValueError:
                if user_input.lower() == "q":
                    raise ExitAppException
                elif user_input.lower() == "d":
                    try:
                        download_paper(selected_paper)
                    except FileExistsError:
                        pass
                    user_input = input(
                        "Enter 'b' to go back, 'd' to download, 's' to search similar, or 'q' to quit: "
                    )
                    continue
                elif user_input.lower() == "s":
                    db = ArxivDatabase(str(DATABASE_PATH))
                    lsa = LsaDocumentSearch(str(MODEL_PATH))
                    search_results = lsa.search(db, selected_paper.summary)
                    print_papers(search_results, show_dates=False)

                print("Invalid input. Please try again.")

            user_input = input(
                "Enter the line number to show the full abstract, 'b' to go back, 'd' to download, 's' to search similar, or 'q' to quit: "  # noqa: E501
            )


def print_stats(stats: List[ArxivStats]):
    """
    Print the count of Arxiv papers by their publication date in a formatted manner.

    Parameters
    ----------
    stats : List[ArxivStats]
        A list of ArxivStats objects containing the count of papers by publication date.
    """
    total_count = 0

    print("Date       | Count")
    print("-------------------")

    for stat in stats:
        print(f"{colored(stat.date, 'yellow')} | {stat.count}")
        total_count += stat.count

    print("-------------------")
    print(f"Total count: {total_count}")
