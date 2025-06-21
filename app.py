import streamlit as st
import json
import os
from typing import List
import base64

# ======================= 调试代码开始 =======================
# 这部分代码将帮助我们诊断云端服务器的文件系统问题
st.write("--- 调试信息 ---")
try:
    # 获取当前工作目录
    cwd = os.getcwd()
    st.write(f"当前工作目录 (Current Working Directory): {cwd}")

    # 列出当前目录下的所有文件和文件夹
    st.write("当前目录内容 (Contents of Current Directory):")
    st.write(os.listdir('.'))

    # 尝试列出 templates 文件夹的内容
    templates_path = 'templates'
    st.write(f"检查 '{templates_path}' 文件夹是否存在...")
    if os.path.exists(templates_path):
        st.success(f"文件夹 '{templates_path}' 存在！")
        st.write(f"'{templates_path}' 文件夹内容:")
        st.write(os.listdir(templates_path))
    else:
        st.error(f"致命错误：在当前目录下找不到 '{templates_path}' 文件夹！")
        st.info("请检查您的GitHub仓库，确认 'templates' 文件夹（全小写）和其中的 'structured_data_templates.json' 文件已正确上传。")


except Exception as e:
    st.error(f"在调试阶段发生异常: {e}")
st.write("--- 调试信息结束 ---")
# ======================== 调试代码结束 ========================


st.set_page_config(page_title="结构化数据工具", layout="wide")

# 加载模板库
def load_templates():
    path = 'templates/structured_data_templates.json'
    if not os.path.exists(path):
        # 即使这里有检查，上面的调试代码会更早地暴露问题
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

# 主题色方案
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
if 'theme' not in st.session_state:
    st.session_state['theme'] = '大地色'
cur_theme = THEMES[st.session_state['theme']]

# 注入全局自定义CSS（支持主题切换）
st.markdown(f'''
<style>
body, .stApp {{
    background-color: {cur_theme['bg']} !important;
    font-family: 'Nunito', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    color: {cur_theme['text']};
}}

h1, h2, h3, h4, h5, h6 {{
    color: {cur_theme['text']} !important;
    font-family: 'Nunito', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    font-weight: 800;
    letter-spacing: 1px;
}}

.stTabs [data-baseweb="tab-list"] {{
    background: {cur_theme['card']};
    border-radius: 18px 18px 0 0;
    box-shadow: 0 2px 8px {cur_theme['shadow']};
    padding: 0.5rem 1rem;
}}

.stTabs [data-baseweb="tab"] {{
    color: {cur_theme['accent']} !important;
    font-weight: 700;
    font-size: 1.1rem;
    border-radius: 12px 12px 0 0;
    margin-right: 8px;
}}

.stTabs [aria-selected="true"] {{
    background: {cur_theme['code']} !important;
    color: {cur_theme['text']} !important;
    box-shadow: 0 2px 8px {cur_theme['shadow']};
}}

.stButton > button {{
    background: linear-gradient(90deg, {cur_theme['button']} 60%, {cur_theme['accent']} 100%);
    color: #fff;
    border: none;
    border-radius: 16px;
    font-weight: 700;
    font-size: 1.1rem;
    box-shadow: 0 2px 8px {cur_theme['shadow']};
    padding: 0.5rem 1.5rem;
    margin: 0.5rem 0;
    transition: background 0.2s, box-shadow 0.2s;
}}
.stButton > button:hover {{
    background: linear-gradient(90deg, {cur_theme['accent']} 60%, {cur_theme['button']} 100%);
    box-shadow: 0 4px 16px {cur_theme['button']};
}}

.stTextArea textarea, .stTextInput input {{
    background: {cur_theme['input']} !important;
    color: {cur_theme['text']} !important;
    border-radius: 12px !important;
    border: 1.5px solid {cur_theme['border']} !important;
    font-family: 'Nunito', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    font-size: 1.05rem;
    box-shadow: 0 2px 8px {cur_theme['shadow']};
}}

.stCode, .stMarkdown code {{
    background: {cur_theme['code']} !important;
    color: {cur_theme['text']} !important;
    border-radius: 12px !important;
    font-family: 'Fira Mono', 'Consolas', 'Menlo', 'Monaco', 'Courier New', monospace;
    font-size: 1.02rem;
    box-shadow: 0 2px 8px {cur_theme['shadow']};
}}

.block-card {{
    background: {cur_theme['card']};
    border-radius: 18px;
    box-shadow: 0 4px 24px {cur_theme['shadow']};
    padding: 2rem 2.5rem 1.5rem 2.5rem;
    margin-bottom: 2rem;
}}

.diagnose-card {{
    background: {cur_theme['code']};
    border-radius: 14px;
    box-shadow: 0 2px 8px {cur_theme['shadow']};
    padding: 1.2rem 1.5rem 1rem 1.5rem;
    margin-bottom: 1.2rem;
    color: {cur_theme['text']};
}}

hr {{
    border: 0;
    border-top: 1.5px dashed {cur_theme['shadow']};
    margin: 1.2rem 0;
}}

.main-center {{
    max-width: 900px;
    margin: 0 auto;
}}

.diagnose-indent {{
    margin-left: 2.2em;
}}
</style>
''', unsafe_allow_html=True)

