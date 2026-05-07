import pytest
import os
import json
import tempfile
from bt_core.nodes import SubtreeNode
from bt_core.config import NodeConfig
from bt_core.status import NodeStatus
from bt_core.context import ExecutionContext


class TestSubtreeNode:
    def test_initialization(self):
        config = NodeConfig(name="登录流程")
        config.set("subtree_path", "subtrees/login.json")
        config.set("blackboard_mode", "inherit")
        
        node = SubtreeNode(config=config)
        
        assert node.subtree_path == "subtrees/login.json"
        assert node.blackboard_mode == "inherit"
        assert node._subtree_root is None
    
    def test_blackboard_mode_default(self):
        node = SubtreeNode()
        assert node.blackboard_mode == "inherit"
    
    def test_resolve_relative_path(self):
        config = NodeConfig()
        config.set("subtree_path", "subtrees/login.json")
        
        node = SubtreeNode(config=config)
        
        ctx = ExecutionContext(project_root="D:/project")
        resolved = node._resolve_path(ctx)
        
        assert "subtrees" in resolved
        assert "login.json" in resolved
    
    def test_resolve_absolute_path(self):
        config = NodeConfig()
        config.set("subtree_path", "D:/project/subtrees/login.json")
        
        node = SubtreeNode(config=config)
        
        ctx = ExecutionContext()
        resolved = node._resolve_path(ctx)
        
        assert resolved == "D:/project/subtrees/login.json"
    
    def test_tick_returns_failure_when_path_empty(self):
        node = SubtreeNode(config=NodeConfig(name="空子树"))
        ctx = ExecutionContext()
        
        status = node.tick(ctx)
        assert status == NodeStatus.FAILURE
    
    def test_tick_returns_failure_when_file_not_found(self):
        config = NodeConfig(name="不存在的子树")
        config.set("subtree_path", "nonexistent.json")
        
        node = SubtreeNode(config=config)
        ctx = ExecutionContext()
        
        status = node.tick(ctx)
        assert status == NodeStatus.FAILURE
    
    def test_create_subtree_context_inherit(self):
        config = NodeConfig()
        config.set("blackboard_mode", "inherit")
        
        node = SubtreeNode(config=config)
        parent_ctx = ExecutionContext()
        parent_ctx.blackboard.set("test_var", "parent_value")
        
        sub_ctx = node._create_subtree_context(parent_ctx)
        
        assert sub_ctx is not parent_ctx
        assert sub_ctx.blackboard is parent_ctx.blackboard
        assert sub_ctx.blackboard.get("test_var") == "parent_value"
    
    def test_create_subtree_context_isolated(self):
        config = NodeConfig()
        config.set("blackboard_mode", "isolated")
        
        node = SubtreeNode(config=config)
        parent_ctx = ExecutionContext()
        parent_ctx.blackboard.set("test_var", "parent_value")
        
        sub_ctx = node._create_subtree_context(parent_ctx)
        
        assert sub_ctx is not parent_ctx
        assert sub_ctx.blackboard.get("test_var") is None
    
    def test_create_subtree_context_namespaced(self):
        config = NodeConfig()
        config.set("blackboard_mode", "namespaced")
        config.set("namespace", "login")
        
        node = SubtreeNode(config=config)
        parent_ctx = ExecutionContext()
        
        sub_ctx = node._create_subtree_context(parent_ctx)
        
        from bt_core.blackboard import NamespacedBlackboard
        assert isinstance(sub_ctx.blackboard, NamespacedBlackboard)
        
        sub_ctx.blackboard.set("username", "admin")
        assert parent_ctx.blackboard.get("login.username") == "admin"
    
    def test_to_dict_includes_subtree_config(self):
        config = NodeConfig(name="登录流程")
        config.set("subtree_path", "login.json")
        config.set("blackboard_mode", "namespaced")
        config.set("namespace", "login")
        
        node = SubtreeNode(config=config)
        data = node.to_dict()
        
        assert data["config"]["subtree_path"] == "login.json"
        assert data["config"]["blackboard_mode"] == "namespaced"
        assert data["config"]["namespace"] == "login"
    
    def test_reset_propagates_to_subtree(self):
        node = SubtreeNode(config=NodeConfig(name="test"))
        node._subtree_root = None
        
        node.reset()
        assert node.current_index == 0
    
    def test_node_type(self):
        node = SubtreeNode()
        assert node.NODE_TYPE == "SubtreeNode"
