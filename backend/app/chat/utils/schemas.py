from pydantic import BaseModel, Field
from typing import List


class EventsAnalyzed(BaseModel):
    balance: bool = Field(
        description="Balance between wellness and work events",
    )
    analysis: str = Field(
        description="Analysis of the events in the calendar if they are lots of work events or not",
    )
    proposed_steps: str = Field(
        description="Proposed steps to take to balance the work and non work events",
    )


class EventSearchResults(BaseModel):
    title: str
    date: str
    address: str
    description: str
    image: str
    link: str


class SearchResults(BaseModel):
    results: List
