from uuid import UUID
from dataclasses import dataclass, field


@dataclass
class Bucket:
    id: UUID
    owner_id: UUID
    organization_id: UUID
    name: str
    host: str
    base_url: str = '/*'
    protocol_https: bool = True
    protocol_http: bool = False
    description: str = ""
    extra_data: dict = field(default_factory=dict)
    created_at: str = ""
    updated_at: str = ""
