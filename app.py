import streamlit as st
import json
from typing import List
import base64

# --- 全局配置，必须是第一个Streamlit命令 ---
st.set_page_config(page_title="结构化数据工具", layout="wide")

# --- 内置模板数据，不再需要外部JSON文件 ---
def get_internal_templates():
    return {
      "Organization": "<script type=\"application/ld+json\">\n{\n  \"@context\": \"https://schema.org\",\n  \"@type\": \"Corporation\",\n  \"name\": \"CHINT\",\n  \"legalName\": \"Chint Group Co., Ltd.\",\n  \"url\": \"https://www.chintglobal.com/\",\n  \"logo\": \"https://www.chintglobal.com/favicon.ico\",\n  \"foundingDate\": \"1984\",\n  \"address\": {\n    \"@type\": \"PostalAddress\",\n    \"streetAddress\": \"No. 1, CHINT Road, CHINT Industrial Zone, North Baixiang, Yueqing\",\n    \"addressLocality\": \"Yueqing\",\n    \"addressRegion\": \"Zhejiang\",\n    \"postalCode\": \"325603\",\n    \"addressCountry\": \"China\"\n  },\n  \"contactPoint\": {\n    \"@type\": \"ContactPoint\",\n    \"contactType\": \"customer support\",\n    \"telephone\": \"+86 21 6777 7777\",\n    \"email\": \"global-sales@chint.com\"\n  },\n  \"sameAs\": [\n    \"https://chintglobal.com/\",\n    \"https://www.facebook.com/chintgroup/\",\n    \"https://twitter.com/GroupChint/\",\n    \"https://www.linkedin.com/company/chintelectric/\"\n  ]\n}\n</script>",
      "LocalBusiness": "<script type=\"application/ld+json\">\n{\n  \"@context\": \"https://schema.org\",\n  \"@type\": \"LocalBusiness\",\n  \"name\": \"Your Local Store\",\n  \"address\": {\n    \"@type\": \"PostalAddress\",\n    \"streetAddress\": \"123 Main St\",\n    \"addressLocality\": \"Your City\",\n    \"addressRegion\": \"Your State\",\n    \"postalCode\": \"12345\"\n  },\n  \"telephone\": \"+1-555-1212\"\n}\n</script>",
      "Product": "<script type=\"application/ld+json\">\n{\n  \"@context\": \"https://schema.org\",\n  \"@type\": \"Product\",\n  \"name\": \"Awesome Gadget\",\n  \"image\": \"https://yourwebsite.com/images/gadget.jpg\",\n  \"description\": \"A revolutionary gadget for everyday use.\",\n  \"offers\": {\n    \"@type\": \"Offer\",\n    \"priceCurrency\": \"USD\",\n    \"price\": \"29.99\",\n    \"availability\": \"https://schema.org/InStock\"\n  }\n}\n</script>",
      "BreadcrumbList": "<script type=\"application/ld+json\">\n{\n  \"@context\": \"https://schema.org\",\n  \"@type\": \"BreadcrumbList\",\n  \"itemListElement\": [\n    {\n      \"@type\": \"ListItem\",\n      \"position\": 1,\n      \"name\": \"Home\",\n      \"item\": \"https://yourwebsite.com\"\n    },\n    {\n      \"@type\": \"ListItem\",\n      \"position\": 2,\n      \"name\": \"Products\",\n      \"item\": \"https://yourwebsite.com/products\"\n    }\n  ]\n}\n</script>",
      "NewsArticle": "<script type=\"application/ld+json\">\n{\n  \"@context\": \"https://schema.org\",\n  \"@type\": \"NewsArticle\",\n  \"headline\": \"Title of a News Article\",\n  \"image\": [\n    \"https://example.com/photos/1x1/photo.jpg\",\n    \"https://example.com/photos/4x3/photo.jpg\",\n    \"https://example.com/photos/16x9/photo.jpg\"\n  ],\n  \"datePublished\": \"2025-03-18\",\n  \"dateModified\": \"2025-03-20\",\n  \"author\": [\n    {\n      \"@type\": \"Person\",\n      \"name\": \"JerryZhi\",\n      \"url\": \"https://zhi.wtf\"\n    },\n    {\n      \"@type\": \"Organization\",\n      \"name\": \"Yeehai\",\n      \"url\": \"https://example.com/profile/johndoe123\"\n    }\n  ]\n}\n</script>",
      "Event": "<script type=\"application/ld+json\">\n{\n  \"@context\": \"https://schema.org\",\n  \"@type\": \"Event\",\n  \"name\": \"Tech Conference 2025\",\n  \"startDate\": \"2025-12-15T09:00:00-08:00\",\n  \"location\": {\n    \"@type\": \"Place\",\n    \"name\": \"Convention Center\"\n  }\n}\n</script>",
      "FAQPage": "<script type=\"application/ld+json\">\n{\n  \"@context\": \"https://schema.org\",\n  \"@type\": \"FAQPage\",\n  \"mainEntity\": [\n    {\n      \"@type\": \"Question\",\n      \"name\": \"What is your return policy?\",\n      \"acceptedAnswer\": {\n        \"@type\": \"Answer\",\n        \"text\": \"We offer a 30-day money-back guarantee.\"\n      }\n    }\n  ]\n}\n</script>",
      "HowTo": "<script type=\"application/ld+json\">\n{\n  \"@context\": \"https://schema.org\",\n  \"@type\": \"HowTo\",\n  \"name\": \"How to Bake a Cake\",\n  \"step\": [\n    {\n      \"@type\": \"HowToStep\",\n      \"text\": \"Preheat your oven to 350°F (175°C).\"\n    }\n  ]\n}\n</script>",
      "JobPosting": "<script type=\"application/ld+json\">\n{\n  \"@context\": \"https://schema.org\",\n  \"@type\": \"JobPosting\",\n  \"title\": \"Software Engineer\",\n  \"description\": \"We are looking for a skilled software engineer...\",\n  \"datePosted\": \"2025-06-15\",\n  \"hiringOrganization\": {\n    \"@type\": \"Organization\",\n    \"name\": \"Tech Innovations Inc.\"\n  }\n}\n</script>",
      "ImageObject": "<script type=\"application/ld+json\">\n[\n  {\n    \"@context\": \"https://schema.org/\",\n    \"@type\": \"ImageObject\",\n    \"contentUrl\": \"https://www.chintglobal.com/content/dam/chint/global/product-center/low-voltage/iec/secondary-power-distribution/mccb/nm1/product-image/new/NM1-125H-2300-MCCB-Front.png\",\n    \"license\": \"https://www.chintglobal.com/en/license\",\n    \"creditText\": \"ChintGlobal\",\n    \"creator\": {\n      \"@type\": \"Organization\",\n      \"name\": \"Chint Global\"\n    }\n  }\n]\n</script>",
      "VideoObject": "<script type=\"application/ld+json\">\n{\n  \"@context\": \"https://schema.org\",\n  \"@type\": \"VideoObject\",\n  \"name\": \"Introducing the detal of NM1 mccb from chint\",\n  \"description\": \"detail of NM1-125H-2300-MCCB\",\n  \"thumbnailUrl\": [\n    \"https://example.com/photos/1x1/photo.jpg\",\n    \"https://example.com/photos/4x3/photo.jpg\",\n    \"https://example.com/photos/16x9/photo.jpg\"\n  ],\n  \"uploadDate\": \"2024-03-31T08:00:00+08:00\",\n  \"contentUrl\": \"https://www.chintglobal.com/content/dam/chint/global/product-center/low-voltage/iec/secondary-power-distribution/mccb/nm1/product-video/NM1-MCCB-Video-02.wmv\",\n  \"regionsAllowed\": \"US,UK\"\n}\n</script>",
      "SoftwareApplication": "<script type=\"application/ld+json\">\n[\n  {\n    \"@context\": \"https://schema.org\",\n    \"@type\": \"SoftwareApplication\",\n    \"name\": \"Free AI Face Swap Online\",\n    \"description\": \"Free online face changer that allows you to swap heads and replace faces in photos & Videos\",\n    \"applicationCategory\": \"LifestyleApplication\",\n    \"operatingSystem\": \"Windows 7+, OSX 10.6+, Android, iOS\",\n    \"aggregateRating\": {\n      \"@type\": \"AggregateRating\",\n      \"ratingValue\": \"4.9\",\n      \"ratingCount\": \"35926\"\n    },\n    \"offers\": {\n      \"@type\": \"Offer\",\n      \"price\": \"0\",\n      \"priceCurrency\": \"USD\"\n    }\n  }\n]\n</script>",
      "WebApplication": "<script type=\"application/ld+json\">\n{\n  \"@context\": \"https://schema.org\",\n  \"@type\": \"WebApplication\",\n  \"name\": \"VidAU Face Swap\",\n  \"operatingSystem\": \"Windows, MacOS, Linux, Chrome OS, iOS, Android\",\n  \"applicationCategory\": \"BrowserApplication\",\n  \"aggregateRating\": {\n    \"@type\": \"AggregateRating\",\n    \"ratingValue\": \"4.9\",\n    \"reviewCount\": \"10086\"\n  },\n  \"offers\": {\n    \"@type\": \"Offer\",\n    \"price\": \"0\",\n    \"priceCurrency\": \"USD\"\n  },\n  \"description\": \"Discover the powerful AI video face swap tool for creating interesting, valuable content. Swap faces with free online AI tools for realistic video.\"\n}\n</script>",
      "WebSite": "<script type=\"application/ld+json\">\n{\n  \"@context\": \"https://schema.org\",\n  \"@type\": \"WebSite\",\n  \"name\": \"Your Website\",\n  \"url\": \"https://yourwebsite.com\",\n  \"potentialAction\": {\n    \"@type\": \"SearchAction\",\n    \"target\": \"https://yourwebsite.com/search?q={search_term_string}\",\n    \"query-input\": \"required name=search_term_string\"\n  }\n}\n</script>"
    }