# 侧边栏与主区联动状态
if 'tab_idx' not in st.session_state:
    st.session_state['tab_idx'] = 0
if 'search_type' not in st.session_state:
    st.session_state['search_type'] = ''
if 'history' not in st.session_state:
    st.session_state['history'] = []
if 'favorites' not in st.session_state:
    st.session_state['favorites'] = []
if 'editor_content' not in st.session_state:
    st.session_state['editor_content'] = {}

# 侧边栏UI实现
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; margin-bottom:1.5rem;'>
        <img src='https://img.icons8.com/color/96/000000/structural.png' style='width:60px; border-radius:16px; box-shadow:0 2px 8px #E0C9A6;'>
        <div style='font-size:1.5rem; font-weight:900; color:#A67C52; margin-top:0.5rem; letter-spacing:2px;'>结构化数据工具</div>
        <div style='font-size:1rem; color:#7C5C3B; margin-top:0.2rem;'>让SEO结构化更简单</div>
    </div>
    """, unsafe_allow_html=True)

    # 主功能导航
    navs = ["生成/编辑", "解析/诊断", "外部资源"]
    nav_icons = ["🏠", "🧩", "🌐"]
    for i, (nav, icon) in enumerate(zip(navs, nav_icons)):
        if st.button(f"{icon} {nav}", key=f"nav_{i}", use_container_width=True):
            st.session_state['tab_idx'] = i
            st.rerun()

    st.markdown("---")

    # 主题切换
    st.markdown("#### 主题切换")
    theme = st.selectbox("选择主题", list(THEMES.keys()), index=list(THEKES.keys()).index(st.session_state['theme']))
    if theme != st.session_state['theme']:
        st.session_state['theme'] = theme
        st.rerun()

    st.markdown("---")

    # 高级功能区
    st.markdown("#### 🚀 高级功能（可扩展）")
    st.markdown('''
    <ul style='list-style:disc inside; color:#7C5C3B; font-size:1rem;'>
        <li>批量校验/批量生成结构化数据</li>
        <li>富摘要模拟预览</li>
        <li>结构化数据对比/差异分析</li>
        <li>多语言支持/国际化</li>
        <li>API接口/自动化集成</li>
        <li>用户登录/个性化/云端存储</li>
        <li>数据可视化与SEO趋势分析</li>
        <li>SEO富摘要监控与推送</li>
        <li>团队协作/权限管理</li>
        <li>结构化数据知识库/案例库</li>
        <li>AI智能诊断报告/一键导出</li>
        <li>Schema.org标准自动更新</li>
        <li>内容与结构一体化编辑</li>
        <li>行业模板市场/社区生态</li>
    </ul>
    ''', unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align:center; color:#A67C52; font-size:0.98rem; margin-top:2rem;'>
        <div>© 2024 结构化数据工具</div>
        <div style='color:#7C5C3B;'>v1.0.0 | 由AI驱动</div>
    </div>
    """, unsafe_allow_html=True)

st.title("结构化数据生成与解析工具")

# 主内容区Tab联动
cur_tab = st.session_state.get('tab_idx', 0)
tabs = st.tabs(["生成/编辑", "解析/诊断", "外部资源", "高级功能"])

