from typing import Optional
from .core_client import CoreClient


class RuntimeBridge:
    """行为树运行时 API 桥接"""

    def __init__(self, client: CoreClient):
        self._client = client

    def start_tree(self, tree_json: dict, project_root: str = "") -> dict:
        return self._client.send_request("tree.start", {
            "tree": tree_json,
            "project_root": project_root
        })

    def stop_tree(self) -> dict:
        return self._client.send_request("tree.stop")

    def pause_tree(self) -> dict:
        return self._client.send_request("tree.pause")

    def resume_tree(self) -> dict:
        return self._client.send_request("tree.resume")

    def get_status(self) -> dict:
        return self._client.send_request("tree.status")

    def validate_tree(self, tree_json: dict) -> dict:
        return self._client.send_request("tree.validate", {
            "tree": tree_json
        })

    def get_logs(self) -> dict:
        return self._client.send_request("runtime.logs")

    def get_stats(self) -> dict:
        return self._client.send_request("runtime.stats")