# --- 辅助函数 ---
def extract_json_from_script(script_str: str) -> str:
    """A more robust function to extract JSON content from a <script> tag."""
    try:
        # Prioritize finding a JSON array first
        start_pos = script_str.find('[')
        if start_pos == -1:
            # If no array, find a JSON object
            start_pos = script_str.find('{')

        if start_pos == -1:
            return "{}"

        # Find the corresponding closing bracket/brace
        if script_str[start_pos] == '[':
            end_pos = script_str.rfind(']') + 1
        else:
            end_pos = script_str.rfind('}') + 1
            
        if end_pos == 0:
            return "{}"
            
        return script_str[start_pos:end_pos]
    except Exception:
        return "{}"

def get_type_brief(type_name):
    briefs = {
        'Organization': '用于描述公司、机构等，有助于品牌知识面板展示。', 'Corporation': '用于描述公司、机构等，有助于品牌知识面板展示。',
        'LocalBusiness': '本地企业，适合有实体门店的商家，可提升本地搜索曝光。', 'Product': '产品信息，支持价格、库存、评论等，利于获得商品富摘要。',
        'BreadcrumbList': '面包屑导航，提升页面结构清晰度，有助于收录。', 'NewsArticle': '新闻/博客文章，利于获得Top Stories等富摘要。',
        'Event': '活动信息，支持时间、地点等，利于活动富摘要。', 'FAQPage': '常见问答，利于FAQ富摘要展示。', 'HowTo': '操作指南，利于HowTo富摘要展示。',
        'JobPosting': '职位招聘，支持职位富摘要。', 'ImageObject': '图片元数据，提升图片搜索表现。', 'VideoObject': '视频元数据，提升视频搜索表现。',
        'SoftwareApplication': '软件应用，支持应用富摘要。', 'WebApplication': 'Web应用，支持应用富摘要。', 'WebSite': '网站主页，支持站内搜索等功能。',
    }
    return briefs.get(type_name, '结构化数据类型，提升搜索引擎理解和富摘要机会。')

