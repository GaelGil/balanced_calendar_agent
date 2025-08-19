export interface Event {
  id: string;
  summary: string;
  start: { dateTime?: string; date?: string };
  end: { dateTime?: string; date?: string };
}

export interface CalendarEventProps {
  event: Event;
}

export interface EventProps {
  events: Event[];
}

export type GoogleEvent = {
  id: string;
  summary?: string;
  start: { date?: string; dateTime?: string };
  end?: { date?: string; dateTime?: string };
  // other fields you might have...
};

export type NormalizedEvent = {
  id: string;
  summary: string;
  dateKey: string; // "YYYY-MM-DD"
  time?: string; // e.g. "10:30 AM" (for timed events), undefined for all-day
};
