from pydantic import BaseModel, Field
from typing import List, Optional


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
    title: Optional[str] = None
    date: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None
    link: Optional[str] = None


class SearchResults(BaseModel):
    results: List
