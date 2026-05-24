from bt_core.nodes import ConditionNode
from bt_core.config import NodeConfig
from typing import Dict, Any, Tuple, Optional
from bt_utils.ocr_manager import OCRManager


LANGUAGE_MAP = {
    "English": "eng",
    "简体中文": "chi_sim",
    "繁体中文": "chi_tra",
    "eng": "eng",
    "chi_sim": "chi_sim",
    "chi_tra": "chi_tra",
}

LANGUAGE_REVERSE_MAP = {
    "eng": "English",
    "chi_sim": "简体中文",
    "chi_tra": "繁体中文",
}

PREPROCESS_MODE_MAP = {
    "默认": "normal",
    "复杂色彩": "game",
    "自适应": "adaptive",
    "自动调优": "auto",
}

PREPROCESS_MODE_REVERSE_MAP = {
    "normal": "默认",
    "game": "复杂色彩",
    "adaptive": "自适应",
    "auto": "自动调优",
}


class OCRConditionNode(ConditionNode):
    NODE_TYPE = "OCRConditionNode"

    def __init__(self, node_id: str = None, config: NodeConfig = None):
        super().__init__(node_id, config)
        self.region: Optional[Tuple[int, int, int, int]] = self._parse_region(self.config.get("region", None))
        self.keywords = self.config.get("keywords", "")
        language_display = self.config.get("language", "简体中文")
        self.language = LANGUAGE_MAP.get(language_display, "chi_sim")
        preprocess_display = self.config.get("preprocess_mode", "默认")
        self.preprocess_mode = PREPROCESS_MODE_MAP.get(preprocess_display, "normal")
        
        self.search_direction = self.config.get("search_direction", "左上")

        self.position_key = self.config.get("position_key", "last_detection_position")

    def _check_condition(self, context) -> bool:
        try:
            screenshot = self._get_region_image(context)
            if screenshot is None:
                return False

            from bt_utils.direction import SearchDirection
            search_direction = self.config.get("search_direction", "左上")
            direction = SearchDirection.VALUE_MAP.get(search_direction, SearchDirection.TOP_LEFT)

            keywords = self.config.get("keywords", "")
            language_display = self.config.get("language", "简体中文")
            language = LANGUAGE_MAP.get(language_display, "chi_sim")
            preprocess_display = self.config.get("preprocess_mode", "默认")
            preprocess_mode = PREPROCESS_MODE_MAP.get(preprocess_display, "normal")

            found, position, all_text = OCRManager().recognize(
                screenshot, keywords, language,
                preprocess_mode=preprocess_mode, region=self._parse_region(self.config.get("region", None)),
                search_direction=direction
            )

            if found:
                self._save_position(context, position)
                self._log_condition_result(True)
                return True
            else:
                reason = f"未找到关键词: {keywords}"
                extra = f"识别到的文本: {all_text}" if all_text else None
                self._log_condition_result(False, reason, extra)
                return False
        except Exception as e:
            from bt_utils.exception_handler import log_exception
            log_exception(e, f"OCRConditionNode '{self.name}'")
            self._log_condition_result(False, "检测异常，详情见终端日志")
            return False


