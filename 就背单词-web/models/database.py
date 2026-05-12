# -*- coding: utf-8 -*-
"""
数据持久化模块
使用 JSON 文件存储用户学习进度
"""

import os
import json
from .user_progress import UserProgress


class Database:
    """数据库类 - JSON文件存储"""
    
    def __init__(self, data_path: str):
        self.data_path = data_path
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        data_dir = os.path.dirname(self.data_path)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir)
    
    def save_progress(self, progress: UserProgress) -> bool:
        """保存用户进度"""
        try:
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump(progress.to_dict(), f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存进度失败: {e}")
            return False
    
    def load_progress(self) -> UserProgress:
        """加载用户进度"""
        if not os.path.exists(self.data_path):
            return UserProgress()
        
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return UserProgress.from_dict(data)
        except Exception as e:
            print(f"加载进度失败: {e}")
            return UserProgress()
    
    def clear_progress(self) -> bool:
        """清除所有进度"""
        try:
            if os.path.exists(self.data_path):
                os.remove(self.data_path)
            return True
        except Exception as e:
            print(f"清除进度失败: {e}")
            return False
