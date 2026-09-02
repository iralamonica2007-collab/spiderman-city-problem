#!/usr/bin/env python3
"""Spider-Man Neighbourhood Response System -- Mission Planner.

Spider-Man has to respond to incidents all over the city, but he is rarely
standing next to one when it happens.  This Mission Planner tells him where
to go and which mission makes the most sense from his current location.

What Spider-Man provides
    * His current location.
    * The active incidents: each has a name, a location and a priority score.

What this system determines
    * Whether a location is valid (it must exist on the city map).
    * The travel distance between two locations.
    * The best route between them, using real, connected roads only.
    * A score for every mission:

          MISSION SCORE = PRIORITY SCORE - DISTANCE

      The mission with the highest score is recommended.

Features
    1.  Accepts and validates Spider-Man's current location.
    2.  Accepts and validates incident locations.
    3.  Rejects unknown locations with a clear error message.
    4.  Computes travel distance over the real road network.
    5.  Plans the shortest route (Dijkstra) using only real roads.
    6.  Handles multiple missions at once.
    7.  Scores every mission (priority - distance).
    8.  Ranks missions and recommends the best one (a tie goes to the
        closer incident).
    9.  Pure Python standard library: no Google Maps, no GPS, no APIs, no
        databases.  All neighbour (road) information is right here.
    10. Ships with built-in test scenarios covering all of the above.

Usage
    python spiderman_mission_planner.py                # demo + tests
    python spiderman_mission_planner.py --interactive  # plan your own
"""

from __future__ import annotations

import heapq
import sys
from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Tuple

# ---------------------------------------------------------------------------
# KNOW YOUR CITY
# The direct road connections of the city (all two-way), with distances in
# kilometres.  This neighbour information is the only data source the
# planner is allowed to use.
# ---------------------------------------------------------------------------

Location = str
DistanceKm = float
Road = Tuple[Location, Location, DistanceKm]

ROAD_NETWORK: Tuple[Road, ...] = (
    # from                to                    distance (km)
    ("Queens Street",     "Midtown School",     4.0),
    ("Midtown School",    "Park Avenue",        3.0),
    ("Park Avenue",       "City Hospital",      2.0),
    ("Queens Street",     "City Hospital",     10.0),
    ("Midtown School",    "Times Square",       5.0),
    ("Park Avenue",       "Stark Tower",        4.0),
    ("City Hospital",     "Central Park",       6.0),
    ("Times Square",      "Central Park",       3.0),
    ("Stark Tower",       "Daily Bugle",        2.0),
    ("Times Square",      "Daily Bugle",        4.0),
    ("Central Park",      "Grand Central",      3.0),
    ("Grand Central",     "City Hospital",      5.0),
    ("Brooklyn Bridge",   "Queens Street",      6.0),
    ("Brooklyn Bridge",   "Daily Bugle",        7.0),
    ("Park Avenue",       "Grand Central",      3.0),
)

MIN_PRIORITY = 1
MAX_PRIORITY = 100

__all__ = [
    "ROAD_NETWORK",
    "Incident",
    "Mission",
    "MissionPlanner",
    "MissionPlannerError",
    "Route",
    "UnknownLocationError",
    "UnreachableLocationError",
]


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class MissionPlannerError(ValueError):
    """Base class for all mission-planner input problems."""


class UnknownLocationError(MissionPlannerError):
    """Raised when a location is not part of the city map."""


class UnreachableLocationError(MissionPlannerError):
    """Raised when no sequence of real roads connects two locations."""


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Route:
    """A route between two locations that follows real roads only."""

    start: Location
    goal: Location
    path: Tuple[Location, ...]
    distance_km: DistanceKm


@dataclass(frozen=True)
class Incident:
    """Something that needs Spider-Man, somewhere in the city."""

    name: str
    location: Location
    priority: int  # 1 = minor nuisance ... 100 = city in danger


@dataclass(frozen=True)
class Mission:
    """A fully planned response to one incident."""

    incident: Incident
    route: Route

    @property
    def mission_score(self) -> float:
        """MISSION SCORE = PRIORITY SCORE - DISTANCE (km)."""
        return self.incident.priority - self.route.distance_km


# ---------------------------------------------------------------------------
# The planner
# ---------------------------------------------------------------------------


