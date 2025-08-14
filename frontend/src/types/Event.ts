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
