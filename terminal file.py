from datetime import datetime

incidents = []

incident_types = [
    "Robbery",
    "Accident",
    "Fire",
    "Medical Emergency",
    "Missing Person",
    "Suspicious Activity"
]

locations = [
    "Queens Street",
    "Midtown School",
    "City Hospital",
    "Park Avenue",
    "Queens Residence",
    "Central Mall",
    "Police Station",
    "Metro Station"
]

severities = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


# Create a new incident
def create_incident():
    print("\n--- REPORT NEW INCIDENT ---")

    # Incident type
    print("\nIncident Types:")
    for item in incident_types:
        print("-", item)

    incident_type = input("Enter incident type: ").strip()

    # Check incident type
    valid_type = None

    for item in incident_types:
        if incident_type.lower() == item.lower():
            valid_type = item

    if valid_type is None:
        print("Invalid incident type.")
        return

    # Location
    print("\nLocations:")
    for item in locations:
        print("-", item)

    location = input("Enter location: ").strip()

    valid_location = None

    for item in locations:
        if location.lower() == item.lower():
            valid_location = item

    if valid_location is None:
        print("Invalid location.")
        return

    # Severity
    print("\nSeverity:")
    print("LOW")
    print("MEDIUM")
    print("HIGH")
    print("CRITICAL")

    severity = input("Enter severity: ").strip().upper()

    if severity not in severities:
        print("Invalid severity.")
        return

    # People affected
    people = input("Enter people affected: ").strip()

    if not people.isdigit():
        print("People affected must be a non-negative integer.")
        return

    people = int(people)

    # Description
    description = input("Enter description: ").strip()

    if description == "":
        print("Description cannot be empty.")
        return

    # Check duplicate
    for incident in incidents:
        if (
            incident["type"].lower() == valid_type.lower()
            and incident["location"].lower() == valid_location.lower()
        ):
            print("\nPOSSIBLE DUPLICATE!")
            print("Existing Incident:", incident["id"])

            answer = input("Continue anyway? (yes/no): ").strip().lower()

            if answer != "yes":
                print("Incident not created.")
                return

    # Create ID
    number = len(incidents) + 1
    incident_id = "INC-" + str(number).zfill(3)

    # Create incident
    incident = {
        "id": incident_id,
        "type": valid_type,
        "location": valid_location,
        "severity": severity,
        "people": people,
        "description": description,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "REPORTED"
    }

    incidents.append(incident)

    print("\nINCIDENT CREATED")
    print("Incident ID:", incident_id)
    print("Status:", "REPORTED")


# Find incident
def find_incident():
    print("\n--- FIND INCIDENT ---")

    incident_id = input("Enter incident ID: ").strip().upper()

    for incident in incidents:
        if incident["id"] == incident_id:
            print("\nIncident Found")
            print("ID:", incident["id"])
            print("Type:", incident["type"])
            print("Location:", incident["location"])
            print("Severity:", incident["severity"])
            print("People Affected:", incident["people"])
            print("Description:", incident["description"])
            print("Reported Time:", incident["time"])
            print("Status:", incident["status"])
            return

    print("Incident not found.")


# Show all incidents
def show_all_incidents():
    print("\n--- ALL INCIDENTS ---")

    if len(incidents) == 0:
        print("No incidents found.")
        return

    for incident in incidents:
        print("\n----------------------")
        print("ID:", incident["id"])
        print("Type:", incident["type"])
        print("Location:", incident["location"])
        print("Severity:", incident["severity"])
        print("People:", incident["people"])
        print("Description:", incident["description"])
        print("Time:", incident["time"])
        print("Status:", incident["status"])


# Main program
while True:

    print("\n==============================")
    print("   INCIDENT MANAGEMENT SYSTEM")
    print("==============================")

    print("1. Report New Incident")
    print("2. Find Incident")
    print("3. Show All Incidents")
    print("4. Exit")

    choice = input("Enter your choice: ").strip()

    if choice == "1":
        create_incident()

    elif choice == "2":
        find_incident()

    elif choice == "3":
        show_all_incidents()

    elif choice == "4":
        print("Program ended.")
        break

    else:
        print("Invalid choice.")