class MissionPlanner:
    """Plans routes and missions across the city road network."""

    def __init__(self, road_network: Sequence[Road] = ROAD_NETWORK) -> None:
        self.road_network: Tuple[Road, ...] = tuple(road_network)
        self._adjacency: Dict[Location, Dict[Location, DistanceKm]] = {}
        for here, there, distance in self.road_network:
            self._adjacency.setdefault(here, {})[there] = distance
            self._adjacency.setdefault(there, {})[here] = distance
        self.locations: frozenset[Location] = frozenset(self._adjacency)

    # -- location validation --------------------------------------------

    def knows_location(self, location: Location) -> bool:
        """Return True when ``location`` exists on the city map."""
        return location in self._adjacency

    def validate_location(self, location: Location) -> None:
        """Raise :class:`UnknownLocationError` for off-map locations."""
        if not self.knows_location(location):
            raise UnknownLocationError(
                f"Unknown location: {location!r}. Known locations: "
                + ", ".join(sorted(self.locations))
            )

    def road_exists(self, first: Location, second: Location) -> bool:
        """Return True when a direct road connects the two locations."""
        return second in self._adjacency.get(first, {})

    # -- route planning -------------------------------------------------

    def plan_route(self, start: Location, goal: Location) -> Route:
        """Return the shortest route from ``start`` to ``goal``.

        Only real, connected roads are used (Dijkstra's algorithm), so the
        answer is always a legal path through the city -- never a straight
        line "as the crow flies".
        """
        self.validate_location(start)
        self.validate_location(goal)

        if start == goal:
            return Route(start, goal, (start,), 0.0)

        shortest_distance: Dict[Location, DistanceKm] = {start: 0.0}
        previous_stop: Dict[Location, Location] = {}
        settled: set = set()
        queue = [(0.0, start)]

        while queue:
            distance_so_far, current = heapq.heappop(queue)
            if current in settled:
                continue  # stale queue entry
            settled.add(current)
            if current == goal:
                break
            for neighbour, road_distance in self._adjacency[current].items():
                candidate_distance = distance_so_far + road_distance
                if candidate_distance < shortest_distance.get(
                    neighbour, float("inf")
                ):
                    shortest_distance[neighbour] = candidate_distance
                    previous_stop[neighbour] = current
                    heapq.heappush(queue, (candidate_distance, neighbour))

        if goal not in shortest_distance:
            raise UnreachableLocationError(
                f"No road connects {start!r} and {goal!r}."
            )

        path = [goal]
        while path[-1] != start:
            path.append(previous_stop[path[-1]])
        path.reverse()

        return Route(start, goal, tuple(path), shortest_distance[goal])

    # -- mission planning -----------------------------------------------

    def plan_mission(
        self, spiderman_location: Location, incident: Incident
    ) -> Mission:
        """Plan how Spider-Man would respond to a single incident."""
        route = self.plan_route(spiderman_location, incident.location)
        return Mission(incident=incident, route=route)

    def plan_missions(
        self, spiderman_location: Location, incidents: Iterable[Incident]
    ) -> List[Mission]:
        """Plan a mission per incident and rank them, best first.

        Ranking rules: highest mission score wins; on a tie the closer
        mission wins; names break any remaining tie for a stable order.
        """
        self.validate_location(spiderman_location)
        missions = [
            self.plan_mission(spiderman_location, incident)
            for incident in incidents
        ]
        missions.sort(
            key=lambda mission: (
                -mission.mission_score,
                mission.route.distance_km,
                mission.incident.name,
            )
        )
        return missions

    def recommend_mission(
        self, spiderman_location: Location, incidents: Iterable[Incident]
    ) -> Mission:
        """Return the mission that makes the most sense right now."""
        missions = self.plan_missions(spiderman_location, incidents)
        if not missions:
            raise MissionPlannerError("No incidents provided, nothing to plan.")
        return missions[0]


# ---------------------------------------------------------------------------
# Console reporting
# ---------------------------------------------------------------------------


def format_route(route: Route) -> str:
    """Render a route as 'Queens Street -> Midtown School -> Park Avenue'."""
    return " -> ".join(route.path)


def print_city_map(planner: MissionPlanner) -> None:
    """Print the known direct road connections ('know your city')."""
    print("KNOW YOUR CITY - direct roads (all two-way):")
    for here, there, distance in planner.road_network:
        print(f"  {here} <-> {there}: {distance:.0f} km")
    print()