def get_required_fields(type_name):
    required = {
        'Organization': ['@context', '@type', 'name'], 'Corporation': ['@context', '@type', 'name'],
        'Product': ['@context', '@type', 'name', 'offers'], 'FAQPage': ['@context', '@type', 'mainEntity'],
        'BreadcrumbList': ['@context', '@type', 'itemListElement'], 'NewsArticle': ['@context', '@type', 'headline', 'datePublished', 'author'],
        'Event': ['@context', '@type', 'name', 'startDate', 'location'], 'HowTo': ['@context', '@type', 'name', 'step'],
        'JobPosting': ['@context', '@type', 'title', 'description', 'datePosted', 'hiringOrganization'],
    }
    return required.get(type_name, ['@context', '@type'])

def get_recommended_fields(type_name):
    recommended = {
        'Organization': ['url', 'logo', 'contactPoint', 'sameAs'], 'Corporation': ['url', 'logo', 'contactPoint', 'sameAs'],
        'Product': ['image', 'description', 'brand', 'review'], 'FAQPage': [], 'BreadcrumbList': [], 'NewsArticle': ['image', 'dateModified'],
        'Event': ['description', 'image'], 'HowTo': ['image', 'description'], 'JobPosting': ['employmentType', 'jobLocation'],
    }
    return recommended.get(type_name, [])

def get_google_rich_snippet_support(type_name):
    support = {
        'Organization': '支持品牌知识面板（Brand Panel）', 'Corporation': '支持品牌知识面板（Brand Panel）',
        'Product': '支持商品富摘要（Product Rich Result）', 'FAQPage': '支持FAQ富摘要（FAQ Rich Result）',
        'BreadcrumbList': '支持面包屑富摘要（Breadcrumb Rich Result）', 'NewsArticle': '支持Top Stories等新闻富摘要。',
        'Event': '支持活动富摘要（Event Rich Result）', 'HowTo': '支持HowTo富摘要（HowTo Rich Result）',
        'JobPosting': '支持职位富摘要（Job Posting Rich Result）',
    }
    return support.get(type_name, '无特殊富摘要，但有助于SEO结构化。')

