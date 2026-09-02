# SPIDER-MAN COMMAND CENTRE (Unified Execution System)

from spiderman_incident_display import (
    calculate_priority_score,
    rank_incidents,
    print_response_priority
)
from priority_search_using_dijkstra import (
    MissionPlanner,
    Incident as DijkstraIncident,
    UnknownLocationError
)
from terminal_file import create_incident_entry

incidents = []
planner = MissionPlanner()
SPIDERMAN_LOCATION = "Queens Street"


def report_incident():
    new_inc = create_incident_entry(incidents)
    if new_inc:
        incidents.append(new_inc)
        print(f"\nSuccessfully reported Incident {new_inc['id']}!")


def view_active_incidents():
    print("\n--- ACTIVE INCIDENTS ---")
    active = [i for i in incidents if i["status"] != "RESOLVED"]
    if not active:
        print("No active incidents.")
        return

    for inc in active:
        print(f"\nID: {inc['id']} | Type: {inc['type']} | Status: {inc['status']}")
        print(f"Location: {inc['location']} | Severity: {inc['severity']} | People: {inc['people_affected']}")


def view_response_priority():
    ranked = rank_incidents(incidents)
    print_response_priority(ranked)


def get_next_mission():
    print("\n--- NEXT MISSION (OPTIMIZED ROUTE) ---")
    active_dict_incidents = rank_incidents(incidents)
    if not active_dict_incidents:
        print("No active incidents to generate missions.")
        return

    # Convert dictionary incidents into Dijkstra Incident dataclass objects
    dijkstra_incidents = []
    for inc in active_dict_incidents:
        score = calculate_priority_score(inc)
        dijkstra_incidents.append(
            DijkstraIncident(
                id=inc["id"],
                name=f"{inc['type']} at {inc['location']}",
                location=inc["location"],
                priority=score
            )
        )

    try:
        best_mission = planner.recommend_mission(SPIDERMAN_LOCATION, dijkstra_incidents)
        route_str = " -> ".join(best_mission.route.path)

        print(f"\nRECOMMENDED MISSION FOR SPIDER-MAN")
        print(f"Current Location : {SPIDERMAN_LOCATION}")
        print(f"Incident Target  : {best_mission.incident.name} (ID: {best_mission.incident.id})")
        print(f"Priority Score   : {best_mission.incident.priority}")
        print(f"Route Distance   : {best_mission.route.distance_km:.1f} km")
        print(f"Mission Score    : {best_mission.mission_score:.1f}")
        print(f"Optimal Path     : {route_str}")

    except UnknownLocationError as e:
        print(f"Pathfinding Error: {e}")


def update_incident():
    print("\n--- UPDATE INCIDENT STATUS ---")
    if not incidents:
        print("No incidents found.")
        return

    inc_id = input("Enter Incident ID to update (e.g., INC-001): ").strip().upper()
    target = next((i for i in incidents if i["id"] == inc_id), None)

    if not target:
        print("Incident ID not found.")
        return

    print(f"Current Status of {target['id']}: {target['status']}")
    print("1. Set IN_PROGRESS\n2. Set RESOLVED\n3. Cancel")
    choice = input("Choice: ").strip()

    if choice == "1":
        target["status"] = "IN_PROGRESS"
        print("Status updated to IN_PROGRESS.")
    elif choice == "2":
        target["status"] = "RESOLVED"
        print("Status updated to RESOLVED.")


def show_menu():
    print("\n" + "=" * 40)
    print("     SPIDER-MAN COMMAND CENTRE")
    print("=" * 40)
    print("1. Report Incident")
    print("2. View Active Incidents")
    print("3. View Response Priority")
    print("4. Get Next Mission (Dijkstra Pathfinding)")
    print("5. Update Incident Status")
    print("6. Exit")
    print("=" * 40)


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
            print("\nExiting Command Centre. Stay safe, Spider-Man!")
            break
        else:
            print("Invalid selection. Try again.")


if __name__ == "__main__":
    main()
