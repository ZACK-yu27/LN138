import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import jieba
import re
import os
import io
import time
from datetime import datetime
import numpy as np
from PIL import Image
from docx import Document

st.set_page_config(
    page_title="CloudWord Pro - 智能词云生成工具",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

FONT_PATH = os.path.join(os.path.dirname(__file__), "HGLS.TTF")

CHINESE_STOPWORDS = {
    '的', '了', '在', '是', '和', '也', '就', '都', '而', '及', '与', '为', '对', '等', '这', '那',
    '你', '我', '他', '她', '它', '我们', '你们', '他们', '她们', '它们', '什么', '这', '那', '这个',
    '那个', '这些', '那些', '自己', '可以', '没有', '可能', '应该', '因为', '所以', '但是', '如果',
    '虽然', '还是', '或者', '而且', '然后', '已经', '能够', '需要', '进行', '通过', '使用', '这里',
    '那里', '一些', '一下', '一点', '这样', '那样', '怎么', '怎样', '为什么', '多少', '几个',
    '还有', '就是', '不是', '只是', '因此', '而且', '其中', '包括', '由于', '关于', '对于', '根据',
    '按照', '通过', '经过', '作为', '如此', '一样', '一直', '一定', '一般', '一种', '一样', '一共',
    '不会', '不能', '不要', '没', '不', '有', '把', '被', '给', '让', '向', '往', '到', '从', '比'
}

ENGLISH_STOPWORDS = {
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
    'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'shall',
    'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by',
    'from', 'as', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between',
    'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how',
    'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
    'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'also', 'now', 'only',
    'even', 'still', 'back', 'well', 'much', 'more', 'most', 'any', 'about', 'out', 'up', 'down',
    'off', 'over', 'under', 'again', 'further', 'then', 'once', 'i', 'me', 'my', 'myself', 'we',
    'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him',
    'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them',
    'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these',
    'those', 'am', 'being', 'having', 'doing', 'would', 'could', 'should', 'might', 'must'
}

def clean_text(text):
    text = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', text)
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def tokenize_text(text):
    words = []
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
    english_pattern = re.compile(r'[a-zA-Z]+')

    chinese_parts = chinese_pattern.findall(text)
    english_parts = english_pattern.findall(text)

    for part in chinese_parts:
        if part:
            jieba_tokens = jieba.lcut(part)
            words.extend(jieba_tokens)

    for part in english_parts:
        if part:
            words.extend(part.lower().split())

    return words

def filter_stopwords(words):
    filtered = []
    for word in words:
        word = word.strip()
        if len(word) <= 1:
            continue
        if word in CHINESE_STOPWORDS:
            continue
        if word.lower() in ENGLISH_STOPWORDS:
            continue
        if word.isdigit():
            continue
        if re.match(r'^[\u4e00-\u9fff]$', word):
            continue
        if word:
            filtered.append(word)
    return filtered

def process_text(text):
    cleaned = clean_text(text)
    words = tokenize_text(cleaned)
    filtered = filter_stopwords(words)
    word_freq = {}
    for word in filtered:
        word_freq[word] = word_freq.get(word, 0) + 1
    return word_freq

def read_docx(file):
    try:
        doc = Document(file)
        text = []
        for para in doc.paragraphs:
            text.append(para.text)
        return '\n'.join(text)
    except Exception as e:
        st.error(f"读取DOCX文件失败: {str(e)}")
        return ""

def read_doc(file):
    try:
        import olefile
        from docx import Document as DocxDocument
        ole = olefile.OleFileIO(file)
        xml = ole.open('WordDocument').read()
        ole.close()
        import re
        text = re.sub(r'<[^>]+>', '', xml.decode('utf-8', errors='ignore'))
        return text
    except Exception as e:
        st.error(f"读取DOC文件失败: {str(e)}")
        return ""

def generate_wordcloud(word_freq, width=800, height=400, background_color='#0F172A', colormap='viridis'):
    if not word_freq:
        return None

    wc = WordCloud(
        font_path=FONT_PATH,
        width=width,
        height=height,
        background_color=background_color,
        colormap=colormap,
        max_words=200,
        max_font_size=150,
        min_font_size=10,
        random_state=42,
        prefer_horizontal=0.7,
        relative_scaling=0.5
    )
    return wc.generate_from_frequencies(word_freq)

def create_color_func(colors):
    def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
        return random_state.choice(colors)
    return color_func

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap');

    * {
        font-family: 'Noto Sans SC', 'Segoe UI', sans-serif;
    }

    .stApp {
        background: #0F172A;
    }

    .main-header {
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 50%, #EC4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 42px;
        font-weight: 700;
        text-align: center;
        padding: 20px 0;
        margin-bottom: 30px;
        letter-spacing: 2px;
    }

    .subtitle {
        text-align: center;
        color: #94A3B8;
        font-size: 16px;
        margin-top: -20px;
        margin-bottom: 30px;
    }

    .card {
        background: linear-gradient(145deg, #1E293B 0%, #0F172A 100%);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid #334155;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }

    .card:hover {
        border-color: #6366F1;
        transition: all 0.3s ease;
    }

    .section-title {
        color: #F8FAFC;
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .stTextArea textarea {
        background: #0F172A !important;
        color: #F8FAFC !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        padding: 16px !important;
        font-size: 15px !important;
    }

    .stTextArea textarea:focus {
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2) !important;
    }

    .stTextArea textarea::placeholder {
        color: #64748B !important;
    }

    .upload-box {
        border: 2px dashed #475569;
        border-radius: 12px;
        padding: 30px;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
        background: rgba(15, 23, 42, 0.5);
    }

    .upload-box:hover {
        border-color: #6366F1;
        background: rgba(99, 102, 241, 0.1);
    }

    .upload-icon {
        font-size: 48px;
        margin-bottom: 10px;
    }

    .upload-text {
        color: #94A3B8;
        font-size: 14px;
    }

    .btn-primary {
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 28px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }

    .btn-primary:hover {
        transform: scale(1.02);
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4);
    }

    .btn-primary:active {
        transform: scale(0.98);
    }

    .btn-secondary {
        background: #334155 !important;
        color: #F8FAFC !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        font-size: 14px !important;
    }

    .btn-download {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
    }

    .wordcloud-container {
        background: #1E293B;
        border-radius: 16px;
        padding: 20px;
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 400px;
        border: 1px solid #334155;
    }

    .placeholder-box {
        color: #64748B;
        text-align: center;
        padding: 60px;
    }

    .stats-badge {
        display: inline-block;
        background: rgba(99, 102, 241, 0.2);
        color: #A5B4FC;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        margin: 4px;
    }

    .stRadio > div {
        gap: 20px !important;
    }

    .stRadio label {
        color: #F8FAFC !important;
    }

    .stSelectbox label {
        color: #F8FAFC !important;
    }

    div[data-testid="stFileUploader"] {
        background: transparent !important;
    }

    div[data-testid="stFileUploader"] > div {
        background: transparent !important;
    }

    .stAlert {
        background: rgba(239, 68, 68, 0.1) !important;
        border: 1px solid #EF4444 !important;
        color: #FCA5A5 !important;
    }

    div[data-testid="stSuccess"] {
        background: rgba(16, 185, 129, 0.1) !important;
        border: 1px solid #10B981 !important;
        color: #6EE7B7 !important;
    }

    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #334155, transparent);
        margin: 20px 0;
    }

    footer {
        text-align: center;
        color: #64748B;
        font-size: 13px;
        padding: 20px;
        margin-top: 40px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">☁️ CloudWord Pro</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">智能词云生成工具 | 支持中英文混合文本与Word文件</p>', unsafe_allow_html=True)

col1, col2 = st.columns([35, 65], gap="large")

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📝 文本输入</div>', unsafe_allow_html=True)

    text_input = st.text_area(
        "在此粘贴或输入文本...",
        height=280,
        help="支持中英文混合文本输入"
    )

    if text_input:
        char_count = len(text_input)
        st.markdown(f'<span class="stats-badge">字符数: {char_count}</span>', unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">📁 Word文件上传</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "支持 .doc 和 .docx 格式，最大5MB",
        type=['doc', 'docx'],
        help="上传Word文档自动提取文本"
    )

    file_text = ""
    if uploaded_file:
        file_size = uploaded_file.size / 1024
        st.markdown(f'<span class="stats-badge">📄 {uploaded_file.name}</span>', unsafe_allow_html=True)
        st.markdown(f'<span class="stats-badge">📊 {file_size:.1f} KB</span>', unsafe_allow_html=True)

        with st.spinner("正在解析文件..."):
            try:
                if uploaded_file.name.endswith('.docx'):
                    file_text = read_docx(uploaded_file)
                elif uploaded_file.name.endswith('.doc'):
                    file_text = read_doc(uploaded_file)

                if file_text:
                    st.success(f"✅ 文件解析成功，提取到 {len(file_text)} 个字符")
            except Exception as e:
                st.error(f"❌ 文件解析失败: {str(e)}")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">⚙️ 词云设置</div>', unsafe_allow_html=True)

    col_setting1, col_setting2 = st.columns(2)

    with col_setting1:
        colormap = st.selectbox(
            "颜色方案",
            ['viridis', 'plasma', 'inferno', 'magma', 'cividis', 'twilight', 'twilight_shifted',
             'RdBu', 'coolwarm', 'Spectral', 'ocean', 'gist_earth', 'terrain']
        )

    with col_setting2:
        max_words = st.slider("最大词数", 50, 500, 200)

    bg_color = st.color_picker("背景颜色", "#0F172A")

    show_settings = st.expander("更多设置")
    with show_settings:
        remove_numbers = st.checkbox("移除数字", value=True)
        min_word_length = st.slider("最小词长", 1, 3, 2)

    generate_btn = st.button("🎨 生成词云", key="generate", help="点击生成词云")

    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">☁️ 词云预览</div>', unsafe_allow_html=True)

    combined_text = text_input
    if file_text:
        if combined_text:
            combined_text = combined_text + " " + file_text
        else:
            combined_text = file_text

    if generate_btn:
        if not combined_text or not combined_text.strip():
            st.error("⚠️ 请输入文本或上传Word文件")
        else:
            with st.spinner("🔄 正在处理文本并生成词云..."):
                try:
                    word_freq = process_text(combined_text)

                    if not word_freq:
                        st.error("❌ 未提取到有效词语，请检查输入内容")
                    else:
                        width = 1000
                        height = 500

                        wordcloud = generate_wordcloud(
                            word_freq,
                            width=width,
                            height=height,
                            background_color=bg_color,
                            colormap=colormap
                        )

                        if wordcloud:
                            fig, ax = plt.subplots(figsize=(12, 6))
                            ax.imshow(wordcloud, interpolation='bilinear')
                            ax.axis('off')
                            ax.set_facecolor(bg_color)
                            fig.patch.set_facecolor(bg_color)

                            st.pyplot(fig)

                            total_words = sum(word_freq.values())
                            unique_words = len(word_freq)

                            st.markdown(f"""
                                <div style="display: flex; gap: 10px; margin-top: 20px; flex-wrap: wrap;">
                                    <span class="stats-badge">📊 词汇总数: {total_words}</span>
                                    <span class="stats-badge">🔤 唯一词数: {unique_words}</span>
                                </div>
                            """, unsafe_allow_html=True)

                            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

                            st.markdown('<div class="section-title">💾 下载词云</div>', unsafe_allow_html=True)

                            dl_col1, dl_col2 = st.columns([1, 1])

                            with dl_col1:
                                download_format = st.radio("选择格式", ["PNG", "JPG"], horizontal=True)

                            with dl_col2:
                                scale = st.selectbox("分辨率", [1, 2, 3], index=0, format_func=lambda x: f"{x}x")

                            if st.button("⬇️ 下载词云图片", key="download"):
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

                                buffer = io.BytesIO()
                                fig_width = width * scale / 100
                                fig_height = height * scale / 100

                                fig_download, ax_download = plt.subplots(figsize=(fig_width, fig_height))
                                ax_download.imshow(wordcloud, interpolation='bilinear')
                                ax_download.axis('off')
                                ax_download.set_facecolor(bg_color)
                                fig_download.patch.set_facecolor(bg_color)

                                if download_format == "PNG":
                                    fig_download.savefig(buffer, format='png', dpi=100*scale, bbox_inches='tight', facecolor=bg_color)
                                    mime_type = "image/png"
                                    extension = "png"
                                else:
                                    fig_download.savefig(buffer, format='jpeg', dpi=100*scale, bbox_inches='tight', facecolor=bg_color)
                                    mime_type = "image/jpeg"
                                    extension = "jpg"

                                buffer.seek(0)

                                st.download_button(
                                    label=f"✅ 下载 {download_format} ({scale}x)",
                                    data=buffer,
                                    file_name=f"wordcloud_{timestamp}.{extension}",
                                    mime=mime_type,
                                    key="download_btn"
                                )

                                plt.close(fig_download)

                except Exception as e:
                    st.error(f"❌ 生成词云时出错: {str(e)}")
    else:
        st.markdown("""
            <div class="placeholder-box">
                <div style="font-size: 64px; margin-bottom: 20px;">☁️</div>
                <div style="font-size: 20px; color: #94A3B8; margin-bottom: 10px;">等待生成词云</div>
                <div style="color: #64748B;">请在左侧输入文本或上传Word文件，然后点击"生成词云"按钮</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
    <footer>
        CloudWord Pro © 2024 | 智能词云生成工具 | 支持中英文混合文本处理
    </footer>
""", unsafe_allow_html=True)