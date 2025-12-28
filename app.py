"""
风筝设计系统 - 单Bin版
所有设计都上传到同一个 Bin，自动累加
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

# 固定的 Bin ID（第一次会自动创建）
FIXED_BIN_FILE = "fixed_bin_id.txt"

# 初始化
if 'fixed_bin_id' not in st.session_state:
    # 尝试从文件读取
    try:
        with open(FIXED_BIN_FILE, 'r') as f:
            st.session_state.fixed_bin_id = f.read().strip()
    except:
        st.session_state.fixed_bin_id = None

if 'last_upload_time' not in st.session_state:
    st.session_state.last_upload_time = None

if 'material_selections' not in st.session_state:
    st.session_state.material_selections = {
        '骨架材料': [],
        '风筝面料': [],
        '绳索材料': []
    }

if 'design_count' not in st.session_state:
    st.session_state.design_count = 0

# 材料数据库
MATERIALS = {
    '骨架材料': ['竹子', '铝合金', '碳纤维'],
    '风筝面料': ['丝绸', '尼龙', 'Mylar膜'],
    '绳索材料': ['麻绳', '钢索', '凯夫拉']
}

st.title("🪁 风筝设计系统 - 单Bin版")
st.caption("所有设计都保存在同一个 Bin 中，自动累加")


def save_fixed_bin_id(bin_id: str):
    """保存固定的 Bin ID"""
    try:
        with open(FIXED_BIN_FILE, 'w') as f:
            f.write(bin_id)
        # 同时保存到 latest_bin.txt 供评分系统使用
        with open('latest_bin.txt', 'w') as f:
            f.write(bin_id)
    except Exception as e:
        st.warning(f"保存 Bin ID 失败: {str(e)}")


def get_existing_designs(service: JSONBinService, bin_id: str) -> list:
    """获取已有的设计列表"""
    try:
        response = service.read_bin(bin_id)
        data = response.get('record', response)
        return data.get('designs', [])
    except Exception as e:
        print(f"读取已有设计失败: {str(e)}")
        return []


def upload_design(canvas_data, materials):
    """上传设计到固定的 Bin"""
    try:
        service = JSONBinService(API_KEY)
        
        # 转换画布数据
        if canvas_data is not None and canvas_data.image_data is not None:
            img = Image.fromarray(canvas_data.image_data.astype('uint8'), 'RGBA')
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
        
        # 创建新设计对象
        new_design = {
            'design_id': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'drawing': drawing_data,
            'materials': materials,
            'created_at': datetime.now().isoformat()
        }
        
        # 如果没有固定 Bin，创建新的
        if not st.session_state.fixed_bin_id:
            complete_data = {
                'designs': [new_design],
                'metadata': {
                    'created_at': datetime.now().isoformat(),
                    'last_updated': datetime.now().isoformat(),
                    'total_designs': 1
                }
            }
            
            result = service.create_bin(complete_data, bin_name="kite_designs_collection")
            st.session_state.fixed_bin_id = result['metadata']['id']
            save_fixed_bin_id(st.session_state.fixed_bin_id)
            
            st.success(f"✅ 首次创建！Bin ID: {st.session_state.fixed_bin_id[:20]}...")
            st.info("💡 后续所有设计都会保存到这个 Bin")
            
        else:
            # 读取已有设计
            existing_designs = get_existing_designs(service, st.session_state.fixed_bin_id)
            
            # 添加新设计
            existing_designs.append(new_design)
            
            # 更新完整数据
            complete_data = {
                'designs': existing_designs,
                'metadata': {
                    'created_at': existing_designs[0]['created_at'] if existing_designs else datetime.now().isoformat(),
                    'last_updated': datetime.now().isoformat(),
                    'total_designs': len(existing_designs)
                }
            }
            
            # 更新 Bin
            service.update_bin(st.session_state.fixed_bin_id, complete_data)
            
            st.success(f"✅ 设计已添加！当前共 {len(existing_designs)} 个设计")
        
        st.session_state.last_upload_time = datetime.now().strftime("%H:%M:%S")
        st.session_state.design_count = len(get_existing_designs(service, st.session_state.fixed_bin_id))
        
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
    
    st.subheader("☁️ Bin 信息")
    if st.session_state.fixed_bin_id:
        st.code(st.session_state.fixed_bin_id[:25] + "...")
        st.metric("设计数量", st.session_state.design_count)
        if st.session_state.last_upload_time:
            st.caption(f"最后上传: {st.session_state.last_upload_time}")
    else:
        st.info("还未创建 Bin")
    
    # 重置按钮
    st.divider()
    if st.button("🔄 重置 Bin ID", help="创建新的 Bin（慎用！）"):
        st.session_state.fixed_bin_id = None
        try:
            import os
            os.remove(FIXED_BIN_FILE)
            os.remove('latest_bin.txt')
        except:
            pass
        st.warning("Bin ID 已重置，下次上传将创建新 Bin")
        st.rerun()

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
    
    st.info("💡 所有设计都会保存到同一个 Bin 中")

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
    st.subheader("☁️ 添加到收藏集")
    
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
    
    if st.button("🚀 添加设计", type="primary", use_container_width=True, 
                 disabled=not (has_drawing or has_materials)):
        with st.spinner("正在上传..."):
            if upload_design(canvas_result, st.session_state.material_selections):
                st.balloons()
                st.success("🎉 设计已添加到收藏集！")

# 使用说明
with st.expander("📖 使用指南"):
    st.markdown("""
    ### 🎯 单Bin模式说明
    
    **与之前的区别：**
    - ❌ 旧版：每次上传创建新 Bin
    - ✅ 新版：所有设计保存在同一个 Bin
    
    **优势：**
    1. **统一管理** - 所有设计在一个地方
    2. **历史记录** - 自动保存设计历史
    3. **评分友好** - 评分系统只需监控一个 Bin
    4. **节省空间** - 不会创建大量 Bin
    
    ### 📋 使用流程
    
    **首次使用：**
    1. 绘制设计 + 选材料
    2. 点击"添加设计"
    3. 系统自动创建固定 Bin
    4. Bin ID 保存到 `fixed_bin_id.txt`
    
    **后续使用：**
    1. 绘制新设计 + 选材料
    2. 点击"添加设计"
    3. 新设计添加到现有 Bin ✅
    
    ### 🔧 数据结构
    
    ```json
    {
      "designs": [
        {
          "design_id": "20241228_143015",
          "drawing": {...},
          "materials": {...},
          "created_at": "2024-12-28T14:30:15"
        },
        {
          "design_id": "20241228_143520",
          "drawing": {...},
          "materials": {...},
          "created_at": "2024-12-28T14:35:20"
        }
      ],
      "metadata": {
        "total_designs": 2,
        "last_updated": "2024-12-28T14:35:20"
      }
    }
    ```
    
    ### ⚠️ 重置 Bin
    
    如果需要重新开始（清空所有设计）：
    1. 点击侧边栏的"🔄 重置 Bin ID"
    2. 下次上传会创建新的 Bin
    
    **注意：** 旧 Bin 不会被删除，只是不再使用
    """)