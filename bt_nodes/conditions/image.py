from bt_core.nodes import ConditionNode
from bt_core.config import NodeConfig
from typing import Dict, Any, Tuple, Optional
from PIL import Image
import os
from bt_utils.image_processor import ImageProcessor


class ImageConditionNode(ConditionNode):
    NODE_TYPE = "ImageConditionNode"

    def __init__(self, node_id: str = None, config: NodeConfig = None):
        super().__init__(node_id, config)
        self.region: Optional[Tuple[int, int, int, int]] = self._parse_region(self.config.get("region", None))
        self.template_path = self.config.get("template_path", "")
        self.threshold = self.config.get_float("threshold", 0.8)

    def _check_condition(self, context) -> bool:
        try:
            resolved_path = self._resolve_template_path(context)
            if resolved_path is None:
                return False

            screenshot = self._get_region_image(context)
            if screenshot is None:
                return False

            if not os.path.exists(resolved_path):
                self._log_condition_result(False, f"模板文件不存在: {self.template_path}")
                return False

            template = Image.open(resolved_path)
            if template is None:
                self._log_condition_result(False, f"无法加载模板文件: {self.template_path}")
                return False

            found, position, confidence = ImageProcessor.find_template(
                screenshot, template, self.threshold
            )

            if found:
                actual_position = self._adjust_position(position)
                self._save_position(context, actual_position)
                self._log_condition_result(True)
                return True
            else:
                self._log_condition_result(False, f"未找到匹配模板 (阈值: {self.threshold}, 最高置信度: {confidence:.2f})")
                return False
        except Exception as e:
            from bt_utils.exception_handler import log_exception
            log_exception(e, f"ImageConditionNode '{self.name}'")
            self._log_condition_result(False, "检测异常，详情见终端日志")
            return False

    def _resolve_template_path(self, context) -> Optional[str]:
        """解析模板路径

        Args:
            context: 执行上下文

        Returns:
            解析后的绝对路径，或None
        """
        if not self.template_path:
            self._log_condition_result(False, "未设置模板路径")
            return None

        if self.template_path.startswith("./") and hasattr(context, 'resolve_path'):
            return context.resolve_path(self.template_path)

        return self.template_path

    def _adjust_position(self, position: tuple) -> tuple:
        """调整坐标（加上区域偏移）

        Args:
            position: 相对位置

        Returns:
            绝对位置
        """
        if position is None:
            return None
        if self.region:
            return (position[0] + self.region[0], position[1] + self.region[1])
        return position

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["config"]["region"] = list(self.region) if self.region else None
        data["config"]["template_path"] = self.template_path
        data["config"]["threshold"] = self.threshold
        data["config"]["offset"] = list(self.offset)
        return data
