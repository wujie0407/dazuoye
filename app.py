"""
风筝设计系统 - 真·自动上传版 + 智能追踪
画完 → 自动保存 → 选材料 → 一键上传 → 自动保存Bin ID供评分系统使用
使用 streamlit-drawable-canvas 组件
"""

import streamlit as st
from streamlit_drawable_canvas import st_canvas
import json
from datetime import datetime
from PIL import Image
import io
import base64

from jsonbin import JSONBinService

# 页面配置
st.set_page_config(
    page_title="风筝设计系统",
    page_icon="🪁",
    layout="wide"
)

# API 配置
API_KEY = "$2a$10$pleOacf0lQu1mvIU//jjfeYPUCb.kiFXX.08qupD/90UYKwHtU8e."
BIN_ID = ""

# 初始化
if 'current_bin_id' not in st.session_state:
    st.session_state.current_bin_id = BIN_ID
if 'last_upload_time' not in st.session_state:
    st.session_state.last_upload_time = None
if 'material_selections' not in st.session_state:
    st.session_state.material_selections = {
        '骨架材料': [],
        '风筝面料': [],
        '绳索材料': []
    }

# 材料数据库
MATERIALS = {
    '骨架材料': ['竹子', '铝合金', '碳纤维'],
    '风筝面料': ['丝绸', '尼龙', 'Mylar膜'],
    '绳索材料': ['麻绳', '钢索', '凯夫拉']
}

st.title("🪁 风筝设计系统")
st.caption("画完自动保存 → 选材料 → 一键上传 → 自动追踪")

# 保存 Bin ID 供评分系统使用
def save_bin_id_for_scorer(bin_id: str):
    """保存 Bin ID 到文件，供评分系统读取"""
    try:
        with open('latest_bin.txt', 'w') as f:
            f.write(bin_id)
    except:
        pass

# 上传函数
def upload_complete_design(canvas_data, materials):
    try:
        # 转换画布数据
        if canvas_data is not None and canvas_data.image_data is not None:
            # 将 numpy 数组转为 PIL Image
            img = Image.fromarray(canvas_data.image_data.astype('uint8'), 'RGBA')
            
            # 转为 base64
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            drawing_data = {
                'image': f"data:image/png;base64,{img_str}",
                'canvas_data': {
                    'objects': canvas_data.json_data['objects'] if canvas_data.json_data else [],
                    'background': canvas_data.json_data['background'] if canvas_data.json_data else None
                },
                'statistics': {
                    'objectCount': len(canvas_data.json_data['objects']) if canvas_data.json_data else 0
                },
                'timestamp': datetime.now().isoformat()
            }
        else:
            drawing_data = None
        
        complete_data = {
            'drawing': drawing_data,
            'materials': materials,
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'design_type': '风筝设计'
            }
        }
        
        service = JSONBinService(API_KEY)
        
        if st.session_state.current_bin_id:
            try:
                service.update_bin(st.session_state.current_bin_id, complete_data)
                st.success("✅ 设计已更新！")
                st.session_state.last_upload_time = datetime.now().strftime("%H:%M:%S")
                
                # 保存 Bin ID
                save_bin_id_for_scorer(st.session_state.current_bin_id)
                
                return True
            except Exception as e:
                if "404" in str(e):
                    result = service.create_bin(complete_data)
                    st.session_state.current_bin_id = result['metadata']['id']
                    
                    # 保存 Bin ID
                    save_bin_id_for_scorer(st.session_state.current_bin_id)
                    
                    st.success(f"✅ 设计已保存！Bin: {st.session_state.current_bin_id[:20]}...")
                    st.info("💡 评分系统现在可以自动监控这个 Bin 了！")
                    st.session_state.last_upload_time = datetime.now().strftime("%H:%M:%S")
                    return True
                raise
        else:
            result = service.create_bin(complete_data)
            st.session_state.current_bin_id = result['metadata']['id']
            
            # 保存 Bin ID
            save_bin_id_for_scorer(st.session_state.current_bin_id)
            
            st.success(f"✅ 设计已保存！Bin: {st.session_state.current_bin_id[:20]}...")
            st.info("💡 评分系统现在可以自动监控这个 Bin 了！")
            st.session_state.last_upload_time = datetime.now().strftime("%H:%M:%S")
            return True
    except Exception as e:
        st.error(f"❌ 上传失败: {str(e)}")
        import traceback
        with st.expander("查看详细错误"):
            st.code(traceback.format_exc())
        return False

# 侧边栏
with st.sidebar:
    st.header("📦 材料选择")
    
    for category, options in MATERIALS.items():
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
    
    st.subheader("☁️ 上传记录")
    if st.session_state.current_bin_id:
        st.code(st.session_state.current_bin_id[:25] + "...")
        if st.session_state.last_upload_time:
            st.caption(f"最后: {st.session_state.last_upload_time}")
    else:
        st.info("还未上传")

# 主界面
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🖌️ 绘图区")
    
    # 画笔设置
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
    
    # 创建画布
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
    
    st.info("💡 画完后，直接选择材料并点击下方'上传完整设计'按钮")

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
    
    # 图形预览
    st.divider()
    if canvas_result.image_data is not None:
        st.write("**绘图预览:**")
        st.image(canvas_result.image_data, use_container_width=True)
        
        if canvas_result.json_data:
            obj_count = len(canvas_result.json_data.get('objects', []))
            st.metric("对象数", obj_count)
    else:
        st.info("👈 开始绘制")

# 上传按钮
st.divider()
col_x, col_y, col_z = st.columns([1, 2, 1])

with col_y:
    st.subheader("☁️ 上传完整设计")
    
    has_drawing = canvas_result.image_data is not None
    has_materials = any(st.session_state.material_selections.values())
    
    c1, c2 = st.columns(2)
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
    
    if st.button("🚀 上传完整设计", type="primary", use_container_width=True, 
                 disabled=not (has_drawing or has_materials)):
        with st.spinner("正在上传..."):
            if upload_complete_design(canvas_result, st.session_state.material_selections):
                st.balloons()
                st.success("🎉 设计已成功上传到云端！")
                st.info("💡 现在可以启动评分系统监控这个设计了")

# 使用说明
with st.expander("📖 使用指南"):
    st.markdown("""
    ### 🎯 完整流程（超简单！）
    
    **步骤 1：绘制设计**
    - 在画布上自由绘制
    - 可以选择不同工具（画笔、直线、矩形、圆形）
    - 调整笔触粗细和颜色
    
    **步骤 2：选择材料**
    - 在左侧边栏选择三类材料
    - 每类支持多选
    
    **步骤 3：上传**
    - 点击"🚀 上传完整设计"按钮
    - 完成！
    
    **步骤 4：启动评分系统**
    - 打开新终端
    - 运行: `python smart_scorer.py`
    - 评分系统会自动监控这个 Bin
    
    ### ✨ 特点
    
    - **自动保存**：画完就保存，无需下载文件
    - **实时预览**：右侧即时预览
    - **一键上传**：图形和材料一起上传
    - **智能追踪**：自动保存 Bin ID 供评分系统使用
    - **手机友好**：完全适配手机操作
    
    ### 🛠️ 绘图工具
    
    - **freedraw**：自由绘制
    - **line**：画直线
    - **rect**：画矩形
    - **circle**：画圆形
    - **transform**：移动/调整对象
    """)