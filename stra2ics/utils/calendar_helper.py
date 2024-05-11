from icalendar import Calendar, Event
from stravalib.model import Activity


def activities_to_calendar(
    activities: dict[str, list[Activity]],
    prodid: str = "-//Strava Activities//",
    version: str = "2.0",
) -> Calendar:
    calendar = Calendar()
    calendar.add("prodid", prodid)
    calendar.add("version", version)
    for activity in activities["activities"]:
        if (
            activity.start_date is not None
            and activity.elapsed_time is not None
            and activity.distance is not None
        ):
            event = Event()
            event.add(
                name="dtstart",
                value=activity.start_date,
            )
            event.add(
                name="dtend",
                value=activity.start_date + activity.elapsed_time,
            )
            event.add(
                name="summary",
                value=f"""{activity.name} ({int(activity.distance)/1_000:.1f} km)""",
            )
            event.add(
                name="description",
                value=f"""https://www.strava.com/activities/{activity.id}""",
            )
            calendar.add_component(event)
    return calendar
