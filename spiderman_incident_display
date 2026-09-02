"""Spider-Man Neighbourhood Response System -- Threat Assessment module."""

# ---------------------------------------------------------------------
# Scoring Model & Map Location Mapping
# ---------------------------------------------------------------------

SEVERITY_SCORES = {
    "LOW": 10,
    "MEDIUM": 20,
    "HIGH": 30,
    "CRITICAL": 40,
}

LOCATION_SCORES = {
    "City Hospital": 5,
    "Midtown School": 5,
    "Park Avenue": 4,
    "Queens Street": 3,
    "Times Square": 3,
    "Stark Tower": 4,
    "Central Park": 2,
    "Grand Central": 3,
    "Daily Bugle": 3,
    "Brooklyn Bridge": 2,
}

POINTS_PER_PERSON_AFFECTED = 2


def calculate_priority_score(incident: dict) -> int:
    """Calculate an incident's priority score (bounded between 1 and 100)."""
    severity_score = SEVERITY_SCORES.get(incident.get("severity", "LOW"), 10)
    people_score = incident.get("people_affected", 0) * POINTS_PER_PERSON_AFFECTED
    location_score = LOCATION_SCORES.get(incident.get("location", ""), 1)

    raw_score = severity_score + people_score + location_score
    return min(max(raw_score, 1), 100)


def rank_incidents(incidents: list) -> list:
    """Return active incidents in response-priority order."""
    active_incidents = [inc for inc in incidents if inc.get("status") != "RESOLVED"]

    # Stable sort: 3rd priority -> 2nd priority -> 1st priority
    active_incidents.sort(key=lambda inc: inc.get("reported_at", 0))
    active_incidents.sort(key=lambda inc: inc.get("people_affected", 0), reverse=True)
    active_incidents.sort(key=calculate_priority_score, reverse=True)

    return active_incidents


def get_next_response(ranked_incidents: list):
    """Return the single incident Spider-Man should respond to next."""
    if not ranked_incidents:
        return None
    return ranked_incidents[0]


def print_response_priority(ranked_incidents: list) -> None:
    """Print the ranked list of active incidents."""
    print("\n--- RESPONSE PRIORITY ---")
    if not ranked_incidents:
        print("No active incidents.")
        return

    for position, incident in enumerate(ranked_incidents, start=1):
        score = calculate_priority_score(incident)
        inc_id = str(incident.get("id", "N/A")).ljust(10)
        severity = str(incident.get("severity", "N/A")).ljust(11)
        location = str(incident.get("location", "N/A")).ljust(18)
        print(f"{position}. {inc_id} {severity} {location} Score: {score}")

    next_inc = get_next_response(ranked_incidents)
    print("\nNEXT RESPONSE:")
    if next_inc:
        print(f"Incident {next_inc['id']} - {next_inc['type']} at {next_inc['location']}")
    else:
        print("No active incidents.")
