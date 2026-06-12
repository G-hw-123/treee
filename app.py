import re
from collections import Counter

import pandas as pd
import streamlit as st

st.set_page_config(page_title="文本分析器", page_icon="📝", layout="wide")

st.title("📝 文本分析器")
st.write("粘贴任意文本，快速查看词频、长度和关键统计信息。")

text = st.text_area(
    "输入文本",
    height=220,
    placeholder="在这里粘贴一段中文或英文文本…",
)


def analyze_text(raw_text: str) -> dict:
    if not raw_text or not raw_text.strip():
        return {
            "characters": 0,
            "characters_no_space": 0,
            "words": 0,
            "sentences": 0,
            "average_word_length": 0.0,
            "top_words": [],
            "repeat_words": [],
        }

    cleaned = raw_text.strip()
    characters = len(cleaned)
    characters_no_space = len(re.sub(r"\s+", "", cleaned))

    words = re.findall(r"[A-Za-z0-9\u4e00-\u9fff]+", cleaned.lower())
    sentences = [s for s in re.split(r"(?<=[。！？.!?])\s+", cleaned) if s.strip()]

    if words:
        average_word_length = round(sum(len(w) for w in words) / len(words), 2)
    else:
        average_word_length = 0.0

    word_counter = Counter(words)
    top_words = word_counter.most_common(10)
    repeat_words = [(word, count) for word, count in word_counter.items() if count > 1]

    return {
        "characters": characters,
        "characters_no_space": characters_no_space,
        "words": len(words),
        "sentences": len(sentences),
        "average_word_length": average_word_length,
        "top_words": top_words,
        "repeat_words": repeat_words,
    }


if text:
    analysis = analyze_text(text)
    st.subheader("统计结果")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("字符数", analysis["characters"])
    c2.metric("去空格字符数", analysis["characters_no_space"])
    c3.metric("单词数", analysis["words"])
    c4.metric("句子数", analysis["sentences"])

    st.caption(f"平均单词长度：{analysis['average_word_length']}")

    st.subheader("关键词 Top 10")
    if analysis["top_words"]:
        df = pd.DataFrame(analysis["top_words"], columns=["词", "频次"])
        st.dataframe(df, use_container_width=True)
        st.bar_chart(df.set_index("词"))
    else:
        st.info("没有提取到关键词。")

    st.subheader("重复词")
    if analysis["repeat_words"]:
        repeat_df = pd.DataFrame(analysis["repeat_words"], columns=["词", "出现次数"])
        st.dataframe(repeat_df, use_container_width=True)
    else:
        st.info("没有重复词。")

else:
    st.info("请输入文本后开始分析。")
