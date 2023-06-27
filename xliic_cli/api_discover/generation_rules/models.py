from uuid import UUID
from dataclasses import dataclass, field


@dataclass
class GenerationRule:
    id: UUID
    name: str
    bucket_id: UUID
    openapi_base_id: UUID = None
    description: str = ""
    created_at: str = ""
    updated_at: str = ""
    http_calls: list = field(default_factory=list)
    configuration: dict = field(default_factory=dict)
    extra_data: dict = field(default_factory=dict)
    openapi_base: dict = field(default_factory=dict)
