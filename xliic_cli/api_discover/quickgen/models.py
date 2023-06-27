from uuid import UUID
from dataclasses import dataclass, field


@dataclass
class QuickGen:
    id: UUID
    bucket_id: UUID
    rule_id: UUID
    owner_id: UUID
    is_complete: bool
    extra_data: dict = field(default_factory=dict)
    created_at: str = ""
    updated_at: str = ""


__all__ = ["QuickGen"]
