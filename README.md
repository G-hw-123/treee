# 文本分析器

这是一个基于 Streamlit 的简单文本分析 Web 应用，支持：

- 统计字符数、单词数、句子数
- 计算平均单词长度
- 提取关键词 Top 10
- 展示重复词

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