# 类型快速搜索联动
templates = load_templates()
type_list = list(templates.keys())
search_kw = st.session_state.get('search_type', '').strip().lower()
if search_kw:
    filtered_types = [t for t in type_list if search_kw in t.lower()]
else:
    filtered_types = type_list

# 生成/编辑Tab
with tabs[0]:
    st.header("结构化数据生成与编辑")
    # 多类型选择联动
    if 'selected_types' not in st.session_state:
        st.session_state['selected_types'] = [filtered_types[0]] if filtered_types else []
    selected_types = st.multiselect("选择结构化数据类型（可多选）", filtered_types, default=st.session_state['selected_types'])
    st.session_state['selected_types'] = selected_types
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
    
    # 根据选择的类型数量决定输出是对象还是数组
    if len(json_array) == 1:
        # 如果只有一个类型，直接输出该JSON对象
        final_json_output = json_array[0]
    else:
        # 如果有多个类型，输出一个JSON数组
        final_json_output = json_array

    formatted_json = json.dumps(final_json_output, ensure_ascii=False, indent=2)
    script_block = f'<script type="application/ld+json">\n{formatted_json}\n</script>'
    
    # 编辑区内容联动
    # 当选择的类型变化时，更新编辑区内容
    # 创建一个唯一的key来表示当前的选择状态
    selection_key = ",".join(sorted(selected_types))
    if 'last_selection_key' not in st.session_state or st.session_state['last_selection_key'] != selection_key:
        st.session_state['editor_content'] = script_block
        st.session_state['last_selection_key'] = selection_key

    user_script = st.text_area("请直接编辑下方完整代码，包括<script>标签", value=st.session_state['editor_content'], height=400, key="main_editor")
    st.session_state['editor_content'] = user_script
    
    # 自动提取JSON部分并校验
    def extract_json_from_full_script(s):
        try:
            # 更鲁棒的提取方法，处理前后可能存在的空格或换行
            start = s.find('{')
            end = s.rfind('}') + 1
            if start != -1 and end != 0:
                 # 尝试处理数组的情况
                if s.strip().startswith('<script type="application/ld+json">\n[') :
                    start = s.find('[')
                    end = s.rfind(']') + 1
                return s[start:end]
        except Exception:
            pass
        # 旧方法作为备用
        lines = s.strip().splitlines()
        json_lines = [line for line in lines if not line.strip().startswith('<script') and not line.strip().startswith('</script>')]
        return '\n'.join(json_lines)

    json_part = extract_json_from_full_script(user_script)
    try:
        parsed = json.loads(json_part)
        formatted = json.dumps(parsed, ensure_ascii=False, indent=2)
        st.success("格式正确！最终可用代码如下：")
        st.code(f'<script type="application/ld+json">\n{formatted}\n</script>', language='html')
        st.session_state['last_generated_code'] = f'<script type="application/ld+json">\n{formatted}\n</script>'
        # 写入历史记录
        if st.button("保存到历史记录", key="save_history"):
            st.session_state['history'].append(user_script)
            st.toast("已保存到历史记录！", icon="📜")
        if st.button("收藏当前结构化数据", key="save_fav"):
            st.session_state['favorites'].append(user_script)
            st.toast("已收藏！", icon="⭐")
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
            return extract_json_from_full_script(s) # 使用上面改进的函数
        return s
    
    if st.button("诊断分析", key="parse_btn"):
        json_part_to_diagnose = auto_extract_json(input_code)
        def diagnose_item(item, global_idx, level=0):
            prefix = "&nbsp;&nbsp;" * level * 2 # 增加缩进
            title_prefix = "#" * (3 + min(level, 2))  # h3/h4/h5
            
            # 卡片式包裹
            st.markdown(f"<div class='diagnose-card' style='margin-left: {level*20}px'>", unsafe_allow_html=True)

            if isinstance(item, dict):
                type_name = item.get('@type', '未知')
                st.markdown(f"<{title_prefix}>第[{global_idx[0]}]个结构化数据块：{type_name}</{title_prefix}>", unsafe_allow_html=True)
                
                st.markdown(f"**类型说明：** {get_type_brief(type_name)}")
                
                required = get_required_fields(type_name)
                missing = [f for f in required if f not in item]
                if missing:
                    st.warning(f"缺失必填字段：`{', '.join(missing)}`。请补充以保证结构化数据被正确识别。")
                else:
                    st.success(f"所有必填字段均已填写。")
                
                recommended = get_recommended_fields(type_name)
                rec_missing = [f for f in recommended if f not in item]
                if rec_missing:
                    st.info(f"建议补充推荐字段：`{', '.join(rec_missing)}`，有助于提升SEO效果和富摘要丰富度。")
                
                st.markdown(f"**Google富摘要支持：** {get_google_rich_snippet_support(type_name)}")

                # 其他专业建议
                if type_name == 'Product':
                    if 'offers' in item and isinstance(item['offers'], dict):
                        if 'price' not in item['offers']:
                            st.warning(f"Product的offers建议包含`price`字段，利于价格富摘要展示。")
                    if 'image' not in item:
                        st.info(f"建议为Product补充`image`字段，提升商品吸引力。")
                if type_name == 'FAQPage':
                    if 'mainEntity' in item and isinstance(item['mainEntity'], list):
                        for q_idx, q in enumerate(item['mainEntity']):
                            if 'acceptedAnswer' not in q:
                                st.warning(f"FAQ第 {q_idx+1} 个问题 (Question) 建议包含`acceptedAnswer`字段。")
            
            elif isinstance(item, list):
                 st.info(f"这是一个结构化数据数组，共包含 {len(item)} 项。")
                 for sub_item in item:
                    if isinstance(sub_item, dict):
                        global_idx[0] += 1
                        diagnose_item(sub_item, global_idx, level+1)
                    else:
                        st.warning(f"数组中包含无法识别的数据类型: {type(sub_item)}")
            else:
                 st.error(f"无法识别的数据类型: {type(item)}")

            st.markdown("</div>", unsafe_allow_html=True)

        try:
            parsed = json.loads(json_part_to_diagnose)
            items_to_diagnose = parsed if isinstance(parsed, list) else [parsed]
            global_idx = [0]
            diagnose_item(items_to_diagnose, global_idx)
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

