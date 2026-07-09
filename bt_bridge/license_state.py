from dataclasses import dataclass, field
from typing import List


@dataclass
class LicenseState:
    activated: bool = False
    valid: bool = False
    edition: str = ""
    expire_at: str = ""
    machine_code: str = ""
    features: List[str] = field(default_factory=list)
    error: str = ""

    @property
    def display_text(self) -> str:
        if self.valid:
            exp = self.expire_at or "未知到期时间"
            ed = self.edition or "unknown"
            return f"已授权：{ed} / 到期：{exp}"
        if self.activated:
            return "授权异常"
        return "未激活"

    @property
    def can_run(self) -> bool:
        return self.valid