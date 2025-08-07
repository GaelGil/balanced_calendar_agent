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

export const createCalenderEvent = async (
  name: string,
  date: string,
  time: string
) => {
  const res = await fetch(`${BASE_URL}/calendar/new_event`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json", // ✅ Important for Flask to parse JSON
    },
    body: JSON.stringify({ name, date, time }),
  });
  if (!res.ok) {
    return new Error("Error");
  }
  const data = await res.json();
  return data;
};
