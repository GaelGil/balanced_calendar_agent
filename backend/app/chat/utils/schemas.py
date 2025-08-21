from pydantic import BaseModel, Field
from typing import List


class EventsAnalyzed(BaseModel):
    balance: bool = Field(
        description="Balance between wellness and work events",
    )
    analysis: str = Field(
        description="Analysis of the events in the calendar if they are lots of work events or not",
    )


class EventSearchResults(BaseModel):
    title: str
    date: str
    address: str
    description: str
    image: str
    link: str


class FinanceSearchResults(BaseModel):
    extracted_price: str
    link: str
    name: str
    price: str
    movement: str
    percentage: str
    stock: str


class SearchResults(BaseModel):
    results: List