# --- 主程序 ---
templates = get_internal_templates()
type_list = list(templates.keys())

# --- 会话状态 (Session State) 初始化 ---
if 'selected_types' not in st.session_state:
    st.session_state['selected_types'] = [type_list[0]] if type_list else []
if 'theme' not in st.session_state:
    st.session_state['theme'] = '大地色'
if 'editor_content' not in st.session_state:
    st.session_state['editor_content'] = ''
if 'last_selection_key' not in st.session_state:
    st.session_state['last_selection_key'] = ""


THEMES = {
    '大地色': {
        'bg': '#F5E9DA', 'card': '#FFF8F0', 'accent': '#A67C52', 'button': '#D7B899', 'text': '#4E3B31', 'shadow': '#E0C9A6', 'code': '#F3E7D9', 'input': '#FFF8F0', 'border': '#E0C9A6', 'info': '#7C5C3B'
    },
    '深色': {
        'bg': '#2D2A26', 'card': '#3B362F', 'accent': '#D7B899', 'button': '#A67C52', 'text': '#FFF8F0', 'shadow': '#4E3B31', 'code': '#3B362F', 'input': '#4E3B31', 'border': '#A67C52', 'info': '#D7B899'
    },
    '浅色': {
        'bg': '#F8F8F8', 'card': '#FFFFFF', 'accent': '#A67C52', 'button': '#D7B899', 'text': '#4E3B31', 'shadow': '#E0C9A6', 'code': '#F3E7D9', 'input': '#FFF8F0', 'border': '#E0C9A6', 'info': '#7C5C3B'
    }
}
cur_theme = THEMES[st.session_state['theme']]

st.markdown(f'''
<style>
/* CSS styles here, no changes needed from your original code */
</style>
''', unsafe_allow_html=True)


# --- 侧边栏 ---
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; margin-bottom:1.5rem;'>
        <img src='https://img.icons8.com/color/96/000000/structural.png' style='width:60px; border-radius:16px; box-shadow:0 2px 8px #E0C9A6;'>
        <div style='font-size:1.5rem; font-weight:900; color:#A67C52; margin-top:0.5rem; letter-spacing:2px;'>结构化数据工具</div>
        <div style='font-size:1rem; color:#7C5C3B; margin-top:0.2rem;'>让SEO结构化更简单</div>
    </div>
    """, unsafe_allow_html=True)
    
    navs = ["生成/编辑", "解析/诊断", "外部资源"]
    nav_icons = ["🏠", "🧩", "🌐"]
    if 'tab_idx' not in st.session_state:
        st.session_state['tab_idx'] = 0

    for i, (nav, icon) in enumerate(zip(navs, nav_icons)):
        if st.button(f"{icon} {nav}", key=f"nav_{i}", use_container_width=True):
            st.session_state['tab_idx'] = i
            st.rerun()

    st.markdown("---")

    st.markdown("#### 主题切换")
    theme = st.selectbox("选择主题", list(THEMES.keys()), index=list(THEMES.keys()).index(st.session_state['theme']))
    if theme != st.session_state['theme']:
        st.session_state['theme'] = theme
        st.rerun()

    st.markdown("---")

    st.markdown("#### 🚀 高级功能（可扩展）")
    st.markdown('''
    <ul style='list-style:disc inside; color:#7C5C3B; font-size:1rem;'>
        <li>批量校验/批量生成结构化数据</li>
        <li>富摘要模拟预览</li>
    </ul>
    ''', unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align:center; color:#A67C52; font-size:0.98rem; margin-top:2rem;'>
        <div>© 2025 结构化数据工具</div>
        <div style='color:#7C5C3B;'>v2.0.0 | 由AI驱动</div>
    </div>
    """, unsafe_allow_html=True)

# --- 主页面 ---
st.title("结构化数据生成与解析工具")
tabs = st.tabs(["生成/编辑", "解析/诊断", "外部资源", "高级功能"])

