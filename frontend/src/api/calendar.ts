// api/calendar.ts
import { BASE_URL } from "./url";

export async function fetchCalendarEvents() {
  const res = await fetch(`${BASE_URL}/calendar/events`, {
    credentials: "include",
  });
  if (!res.ok) {
    throw new Error("Failed to fetch calendar events");
  }
  return await res.json(); // array of events
}
