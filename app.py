import json
import re
from collections import Counter
from itertools import islice
from typing import List, Tuple

import pandas as pd
import streamlit as st

st.set_page_config(page_title="文本分析器", page_icon="📝", layout="wide")

st.title("📝 文本分析器")
st.write("支持文本清洗、词频分析、句子分析、N-gram 和结果导出。")

DEFAULT_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "but",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "was",
    "were",
    "will",
    "with",
    "你",
    "我",
    "我们",
    "的",
    "了",
    "是",
    "在",
    "和",
    "有",
    "也",
    "就",
    "不",
    "要",
    "一个",
    "这个",
    "那个",
    "这样",
    "那样",
    "可以",
    "吗",
    "吗",
}


@st.cache_data(show_spinner=False)
def analyze_text(
    raw_text: str,
    lower_case: bool,
    remove_numbers: bool,
    remove_urls: bool,
    remove_emails: bool,
    remove_punctuation: bool,
    use_stopwords: bool,
    min_word_length: int,
    top_n: int,
    ngram_size: int,
) -> dict:
    if not raw_text or not raw_text.strip():
        return {
            "cleaned_text": "",
            "characters": 0,
            "characters_no_space": 0,
            "lines": 0,
            "paragraphs": 0,
            "words": 0,
            "unique_words": 0,
            "sentences": 0,
            "average_word_length": 0.0,
            "average_sentence_length": 0.0,
            "longest_sentence": "",
            "top_words": [],
            "repeat_words": [],
            "ngrams": [],
            "word_list": [],
        }

    text = raw_text.strip()
    if remove_urls:
        text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    if remove_emails:
        text = re.sub(r"\S+@\S+", " ", text)
    if remove_punctuation:
        text = re.sub(r"[^\w\s\u4e00-\u9fff]", " ", text)
    if remove_numbers:
        text = re.sub(r"\d+", " ", text)
    if lower_case:
        text = text.lower()

    text = re.sub(r"\s+", " ", text).strip()

    characters = len(raw_text)
    characters_no_space = len(re.sub(r"\s+", "", raw_text))
    lines = len(raw_text.splitlines())
    paragraphs = len([p for p in re.split(r"\n\s*\n", raw_text.strip()) if p.strip()])

    sentences = [s.strip() for s in re.split(r"(?<=[。！？.!?])\s+|(?<=\n)", raw_text) if s.strip()]
    word_pattern = re.compile(r"[A-Za-z0-9\u4e00-\u9fff]+")
    words = [token for token in word_pattern.findall(text)]

    if use_stopwords:
        words = [w for w in words if w not in DEFAULT_STOPWORDS and len(w) >= min_word_length]
    else:
        words = [w for w in words if len(w) >= min_word_length]

    if words:
        word_counter = Counter(words)
        top_words = word_counter.most_common(top_n)
        repeat_words = [(word, count) for word, count in word_counter.items() if count > 1]
        average_word_length = round(sum(len(w) for w in words) / len(words), 2)
        average_sentence_length = round(len(words) / len(sentences), 2) if sentences else 0.0
        longest_sentence = max(sentences, key=lambda s: len(s), default="")
    else:
        word_counter = Counter()
        top_words = []
        repeat_words = []
        average_word_length = 0.0
        average_sentence_length = 0.0
        longest_sentence = ""

    ngrams: List[Tuple[str, ...]] = []
    if words and ngram_size > 1:
        ngrams = [tuple(gram) for gram in [words[i : i + ngram_size] for i in range(len(words) - ngram_size + 1)]]
        ngram_counter = Counter(ngrams)
        ngrams = [((" ".join(g), count)) for g, count in ngram_counter.most_common(top_n)]

    return {
        "cleaned_text": text,
        "characters": characters,
        "characters_no_space": characters_no_space,
        "lines": lines,
        "paragraphs": paragraphs,
        "words": len(words),
        "unique_words": len(word_counter),
        "sentences": len(sentences),
        "average_word_length": average_word_length,
        "average_sentence_length": average_sentence_length,
        "longest_sentence": longest_sentence,
        "top_words": top_words,
        "repeat_words": repeat_words,
        "ngrams": ngrams,
        "word_list": sorted(word_counter.keys()),
    }


