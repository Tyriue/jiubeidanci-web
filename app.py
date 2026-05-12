# -*- coding: utf-8 -*-
"""
就背单词 - Streamlit Web 版
基于间隔重复算法(SM-2)的单词记忆应用
"""

import os
import random
import streamlit as st
from pathlib import Path

from models.word import WordLoader
from models.user_progress import UserProgress, WordStatus
from models.spaced_repetition import SpacedRepetition
from models.database import Database

# ============== 页面配置 ==============
st.set_page_config(
    page_title="就背单词",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============== 样式 ==============
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem !important;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
    }
    .word-card {
        background: #f0f2f6;
        padding: 2rem;
        border-radius: 15px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
    }
    .word-title {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .word-text {
        font-size: 1.1rem;
        color: #333;
        line-height: 1.8;
    }
    .streak-badge {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ============== 初始化 ==============
@st.cache_resource
def init_data():
    """初始化数据"""
    # 查找词书文件
    possible_paths = [
        os.path.join(os.path.dirname(__file__), "word-list.yaml"),
        os.path.join(os.path.dirname(__file__), "..", "就背单词-v1", "word-list.yaml"),
        "word-list.yaml",
        r"d:\program\A_Tyriue_program\就背单词-v1\word-list.yaml",
    ]
    
    word_list_path = None
    for path in possible_paths:
        if os.path.exists(path):
            word_list_path = path
            break
    
    # 加载单词
    if word_list_path:
        loader = WordLoader(word_list_path)
        words = loader.load()
    else:
        words = []
    
    # 初始化数据库
    db_path = os.path.join(os.path.dirname(__file__), "data", "progress.json")
    db = Database(db_path)
    
    return words, db

# 初始化 session state
if 'initialized' not in st.session_state:
    words, db = init_data()
    st.session_state.words = words
    st.session_state.db = db
    st.session_state.progress = db.load_progress()
    st.session_state.current_word = None
    st.session_state.show_answer = False
    st.session_state.initialized = True

words = st.session_state.words
progress = st.session_state.progress
db = st.session_state.db

# ============== 侧边栏导航 ==============
st.sidebar.markdown("## 📚 就背单词")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "选择功能",
    ["🏠 首页", "📝 学习模式", "🔄 复习模式", "📖 词书浏览", "⚙️ 设置"]
)

# ============== 保存进度函数 ==============
def save_progress():
    """保存学习进度"""
    db.save_progress(progress)
    st.session_state.progress = progress

# ============== 首页 ==============
if page == "🏠 首页":
    st.markdown('<p class="main-header">📚 就背单词</p>', unsafe_allow_html=True)
    st.markdown("基于间隔重复算法(SM-2)的智能单词记忆系统")
    
    # 统计卡片
    stats = progress.get_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{stats['total_words']}</div>
            <div>已学习</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
            <div class="stat-number">{stats['mastered']}</div>
            <div>已掌握</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        today_due = len(progress.get_due_words())
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #fc4a1a 0%, #f7b733 100%);">
            <div class="stat-number">{today_due}</div>
            <div>待复习</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        streak = progress.get_streak_days()
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <div class="stat-number">{streak}</div>
            <div>连续天数</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 今日进度
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 学习状态分布")
        labels = ['新词', '学习中', '待复习', '已掌握']
        values = [stats['new_words'], stats['learning'], stats['review'], stats['mastered']]
        
        import plotly.graph_objects as go
        colors = ['#ff9999', '#66b3ff', '#ffcc99', '#99ff99']
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3, marker_colors=colors)])
        fig.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📅 今日任务")
        st.markdown(f"""
        - 📝 今日新学: **{stats['today_learned']}** 词
        - 🔄 今日复习: **{stats['today_reviewed']}** 词
        - 📌 待复习: **{today_due}** 词
        """)
        
        # 快速操作按钮
        if today_due > 0:
            if st.button("🔄 开始复习", type="primary", use_container_width=True):
                st.switch_page(page="🔄 复习模式")
        
        new_count = len(progress.get_new_words([w.word for w in words], limit=9999))
        if new_count > 0:
            if st.button("📝 开始学习", type="primary", use_container_width=True):
                st.switch_page(page="📝 学习模式")
    
    # 学习日历
    st.markdown("---")
    st.subheader("📅 学习日历")
    if progress.daily_stats:
        dates = sorted(progress.daily_stats.keys())[-30:]  # 最近30天
        chart_data = {
            '日期': dates,
            '学习': [progress.daily_stats[d].get('learned', 0) for d in dates],
            '复习': [progress.daily_stats[d].get('reviewed', 0) for d in dates]
        }
        
        import pandas as pd
        df = pd.DataFrame(chart_data)
        st.bar_chart(df.set_index('日期'), use_container_width=True)
    else:
        st.info("还没有学习记录，开始你的第一次学习吧！")

