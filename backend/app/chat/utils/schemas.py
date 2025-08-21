from pydantic import BaseModel, Field


class EventsAnalyzed(BaseModel):
    balance: bool = Field(
        description="Balance between wellness and work events",
    )
    analysis: str = Field(
        description="Analysis of the events in the calendar if they are lots of work events or not",
    )
