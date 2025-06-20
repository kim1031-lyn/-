import streamlit as st
import json
import os

# 加载模板库
def load_templates():
    path = 'templates/structured_data_templates.json'
    if not os.path.exists(path):
        st.error(f"找不到模板文件: {path}，请检查文件路径和上传情况。")
        st.stop()
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

st.set_page_config(page_title="结构化数据工具", layout="wide")
st.title("结构化数据生成与编辑工具")
st.markdown(">请选择结构化数据类型，编辑并复制JSON-LD代码。\n")

# 读取模板
templates = load_templates()
type_list = list(templates.keys())

# 侧边栏类型选择
st.sidebar.header("选择结构化数据类型")
type_selected = st.sidebar.selectbox("类型", type_list)

# 获取模板代码
raw_code = templates[type_selected]

# 解析出JSON部分（去除<script>标签）
def extract_json_from_script(script_str):
    lines = script_str.strip().splitlines()
    json_lines = [line for line in lines if not line.strip().startswith('<script') and not line.strip().startswith('</script>')]
    return '\n'.join(json_lines)

json_code = extract_json_from_script(raw_code)

# 可编辑区
st.subheader(f"{type_selected} 可编辑JSON-LD代码")
user_code = st.text_area("请编辑下方JSON-LD代码（仅编辑JSON部分，无需<script>标签）", value=json_code, height=350)

# 自动格式化与校验
try:
    parsed = json.loads(user_code)
    formatted_code = json.dumps(parsed, ensure_ascii=False, indent=2)
    st.success("JSON格式正确！可直接复制下方代码到网页。")
    st.code(formatted_code, language='json')
except Exception as e:
    st.error(f"JSON格式有误，请检查：{e}")
    st.code(user_code, language='json')

# 生成完整<script>代码
if st.button("生成完整<script>嵌入代码"):
    if 'parsed' in locals():
        script_block = f'<script type="application/ld+json">\n{formatted_code}\n</script>'
        st.code(script_block, language='html')
        st.success("已生成完整嵌入代码，可直接复制到网页！")

# 预留：结构化数据解析、诊断、多类型合并等功能
# ... 