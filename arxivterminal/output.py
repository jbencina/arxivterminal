from typing import List

from termcolor import colored

from arxivterminal.db import ArxivStats
from arxivterminal.fetch import ArxivPaper


def print_papers(papers: List[ArxivPaper]):
    """
    Print a list of Arxiv papers and their publication date in a formatted manner.

    Parameters
    ----------
    papers : List[ArxivPaper]
        A list of ArxivPaper objects to be printed.
    """
    current_date = None
    total_papers = len(papers)

    while True:
        for i, paper in enumerate(papers):
            paper_date = paper.published.date()
            if paper_date != current_date:
                print(colored(f"\n{paper_date}", "cyan"))
                print(colored("".join(["-"] * 10), "cyan"))
                current_date = paper_date
            inverted_line_number = total_papers - i
            print(f"{colored(inverted_line_number, 'yellow')}. {paper.title}")

        # Get the line number from the user
        user_input = input(
            "\nEnter the line number to show the full abstract, 'b' to go back, or 'q' to quit: "
        )

        while user_input.lower() != "b":
            try:
                line_number = int(user_input)
                if 1 <= line_number <= total_papers:
                    selected_paper = papers[total_papers - line_number]
                    print(f"\n{colored(selected_paper.title, 'yellow')}")
                    print(f"{colored(selected_paper.entry_id, 'blue')}")
                    print(
                        f"\n{colored('Abstract:', 'cyan')} {selected_paper.summary}\n"
                    )
                else:
                    print("Invalid line number. Please try again.")
            except ValueError:
                if user_input.lower() == "q":
                    return
                print("Invalid input. Please try again.")

            user_input = input(
                "Enter the line number to show the full abstract, 'b' to go back, or 'q' to quit: "
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
