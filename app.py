import streamlit as st
import json
import os
from typing import List

# 加载模板库
def load_templates():
    path = 'templates/structured_data_templates.json'
    if not os.path.exists(path):
        st.error(f"找不到模板文件: {path}，请检查文件路径和上传情况。")
        st.stop()
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# 解析出JSON部分（去除<script>标签）
def extract_json_from_script(script_str):
    lines = script_str.strip().splitlines()
    json_lines = [line for line in lines if not line.strip().startswith('<script') and not line.strip().startswith('</script>')]
    return '\n'.join(json_lines)

def format_script_block(json_str):
    try:
        parsed = json.loads(json_str)
        formatted = json.dumps(parsed, ensure_ascii=False, indent=2)
        return f'<script type="application/ld+json">\n{formatted}\n</script>'
    except Exception:
        return None

def seo_check(parsed_json):
    # 简单SEO字段检查（可扩展）
    required_fields = ["@context", "@type"]
    missing = [f for f in required_fields if f not in parsed_json]
    tips = []
    if missing:
        tips.append(f"缺少必填字段: {', '.join(missing)}")
    if '@type' in parsed_json and parsed_json['@type'] == 'Product':
        for f in ["name", "offers"]:
            if f not in parsed_json:
                tips.append(f"Product类型建议包含字段: {f}")
    return tips

st.set_page_config(page_title="结构化数据工具", layout="wide")
st.title("结构化数据生成与解析工具")
tabs = st.tabs(["生成/编辑", "解析/诊断", "外部资源"])

# 读取模板
templates = load_templates()
type_list = list(templates.keys())

# Tab1: 生成/编辑
with tabs[0]:
    st.header("结构化数据生成与编辑")
    selected_types = st.multiselect("选择结构化数据类型（可多选）", type_list, default=[type_list[0]])
    user_jsons = {}
    for t in selected_types:
        raw_code = templates[t]
        json_code = extract_json_from_script(raw_code)
        st.subheader(f"{t} 可编辑JSON-LD代码")
        user_code = st.text_area(f"请编辑{t}的JSON-LD代码（仅JSON部分）", value=json_code, height=250, key=f"edit_{t}")
        user_jsons[t] = user_code
    if st.button("生成完整<script>嵌入代码", key="gen_script"):
        all_valid = True
        script_blocks = []
        for t, code in user_jsons.items():
            try:
                parsed = json.loads(code)
                formatted = json.dumps(parsed, ensure_ascii=False, indent=2)
                script_blocks.append(f'<script type="application/ld+json">\n{formatted}\n</script>')
            except Exception as e:
                st.error(f"{t} 的JSON格式有误：{e}")
                all_valid = False
        if all_valid:
            st.success("已生成完整嵌入代码，可直接复制到网页！")
            for i, block in enumerate(script_blocks):
                st.code(block, language='html')

# Tab2: 解析/诊断
with tabs[1]:
    st.header("结构化数据解析与诊断")
    st.markdown("粘贴已有的<script type=\"application/ld+json\">代码或纯JSON，自动格式化并结构化展示。")
    input_code = st.text_area("粘贴代码", height=250, key="parse_input")
    # 自动识别并提取JSON
    def auto_extract_json(s):
        if '<script' in s:
            return extract_json_from_script(s)
        return s
    json_part = auto_extract_json(input_code)
    if st.button("解析并诊断", key="parse_btn"):
        try:
            parsed = json.loads(json_part)
            formatted = json.dumps(parsed, ensure_ascii=False, indent=2)
            st.success("格式化结果：")
            st.code(formatted, language='json')
            # 结构化展示主要字段
            st.markdown(f"**@context**: {parsed.get('@context', '无')}")
            st.markdown(f"**@type**: {parsed.get('@type', '无')}")
            st.markdown("**主要属性：**")
            for k, v in parsed.items():
                if k not in ["@context", "@type"]:
                    st.markdown(f"- `{k}`: {v}")
            # SEO检查
            tips = seo_check(parsed)
            if tips:
                for tip in tips:
                    st.warning(tip)
            else:
                st.info("未发现明显SEO必填项缺失。")
        except Exception as e:
            st.error(f"解析失败：{e}")

# Tab3: 外部资源
with tabs[2]:
    st.header("常用结构化数据工具与文档")
    st.markdown("""
- [Google 结构化数据标记辅助工具](https://www.google.com/webmasters/markup-helper/u/0/)
- [Google 富媒体搜索结果测试](https://search.google.com/test/rich-results?hl=zh-cn)
- [Schema.org 验证器](https://validator.schema.org/)
- [Google 结构化数据官方文档](https://developers.google.com/search/docs/appearance/structured-data/sd-policies?hl=zh-cn)
- [Google 支持的结构化数据库 (Search Gallery)](https://developers.google.com/search/docs/appearance/structured-data/search-gallery?hl=zh-cn)
- [Schema.org 官方文档 (字段释义)](https://schema.org/docs/documents.html)
    """)

# 预留：结构化数据解析、诊断、多类型合并等功能
# ... 