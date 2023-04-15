import logging
import sqlite3
from datetime import datetime
from typing import List, Tuple

from arxivterminal.models import ArxivPaper, ArxivStats


class ArxivDatabase:
    def __init__(self, database_path: str):
        """
        Initialize the ArxivDatabase with a database path.

        Parameters
        ----------
        database_path : str
            Path to the database file.
        """
        self.database_path = database_path
        self.create_database()

    def create_database(self):
        logging.info(f"Create database at {self.database_path}")
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()

            # Create the papers table if it doesn't already exist
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS papers (
                    entry_id TEXT PRIMARY KEY,
                    updated TIMESTAMP,
                    published TIMESTAMP,
                    title TEXT,
                    summary TEXT,
                    authors TEXT,
                    categories TEXT
                )
            """
            )
            conn.commit()

    @staticmethod
    def convert_to_paper(row: Tuple) -> ArxivPaper:
        """
        Convert a database row to an ArxivPaper object.

        Parameters
        ----------
        row : Tuple
            A tuple representing a row from the papers table in the database.

        Returns
        -------
        ArxivPaper
            An ArxivPaper object created from the given row.
        """
        return ArxivPaper(
            entry_id=row[0],
            updated=datetime.fromisoformat(row[1]),
            published=datetime.fromisoformat(row[2]),
            title=row[3],
            summary=row[4],
            authors=row[5].split(","),
            categories=row[6].split(","),
        )

    def save_papers(self, papers: List[ArxivPaper]):
        """
        Save a list of ArxivPaper objects to the database.

        Parameters
        ----------
        papers : List[ArxivPaper]
            A list of ArxivPaper objects to be saved in the database.
        """
        # Connect to the database
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()

            # Fetch all existing paper IDs in a single query
            cursor.execute("SELECT entry_id FROM papers")
            existing_ids = set(row[0] for row in cursor.fetchall())

            # Loop over the papers and insert or update them in the database
            num_inserted = 0
            num_updated = 0
            for paper in papers:
                if paper.entry_id in existing_ids:
                    # If the paper already exists, update its information
                    cursor.execute(
                        """
                        UPDATE papers SET
                            updated=?,
                            published=?,
                            title=?,
                            summary=?,
                            authors=?,
                            categories=?
                        WHERE entry_id=?
                    """,
                        (
                            paper.updated.isoformat(),
                            paper.published.isoformat(),
                            paper.title,
                            paper.summary,
                            ",".join(paper.authors),
                            ",".join(paper.categories),
                            paper.entry_id,
                        ),
                    )
                    num_updated += 1
                else:
                    # If the paper doesn't exist, insert it into the database
                    cursor.execute(
                        """
                        INSERT INTO papers (
                            entry_id,
                            updated,
                            published,
                            title,
                            summary,
                            authors,
                            categories
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            paper.entry_id,
                            paper.updated.isoformat(),
                            paper.published.isoformat(),
                            paper.title,
                            paper.summary,
                            ",".join(paper.authors),
                            ",".join(paper.categories),
                        ),
                    )
                    num_inserted += 1

            # Commit the changes to the database and close the connection
            conn.commit()

        # Log the number of papers inserted and updated
        logging.info(f"Inserted {num_inserted} papers")
        logging.info(f"Updated {num_updated} papers")

    def get_papers(self, published_after: datetime) -> List[ArxivPaper]:
        """
        Retrieve papers from the database that were published after a specified date.

        Parameters
        ----------
        published_after : datetime
            A datetime object representing the lower bound of the publication date for retrieved papers.

        Returns
        -------
        List[ArxivPaper]
            A list of ArxivPaper objects that match the specified criteria.
        """
        # Connect to the database
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()

            # Query the database for papers published after the specified date
            cursor.execute(
                """
                SELECT entry_id, updated, published, title, summary, authors, categories
                FROM papers
                WHERE published >= ?
                ORDER BY published ASC
            """,
                (published_after.isoformat(),),
            )

            # Parse the results into ArxivPaper objects
            papers = []
            for row in cursor.fetchall():
                paper = self.convert_to_paper(row)
                papers.append(paper)

        return papers

    def delete_papers(self):
        """
        Delete all papers from the database.
        """
        # Connect to the database
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()

            # Execute a DELETE query to remove all records from the papers table
            cursor.execute("DELETE FROM papers")

            # Commit the changes to the database and close the connection
            conn.commit()

        # Log the deletion of records
        logging.info("Deleted all papers from the database")

    def search_papers(self, query: str) -> List[ArxivPaper]:
        """
        Search for papers in the database with a given query in their title or summary.

        Parameters
        ----------
        query : str
            The search query.

        Returns
        -------
        List[ArxivPaper]
            A list of ArxivPaper objects that match the search query.
        """
        # Connect to the database
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()

            # Query the database for papers with the search phrase in the title or summary
            cursor.execute(
                """
                SELECT entry_id, updated, published, title, summary, authors, categories
                FROM papers
                WHERE title LIKE ? OR summary LIKE ?
                ORDER BY published ASC
            """,
                (f"%{query}%", f"%{query}%"),
            )

            # Parse the results into ArxivPaper objects
            papers = []
            for row in cursor.fetchall():
                paper = self.convert_to_paper(row)
                papers.append(paper)

        return papers

    def get_stats(self) -> List[ArxivStats]:
        """
        Retrieve the count of papers by publication date from the database.

        Returns
        -------
        List[ArxivStats]
            A list of ArxivStats objects representing the count of papers by publication date.
        """
        # Connect to the database
        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()

            # Query the database for the count of papers by publish date
            cursor.execute(
                """
                SELECT DATE(published) as date, COUNT(*) as count
                FROM papers
                GROUP BY DATE(published)
                ORDER BY DATE(published) ASC
            """
            )

            # Parse the results into ArxivStats objects
            stats = []
            for row in cursor.fetchall():
                stat = ArxivStats(date=row[0], count=row[1])
                stats.append(stat)

        return stats
