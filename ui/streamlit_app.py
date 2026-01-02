"""
风筝设计系统 - Streamlit 前端
用户交互界面
"""

import streamlit as st
from streamlit_drawable_canvas import st_canvas
from datetime import datetime
import json

# 添加项目路径
import sys
sys.path.insert(0, '.')

from config import get_config
from services import DesignRepository, ZhipuImageService
from core import KiteScorer


# ==================== 页面配置 ====================
st.set_page_config(
    page_title="风筝设计系统",
    page_icon="🪁",
    layout="wide"
)


# ==================== 初始化 ====================
def init_session_state():
    """初始化会话状态"""
    if 'material_selections' not in st.session_state:
        st.session_state.material_selections = {
            '骨架材料': [],
            '风筝面料': [],
            '绳索材料': []
        }
    
    if 'design_count' not in st.session_state:
        st.session_state.design_count = 0
    
    if 'last_generated_image' not in st.session_state:
        st.session_state.last_generated_image = None
    
    if 'repository' not in st.session_state:
        st.session_state.repository = DesignRepository()


init_session_state()
config = get_config()


# ==================== 辅助函数 ====================
def extract_drawing_metadata(canvas_data) -> dict:
    """提取绘图元数据"""
    if canvas_data is None or canvas_data.image_data is None:
        return None
    
    objects = canvas_data.json_data.get('objects', []) if canvas_data.json_data else []
    
    return {
        'object_count': len(objects),
        'timestamp': datetime.now().isoformat(),
        'has_drawing': True,
        'object_types': list(set([obj.get('type', 'unknown') for obj in objects])) if objects else []
    }


def generate_ai_image(materials: dict):
    """生成 AI 图像"""
    try:
        service = ZhipuImageService()
        result = service.generate_kite_image({'materials': materials})
        return result
    except Exception as e:
        st.error(f"图像生成失败: {str(e)}")
        return None


def upload_design(canvas_data, materials, ai_image_url=None):
    """上传设计"""
    try:
        drawing_metadata = extract_drawing_metadata(canvas_data)
        
        new_design = {
            'design_id': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'drawing': drawing_metadata,
            'materials': materials,
            'ai_image_url': ai_image_url,
            'created_at': datetime.now().isoformat()
        }
        
        if st.session_state.repository.add_design(new_design):
            st.session_state.design_count = len(
                st.session_state.repository.get_all_designs()
            )
            return True
        
        return False
        
    except Exception as e:
        st.error(f"上传失败: {str(e)}")
        return False


# ==================== 主界面 ====================
st.title("🪁 风筝设计系统")
st.caption("设计你的风筝，获取实时评分反馈")

# 侧边栏 - 材料选择
with st.sidebar:
    st.header("📦 材料选择")
    
    materials_config = config.materials.categories
    
    for category, options in materials_config.items():
        st.subheader(f"• {category}")
        selected = st.multiselect(
            f"选择{category}",
            options=options,
            default=st.session_state.material_selections[category],
            key=f"mat_{category}"
        )
        st.session_state.material_selections[category] = selected
        
        if selected:
            st.success(f"已选: {', '.join(selected)}")
        else:
            st.info("未选择")
        
        st.divider()
    
    # Bin 信息
    st.subheader("☁️ 存储信息")
    bin_id = st.session_state.repository.bin_id
    
    if bin_id:
        st.code(bin_id[:25] + "...")
        st.metric("设计数量", st.session_state.design_count)
    else:
        st.info("还未创建存储")
    
    st.divider()
    
    if st.button("🔄 重置存储"):
        st.session_state.repository.clear_bin_id()
        st.warning("存储已重置")
        st.rerun()

# 主界面布局
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🖌️ 绘图区")
    
    # 绘图工具栏
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        stroke_width = st.slider("笔触粗细", 1, 25, 3)
    with col_b:
        stroke_color = st.color_picker("笔触颜色", "#000000")
    with col_c:
        drawing_mode = st.selectbox(
            "工具",
            ("freedraw", "line", "rect", "circle", "transform")
        )
    
    # 绘图画布
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color="#FFFFFF",
        height=500,
        width=700,
        drawing_mode=drawing_mode,
        key="canvas",
    )

