import streamlit as st
import json
from pygments import highlight, lexers, formatters

# 加载模板库
def load_templates():
    with open('templates/structured_data_templates.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def code_highlight(code):
    return highlight(code, lexers.JsonLexer(), formatters.HtmlFormatter(style='default', noclasses=True))

st.set_page_config(page_title="结构化数据工具", layout="wide")
st.title("结构化数据生成与编辑工具")
st.markdown("""
> 请选择结构化数据类型，编辑并复制JSON-LD代码。
""")

# 读取模板
templates = load_templates()
type_list = list(templates.keys())

# 侧边栏类型选择
st.sidebar.header("选择结构化数据类型")
type_selected = st.sidebar.selectbox("类型", type_list)

# 显示模板并可编辑
st.subheader(f"{type_selected} 模板")
default_code = json.dumps(templates[type_selected], ensure_ascii=False, indent=2)
user_code = st.text_area("可编辑JSON-LD代码", value=default_code, height=350)

# 代码高亮展示
st.markdown("**高亮预览：**", unsafe_allow_html=True)
st.markdown(f'<div style="background:#f5f5f5;padding:10px;border-radius:8px;">{code_highlight(user_code)}</div>', unsafe_allow_html=True)

# 复制按钮
st.code(user_code, language='json')
st.button("复制到剪贴板", help="可直接选中上方代码复制")

# 预留：结构化数据解析、诊断、多类型合并等功能
# ... 