# --- Tab 1: 生成/编辑 ---
with tabs[0]:
    st.header("结构化数据生成与编辑")

    valid_defaults = [t for t in st.session_state.get('selected_types', []) if t in type_list]
    if not valid_defaults and type_list:
        valid_defaults = [type_list[0]]

    selected_types = st.multiselect(
        "选择结构化数据类型（可多选）",
        options=type_list,
        default=valid_defaults
    )
    st.session_state['selected_types'] = selected_types

    json_array = []
    # If user deselects everything, keep showing the last valid selection to avoid blank state
    effective_selection = selected_types if selected_types else valid_defaults

    for t in effective_selection:
        raw_code = templates.get(t, "{}")
        json_code = extract_json_from_script(raw_code)
        try:
            parsed = json.loads(json_code)
            if isinstance(parsed, list):
                json_array.extend(parsed)
            else:
                json_array.append(parsed)
        except json.JSONDecodeError:
            pass
            
    final_json_output = {}
    if len(json_array) == 1:
        final_json_output = json_array[0]
    elif len(json_array) > 1:
        final_json_output = json_array
        
    formatted_json = json.dumps(final_json_output, ensure_ascii=False, indent=2)
    script_block = f'<script type="application/ld+json">\n{formatted_json}\n</script>'
    
    selection_key = ",".join(sorted(selected_types))
    if st.session_state.get('last_selection_key') != selection_key:
        st.session_state['editor_content'] = script_block
        st.session_state['last_selection_key'] = selection_key

    user_script = st.text_area("请直接编辑下方完整代码", value=st.session_state.get('editor_content', script_block), height=400, key="main_editor")
    st.session_state['editor_content'] = user_script

    try:
        json_part = extract_json_from_script(user_script)
        parsed = json.loads(json_part)
        formatted = json.dumps(parsed, ensure_ascii=False, indent=2)
        st.success("格式正确！最终可用代码如下：")
        st.code(f'<script type="application/ld+json">\n{formatted}\n</script>', language='html')
    except Exception as e:
        st.error(f"JSON格式有误，请检查：{e}")
        st.code(user_script, language='html')


# --- Tab 2: 解析/诊断 ---
with tabs[1]:
    st.header("结构化数据诊断与SEO分析")
    st.markdown("粘贴完整<script>或JSON，获得专业SEO建议和诊断。")
    input_code = st.text_area("粘贴代码", height=250, key="parse_input")
    
    if st.button("诊断分析", key="parse_btn"):
        json_part_to_diagnose = extract_json_from_script(input_code)
        
        def diagnose_item(item, global_idx, level=0):
            st.markdown(f"<div class='diagnose-card' style='margin-left: {level*20}px'>", unsafe_allow_html=True)
            title_prefix = "h4" if level == 0 else "h5"

            if isinstance(item, dict):
                type_name = item.get('@type', '未知')
                st.markdown(f"<{title_prefix}>第[{global_idx[0]}]个结构化数据块：{type_name}</{title_prefix}>", unsafe_allow_html=True)
                st.markdown(f"**类型说明：** {get_type_brief(type_name)}")
                required = get_required_fields(type_name)
                missing = [f for f in required if f not in item]
                if missing:
                    st.warning(f"缺失必填字段：`{', '.join(missing)}`。")
                else:
                    st.success(f"所有必填字段均已填写。")
            elif isinstance(item, list):
                 st.info(f"这是一个结构化数据数组，共包含 {len(item)} 项。")
                 for sub_item in item:
                    global_idx[0] += 1
                    diagnose_item(sub_item, global_idx, level+1)
            else:
                 st.error(f"无法识别的数据类型: {type(item)}")
            st.markdown("</div>", unsafe_allow_html=True)

        try:
            parsed = json.loads(json_part_to_diagnose)
            items_to_diagnose = parsed if isinstance(parsed, list) else [parsed]
            global_idx = [0]
            diagnose_item(items_to_diagnose, global_idx)
        except Exception as e:
            st.error(f"解析失败：{e}")


# --- Tab 3: 外部资源 ---
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

# --- Tab 4: 高级功能 ---
with tabs[3]:
    st.header("高级功能")
    st.markdown("---")
    st.subheader("结构化数据对比/差异分析")
    col1, col2 = st.columns(2)
    with col1:
        data1 = st.text_area("结构化数据1 (JSON)", height=200, key="diff1")
    with col2:
        data2 = st.text_area("结构化数据2 (JSON)", height=200, key="diff2")
    if st.button("对比并高亮差异", key="do_diff"):
        try:
            from deepdiff import DeepDiff
            obj1 = json.loads(extract_json_from_script(data1))
            obj2 = json.loads(extract_json_from_script(data2))
            diff = DeepDiff(obj1, obj2, view='tree', ignore_order=True)
            if not diff:
                st.success("两个结构化数据完全一致！")
            else:
                st.write("差异分析结果:")
                st.json(diff.to_json())
        except Exception as e:
            st.error(f"对比失败：{e}")