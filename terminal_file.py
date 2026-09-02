from datetime import datetime
from spiderman_incident_display import LOCATION_SCORES

INCIDENT_TYPES = [
    "Robbery",
    "Accident",
    "Fire",
    "Medical Emergency",
    "Missing Person",
    "Suspicious Activity"
]

LOCATIONS = sorted(list(LOCATION_SCORES.keys()))
SEVERITIES = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


def create_incident_entry(existing_incidents: list) -> dict | None:
    """Prompt user via terminal to create a standardized incident record."""
    print("\n--- REPORT NEW INCIDENT ---")

    print("Types:", ", ".join(INCIDENT_TYPES))
    inc_type = input("Enter incident type: ").strip().title()
    if inc_type not in INCIDENT_TYPES:
        print("Invalid incident type.")
        return None

    print("\nLocations:", ", ".join(LOCATIONS))
    location = input("Enter location: ").strip().title()
    if location not in LOCATIONS:
        print("Invalid location. Must be a valid city map location.")
        return None

    print("\nSeverities:", ", ".join(SEVERITIES))
    severity = input("Enter severity: ").strip().upper()
    if severity not in SEVERITIES:
        print("Invalid severity level.")
        return None

    people_raw = input("Enter people affected: ").strip()
    if not people_raw.isdigit():
        print("People affected must be a positive integer.")
        return None
    people = int(people_raw)

    description = input("Enter description: ").strip() or "No description provided."

    incident_id = f"INC-{len(existing_incidents) + 1:03d}"

    return {
        "id": incident_id,
        "type": inc_type,
        "location": location,
        "severity": severity,
        "people_affected": people,
        "description": description,
        "reported_at": datetime.now().timestamp(),
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "REPORTED"
    }
