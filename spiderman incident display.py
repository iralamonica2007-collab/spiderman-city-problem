"""
Spider-Man Neighbourhood Response System -- Threat Assessment module.

Takes a list of reported incidents and works out which ones Spider-Man
should respond to, and in what order.

No user input is read at runtime -- incidents are passed in as data
(see main() below). Each incident is just a plain dictionary.
"""


# ---------------------------------------------------------------------
# Scoring model
# priority score = severity score + (people affected x 2) + location importance
# ---------------------------------------------------------------------

SEVERITY_SCORES = {
    "LOW": 10,
    "MEDIUM": 20,
    "HIGH": 30,
    "CRITICAL": 40,
}

LOCATION_SCORES = {
    "SCHOOL": 4,
    "HOSPITAL": 4,
    "RESIDENTIAL": 3,
    "PUBLIC": 2,
    "STREET": 1,
}

POINTS_PER_PERSON_AFFECTED = 2


def calculate_priority_score(incident: dict) -> int:
    """Work out one incident's priority score."""
    severity_score = SEVERITY_SCORES[incident["severity"]]
    people_score = incident["people_affected"] * POINTS_PER_PERSON_AFFECTED
    location_score = LOCATION_SCORES[incident["location"]]
    return severity_score + people_score + location_score


# ---------------------------------------------------------------------
# Ranking rules
# ---------------------------------------------------------------------

def rank_incidents(incidents: list) -> list:
    """Return active incidents in response-priority order.

    - A RESOLVED incident is dropped and never appears.
    - Higher priority score comes first.
    - Equal scores are broken by: more people affected wins, then --
      if still equal -- the older incident (smaller reported_at) wins.
    """
    active_incidents = []
    for incident in incidents:
        if incident["status"] != "RESOLVED":
            active_incidents.append(incident)

    # Python's sort is guaranteed to be stable: it never reorders items
    # that are already equal. So we can sort three separate times,
    # starting with the LEAST important rule -- each later sort only
    # rearranges the ties left over from the sort before it.

    active_incidents.sort(key=lambda incident: incident["reported_at"])
    active_incidents.sort(key=lambda incident: incident["people_affected"], reverse=True)
    active_incidents.sort(key=calculate_priority_score, reverse=True)

    return active_incidents


def get_next_response(ranked_incidents: list):
    """Return the single incident Spider-Man should respond to next."""
    if len(ranked_incidents) == 0:
        return None
    return ranked_incidents[0]


# ---------------------------------------------------------------------
# Display (terminal output)
# ---------------------------------------------------------------------

def print_response_priority(ranked_incidents: list) -> None:
    """Print the ranked list, then the single next incident to respond to."""
    print("RESPONSE PRIORITY")
    print()

    position = 1
    for incident in ranked_incidents:
        score = calculate_priority_score(incident)
        incident_id = incident["id"].ljust(10)
        severity = incident["severity"].ljust(11)
        location = incident["location"].ljust(12)
        print(f"{position}. {incident_id}{severity}{location}Score: {score}")
        position += 1

    print()
    print("NEXT RESPONSE:")
    print()

    next_incident = get_next_response(ranked_incidents)
    if next_incident is None:
        print("No active incidents.")
    else:
        print(next_incident["id"])


# ---------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------

def main() -> None:
    # Sample incidents, passed in as data -- nothing is typed in by a user.
    incidents = [
        {"id": "INC-014", "severity": "CRITICAL", "people_affected": 5,
         "location": "HOSPITAL", "status": "ACTIVE", "reported_at": 1},
        {"id": "INC-009", "severity": "HIGH", "people_affected": 4,
         "location": "SCHOOL", "status": "ACTIVE", "reported_at": 2},
        {"id": "INC-017", "severity": "MEDIUM", "people_affected": 3,
         "location": "PUBLIC", "status": "ACTIVE", "reported_at": 3},
        {"id": "INC-020", "severity": "HIGH", "people_affected": 10,
         "location": "STREET", "status": "RESOLVED", "reported_at": 4},
    ]

    ranked = rank_incidents(incidents)
    print_response_priority(ranked)


if __name__ == "__main__":
    main()