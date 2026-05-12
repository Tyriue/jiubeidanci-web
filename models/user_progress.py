# -*- coding: utf-8 -*-
"""
用户学习进度管理
"""

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Dict, List, Optional


class WordStatus(Enum):
    """单词学习状态"""
    NEW = "new"           # 未学习
    LEARNING = "learning" # 学习中
    REVIEW = "review"     # 待复习
    MASTERED = "mastered" # 已掌握


@dataclass
class WordProgress:
    """单个单词的学习进度"""
    word: str
    status: WordStatus = WordStatus.NEW
    ease_factor: float = 2.5
    interval: int = 0
    repetitions: int = 0
    next_review: Optional[str] = None
    last_study: Optional[str] = None
    study_count: int = 0
    correct_count: int = 0
    incorrect_count: int = 0
    
    def to_dict(self) -> dict:
        return {
            'word': self.word,
            'status': self.status.value,
            'ease_factor': self.ease_factor,
            'interval': self.interval,
            'repetitions': self.repetitions,
            'next_review': self.next_review,
            'last_study': self.last_study,
            'study_count': self.study_count,
            'correct_count': self.correct_count,
            'incorrect_count': self.incorrect_count,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'WordProgress':
        return cls(
            word=data['word'],
            status=WordStatus(data.get('status', 'new')),
            ease_factor=data.get('ease_factor', 2.5),
            interval=data.get('interval', 0),
            repetitions=data.get('repetitions', 0),
            next_review=data.get('next_review'),
            last_study=data.get('last_study'),
            study_count=data.get('study_count', 0),
            correct_count=data.get('correct_count', 0),
            incorrect_count=data.get('incorrect_count', 0),
        )


@dataclass
class UserProgress:
    """用户整体学习进度"""
    word_progress: Dict[str, WordProgress] = field(default_factory=dict)
    favorites: set = field(default_factory=set)
    daily_stats: dict = field(default_factory=dict)
    
    def get_progress(self, word: str) -> WordProgress:
        """获取或创建单词进度"""
        if word not in self.word_progress:
            self.word_progress[word] = WordProgress(word=word)
        return self.word_progress[word]
    
    def get_statistics(self) -> dict:
        """获取学习统计"""
        stats = {
            'total_words': 0,
            'new_words': 0,
            'learning': 0,
            'review': 0,
            'mastered': 0,
            'today_learned': 0,
            'today_reviewed': 0,
        }
        
        today = date.today().isoformat()
        
        for progress in self.word_progress.values():
            stats['total_words'] += 1
            if progress.status == WordStatus.NEW:
                stats['new_words'] += 1
            elif progress.status == WordStatus.LEARNING:
                stats['learning'] += 1
            elif progress.status == WordStatus.REVIEW:
                stats['review'] += 1
            elif progress.status == WordStatus.MASTERED:
                stats['mastered'] += 1
        
        if today in self.daily_stats:
            stats['today_learned'] = self.daily_stats[today].get('learned', 0)
            stats['today_reviewed'] = self.daily_stats[today].get('reviewed', 0)
        
        return stats
    
    def get_new_words(self, all_words: List[str], limit: int = 10) -> List[str]:
        """获取待学习的新单词"""
        new_words = []
        for word in all_words:
            if word not in self.word_progress or self.word_progress[word].status == WordStatus.NEW:
                new_words.append(word)
            if len(new_words) >= limit:
                break
        return new_words
    
    def get_due_words(self, limit: int = 50) -> List[str]:
        """获取今天需要复习的单词"""
        today = date.today().isoformat()
        due = []
        
        for word, progress in self.word_progress.items():
            if progress.status in [WordStatus.LEARNING, WordStatus.REVIEW]:
                if progress.next_review and progress.next_review <= today:
                    due.append(word)
        
        # 按复习日期排序
        due.sort(key=lambda w: self.word_progress[w].next_review or '')
        return due[:limit]
    
    def get_mastered_words(self) -> List[str]:
        """获取已掌握的单词"""
        return [w for w, p in self.word_progress.items() if p.status == WordStatus.MASTERED]
    
    def is_favorited(self, word: str) -> bool:
        """检查是否收藏"""
        return word in self.favorites
    
    def toggle_favorite(self, word: str):
        """切换收藏状态"""
        if word in self.favorites:
            self.favorites.remove(word)
        else:
            self.favorites.add(word)
    
    def record_daily_stat(self, learned: int = 0, reviewed: int = 0):
        """记录每日统计"""
        today = date.today().isoformat()
        if today not in self.daily_stats:
            self.daily_stats[today] = {'learned': 0, 'reviewed': 0}
        
        self.daily_stats[today]['learned'] += learned
        self.daily_stats[today]['reviewed'] += reviewed
    
    def get_streak_days(self) -> int:
        """获取连续学习天数"""
        if not self.daily_stats:
            return 0
        
        sorted_dates = sorted(self.daily_stats.keys(), reverse=True)
        streak = 0
        current = date.today()
        
        for date_str in sorted_dates:
            d = date.fromisoformat(date_str)
            diff = (current - d).days
            
            if diff == streak:
                streak += 1
            elif diff > streak:
                break
        
        return streak
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'word_progress': {w: p.to_dict() for w, p in self.word_progress.items()},
            'favorites': list(self.favorites),
            'daily_stats': self.daily_stats
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'UserProgress':
        """从字典创建"""
        progress = cls()
        
        if 'word_progress' in data:
            for word, p_data in data['word_progress'].items():
                progress.word_progress[word] = WordProgress.from_dict(p_data)
        
        if 'favorites' in data:
            progress.favorites = set(data['favorites'])
        
        if 'daily_stats' in data:
            progress.daily_stats = data['daily_stats']
        
        return progress