# ============== 学习模式 ==============
elif page == "📝 学习模式":
    st.markdown('<p class="main-header">📝 学习模式</p>', unsafe_allow_html=True)
    
    if not words:
        st.error("词书加载失败，请检查 word-list.yaml 文件是否存在")
    else:
        all_word_keys = [w.word for w in words]
        new_words = progress.get_new_words(all_word_keys, limit=20)
        
        if not new_words:
            st.success("🎉 太棒了！你已经学完了所有新单词！")
            st.info("可以去复习模式巩固记忆，或者重置进度重新学习。")
        else:
            st.info(f"📌 今日还有 **{len(new_words)}** 个新单词待学习")
            
            # 选择单词
            if 'study_index' not in st.session_state:
                st.session_state.study_index = 0
            
            idx = st.session_state.study_index
            
            if idx < len(new_words):
                current_word_key = new_words[idx]
                word_obj = next((w for w in words if w.word == current_word_key), None)
                
                if word_obj:
                    # 进度条
                    progress_pct = (idx + 1) / len(new_words)
                    st.progress(progress_pct)
                    st.caption(f"进度: {idx + 1} / {len(new_words)}")
                    
                    # 单词卡片
                    st.markdown(f"""
                    <div class="word-card">
                        <div class="word-title">{word_obj.title}</div>
                        <div class="word-text">{word_obj.text}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 操作按钮
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("❌ 不认识", use_container_width=True):
                            wp = progress.get_progress(current_word_key)
                            wp.status = WordStatus.LEARNING
                            wp.study_count += 1
                            wp.incorrect_count += 1
                            progress.record_daily_stat(learned=1)
                            save_progress()
                            st.session_state.study_index = idx + 1
                            st.rerun()
                    
                    with col2:
                        if st.button("✅ 认识", use_container_width=True):
                            wp = progress.get_progress(current_word_key)
                            wp.status = WordStatus.REVIEW
                            wp.study_count += 1
                            wp.correct_count += 1
                            wp.next_review = "today"
                            SpacedRepetition.update(wp, 3)
                            progress.record_daily_stat(learned=1)
                            save_progress()
                            st.session_state.study_index = idx + 1
                            st.rerun()
            else:
                st.success("🎉 本轮学习完成！")
                if st.button("🔄 再来一轮"):
                    st.session_state.study_index = 0
                    st.rerun()

# ============== 复习模式 ==============
elif page == "🔄 复习模式":
    st.markdown('<p class="main-header">🔄 复习模式</p>', unsafe_allow_html=True)
    
    if not words:
        st.error("词书加载失败，请检查 word-list.yaml 文件是否存在")
    else:
        due_words = progress.get_due_words(limit=50)
        
        if not due_words:
            st.success("🎉 今天没有需要复习的单词！")
            st.info("去学习模式学习新单词吧！")
        else:
            st.info(f"📌 今日有 **{len(due_words)}** 个单词需要复习")
            
            if 'review_index' not in st.session_state:
                st.session_state.review_index = 0
                st.session_state.show_answer = False
            
            idx = st.session_state.review_index
            
            if idx < len(due_words):
                current_word_key = due_words[idx]
                word_obj = next((w for w in words if w.word == current_word_key), None)
                wp = progress.get_progress(current_word_key)
                
                if word_obj:
                    # 进度条
                    progress_pct = (idx + 1) / len(due_words)
                    st.progress(progress_pct)
                    st.caption(f"进度: {idx + 1} / {len(due_words)}")
                    
                    # 状态标签
                    status_color = {
                        WordStatus.NEW: "🔵",
                        WordStatus.LEARNING: "🟡",
                        WordStatus.REVIEW: "🟠",
                        WordStatus.MASTERED: "🟢"
                    }.get(wp.status, "⚪")
                    st.caption(f"状态: {status_color} {wp.status.value} | 复习次数: {wp.repetitions} | 间隔: {wp.interval}天")
                    
                    # 单词卡片（先只显示单词）
                    st.markdown(f"""
                    <div class="word-card">
                        <div class="word-title">{word_obj.title}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if not st.session_state.show_answer:
                        if st.button("👀 显示释义", use_container_width=True, type="primary"):
                            st.session_state.show_answer = True
                            st.rerun()
                    else:
                        # 显示答案
                        st.markdown(f"""
                        <div class="word-card" style="border-left-color: #28a745;">
                            <div class="word-text">{word_obj.text}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # 评分按钮
                        st.markdown("#### 你对这个单词的掌握程度？")
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            if st.button("❌ 忘记", use_container_width=True):
                                quality = SpacedRepetition.get_quality_from_answer(False)
                                SpacedRepetition.update(wp, quality)
                                wp.incorrect_count += 1
                                progress.record_daily_stat(reviewed=1)
                                
                                if wp.status == WordStatus.MASTERED:
                                    wp.status = WordStatus.LEARNING
                                
                                save_progress()
                                st.session_state.show_answer = False
                                st.session_state.review_index = idx + 1
                                st.rerun()
                        
                        with col2:
                            if st.button("🤔 困难", use_container_width=True):
                                quality = SpacedRepetition.get_quality_from_answer(True, False)
                                SpacedRepetition.update(wp, quality)
                                progress.record_daily_stat(reviewed=1)
                                
                                if wp.status == WordStatus.NEW:
                                    wp.status = WordStatus.LEARNING
                                elif wp.status == WordStatus.MASTERED:
                                    wp.status = WordStatus.REVIEW
                                
                                save_progress()
                                st.session_state.show_answer = False
                                st.session_state.review_index = idx + 1
                                st.rerun()
                        
                        with col3:
                            if st.button("👌 还行", use_container_width=True):
                                quality = SpacedRepetition.get_quality_from_answer(True, False)
                                SpacedRepetition.update(wp, quality)
                                progress.record_daily_stat(reviewed=1)
                                
                                if wp.status == WordStatus.NEW:
                                    wp.status = WordStatus.REVIEW
                                
                                save_progress()
                                st.session_state.show_answer = False
                                st.session_state.review_index = idx + 1
                                st.rerun()
                        
                        with col4:
                            if st.button("✅ 简单", use_container_width=True):
                                quality = SpacedRepetition.get_quality_from_answer(True, True)
                                SpacedRepetition.update(wp, quality)
                                progress.record_daily_stat(reviewed=1)
                                
                                if wp.repetitions >= 3:
                                    wp.status = WordStatus.MASTERED
                                else:
                                    if wp.status == WordStatus.NEW:
                                        wp.status = WordStatus.REVIEW
                                
                                save_progress()
                                st.session_state.show_answer = False
                                st.session_state.review_index = idx + 1
                                st.rerun()
            else:
                st.success("🎉 本轮复习完成！")
                if st.button("🔄 再来一轮"):
                    st.session_state.review_index = 0
                    st.session_state.show_answer = False
                    st.rerun()

# ============== 词书浏览 ==============
elif page == "📖 词书浏览":
    st.markdown('<p class="main-header">📖 词书浏览</p>', unsafe_allow_html=True)
    
    if not words:
        st.error("词书加载失败，请检查 word-list.yaml 文件是否存在")
    else:
        # 搜索框
        search = st.text_input("🔍 搜索单词", placeholder="输入单词或中文释义...")
        
        # 筛选
        filter_status = st.selectbox(
            "筛选状态",
            ["全部", "新词", "学习中", "待复习", "已掌握", "收藏"]
        )
        
        # 过滤单词
        filtered_words = words
        
        if search:
            search_lower = search.lower()
            filtered_words = [w for w in words if search_lower in w.word.lower() or search_lower in w.title.lower()]
        
        if filter_status == "新词":
            filtered_words = [w for w in filtered_words if progress.get_progress(w.word).status == WordStatus.NEW]
        elif filter_status == "学习中":
            filtered_words = [w for w in filtered_words if progress.get_progress(w.word).status == WordStatus.LEARNING]
        elif filter_status == "待复习":
            filtered_words = [w for w in filtered_words if progress.get_progress(w.word).status == WordStatus.REVIEW]
        elif filter_status == "已掌握":
            filtered_words = [w for w in filtered_words if progress.get_progress(w.word).status == WordStatus.MASTERED]
        elif filter_status == "收藏":
            filtered_words = [w for w in filtered_words if progress.is_favorited(w.word)]
        
        st.caption(f"共 {len(filtered_words)} 个单词")
        
        # 显示单词列表
        for word_obj in filtered_words:
            wp = progress.get_progress(word_obj.word)
            status_emoji = {
                WordStatus.NEW: "🔵",
                WordStatus.LEARNING: "🟡",
                WordStatus.REVIEW: "🟠",
                WordStatus.MASTERED: "🟢"
            }.get(wp.status, "⚪")
            
            with st.expander(f"{status_emoji} {word_obj.title}"):
                st.markdown(f"**单词**: {word_obj.word}")
                st.markdown(f"**释义**: {word_obj.text}")
                st.markdown(f"**状态**: {wp.status.value}")
                st.markdown(f"**复习次数**: {wp.repetitions} | **间隔**: {wp.interval}天")
                
                # 收藏按钮
                fav_emoji = "⭐" if progress.is_favorited(word_obj.word) else "☆"
                if st.button(f"{fav_emoji} 收藏", key=f"fav_{word_obj.word}"):
                    progress.toggle_favorite(word_obj.word)
                    save_progress()
                    st.rerun()

# ============== 设置页面 ==============
elif page == "⚙️ 设置":
    st.markdown('<p class="main-header">⚙️ 设置</p>', unsafe_allow_html=True)
    
    st.subheader("🔄 数据管理")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 手动保存进度", use_container_width=True):
            if save_progress():
                st.success("进度已保存！")
    
    with col2:
        if st.button("🗑️ 重置所有进度", use_container_width=True, type="secondary"):
            st.warning("⚠️ 确定要重置所有学习进度吗？此操作不可恢复！")
            if st.button("确认重置", type="primary", key="confirm_reset"):
                db.clear_progress()
                st.session_state.progress = UserProgress()
                st.success("进度已重置！")
                st.rerun()
    
    st.markdown("---")
    st.subheader("📊 统计数据")
    
    stats = progress.get_statistics()
    st.markdown(f"""
    - 📚 总学习单词: **{stats['total_words']}**
    - 🔵 新词: **{stats['new_words']}**
    - 🟡 学习中: **{stats['learning']}**
    - 🟠 待复习: **{stats['review']}**
    - 🟢 已掌握: **{stats['mastered']}**
    - ⭐ 收藏: **{len(progress.favorites)}**
    - 🔥 连续学习: **{progress.get_streak_days()}** 天
    """)
    
    st.markdown("---")
    st.subheader("ℹ️ 关于")
    st.markdown("""
    **就背单词 Web 版**
    
    基于间隔重复算法(SM-2)的智能单词记忆系统。
    
    功能特点：
    - 🧠 智能复习调度
    - 📊 学习进度追踪
    - 📅 连续学习记录
    - ⭐ 单词收藏
    
    *注意：在线部署时数据可能因会话结束而重置，建议定期导出备份。*
    """)