def print_mission_report(missions: Sequence[Mission]) -> None:
    """Print a ranked report of the planned missions."""
    print("MISSION REPORT")
    print("-" * 64)
    for mission in missions:
        incident = mission.incident
        print(f"{incident.name} -> {incident.location}")
        print(f"  Route    : {format_route(mission.route)}")
        print(f"  Distance : {mission.route.distance_km:.1f} km")
        print(f"  Priority : {incident.priority}")
        print(f"  Score    : {mission.mission_score:.1f}  (priority - distance)")
        print()
    if missions:
        best = missions[0]
        print("-" * 64)
        print(f"RECOMMENDED MISSION: {best.incident.name} "
              f"(score {best.mission_score:.1f}) - go get 'em, Spidey!")


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

SPIDERMAN_START: Location = "Queens Street"

DEMO_INCIDENTS: Tuple[Incident, ...] = (
    Incident(name="Incident A", location="Park Avenue", priority=90),
    Incident(name="Incident B", location="City Hospital", priority=70),
)


def run_demo() -> None:
    """Run the classic demo: two incidents, one recommendation."""
    planner = MissionPlanner()

    print("=" * 64)
    print("  SPIDER-MAN NEIGHBOURHOOD RESPONSE SYSTEM")
    print("  MISSION PLANNER")
    print("=" * 64)
    print()
    print_city_map(planner)
    print(f"Spider-Man's current location: {SPIDERMAN_START}")
    print()
    print("Active incidents:")
    for incident in DEMO_INCIDENTS:
        print(f"  * {incident.name}: {incident.location} "
              f"(priority {incident.priority})")
    print()

    missions = planner.plan_missions(SPIDERMAN_START, DEMO_INCIDENTS)
    print_mission_report(missions)


# ---------------------------------------------------------------------------
# Built-in test scenarios
# ---------------------------------------------------------------------------


def run_tests() -> None:
    """Run every test scenario and print a pass/fail summary."""

    planner = MissionPlanner()
    results: List[Tuple[str, bool]] = []

    def check(description: str, condition: bool) -> None:
        results.append((description, bool(condition)))

    # 1. The city map is well formed.
    check(
        "every location in the road network is a known location",
        all(
            planner.knows_location(first) and planner.knows_location(second)
            for first, second, _ in ROAD_NETWORK
        ),
    )

    # 2. Known locations are accepted, unknown ones are rejected.
    check("a known location is accepted", planner.knows_location("Park Avenue"))
    try:
        planner.validate_location("Gotham City")
        check("an unknown location is rejected", False)
    except UnknownLocationError:
        check("an unknown location is rejected", True)

    # 3. Travelling to where you already are costs nothing.
    stay_put = planner.plan_route("Park Avenue", "Park Avenue")
    check("route to the same location is 0 km", stay_put.distance_km == 0.0)
    check("route to the same location is trivial",
          stay_put.path == ("Park Avenue",))

    # 4. A direct road is used at its exact distance.
    direct = planner.plan_route("Queens Street", "Midtown School")
    check("direct road distance is used (4 km)", direct.distance_km == 4.0)
    check("direct road route has no detour",
          direct.path == ("Queens Street", "Midtown School"))

    # 5. The shortest route hops through intermediate locations.
    to_park_avenue = planner.plan_route("Queens Street", "Park Avenue")
    check("shortest route to Park Avenue is 7 km",
          to_park_avenue.distance_km == 7.0)
    check("shortest route runs Queens Street -> Midtown School -> Park Avenue",
          to_park_avenue.path
          == ("Queens Street", "Midtown School", "Park Avenue"))

    # 6. A multi-hop route can beat a longer direct road.
    to_hospital = planner.plan_route("Queens Street", "City Hospital")
    check("multi-hop route (9 km) beats the 10 km direct road",
          to_hospital.distance_km == 9.0)

    # 7. Every step of a planned route is a real, connected road.
    def uses_real_roads(path: Sequence[Location]) -> bool:
        return all(
            planner.road_exists(first, second)
            for first, second in zip(path, path[1:])
        )

    check("every step of the route is a real road",
          uses_real_roads(to_hospital.path))

    # 8. Roads are two-way, so distance is symmetric.
    backwards = planner.plan_route("Park Avenue", "Queens Street")
    check("travel distance is the same in both directions",
          backwards.distance_km == to_park_avenue.distance_km)

    # 9. Mission score = priority - distance.
    mission_a = planner.plan_mission(SPIDERMAN_START, DEMO_INCIDENTS[0])
    check("mission score is priority minus distance (90 - 7)",
          mission_a.mission_score == 90 - 7)

    # 10. The best mission is recommended (A: 83 points vs B: 61 points).
    best = planner.recommend_mission(SPIDERMAN_START, DEMO_INCIDENTS)
    check("Incident A (score 83) is recommended over Incident B (score 61)",
          best.incident.name == "Incident A")

    # 11. On equal scores, the closer mission wins.
    tied_incidents = (
        Incident(name="Close Call", location="Midtown School", priority=80),  # 80-4=76
        Incident(name="Far Fuss", location="Park Avenue", priority=83),      # 83-7=76
    )
    winner = planner.recommend_mission(SPIDERMAN_START, tied_incidents)
    check("on a tie the closer mission wins",
          winner.incident.name == "Close Call")

    # 12. Unreachable destinations raise a clear error.
    split_city = MissionPlanner((("A", "B", 1.0), ("C", "D", 1.0)))
    try:
        split_city.plan_route("A", "D")
        check("unreachable destination raises an error", False)
    except UnreachableLocationError:
        check("unreachable destination raises an error", True)

    # 13. Planning with no incidents fails gracefully.
    try:
        planner.recommend_mission(SPIDERMAN_START, ())
        check("no incidents gives a clear error", False)
    except MissionPlannerError:
        check("no incidents gives a clear error", True)

    # Summary.
    passed = sum(1 for _, ok in results if ok)
    print()
    print("=" * 64)
    print("TEST SCENARIOS")
    print("-" * 64)
    for description, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {description}")
    print("-" * 64)
    print(f"  {passed}/{len(results)} scenarios passed")
    print("=" * 64)


