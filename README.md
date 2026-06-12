# 文本分析器 Pro

这是一个功能更丰富的基于 Streamlit 的文本分析 Web 应用，支持：

- 文本上传（.txt / .md / .csv）
- 文本清洗与预处理
- 统计字符数、去空格字符数、单词数、唯一词数、句子数、段落数
- 平均词长、平均句长、最长句子分析
- 关键词 Top N 统计
- 重复词分析
- N-gram 统计
- 文本摘要生成
- 情绪倾向分析
- 可读性分数分析
- 字符频次与词长分布
- 重复句子检测
- Hapax Legomena 罕见词分析
- 正则搜索与匹配结果展示
- 结果导出为 CSV / JSON

## 本地运行

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 部署到 Streamlit Cloud

1. 将这个项目推送到 GitHub 或 Gitee 公共仓库。
2. 登录 Streamlit Cloud。
3. 新建应用，选择对应仓库和分支。
4. 主文件路径填写 `app.py`。
5. 等待构建完成后即可访问公开链接。
