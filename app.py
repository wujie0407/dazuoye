"""
风筝设计系统 - 轻量版
只保存关键数据（材料+参数），不保存图片
完美适配 JSONBin 免费版 100KB 限制
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

# 固定的 Bin ID
FIXED_BIN_FILE = "fixed_bin_id.txt"

# 初始化
if 'fixed_bin_id' not in st.session_state:
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

st.title("🪁 风筝设计系统 - 轻量版")
st.caption("只保存关键数据，完美适配免费版")


def save_fixed_bin_id(bin_id: str):
    """保存固定的 Bin ID"""
    try:
        with open(FIXED_BIN_FILE, 'w') as f:
            f.write(bin_id)
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


def extract_drawing_metadata(canvas_data) -> dict:
    """
    只提取绘图的元数据，不保存图片
    
    Returns:
        轻量级元数据
    """
    if canvas_data is None or canvas_data.image_data is None:
        return None
    
    # 计算简单的几何参数
    objects = canvas_data.json_data.get('objects', []) if canvas_data.json_data else []
    
    # 提取关键信息
    metadata = {
        'object_count': len(objects),
        'timestamp': datetime.now().isoformat(),
        'has_drawing': True
    }
    
    # 尝试提取基本尺寸（如果有路径数据）
    if objects:
        # 简单统计
        metadata['object_types'] = list(set([obj.get('type', 'unknown') for obj in objects]))
    
    return metadata


def upload_design(canvas_data, materials):
    """上传轻量级设计数据"""
    try:
        service = JSONBinService(API_KEY)
        
        # 只提取元数据，不保存图片
        drawing_metadata = extract_drawing_metadata(canvas_data)
        
        # 创建轻量级设计对象
        new_design = {
            'design_id': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'drawing': drawing_metadata,  # 只有元数据，无图片
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
                    'total_designs': 1,
                    'version': 'lightweight'
                }
            }
            
            result = service.create_bin(complete_data, bin_name="kite_designs_lightweight")
            st.session_state.fixed_bin_id = result['metadata']['id']
            save_fixed_bin_id(st.session_state.fixed_bin_id)
            
            st.success(f"✅ 首次创建！Bin ID: {st.session_state.fixed_bin_id[:20]}...")
            st.info("💡 轻量版：只保存材料和参数，不保存图片")
            
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
                    'total_designs': len(existing_designs),
                    'version': 'lightweight'
                }
            }
            
            # 估算大小
            data_size = len(json.dumps(complete_data))
            
            if data_size > 95000:  # 留5KB余量
                st.error(f"❌ 数据接近100KB限制 (当前 {data_size/1024:.1f}KB)")
                st.warning("建议：重置Bin或删除旧设计")
                return False
            
            # 更新 Bin
            service.update_bin(st.session_state.fixed_bin_id, complete_data)
            
            st.success(f"✅ 设计已添加！当前共 {len(existing_designs)} 个设计")
            st.caption(f"数据大小: {data_size/1024:.1f}KB / 100KB")
        
        st.session_state.last_upload_time = datetime.now().strftime("%H:%M:%S")
        st.session_state.design_count = len(get_existing_designs(service, st.session_state.fixed_bin_id))
        
        return True
        
    except Exception as e:
        error_msg = str(e)
        
        if "100kb" in error_msg.lower():
            st.error("❌ 超出免费版100KB限制！")
            st.warning("解决方案：")
            st.info("1. 点击侧边栏'重置 Bin ID'开始新的收藏集")
            st.info("2. 或升级到 JSONBin Pro 版本")
        else:
            st.error(f"❌ 上传失败: {error_msg}")
        
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
        
        # 显示使用情况
        try:
            service = JSONBinService(API_KEY)
            designs = get_existing_designs(service, st.session_state.fixed_bin_id)
            if designs:
                data_size = len(json.dumps({'designs': designs}))
                usage_percent = (data_size / 100000) * 100
                
                st.progress(usage_percent / 100)
                st.caption(f"使用: {data_size/1024:.1f}KB / 100KB ({usage_percent:.1f}%)")
                
                if usage_percent > 80:
                    st.warning("⚠️ 接近容量上限！")
        except:
            pass
    else:
        st.info("还未创建 Bin")
    
    # 重置按钮
    st.divider()
    if st.button("🔄 重置 Bin ID", help="创建新的收藏集"):
        st.session_state.fixed_bin_id = None
        try:
            import os
            os.remove(FIXED_BIN_FILE)
            os.remove('latest_bin.txt')
        except:
            pass
        st.warning("Bin ID 已重置")
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
    
    st.info("💡 轻量版：图片不保存，只记录设计参数")

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

# 使用说明
with st.expander("📖 使用指南 - 轻量版"):
    st.markdown("""
    ### 🎯 轻量版特性
    
    **为什么需要轻量版？**
    - JSONBin 免费版限制：单个 Bin 最大 100KB
    - 带图片的设计：每个约 30-50KB
    - 只能保存 2-3 个设计就超限 ❌
    
    **轻量版解决方案：**
    - ✅ 只保存材料选择
    - ✅ 只保存绘图参数（对象数、类型）
    - ✅ 不保存图片（节省 90%+ 空间）
    - ✅ 可以保存 50+ 个设计
    
    ### 📊 数据对比
    
    **完整版（带图片）：**
    ```json
    {
      "drawing": {
        "image": "data:image/png;base64,iVBORw0KG..." // 30KB
      }
    }
    ```
    单个设计：~40KB
    
    **轻量版（无图片）：**
    ```json
    {
      "drawing": {
        "object_count": 5,
        "has_drawing": true
      },
      "materials": {...}
    }
    ```
    单个设计：~1KB
    
    ### ✨ 评分系统完全兼容
    
    评分系统只需要：
    - ✅ 材料选择
    - ✅ 绘图参数（可以从元数据推算）
    
    不需要图片！所以评分完全正常工作。
    
    ### 💡 使用建议
    
    **如果你需要保存图片：**
    1. 在本地截图保存
    2. 或使用其他图床服务
    3. 或升级 JSONBin Pro（100KB → 1MB）
    
    **如果只需要评分和参数：**
    - 轻量版完美适配！
    """)