uploaded_file = st.file_uploader("上传文本文件（.txt/.md/.csv）", type=["txt", "md", "csv"])
text = ""
if uploaded_file is not None:
    if uploaded_file.name.endswith(".csv"):
        try:
            df = pd.read_csv(uploaded_file)
            text = "\n".join(df.astype(str).stack().astype(str).tolist())
        except Exception:
            st.warning("CSV 解析失败，已改为读取文件原始内容。")
            text = uploaded_file.getvalue().decode("utf-8", errors="ignore")
    else:
        text = uploaded_file.getvalue().decode("utf-8", errors="ignore")

text = st.text_area(
    "输入文本",
    value=text,
    height=220,
    placeholder="在这里粘贴一段中文或英文文本…",
)

with st.sidebar:
    st.header("分析设置")
    lower_case = st.checkbox("统一转为小写", value=True)
    remove_numbers = st.checkbox("去除数字", value=True)
    remove_urls = st.checkbox("去除 URL", value=True)
    remove_emails = st.checkbox("去除邮箱", value=True)
    remove_punctuation = st.checkbox("去除标点符号", value=True)
    use_stopwords = st.checkbox("去除停用词", value=True)
    min_word_length = st.slider("最小词长", 1, 5, 1)
    top_n = st.slider("Top 词数量", 5, 30, 10)
    ngram_size = st.slider("N-gram 长度", 1, 4, 2)

if text:
    analysis = analyze_text(
        text,
        lower_case=lower_case,
        remove_numbers=remove_numbers,
        remove_urls=remove_urls,
        remove_emails=remove_emails,
        remove_punctuation=remove_punctuation,
        use_stopwords=use_stopwords,
        min_word_length=min_word_length,
        top_n=top_n,
        ngram_size=ngram_size,
    )

    tab1, tab2, tab3 = st.tabs(["分析结果", "清洗后文本", "导出结果"])

    with tab1:
        st.subheader("统计结果")
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("字符数", analysis["characters"])
        c2.metric("去空格字符数", analysis["characters_no_space"])
        c3.metric("单词数", analysis["words"])
        c4.metric("唯一词数", analysis["unique_words"])
        c5.metric("句子数", analysis["sentences"])
        c6.metric("段落数", analysis["paragraphs"])

        st.caption(
            f"平均词长：{analysis['average_word_length']}；平均句长：{analysis['average_sentence_length']}"
        )
        if analysis["longest_sentence"]:
            st.write(f"最长句子：{analysis['longest_sentence']}")

        st.subheader("关键词 Top")
        if analysis["top_words"]:
            top_df = pd.DataFrame(analysis["top_words"], columns=["词", "频次"])
            st.dataframe(top_df, use_container_width=True)
            st.bar_chart(top_df.set_index("词"))
        else:
            st.info("没有提取到关键词。")

        st.subheader("重复词")
        if analysis["repeat_words"]:
            repeat_df = pd.DataFrame(analysis["repeat_words"], columns=["词", "出现次数"])
            st.dataframe(repeat_df, use_container_width=True)
        else:
            st.info("没有重复词。")

        st.subheader("N-gram")
        if analysis["ngrams"]:
            ngram_df = pd.DataFrame(analysis["ngrams"], columns=["短语", "频次"])
            st.dataframe(ngram_df, use_container_width=True)
        else:
            st.info("没有可展示的 N-gram。")

    with tab2:
        st.subheader("清洗后文本")
        st.text_area("处理后的文本", value=analysis["cleaned_text"], height=260)
        st.subheader("词表")
        if analysis["word_list"]:
            st.write(", ".join(analysis["word_list"]))
        else:
            st.info("没有可显示的词表。")

    with tab3:
        st.subheader("导出结果")
        top_df = pd.DataFrame(analysis["top_words"], columns=["词", "频次"])
        repeat_df = pd.DataFrame(analysis["repeat_words"], columns=["词", "出现次数"])
        ngram_df = pd.DataFrame(analysis["ngrams"], columns=["短语", "频次"])

        csv_bytes = top_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="下载词频 CSV",
            data=csv_bytes,
            file_name="word_frequency.csv",
            mime="text/csv",
        )

        json_bytes = json.dumps(analysis, ensure_ascii=False, indent=2).encode("utf-8")
        st.download_button(
            label="下载完整 JSON",
            data=json_bytes,
            file_name="text_analysis.json",
            mime="application/json",
        )

else:
    st.info("请输入文本或上传文件后开始分析。")