# ---------------------------------------------------------------------------
# Interactive mode
# ---------------------------------------------------------------------------


def _ask_for_location(planner: MissionPlanner, prompt: str) -> Location:
    """Keep asking until the user names a location on the city map."""
    while True:
        answer = input(f"{prompt}: ").strip()
        if planner.knows_location(answer):
            return answer
        print(f"  {answer!r} is not on the map - pick one from the list above.")


def _ask_for_int(prompt: str, minimum: int, maximum: int) -> int:
    """Keep asking until the user enters an int within the bounds."""
    while True:
        answer = input(f"{prompt}: ").strip()
        try:
            value = int(answer)
        except ValueError:
            print(f"  Please enter a whole number ({minimum}-{maximum}).")
            continue
        if minimum <= value <= maximum:
            return value
        print(f"  Please enter a number between {minimum} and {maximum}.")


def run_interactive() -> None:
    """Plan a mission from locations typed in at the terminal."""
    planner = MissionPlanner()
    print("=" * 64)
    print("  SPIDER-MAN MISSION PLANNER (interactive mode)")
    print("=" * 64)
    print()
    print("Known locations:")
    for location in sorted(planner.locations):
        print(f"  - {location}")
    print()

    spiderman_location = _ask_for_location(planner, "Spider-Man's current location")
    incident_count = _ask_for_int("How many incidents are active",
                                  minimum=1, maximum=10)

    incidents: List[Incident] = []
    for number in range(1, incident_count + 1):
        print(f"\nIncident {number} of {incident_count}:")
        default_name = f"Incident {chr(ord('A') + number - 1)}"
        name = input(f"  Name [{default_name}]: ").strip() or default_name
        location = _ask_for_location(planner, "  Location of the incident")
        priority = _ask_for_int("  Priority (1-100)",
                                minimum=MIN_PRIORITY, maximum=MAX_PRIORITY)
        incidents.append(Incident(name=name, location=location, priority=priority))

    print()
    print(f"Spider-Man's current location: {spiderman_location}")
    print()
    missions = planner.plan_missions(spiderman_location, incidents)
    print_mission_report(missions)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main(argv: Sequence[str] = ()) -> None:
    if "--interactive" in argv:
        run_interactive()
    else:
        run_demo()
        run_tests()


if __name__ == "__main__":
    main(sys.argv[1:])