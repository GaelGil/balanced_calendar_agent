// in your React component
import { useEffect, useMemo, useState } from "react";
import { fetchCalendarEvents } from "../../api/calendar";
import type { GoogleEvent, NormalizedEvent } from "../../types/Event";

const year = new Date().getFullYear(); // get current year
const month = new Date().getMonth(); // get current month
const firstDayOfMonth = new Date(year, month, 1).getDay(); // get first day of month
const daysInMonth = new Date(year, month + 1, 0).getDate(); // get number of days in month
const days: (number | null)[] = []; // generate calendar cells (null = leading blank)
for (let i = 0; i < firstDayOfMonth; i++) days.push(null); // for days not part of current month
for (let d = 1; d <= daysInMonth; d++) days.push(d); // for days in current month

// helper: format "YYYY-MM-DD"
const toDateKey = (d: Date) =>
  `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(
    d.getDate()
  ).padStart(2, "0")}`; // parse to YYYY-MM-DD

// get dateKey from Google event start
function dateKeyFromGoogleEvent(ev: GoogleEvent): string {
  const s = ev.start; // event start
  // if datetime
  if (s.dateTime) {
    // parse to YYYY-MM-DD
    const dt = new Date(s.dateTime);
    // return date as YYYY-MM-DD
    return toDateKey(dt);
  }
  if (s.date) {
    // date is already YYYY-MM-DD in Google API
    return s.date;
  }
  // fallback to today
  return toDateKey(new Date());
}

function localTimeFromGoogleEvent(ev: GoogleEvent): string | undefined {
  if (ev.start.dateTime) {
    const dt = new Date(ev.start.dateTime);
    // format time in local locale, short time
    return dt.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
  }
  return undefined; // all-day events
}
export default function CalendarEvents() {
  const [rawEvents, setRawEvents] = useState<GoogleEvent[]>([]); // raw events
  const [loading, setLoading] = useState(true); // loading state
  const [error, setError] = useState<string | null>(null); // error state

  // load events
  useEffect(() => {
    async function loadEvents() {
      setLoading(true);
      setError(null);
      try {
        const events = await fetchCalendarEvents(); // must return GoogleEvent[]
        setRawEvents(events ?? []); // set events
      } catch (err: any) {
        console.error("Failed to load events", err);
        setError(err?.message ?? "Failed to load events");
      } finally {
        setLoading(false);
      }
    }
    loadEvents();
  }, []);

  // Normalize and group by dateKey. Memoized so re-computation is minimized.
  const eventsByDate = useMemo(() => {
    const map = new Map<string, NormalizedEvent[]>();
    for (const ev of rawEvents) {
      const key = dateKeyFromGoogleEvent(ev);
      const normalized: NormalizedEvent = {
        id: ev.id,
        summary: ev.summary ?? "(no title)",
        dateKey: key,
        time: localTimeFromGoogleEvent(ev),
      };
      const arr = map.get(key) ?? [];
      arr.push(normalized);
      map.set(key, arr);
    }
    // Optionally sort events within each day by time (all-day first or last)
    for (const [k, arr] of map) {
      arr.sort((a, b) => {
        if (!a.time && !b.time) return 0;
        if (!a.time) return -1; // place all-day events before timed events (adjust as desired)
        if (!b.time) return 1;
        // compare hh:mm by Date parse
        const ta = Date.parse(`${k}T${to24Hour(a.time)}`);
        const tb = Date.parse(`${k}T${to24Hour(b.time)}`);
        return ta - tb;
      });
      map.set(k, arr);
    }
    return map;
  }, [rawEvents]);

  // small helper to convert e.g. "9:30 AM" -> "09:30:00" for Date.parse on YYYY-MM-DDT... use a quick approach:
  function to24Hour(timeStr: string) {
    // rely on Date parsing by constructing a Date and then returning hh:mm:ss
    const parsed = new Date(`1970-01-01 ${timeStr}`);
    const hh = String(parsed.getHours()).padStart(2, "0");
    const mm = String(parsed.getMinutes()).padStart(2, "0");
    return `${hh}:${mm}:00`;
  }

  const formatDate = (day: number) =>
    `${year}-${String(month + 1).padStart(2, "0")}-${String(day).padStart(
      2,
      "0"
    )}`;

  if (loading) {
    return (
      <p className="text-center text-primary-600 font-semibold">Loading …</p>
    );
  }

  if (error) {
    return (
      <p className="text-center text-red-600 font-semibold">
        Error loading events: {error}
      </p>
    );
  }

  return (
    <div>
      <div className="grid grid-cols-7 gap-1 text-secondary-300 text-center font-semibold">
        {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((d) => (
          <div key={d} className="py-2">
            {d}
          </div>
        ))}
      </div>

      <div className="grid grid-cols-7 gap-1 mt-1">
        {/* loop over days in current month */}
        {days.map((day, idx) => {
          // skip empty days/days not part of current month
          if (!day)
            return (
              <div key={idx} className="py-8 border border-secondary-300"></div>
            );

          const dateKey = formatDate(day); // get date key which is YYYY-MM-DD
          const dayEvents = eventsByDate.get(dateKey) ?? []; // get events for this day

          return (
            // if today, highlight
            <div
              key={idx}
              className={`border border-gray-200 p-2 h-32 flex flex-col ${
                dateKey === toDateKey(new Date()) ? "bg-yellow-50" : ""
              }`}
            >
              <div className="font-semibold mb-1 text-secondary-300">{day}</div>

              <div className="flex-1 overflow-y-auto">
                {dayEvents.length === 0 ? (
                  // if no events
                  <div className="text-xs text-secondary-300">No events</div>
                ) : (
                  // if events
                  // for each event
                  dayEvents.map((ev) => (
                    // display
                    <div
                      key={ev.id}
                      className="bg-blue-500 text-white text-xs px-1 py-0.5 rounded mb-0.5 truncate"
                      title={`${ev.time ? ev.time + " • " : ""}${ev.summary}`}
                    >
                      {ev.time ? `${ev.time} ` : ""}
                      {ev.summary}
                    </div>
                  ))
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
