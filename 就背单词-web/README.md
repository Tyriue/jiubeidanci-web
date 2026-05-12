# 就背单词 (Web版)

基于 Streamlit 的在线背单词应用，支持间隔重复（SM-2）算法，帮助用户高效记忆英语单词。

## 功能特性

- 每日学习：智能分配新单词进行学习
- 复习模式：基于 SM-2 间隔重复算法安排复习
- 词书浏览：查看完整词书内容和搜索
- 统计仪表盘：学习进度、连续天数、词汇量统计
- 进度持久化：自动保存学习记录到 JSON
- 响应式设计：支持桌面和移动端浏览器

## 技术栈

- **前端/UI**: Streamlit
- **算法**: SM-2 间隔重复算法
- **数据持久化**: JSON 文件
- **图表**: Plotly
- **词书格式**: YAML

## 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用
streamlit run app.py
```

应用将在 http://localhost:8501 运行。

## 部署到 Streamlit Cloud

1. 将代码推送到 GitHub 仓库
2. 访问 [share.streamlit.io](https://share.streamlit.io)
3. 连接 GitHub 仓库并部署
4. 确保 `word-list.yaml` 和 `requirements.txt` 在仓库根目录

## 项目结构

```
就背单词-web/
├── app.py                  # Streamlit 主应用
├── requirements.txt        # Python 依赖
├── word-list.yaml          # 词书数据
├── README.md               # 项目说明
└── models/
    ├── __init__.py
    ├── word.py             # 单词数据模型和加载器
    ├── spaced_repetition.py # SM-2 算法实现
    ├── user_progress.py    # 用户进度管理
    └── database.py         # JSON 持久化存储
```

## 算法说明

复习间隔计算基于 SM-2 算法：
- 根据用户回答质量（0-5分）调整下次复习时间
- 简单度因子（EF）动态调整，最低不低于 1.3
- 记忆效果越好，复习间隔越长

## 作者

用于展示 AI 应用开发能力的个人项目。
