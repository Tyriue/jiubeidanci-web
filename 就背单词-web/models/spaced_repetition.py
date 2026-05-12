# -*- coding: utf-8 -*-
"""
间隔重复算法 (SM-2)
"""

from datetime import date, timedelta


class SpacedRepetition:
    """基于SM-2算法的间隔重复系统"""
    
    MIN_EF = 1.3
    DEFAULT_EF = 2.5
    
    @classmethod
    def update(cls, progress, quality: int):
        """更新学习进度
        
        Args:
            progress: WordProgress 对象
            quality: 0-5 的评分，表示回忆质量
                    0-1: 完全忘记
                    2: 想起但困难
                    3: 经过努力想起
                    4: 容易想起
                    5: 完美回答
        """
        if quality < 0 or quality > 5:
            quality = max(0, min(5, quality))
        
        old_ef = progress.ease_factor
        old_interval = progress.interval
        old_repetitions = progress.repetitions
        
        # 更新简易度因子
        new_ef = old_ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        new_ef = max(cls.MIN_EF, new_ef)
        progress.ease_factor = round(new_ef, 2)
        
        # 计算新的间隔
        if quality < 3:
            # 如果回忆失败，重置重复次数
            progress.repetitions = 0
            progress.interval = 1
        else:
            # 回忆成功
            progress.repetitions += 1
            
            if progress.repetitions == 1:
                progress.interval = 1
            elif progress.repetitions == 2:
                progress.interval = 6
            else:
                progress.interval = round(old_interval * new_ef)
        
        # 更新下次复习日期
        today = date.today()
        progress.next_review = (today + timedelta(days=progress.interval)).isoformat()
        progress.last_study = today.isoformat()
    
    @classmethod
    def get_quality_from_answer(cls, known: bool, easy: bool = False) -> int:
        """根据用户回答转换为质量评分"""
        if not known:
            return 1  # 完全忘记
        if easy:
            return 5  # 完美回答
        return 3  # 经过努力想起
