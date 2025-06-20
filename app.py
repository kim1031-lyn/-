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
    # 合并所有选中类型的JSON为一个数组
    json_array = []
    for t in selected_types:
        raw_code = templates[t]
        json_code = extract_json_from_script(raw_code)
        try:
            parsed = json.loads(json_code)
            json_array.append(parsed)
        except Exception:
            pass
    # 生成初始完整<script>代码
    formatted_array = json.dumps(json_array, ensure_ascii=False, indent=2)
    script_block = f'<script type="application/ld+json">\n{formatted_array}\n</script>'
    st.subheader("可编辑集成版结构化数据代码（含<script>标签）")
    user_script = st.text_area("请直接编辑下方完整代码，包括<script>标签", value=script_block, height=400)
    # 自动提取JSON部分并校验
    def extract_json_from_full_script(s):
        lines = s.strip().splitlines()
        json_lines = [line for line in lines if not line.strip().startswith('<script') and not line.strip().startswith('</script>')]
        return '\n'.join(json_lines)
    json_part = extract_json_from_full_script(user_script)
    try:
        parsed = json.loads(json_part)
        formatted = json.dumps(parsed, ensure_ascii=False, indent=2)
        st.success("格式正确！最终可用代码如下：")
        st.code(f'<script type="application/ld+json">\n{formatted}\n</script>', language='html')
    except Exception as e:
        st.error(f"JSON格式有误，请检查：{e}")
        st.code(user_script, language='html')

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
        def display_structured_data_block(item, idx=None, level=0):
            prefix = "&nbsp;&nbsp;" * level
            if isinstance(item, dict):
                if idx is not None:
                    st.markdown(f"{prefix}---\n**第{idx+1}个结构化数据块：**", unsafe_allow_html=True)
                for k, v in item.items():
                    if k in ["@context", "@type"]:
                        st.markdown(f"{prefix}- **{k}**: {v}", unsafe_allow_html=True)
                for k, v in item.items():
                    if k not in ["@context", "@type"]:
                        if isinstance(v, dict) or (isinstance(v, list) and v and isinstance(v[0], dict)):
                            st.markdown(f"{prefix}- **{k}**:", unsafe_allow_html=True)
                            display_structured_data_block(v, None, level+1)
                        elif isinstance(v, list) and (not v or isinstance(v[0], str)):
                            st.markdown(f"{prefix}- **{k}**:", unsafe_allow_html=True)
                            st.markdown(f"{prefix}<ul>", unsafe_allow_html=True)
                            for s in v:
                                st.markdown(f"{prefix}<li>{s}</li>", unsafe_allow_html=True)
                            st.markdown(f"{prefix}</ul>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"{prefix}- **{k}**: {v}", unsafe_allow_html=True)
            elif isinstance(item, list):
                if idx is not None:
                    st.markdown(f"{prefix}---\n**第{idx+1}个结构化数据块（嵌套数组）:**", unsafe_allow_html=True)
                for sub_idx, sub_item in enumerate(item):
                    display_structured_data_block(sub_item, sub_idx, level+1)
            else:
                st.markdown(f"{prefix}- {item}", unsafe_allow_html=True)

        def get_field_comment(field):
            comments = {
                '@context': '指定schema.org上下文，建议为https://schema.org',
                '@type': '指定结构化数据类型，如Product、Organization等',
                'name': '结构化数据的名称',
                'offers': '产品的报价信息',
                'mainEntity': 'FAQ或HowTo等的主要实体',
                'sameAs': '社交媒体或相关页面链接',
                # 可扩展更多字段注释
            }
            return comments.get(field, '')

        try:
            parsed = json.loads(json_part)
            formatted = json.dumps(parsed, ensure_ascii=False, indent=2)
            st.success("格式化结果：")
            st.code(formatted, language='json')
            st.markdown("**主要属性结构化展示：**")
            if isinstance(parsed, dict):
                display_structured_data_block(parsed)
            elif isinstance(parsed, list):
                for idx, item in enumerate(parsed):
                    display_structured_data_block(item, idx)
            tips = []
            if isinstance(parsed, dict):
                tips = seo_check(parsed)
            elif isinstance(parsed, list):
                for item in parsed:
                    if isinstance(item, dict):
                        tips.extend(seo_check(item))
            if tips:
                for tip in tips:
                    # 诊断建议配合注释说明
                    field = tip.split(':')[1].strip() if ':' in tip else tip
                    comment = get_field_comment(field)
                    st.warning(f"{tip}  {comment}")
            else:
                st.info("未发现明显SEO必填项缺失。\n建议参考schema.org文档补充更多推荐字段。")
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