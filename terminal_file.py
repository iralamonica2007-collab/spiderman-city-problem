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

    print("Incident Types:", ", ".join(INCIDENT_TYPES))
    type_input = input("Enter incident type: ").strip()
    matched_type = next((t for t in INCIDENT_TYPES if t.lower() == type_input.lower()), None)
    if not matched_type:
        print("Invalid incident type.")
        return None

    print("\nLocations:", ", ".join(LOCATIONS))
    location_input = input("Enter location: ").strip()
    matched_location = next((loc for loc in LOCATIONS if loc.lower() == location_input.lower()), None)
    if not matched_location:
        print("Invalid location. Must be a valid city map location.")
        return None

    print("\nSeverities:", ", ".join(SEVERITIES))
    severity_input = input("Enter severity: ").strip().upper()
    if severity_input not in SEVERITIES:
        print("Invalid severity level.")
        return None

    people_raw = input("Enter people affected: ").strip()
    if not people_raw.isdigit():
        print("People affected must be a non-negative integer.")
        return None
    people = int(people_raw)

    description = input("Enter description: ").strip() or "No description provided."

    # Duplicate check against active incidents
    for inc in existing_incidents:
        if (inc["type"].lower() == matched_type.lower() and
            inc["location"].lower() == matched_location.lower() and
            inc["status"] != "RESOLVED"):
            print(f"\nPOSSIBLE DUPLICATE DETECTED! Existing Incident: {inc['id']}")
            answer = input("Continue anyway? (yes/no): ").strip().lower()
            if answer != "yes":
                print("Incident creation cancelled.")
                return None

    incident_id = f"INC-{len(existing_incidents) + 1:03d}"

    return {
        "id": incident_id,
        "type": matched_type,
        "location": matched_location,
        "severity": severity_input,
        "people_affected": people,
        "description": description,
        "reported_at": datetime.now().timestamp(),
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "REPORTED"
    }
