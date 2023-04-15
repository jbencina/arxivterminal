from datetime import datetime
from typing import List

from pydantic import BaseModel


class ArxivStats(BaseModel):
    date: str
    count: int


class ArxivPaper(BaseModel):
    entry_id: str
    updated: datetime
    published: datetime
    title: str
    summary: str
    authors: List[str]
    categories: List[str]
