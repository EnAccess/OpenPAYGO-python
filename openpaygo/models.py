from typing import Any, Dict, List, Optional
try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict


class MetricsDataFormat(TypedDict, total=False):
    id: Optional[int]
    data_order: Optional[List[str]]
    historical_data_order: Optional[List[str]]
    historical_data_interval: Optional[int]


class MetricsHistoricalDataStep(TypedDict, total=False):
    timestamp: Optional[int]
    relative_time: Optional[int]


class MetricsRequestData(TypedDict, total=False):
    serial_number: str
    data_format_id: Optional[int]
    data_format: Optional[MetricsDataFormat]
    data: Optional[Dict[str, Any]]
    historical_data: Optional[List[Any]]
    request_count: Optional[int]
    timestamp: Optional[int]
    auth: Optional[str]
