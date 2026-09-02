# SPIDER-MAN COMMAND CENTRE
# Team Spade

incidents = []
next_id = 1

# -----------------------------
# Fixed Option Lists
# -----------------------------

INCIDENT_TYPES = [
    "Robbery",
    "Fire",
    "Hostage Situation",
    "Break-in",
    "Vehicle Accident",
    "Assault",
    "Bomb Threat",
    "Kidnapping"
]

LOCATIONS = [
    "Queens Street",
    "City Hospital",
    "5th Avenue Bank",
    "Downtown Bank",
    "Museum",
    "Central Park",
    "Times Square",
    "Grand Central Station"
]

SEVERITY_LEVELS = [
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL"
]

SEVERITY_SCORES = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 5
}

PEOPLE_AFFECTED_OPTIONS = [
    "0",
    "1-5",
    "6-15",
    "16-30",
    "31-50",
    "50+"
]

PEOPLE_AFFECTED_VALUES = [0, 3, 10, 20, 40, 60]


# -----------------------------
# Helper Functions
# -----------------------------

def get_incident_by_id(incident_id):
    for incident in incidents:
        if incident["id"] == incident_id:
            return incident
    return None


def calculate_priority(severity_label, people):
    severity_score = SEVERITY_SCORES[severity_label]
    return (severity_score * 10) + people


def print_numbered_menu(title, options):
    print(f"\n{title}")
    for i, option in enumerate(options, start=1):
        print(f"{i}. {option}")


def get_menu_choice(title, options):
    """
    Shows a numbered menu and returns the SELECTED OPTION (not the number).
    Returns None if the user enters anything invalid.
    """
    print_numbered_menu(title, options)
    raw = input("Choose an option: ").strip()

    if not raw.isdigit():
        print("Please enter a valid number.")
        return None

    index = int(raw) - 1

    if index < 0 or index >= len(options):
        print("Invalid option. Please select from the menu.")
        return None

    return options[index]


def get_incident_type():
    return get_menu_choice("Select incident type:", INCIDENT_TYPES)


def get_location():
    return get_menu_choice("Select location:", LOCATIONS)


def get_severity():
    return get_menu_choice("Select severity:", SEVERITY_LEVELS)


def get_people_affected():
    """
    Shows a numbered menu of people-affected RANGES.
    Returns the numeric value used for scoring, or None if invalid.
    """
    selected_range = get_menu_choice("Select people affected:", PEOPLE_AFFECTED_OPTIONS)

    if selected_range is None:
        return None

    index = PEOPLE_AFFECTED_OPTIONS.index(selected_range)
    return PEOPLE_AFFECTED_VALUES[index]


# -----------------------------
# 1. Report Incident
# -----------------------------

def report_incident():
    global next_id

    print("\n--- REPORT INCIDENT ---")

    incident_type = get_incident_type()
    if incident_type is None:
        print("Incident report cancelled.")
        return

    location = get_location()
    if location is None:
        print("Incident report cancelled.")
        return

    severity = get_severity()
    if severity is None:
        print("Incident report cancelled.")
        return

    people = get_people_affected()
    if people is None:
        print("Incident report cancelled.")
        return

    description = input("Brief description: ").strip()
    if description == "":
        description = "No description provided."

    incident = {
        "id": f"INC-{next_id:03d}",
        "type": incident_type,
        "location": location,
        "severity": severity,
        "people": people,
        "description": description,
        "status": "REPORTED"
    }

    incidents.append(incident)

    print("\nIncident reported successfully.")
    print("Incident ID:", incident["id"])

    next_id += 1


# -----------------------------
# 2. View Active Incidents
# -----------------------------

def view_active_incidents():
    print("\n--- ACTIVE INCIDENTS ---")

    active = []

    for incident in incidents:
        if incident["status"] != "RESOLVED":
            active.append(incident)

    if len(active) == 0:
        print("No active incidents.")
        return

    for incident in active:
        print("\nID:", incident["id"])
        print("Type:", incident["type"])
        print("Location:", incident["location"])
        print("Severity:", incident["severity"])
        print("People affected:", incident["people"])
        print("Status:", incident["status"])


# -----------------------------
# 3. View Response Priority
# -----------------------------