# 高级功能Tab
with tabs[3]:
    st.header("高级功能")
    st.markdown("---")
    # 1. 结构化数据对比/差异分析
    st.subheader("结构化数据对比/差异分析")
    col1, col2 = st.columns(2)
    with col1:
        data1 = st.text_area("结构化数据1 (JSON)", height=200, key="diff1")
    with col2:
        data2 = st.text_area("结构化数据2 (JSON)", height=200, key="diff2")
    if st.button("对比并高亮差异", key="do_diff"):
        try:
            from deepdiff import DeepDiff
            # 使用更安全的JSON提取
            obj1 = json.loads(auto_extract_json(data1))
            obj2 = json.loads(auto_extract_json(data2))
            diff = DeepDiff(obj1, obj2, view='tree', ignore_order=True)
            if not diff:
                st.success("两个结构化数据完全一致！")
            else:
                st.write("差异分析结果:")
                st.json(diff.to_json())

        except Exception as e:
            st.error(f"对比失败：{e}")
    st.markdown("---")
    # 2. SEO富摘要监控与推送
    st.subheader("SEO富摘要监控与推送")
    url = st.text_input("输入网站URL进行富摘要监控", key="seo_monitor")
    if st.button("检测富摘要", key="check_rich_snippet"):
        try:
            import requests
            from bs4 import BeautifulSoup
            resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"})
            soup = BeautifulSoup(resp.text, 'html.parser')
            scripts = soup.find_all('script', type='application/ld+json')
            types = []
            if not scripts:
                st.warning("未在该URL中检测到 'application/ld+json' 类型的结构化数据。")
            else:
                for s_idx, s in enumerate(scripts):
                    try:
                        d = json.loads(s.string)
                        st.write(f"第 {s_idx+1} 个 Script 块:")
                        if isinstance(d, dict):
                            types.append(d.get('@type', '未知'))
                        elif isinstance(d, list):
                            types.extend([item.get('@type', '未知') for item in d if isinstance(item, dict)])
                        st.json(d)
                    except Exception as e:
                        st.error(f"解析第 {s_idx+1} 个 script 块失败: {e}")
                        st.code(s.string, language='json')
                st.success(f"检测完成！共发现以下类型的结构化数据：`{', '.join(types)}`")

        except Exception as e:
            st.error(f"检测失败：{e}")
    st.markdown("---")
    # 3. 结构化数据知识库/案例库
    st.subheader("结构化数据知识库/案例库")
    # 简单本地知识库
    kb = [
        {"type": "Product", "desc": "商品结构化数据案例", "json": {"@context": "https://schema.org", "@type": "Product", "name": "示例商品", "offers": {"@type": "Offer", "price": "99.99", "priceCurrency": "CNY"}}},
        {"type": "FAQPage", "desc": "FAQ结构化案例", "json": {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": "退货政策？", "acceptedAnswer": {"@type": "Answer", "text": "支持7天无理由退货。"}}]}},
        {"type": "Event", "desc": "活动结构化案例", "json": {"@context": "https://schema.org", "@type": "Event", "name": "技术大会", "startDate": "2025-12-15T09:00:00+08:00"}}
    ]
    kb_query = st.text_input("搜索schema.org字段/案例", key="kb_query")
    if kb_query:
        kb_results = [item for item in kb if kb_query.lower() in item['type'].lower() or kb_query.lower() in item['desc'].lower() or kb_query in json.dumps(item['json'])]
        for item in kb_results:
            with st.expander(f"**{item['type']}** - {item['desc']}"):
                st.code(json.dumps(item['json'], ensure_ascii=False, indent=2), language='json')
                if st.button(f"使用此模板", key=f"insert_{item['type']}"):
                    st.session_state['editor_content'] = f'<script type="application/ld+json">\n{json.dumps(item["json"], ensure_ascii=False, indent=2)}\n</script>'
                    st.toast(f"已将 {item['type']} 案例应用到编辑区！请切换到“生成/编辑”选项卡查看。")
                    st.rerun()

    st.markdown("---")
    # 4. 内容与结构一体化编辑
    st.subheader("内容与结构一体化编辑")
    content = st.text_area("网页内容编辑区", height=120, key="content_edit")
    if st.button("同步生成结构化数据", key="sync_structured"):
        try:
            # 移除了OpenAI调用，始终使用基于规则的简单生成
            if content:
                st.info("已移除AI生成功能。将根据内容生成基础的Article结构化数据。")
                st.code(json.dumps({"@context": "https://schema.org", "@type": "Article", "text": content}, ensure_ascii=False, indent=2), language='json')
            else:
                st.warning("请输入内容以生成结构化数据。")
        except Exception as e:
            st.error(f"生成失败：{e}")
    st.markdown("---")
    # 5. 行业模板市场/社区生态
    st.subheader("行业模板市场/社区生态")
    if 'market_templates' not in st.session_state:
        st.session_state['market_templates'] = []
    uploaded = st.file_uploader("上传行业结构化数据模板", type=['json'], key="market_upload")
    if uploaded:
        try:
            tpl = json.load(uploaded)
            st.session_state['market_templates'].append({"json": tpl, "score": 0, "fav": False, "name": uploaded.name})
            st.toast("模板上传成功！", icon="✅")
            st.rerun()
        except Exception as e:
            st.error(f"模板上传失败：{e}")
    
    st.write("社区模板:")
    for i, tpl in enumerate(st.session_state['market_templates']):
        with st.expander(f"模板: {tpl.get('name', '未命名')} | 评分: {tpl['score']} | {'⭐' if tpl['fav'] else '☆'}"):
            st.code(json.dumps(tpl['json'], ensure_ascii=False, indent=2), language='json')
            c1, c2, c3 = st.columns(3)
            if c1.button(f"使用", key=f"use_market_{i}"):
                st.session_state['editor_content'] = f'<script type="application/ld+json">\n{json.dumps(tpl["json"], ensure_ascii=False, indent=2)}\n</script>'
                st.toast(f"已应用模板！请切换到“生成/编辑”选项卡查看。")
                st.rerun()
            if c2.button(f"收藏", key=f"fav_market_{i}"):
                tpl['fav'] = not tpl['fav']
                st.rerun()
            if c3.button(f"评分+1", key=f"score_market_{i}"):
                tpl['score'] += 1
                st.rerun()

    st.download_button("下载示例模板", data=json.dumps({"@context": "https://schema.org", "@type": "Product", "name": "示例商品"}, ensure_ascii=False, indent=2), file_name="product_template.json")