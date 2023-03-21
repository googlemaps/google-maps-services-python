from datetime import datetime
from typing import Union, List, Tuple, Dict, Any

from typing_extensions import TypeAlias, TypedDict, Literal


class LocationDict(TypedDict):
    lat: float
    lng: float


Location: TypeAlias = Union[
    str,
    List[float],
    Tuple[float, float],
    LocationDict,
]

Timestamp: TypeAlias = Union[int, datetime]
DictStrAny: TypeAlias = Dict[str, Any]

Unit = Literal["metric", "imperial"]

TrafficMode: TypeAlias = Literal["best_guess", "optimistic", "pessimistic"]
TransitRoutingPreference: TypeAlias = Literal["less_walking", "fewer_transfers"]
TransitMode: TypeAlias = Literal["bus", "subway", "train", "tram", "rail"]
DirectionsMode: TypeAlias = Literal["driving", "walking", "bicycling", "transit"]
DestinationAvoid = Literal["tolls", "highways", "ferries"]
