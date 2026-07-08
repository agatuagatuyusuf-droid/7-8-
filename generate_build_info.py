#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
打包配置生成脚本

在打包前运行此脚本，根据 build_config.json 生成版本信息文件
"""

import json
import os
from datetime import datetime

def get_git_commit():
    """获取当前Git提交哈希"""
    try:
        import subprocess
        result = subprocess.run(
            ['git', 'rev-parse', '--short', 'HEAD'],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return ""

def load_build_config():
    """加载打包配置"""
    config_file = os.path.join(os.path.dirname(__file__), 'build_config.json')
    
    if not os.path.exists(config_file):
        print(f"Warning: {config_file} not found, using default config")
        return {
            "version": "1.0.0",
            "expire_date": "2099-12-31",
            "force_update": False,
            "build_type": "release"
        }
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    return config

def generate_version_info():
    """生成版本信息文件"""
    config = load_build_config()
    
    build_type = config.get("build_type", "release")
    
    debug_config = {
        "enable_logging": build_type != "release",
        "log_level": "DEBUG" if build_type != "release" else "INFO",
        "enable_debug_mode": build_type != "release"
    }
    
    try:
        from bt_utils.brand_manager import load_brand
        brand = load_brand()
    except Exception:
        brand = {}
    
    github_default = {
        "owner": brand.get("repo_owner", ""),
        "repo": brand.get("repo_name", "")
    } if brand.get("repo_owner") else config.get("github", {"owner": "", "repo": ""})
    
    build_info = {
        "version": config.get("version", "1.0.0"),
        "expire_date": config.get("expire_date", "2099-12-31"),
        "force_update": config.get("force_update", False),
        "build_type": build_type,
        "build_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "git_commit": get_git_commit(),
        
        "github": config.get("github", github_default),
        
        "update_links": config.get("update_links", {
            "tool_intro": brand.get("docs_url", ""),
            "download": brand.get("download_url", ""),
            "changelog": brand.get("support_url", "")
        }),
        
        "app_info": config.get("app_info", {
            "name": brand.get("product_name_en", "AutoDoor Pro"),
            "name_cn": brand.get("product_name_cn", "AutoDoor 自动化系统")
        }),
        
        "debug": debug_config
    }
    
    output_file = os.path.join(os.path.dirname(__file__), 'bt_utils', 'build_info.json')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(build_info, f, indent=2, ensure_ascii=False)
    
    print(f"Generated build_info.json:")
    print(f"  Version: {build_info['version']}")
    print(f"  Expire Date: {build_info['expire_date']}")
    print(f"  Force Update: {build_info['force_update']}")
    print(f"  Build Type: {build_info['build_type']}")
    print(f"  Build Time: {build_info['build_time']}")
    print(f"  Git Commit: {build_info['git_commit']}")
    print(f"  GitHub Owner: {build_info['github']['owner']}")
    print(f"  GitHub Repo: {build_info['github']['repo']}")
    print(f"  Debug Mode: {build_info['debug']['enable_debug_mode']}")
    
    return build_info

if __name__ == "__main__":
    generate_version_info()