with col2:
    st.subheader("📋 预览")
    
    # 材料预览
    with st.expander("📦 已选材料", expanded=True):
        has_materials = False
        for category, selected in st.session_state.material_selections.items():
            if selected:
                has_materials = True
                st.write(f"**{category}:**")
                for item in selected:
                    st.write(f"  • {item}")
        
        if not has_materials:
            st.info("还未选择材料")
    
    st.divider()
    
    # 绘图预览
    if canvas_result.image_data is not None:
        st.write("**绘图预览:**")
        st.image(canvas_result.image_data, use_container_width=True)
        
        if canvas_result.json_data:
            obj_count = len(canvas_result.json_data.get('objects', []))
            st.metric("对象数", obj_count)
    else:
        st.info("👈 开始绘制")

# AI 图像生成区
st.divider()
st.subheader("🎨 AI 图像生成")

col_ai1, col_ai2 = st.columns([1, 2])

with col_ai1:
    can_generate = any(st.session_state.material_selections.values())
    
    if st.button(
        "🚀 生成 AI 风筝图片",
        type="primary",
        use_container_width=True,
        disabled=not can_generate
    ):
        with st.spinner("🎨 AI 正在生成图片...（约 10-30 秒）"):
            result = generate_ai_image(st.session_state.material_selections)
            
            if result:
                st.session_state.last_generated_image = result
                st.success("✅ 生成成功！")
            else:
                st.error("❌ 生成失败")

with col_ai2:
    if st.session_state.last_generated_image:
        st.image(
            st.session_state.last_generated_image['url'],
            caption="AI 生成的风筝效果图",
            use_container_width=True
        )

# 保存区域
st.divider()
col_x, col_y, col_z = st.columns([1, 2, 1])

with col_y:
    st.subheader("☁️ 保存设计")
    
    has_drawing = canvas_result.image_data is not None
    has_materials = any(st.session_state.material_selections.values())
    
    # 状态指示
    # 状态指示
    c1, c2, c3 = st.columns(3)
    with c1:
        if has_drawing:
            st.success("✅ 已绘制")
        else:
            st.warning("⚠️ 未绘制")
    with c2:
        if has_materials:
            st.success("✅ 已选材料")
        else:
            st.warning("⚠️ 未选材料")
    
    # 保存按钮
    if st.button(
        "💾 保存完整设计",
        type="secondary",
        use_container_width=True,
        disabled=not (has_drawing or has_materials)
    ):
        ai_url = st.session_state.last_generated_image['url'] if st.session_state.last_generated_image else None
        
        with st.spinner("正在保存..."):
            if upload_design(canvas_result, st.session_state.material_selections, ai_url):
                st.balloons()
                st.success("🎉 设计已保存！")

# 使用说明
with st.expander("📖 使用指南"):
    st.markdown("""
    ### 🎯 完整流程
    
    1. **绘制草图** - 在画布上画出风筝的基本形状
    2. **选择材料** - 在左侧选择骨架、面料、绳索材料
    3. **生成 AI 图片** - 点击生成按钮，AI 会根据材料生成效果图
    4. **保存设计** - 保存到云端，实时评分系统会自动评分
    
    ### 📊 评分系统
    
    保存后，评分系统会根据以下维度打分：
    - **性能 (40%)**: 飞行稳定性、结构强度、抗风能力
    - **可行性 (30%)**: 重量/面积比是否合理
    - **成本 (20%)**: 材料成本
    - **创新 (10%)**: 材料组合多样性
    
    ### 🪁 渡河动画
    
    打开渡河动画页面，会实时监听新设计并播放动画：
    - **≥80 分**: 渡河成功 🎉
    - **50-79 分**: 勉强渡河 😅
    - **<50 分**: 渡河失败 💦
    """)