def view_response_priority():
    print("\n--- RESPONSE PRIORITY ---")

    active = []

    for incident in incidents:
        if incident["status"] != "RESOLVED":
            active.append(incident)

    if len(active) == 0:
        print("No active incidents.")
        return

    # Highest priority first
    active.sort(
        key=lambda x: calculate_priority(x["severity"], x["people"]),
        reverse=True
    )

    for incident in active:
        priority = calculate_priority(incident["severity"], incident["people"])

        print("\nID:", incident["id"])
        print("Severity:", incident["severity"])
        print("Location:", incident["location"])
        print("Priority Score:", priority)


# -----------------------------
# 4. Get Next Mission
# -----------------------------

def get_next_mission():
    print("\n--- NEXT MISSION ---")

    active = []

    for incident in incidents:
        if incident["status"] != "RESOLVED":
            active.append(incident)

    if len(active) == 0:
        print("No available mission.")
        return

    # Find highest priority incident
    mission = max(
        active,
        key=lambda x: calculate_priority(x["severity"], x["people"])
    )

    priority = calculate_priority(mission["severity"], mission["people"])

    distance = 5
    mission_score = priority - distance

    print("\nNEXT MISSION")
    print("Incident :", mission["id"])
    print("Location :", mission["location"])
    print("Priority :", priority)
    print("Distance :", distance, "km")
    print("Score    :", mission_score)

    print("\nRoute:")
    print("Queens Street")
    print("↓")
    print(mission["location"])


# -----------------------------
# 5. Update Incident
# -----------------------------

def update_incident():
    print("\n--- UPDATE INCIDENT ---")

    if len(incidents) == 0:
        print("No incidents to update.")
        return

    incident_options = [f"{inc['id']} ({inc['status']})" for inc in incidents]
    selected = get_menu_choice("Select incident to update:", incident_options)

    if selected is None:
        print("Update cancelled.")
        return

    index = incident_options.index(selected)
    incident = incidents[index]

    print("\nCurrent status:", incident["status"])

    if incident["status"] == "REPORTED":
        update_options = ["Move to IN_PROGRESS", "Cancel"]
        choice = get_menu_choice("Select update:", update_options)

        if choice == "Move to IN_PROGRESS":
            incident["status"] = "IN_PROGRESS"
            print("Incident updated successfully.")
        else:
            print("Update cancelled.")

    elif incident["status"] == "IN_PROGRESS":
        update_options = ["Move to RESOLVED", "Cancel"]
        choice = get_menu_choice("Select update:", update_options)

        if choice == "Move to RESOLVED":
            incident["status"] = "RESOLVED"
            print("Incident resolved successfully.")
        else:
            print("Update cancelled.")

    else:
        print("Resolved incidents cannot be updated.")


# -----------------------------
# 6. Dashboard
# -----------------------------

def view_dashboard():
    print("\n--- DASHBOARD ---")

    active = 0
    critical = 0
    in_progress = 0
    resolved = 0

    for incident in incidents:

        if incident["status"] == "RESOLVED":
            resolved += 1
        else:
            active += 1

        if incident["severity"] == "CRITICAL" and incident["status"] != "RESOLVED":
            critical += 1

        if incident["status"] == "IN_PROGRESS":
            in_progress += 1

    print("Active incidents :", active)
    print("Critical incidents:", critical)
    print("In progress       :", in_progress)
    print("Resolved          :", resolved)


# -----------------------------
# Main Menu
# -----------------------------

def show_menu():
    print("\n================================")
    print("     SPIDER-MAN COMMAND CENTRE")
    print("================================")
    print("1. Report Incident")
    print("2. View Active Incidents")
    print("3. View Response Priority")
    print("4. Get Next Mission")
    print("5. Update Incident")
    print("6. View Dashboard")
    print("7. Exit")
    print("================================")


def main():
    while True:

        show_menu()

        choice = input("Choose an option: ").strip()

        if choice == "1":
            report_incident()

        elif choice == "2":
            view_active_incidents()

        elif choice == "3":
            view_response_priority()

        elif choice == "4":
            get_next_mission()

        elif choice == "5":
            update_incident()

        elif choice == "6":
            view_dashboard()

        elif choice == "7":
            print("\nExiting Command Centre...")
            print("Stay safe, Spider-Man!")
            break

        else:
            print("\n❌ INVALID OPTION")
            print("Please select an option from the menu.")


# -----------------------------
# Start Program
# -----------------------------

if __name__ == "__main__":
    main()
