#!/usr/bin/env python3
"""Spider-Man Neighbourhood Response System -- Mission Planner."""

import heapq
from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Tuple

Location = str
DistanceKm = float
Road = Tuple[Location, Location, DistanceKm]

ROAD_NETWORK: Tuple[Road, ...] = (
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


class MissionPlannerError(ValueError):
    """Base class for mission planner input errors."""


class UnknownLocationError(MissionPlannerError):
    """Raised when a location is not part of the city map."""


class UnreachableLocationError(MissionPlannerError):
    """Raised when no road connects two locations."""


@dataclass(frozen=True)
class Route:
    start: Location
    goal: Location
    path: Tuple[Location, ...]
    distance_km: DistanceKm


@dataclass(frozen=True)
class Incident:
    id: str
    name: str
    location: Location
    priority: int


@dataclass(frozen=True)
class Mission:
    incident: Incident
    route: Route

    @property
    def mission_score(self) -> float:
        return self.incident.priority - self.route.distance_km


class MissionPlanner:
    def __init__(self, road_network: Sequence[Road] = ROAD_NETWORK) -> None:
        self.road_network: Tuple[Road, ...] = tuple(road_network)
        self._adjacency: Dict[Location, Dict[Location, DistanceKm]] = {}
        for here, there, distance in self.road_network:
            self._adjacency.setdefault(here, {})[there] = distance
            self._adjacency.setdefault(there, {})[here] = distance
        self.locations: frozenset[Location] = frozenset(self._adjacency)

    def knows_location(self, location: Location) -> bool:
        return location in self._adjacency

    def validate_location(self, location: Location) -> None:
        if not self.knows_location(location):
            raise UnknownLocationError(f"Unknown location: {location!r}.")

    def plan_route(self, start: Location, goal: Location) -> Route:
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
                continue
            settled.add(current)
            if current == goal:
                break
            for neighbour, road_distance in self._adjacency[current].items():
                candidate = distance_so_far + road_distance
                if candidate < shortest_distance.get(neighbour, float("inf")):
                    shortest_distance[neighbour] = candidate
                    previous_stop[neighbour] = current
                    heapq.heappush(queue, (candidate, neighbour))

        if goal not in shortest_distance:
            raise UnreachableLocationError(f"No road connects {start!r} and {goal!r}.")

        path = [goal]
        while path[-1] != start:
            path.append(previous_stop[path[-1]])
        path.reverse()

        return Route(start, goal, tuple(path), shortest_distance[goal])

    def plan_mission(self, spiderman_location: Location, incident: Incident) -> Mission:
        route = self.plan_route(spiderman_location, incident.location)
        return Mission(incident=incident, route=route)

    def plan_missions(self, spiderman_location: Location, incidents: Iterable[Incident]) -> List[Mission]:
        self.validate_location(spiderman_location)
        missions = [self.plan_mission(spiderman_location, inc) for inc in incidents]
        missions.sort(
            key=lambda m: (-m.mission_score, m.route.distance_km, m.incident.name)
        )
        return missions
