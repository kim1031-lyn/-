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

def get_type_brief(type_name):
    briefs = {
        'Organization': '用于描述公司、机构等，有助于品牌知识面板展示。',
        'Corporation': '用于描述公司、机构等，有助于品牌知识面板展示。',
        'LocalBusiness': '本地企业，适合有实体门店的商家，可提升本地搜索曝光。',
        'Product': '产品信息，支持价格、库存、评论等，利于获得商品富摘要。',
        'BreadcrumbList': '面包屑导航，提升页面结构清晰度，有助于收录。',
        'NewsArticle': '新闻/博客文章，利于获得Top Stories等富摘要。',
        'Event': '活动信息，支持时间、地点等，利于活动富摘要。',
        'FAQPage': '常见问答，利于FAQ富摘要展示。',
        'HowTo': '操作指南，利于HowTo富摘要展示。',
        'JobPosting': '职位招聘，支持职位富摘要。',
        'ImageObject': '图片元数据，提升图片搜索表现。',
        'VideoObject': '视频元数据，提升视频搜索表现。',
        'SoftwareApplication': '软件应用，支持应用富摘要。',
        'WebApplication': 'Web应用，支持应用富摘要。',
        'WebSite': '网站主页，支持站内搜索等功能。',
    }
    return briefs.get(type_name, '结构化数据类型，提升搜索引擎理解和富摘要机会。')

def get_required_fields(type_name):
    # 仅举例，实际可扩展更全
    required = {
        'Organization': ['@context', '@type', 'name'],
        'Corporation': ['@context', '@type', 'name'],
        'Product': ['@context', '@type', 'name', 'offers'],
        'FAQPage': ['@context', '@type', 'mainEntity'],
        'BreadcrumbList': ['@context', '@type', 'itemListElement'],
        'NewsArticle': ['@context', '@type', 'headline', 'datePublished', 'author'],
        'Event': ['@context', '@type', 'name', 'startDate', 'location'],
        'HowTo': ['@context', '@type', 'name', 'step'],
        'JobPosting': ['@context', '@type', 'title', 'description', 'datePosted', 'hiringOrganization'],
    }
    return required.get(type_name, ['@context', '@type'])

def get_recommended_fields(type_name):
    recommended = {
        'Organization': ['url', 'logo', 'contactPoint', 'sameAs'],
        'Corporation': ['url', 'logo', 'contactPoint', 'sameAs'],
        'Product': ['image', 'description', 'brand', 'review'],
        'FAQPage': [],
        'BreadcrumbList': [],
        'NewsArticle': ['image', 'dateModified'],
        'Event': ['description', 'image'],
        'HowTo': ['image', 'description'],
        'JobPosting': ['employmentType', 'jobLocation'],
    }
    return recommended.get(type_name, [])

def get_google_rich_snippet_support(type_name):
    support = {
        'Organization': '支持品牌知识面板（Brand Panel）',
        'Corporation': '支持品牌知识面板（Brand Panel）',
        'Product': '支持商品富摘要（Product Rich Result）',
        'FAQPage': '支持FAQ富摘要（FAQ Rich Result）',
        'BreadcrumbList': '支持面包屑富摘要（Breadcrumb Rich Result）',
        'NewsArticle': '支持Top Stories等新闻富摘要',
        'Event': '支持活动富摘要（Event Rich Result）',
        'HowTo': '支持HowTo富摘要（HowTo Rich Result）',
        'JobPosting': '支持职位富摘要（Job Posting Rich Result）',
    }
    return support.get(type_name, '无特殊富摘要，但有助于SEO结构化。')

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
    st.header("结构化数据诊断与SEO分析")
    st.markdown("粘贴完整<script>或JSON，获得专业SEO建议和诊断。")
    input_code = st.text_area("粘贴代码", height=250, key="parse_input")
    def auto_extract_json(s):
        if '<script' in s:
            return extract_json_from_script(s)
        return s
    json_part = auto_extract_json(input_code)
    if st.button("诊断分析", key="parse_btn"):
        try:
            parsed = json.loads(json_part)
            # 支持数组和单对象
            items = parsed if isinstance(parsed, list) else [parsed]
            for idx, item in enumerate(items):
                type_name = item.get('@type', '未知')
                st.markdown(f"### 第{idx+1}个结构化数据块：{type_name}")
                # 类型简述
                st.info(f"**类型说明：** {get_type_brief(type_name)}")
                # 必填字段检查
                required = get_required_fields(type_name)
                missing = [f for f in required if f not in item]
                if missing:
                    st.warning(f"缺失必填字段：{', '.join(missing)}。请补充以保证结构化数据被正确识别。")
                else:
                    st.success("所有必填字段均已填写。")
                # 推荐字段建议
                recommended = get_recommended_fields(type_name)
                rec_missing = [f for f in recommended if f not in item]
                if rec_missing:
                    st.info(f"建议补充推荐字段：{', '.join(rec_missing)}，有助于提升SEO效果和富摘要丰富度。")
                # Google富摘要支持
                st.info(f"**Google富摘要支持：** {get_google_rich_snippet_support(type_name)}")
                # 其他专业建议（举例）
                if type_name == 'Product':
                    if 'offers' in item and isinstance(item['offers'], dict):
                        if 'price' not in item['offers']:
                            st.warning("Product的offers建议包含price字段，利于价格富摘要展示。")
                    if 'image' not in item:
                        st.info("建议为Product补充image字段，提升商品吸引力。")
                if type_name == 'FAQPage':
                    if 'mainEntity' in item and isinstance(item['mainEntity'], list):
                        for q in item['mainEntity']:
                            if 'acceptedAnswer' not in q:
                                st.warning("FAQ每个问题建议包含acceptedAnswer字段。")
            st.success("诊断与分析完成。如需更详细建议，请参考schema.org官方文档或Google Search Gallery。")
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