import json
import re
from collections import Counter
from typing import List, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from wordcloud import WordCloud

st.set_page_config(page_title="文本分析器", page_icon="📝", layout="wide")

st.title("📝 文本分析器 Pro")
st.write("一站式文本分析工具箱：清洗、统计、摘要、情绪、可读性、重复检测、正则搜索和导出。")

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
}

POSITIVE_WORDS = {
    "good",
    "great",
    "excellent",
    "nice",
    "happy",
    "love",
    "best",
    "better",
    "improve",
    "improved",
    "success",
    "thanks",
    "thank",
    "beautiful",
    "useful",
    "easy",
    "清楚",
    "优秀",
    "好",
    "开心",
    "喜欢",
    "满意",
    "高效",
    "强大",
    "完美",
}
NEGATIVE_WORDS = {
    "bad",
    "terrible",
    "worse",
    "worst",
    "sad",
    "hate",
    "problem",
    "issue",
    "bug",
    "slow",
    "hard",
    "difficult",
    "poor",
    "broken",
    "失败",
    "差",
    "糟糕",
    "问题",
    "麻烦",
    "困难",
    "慢",
    "糟",
    "痛苦",
    "烦人",
}


def estimate_syllables(word: str) -> int:
    word = word.lower()
    if not word:
        return 0
    vowels = "aeiou"
    count = 0
    prev_vowel = False
    for ch in word:
        is_vowel = ch in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    if word.endswith(("e", "es", "ed")) and count > 1:
        count -= 1
    return max(1, count)


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
    summary_sentences: int,
    regex_pattern: str,
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
            "char_frequency": [],
            "word_length_distribution": [],
            "duplicate_sentences": [],
            "summary": [],
            "sentiment": "neutral",
            "sentiment_score": 0,
            "readability": 0.0,
            "type_token_ratio": 0.0,
            "hapax_legomena": [],
            "regex_matches": [],
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

    sentence_split_pattern = re.compile(r"(?<=[。！？.!?])\s+|(?<=\n)")
    sentences = [s.strip() for s in sentence_split_pattern.split(raw_text) if s.strip()]
    word_pattern = re.compile(r"[A-Za-z0-9\u4e00-\u9fff]+")
    words = [token for token in word_pattern.findall(text)]

    if use_stopwords:
        words = [w for w in words if w not in DEFAULT_STOPWORDS and len(w) >= min_word_length]
    else:
        words = [w for w in words if len(w) >= min_word_length]

    word_counter = Counter(words)
    top_words = word_counter.most_common(top_n)
    repeat_words = [(word, count) for word, count in word_counter.items() if count > 1]
    average_word_length = round(sum(len(w) for w in words) / len(words), 2) if words else 0.0
    average_sentence_length = round(len(words) / len(sentences), 2) if sentences else 0.0
    longest_sentence = max(sentences, key=lambda s: len(s), default="")
    char_counter = Counter(text)
    char_frequency = [(ch, count) for ch, count in char_counter.most_common(30)]
    word_length_distribution = [(length, count) for length, count in Counter(len(w) for w in words).most_common()]

    sentence_counts = Counter(sentences)
    duplicate_sentences = [(sentence, count) for sentence, count in sentence_counts.items() if count > 1]

    if words:
        type_token_ratio = round(len(word_counter) / len(words), 3)
        hapax_legomena = [(word, count) for word, count in word_counter.items() if count == 1]
    else:
        type_token_ratio = 0.0
        hapax_legomena = []

    sentiment_score = 0
    for word in words:
        if word in POSITIVE_WORDS:
            sentiment_score += 1
        if word in NEGATIVE_WORDS:
            sentiment_score -= 1
    if sentiment_score > 0:
        sentiment = "positive"
    elif sentiment_score < 0:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    if words and sentences:
        syllables = sum(estimate_syllables(w) for w in words)
        readability = round(206.835 - 1.015 * (len(words) / len(sentences)) - 84.6 * (syllables / len(words)), 2)
    else:
        readability = 0.0

    summary_candidates = []
    if sentences:
        sentence_scores = []
        for sentence in sentences:
            sent_tokens = [t for t in word_pattern.findall(sentence.lower()) if t not in DEFAULT_STOPWORDS]
            score = sum(word_counter.get(token, 0) for token in sent_tokens)
            sentence_scores.append((score, sentence))
        summary_candidates = [s for _, s in sorted(sentence_scores, key=lambda item: item[0], reverse=True)[:summary_sentences]]

    ngrams: List[Tuple[str, ...]] = []
    if words and ngram_size > 1:
        ngram_counter = Counter(tuple(words[i : i + ngram_size]) for i in range(len(words) - ngram_size + 1))
        ngrams = [(" ".join(g), count) for g, count in ngram_counter.most_common(top_n)]

    regex_matches = []
    if regex_pattern:
        try:
            for match in re.finditer(regex_pattern, raw_text, flags=re.IGNORECASE):
                regex_matches.append(
                    {
                        "match": match.group(0),
                        "start": match.start(),
                        "end": match.end(),
                    }
                )
        except re.error:
            regex_matches = []

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
        "char_frequency": char_frequency,
        "word_length_distribution": word_length_distribution,
        "duplicate_sentences": duplicate_sentences,
        "summary": summary_candidates,
        "sentiment": sentiment,
        "sentiment_score": sentiment_score,
        "readability": readability,
        "type_token_ratio": type_token_ratio,
        "hapax_legomena": hapax_legomena,
        "regex_matches": regex_matches,
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
    summary_sentences = st.slider("摘要句子数", 1, 5, 3)
    regex_pattern = st.text_input("正则搜索模式", value="")

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
        summary_sentences=summary_sentences,
        regex_pattern=regex_pattern,
    )

    tab1, tab2, tab3, tab4 = st.tabs(["综合分析", "清洗后文本", "高级指标", "导出结果"])

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

        st.subheader("摘要")
        if analysis["summary"]:
            for idx, sentence in enumerate(analysis["summary"], 1):
                st.write(f"{idx}. {sentence}")
        else:
            st.info("没有可生成的摘要。")

        st.subheader("关键词 Top")
        if analysis["top_words"]:
            top_df = pd.DataFrame(analysis["top_words"], columns=["词", "频次"])
            st.dataframe(top_df, use_container_width=True)
            st.bar_chart(top_df.set_index("词"))

            st.subheader("词云图")
            word_freq = dict(analysis["top_words"])
            if word_freq:
                wc = WordCloud(width=900, height=500, background_color="white", collocations=False)
                cloud = wc.generate_from_frequencies(word_freq)
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(cloud, interpolation="bilinear")
                ax.axis("off")
                st.pyplot(fig)
                plt.close(fig)
            else:
                st.info("没有可生成的词云。")
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
        st.subheader("高级指标")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("情绪倾向", analysis["sentiment"])
        c2.metric("情绪得分", analysis["sentiment_score"])
        c3.metric("可读性分数", round(analysis["readability"], 2))
        c4.metric("词汇丰富度", round(analysis["type_token_ratio"], 3))

        st.subheader("字符频次")
        if analysis["char_frequency"]:
            char_df = pd.DataFrame(analysis["char_frequency"], columns=["字符", "频次"])
            st.dataframe(char_df, use_container_width=True)
        else:
            st.info("没有可展示的字符频次。")

        st.subheader("词长分布")
        if analysis["word_length_distribution"]:
            length_df = pd.DataFrame(analysis["word_length_distribution"], columns=["长度", "频次"])
            st.dataframe(length_df, use_container_width=True)
        else:
            st.info("没有可展示的词长分布。")

        st.subheader("重复句子")
        if analysis["duplicate_sentences"]:
            dup_df = pd.DataFrame(analysis["duplicate_sentences"], columns=["句子", "次数"])
            st.dataframe(dup_df, use_container_width=True)
        else:
            st.info("没有重复句子。")

        st.subheader("Hapax Legomena")
        if analysis["hapax_legomena"]:
            hapax_df = pd.DataFrame(analysis["hapax_legomena"], columns=["词", "次数"])
            st.dataframe(hapax_df, use_container_width=True)
        else:
            st.info("没有罕见词。")

    with tab4:
        st.subheader("正则搜索")
        if analysis["regex_matches"]:
            regex_df = pd.DataFrame(analysis["regex_matches"])
            st.dataframe(regex_df, use_container_width=True)
        else:
            st.info("没有匹配结果。")

        st.subheader("导出结果")
        top_df = pd.DataFrame(analysis["top_words"], columns=["词", "频次"])
        repeat_df = pd.DataFrame(analysis["repeat_words"], columns=["词", "出现次数"])
        ngram_df = pd.DataFrame(analysis["ngrams"], columns=["短语", "频次"])
        char_df = pd.DataFrame(analysis["char_frequency"], columns=["字符", "频次"])
        length_df = pd.DataFrame(analysis["word_length_distribution"], columns=["长度", "频次"])

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
