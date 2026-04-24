from bt_core.nodes import ConditionNode
from bt_core.config import NodeConfig
from typing import Dict, Any, Tuple, Optional


class ColorConditionNode(ConditionNode):
    NODE_TYPE = "ColorConditionNode"

    def __init__(self, node_id: str = None, config: NodeConfig = None):
        super().__init__(node_id, config)
        self.region: Optional[Tuple[int, int, int, int]] = self._parse_region(self.config.get("region", None))
        self.target_color = self._parse_color(self.config.get("target_color", None))
        self.tolerance = self.config.get_int("tolerance", 30)
        self.match_mode = self.config.get("match_mode", "any")

    def _check_condition(self, context) -> bool:
        try:
            if self.region is None:
                self._log_condition_result(False, "请先设置检测区域")
                return False

            screenshot = self._get_region_image(context)
            if screenshot is None:
                return False

            from PIL import Image
            import numpy as np

            img_array = np.array(screenshot)
            target = np.array(self.target_color)

            diff = np.abs(img_array[:, :, :3].astype(int) - target.astype(int))
            matches = np.all(diff <= self.tolerance, axis=2)

            if self.match_mode == "all":
                result = bool(np.all(matches))
            else:
                result = bool(np.any(matches))

            if result:
                match_positions = np.argwhere(matches)
                if len(match_positions) > 0:
                    center_idx = len(match_positions) // 2
                    y, x = match_positions[center_idx]
                    position = (int(x) + self.region[0], int(y) + self.region[1])
                    self._save_position(context, position)

                self._log_condition_result(True)
                return True
            else:
                self._log_condition_result(False,
                    f"未找到匹配颜色 RGB{self.target_color} (容差: {self.tolerance})")
                return False
        except Exception as e:
            from bt_utils.exception_handler import log_exception
            log_exception(e, f"ColorConditionNode '{self.name}'")
            self._log_condition_result(False, "检测异常，详情见终端日志")
            return False

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["config"]["region"] = list(self.region) if self.region else None
        data["config"]["target_color"] = list(self.target_color) if self.target_color else None
        data["config"]["tolerance"] = self.tolerance
        data["config"]["match_mode"] = self.match_mode
        data["config"]["offset"] = list(self.offset)
        return data
