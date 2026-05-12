# -*- coding: utf-8 -*-
"""
单词数据模型
"""

import os
import yaml
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Word:
    """单词数据类"""
    word: str
    title: str
    text: str


class WordLoader:
    """单词加载器"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.words: List[Word] = []
    
    def load(self) -> List[Word]:
        """加载单词列表（容错模式）"""
        if not os.path.exists(self.file_path):
            return []
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            
            self.words = []
            for key, value in data.items():
                if isinstance(value, dict):
                    self.words.append(Word(
                        word=key,
                        title=value.get('title', key),
                        text=value.get('text', '')
                    ))
        except Exception:
            # 容错解析：按行读取，提取有效条目
            self.words = self._load_robust()
        
        return self.words
    
    def _load_robust(self) -> List[Word]:
        """鲁棒性加载：逐行解析，跳过损坏条目"""
        words = []
        current_key = None
        current_title = None
        current_text_lines = []
        
        with open(self.file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            # 跳过空行和注释行
            if not stripped or stripped.startswith('#') or stripped.startswith('---'):
                i += 1
                continue
            
            # 新条目开始：key:
            if stripped.endswith(':') and not stripped.startswith('text:') and not stripped.startswith('title:'):
                # 保存之前的条目
                if current_key and current_text_lines:
                    text = '\n'.join(current_text_lines).strip()
                    title = current_title or current_key
                    words.append(Word(word=current_key, title=title, text=text))
                
                current_key = stripped[:-1].strip()
                current_title = None
                current_text_lines = []
                i += 1
                continue
            
            # 标题行
            if stripped.startswith('title:'):
                current_title = stripped[len('title:'):].strip()
                i += 1
                continue
            
            # 文本内容开始
            if stripped.startswith('text:'):
                # 可能是 text: | 或 text: 单行
                text_content = stripped[len('text:'):].strip()
                if text_content == '|':
                    # 多行文本，读取后续缩进行
                    i += 1
                    while i < len(lines):
                        next_line = lines[i]
                        if next_line.startswith('    ') or next_line.startswith('\t'):
                            current_text_lines.append(next_line.strip())
                            i += 1
                        else:
                            break
                else:
                    if text_content:
                        current_text_lines.append(text_content)
                    i += 1
                continue
            
            # 其他行，可能是前一条目的延续（多行文本）
            if line.startswith('    ') and current_key:
                current_text_lines.append(stripped)
            
            i += 1
        
        # 保存最后一个条目
        if current_key and current_text_lines:
            text = '\n'.join(current_text_lines).strip()
            title = current_title or current_key
            words.append(Word(word=current_key, title=title, text=text))
        
        return words
    
    def get_word(self, word: str) -> Optional[Word]:
        """获取指定单词"""
        for w in self.words:
            if w.word == word:
                return w
        return None
    
    def search(self, keyword: str) -> List[Word]:
        """搜索单词"""
        keyword = keyword.lower()
        return [w for w in self.words if keyword in w.word.lower() or keyword in w.title.lower()]
