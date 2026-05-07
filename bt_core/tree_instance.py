from dataclasses import dataclass, field
from typing import Optional, Any

from .engine import BehaviorTreeEngine
from .context import ExecutionContext
from .blackboard import Blackboard


@dataclass
class TreeInstance:
    """行为树实例

    封装单个行为树实例的运行时状态。
    """
    name: str
    engine: BehaviorTreeEngine
    context: ExecutionContext
    blackboard: Blackboard
    status: str = "idle"
    error_message: Optional[str] = None
    start_time: Optional[float] = None
    tick_count: int = 0

    def to_dict(self) -> dict:
        """导出为字典"""
        return {
            "name": self.name,
            "status": self.status,
            "error_message": self.error_message,
            "tick_count": self.tick_count,
        }
