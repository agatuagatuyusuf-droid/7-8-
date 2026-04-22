from bt_core.nodes import ConditionNode
from bt_core.config import NodeConfig
from typing import Dict, Any, Tuple, Optional
from bt_utils.ocr_manager import OCRManager


EXTRACT_MODE_MAP = {
    "无规则": "无规则",
    "x": "x",
    "y": "y",
    "自定义": "自定义",
}


class NumberConditionNode(ConditionNode):
    NODE_TYPE = "NumberConditionNode"

    def __init__(self, node_id: str = None, config: NodeConfig = None):
        super().__init__(node_id, config)
        self.region: Optional[Tuple[int, int, int, int]] = self._parse_region(self.config.get("region", None))
        self.comparison = self.config.get("comparison", ">=")
        self.target_value = self.config.get_float("target_value", 0)
        self.extract_mode = self.config.get("extract_mode", "无规则")
        self.extract_pattern = self.config.get("extract_pattern", "")
        language_display = self.config.get("language", "简体中文")
        from bt_nodes.conditions.ocr import LANGUAGE_MAP
        self.language = LANGUAGE_MAP.get(language_display, "chi_sim")
        preprocess_display = self.config.get("preprocess_mode", "默认")
        self.preprocess_mode = "game" if preprocess_display == "复杂色彩" else "normal"

    def _check_condition(self, context) -> bool:
        try:
            if self.region is None:
                self._log_condition_result(False, "请先设置检测区域")
                return False

            screenshot = self._get_region_image(context)
            if screenshot is None:
                return False

            success, value, all_text, position = OCRManager().recognize_number_with_position(
                screenshot,
                language=self.language,
                preprocess_mode=self.preprocess_mode,
                extract_mode=self.extract_mode,
                extract_pattern=self.extract_pattern
            )

            if not success or value is None:
                self._log_condition_result(False, f"无法识别数字 (文本: {all_text})")
                return False

            if position:
                actual_position = (position[0] + self.region[0], position[1] + self.region[1])
                self._save_position(context, actual_position)

            result = self._compare_value(value)

            if result:
                self._log_condition_result(True, extra_info=f"值: {value}")
                return True
            else:
                self._log_condition_result(False,
                    f"数值比较失败: {value} {self.comparison} {self.target_value}")
                return False
        except Exception as e:
            self._log_condition_result(False, str(e))
            return False

    def _compare_value(self, value: float) -> bool:
        """比较数值

        Args:
            value: 识别到的数值

        Returns:
            比较结果
        """
        ops = {
            ">": lambda a, b: a > b,
            ">=": lambda a, b: a >= b,
            "<": lambda a, b: a < b,
            "<=": lambda a, b: a <= b,
            "==": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
        }
        op = ops.get(self.comparison, lambda a, b: False)
        return op(value, self.target_value)

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["config"]["region"] = list(self.region) if self.region else None
        data["config"]["comparison"] = self.comparison
        data["config"]["target_value"] = self.target_value
        data["config"]["extract_mode"] = self.extract_mode
        data["config"]["extract_pattern"] = self.extract_pattern
        from bt_nodes.conditions.ocr import LANGUAGE_MAP
        reverse_language_map = {"eng": "English", "chi_sim": "简体中文", "chi_tra": "繁体中文"}
        data["config"]["language"] = reverse_language_map.get(self.language, self.language)
        data["config"]["preprocess_mode"] = "复杂色彩" if self.preprocess_mode == "game" else "默认"
        data["config"]["offset"] = list(self.offset)
        return data
