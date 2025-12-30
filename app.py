"""
风筝设计系统 - AI 图像生成版
轻量版 + 智谱 AI 图像生成
"""

import streamlit as st
from streamlit_drawable_canvas import st_canvas
import json
from datetime import datetime
from PIL import Image
import io
import base64

from jsonbin import JSONBinService
from zhipu_image import ZhipuImageGenerator

# 页面配置
st.set_page_config(
    page_title="风筝设计系统 - AI生成",
    page_icon="🪁",
    layout="wide"
)

# API 配置
JSONBIN_API_KEY = "$2a$10$pleOacf0lQu1mvIU//jjfeYPUCb.kiFXX.08qupD/90UYKwHtU8e."
ZHIPU_API_KEY = "b91a0c07fd0640f488491d6bd0fa4e7f.z5j8U7iiyrWkO5sc"

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

if 'last_generated_image' not in st.session_state:
    st.session_state.last_generated_image = None

if 'generating_image' not in st.session_state:
    st.session_state.generating_image = False

# 材料数据库
MATERIALS = {
    '骨架材料': ['竹子', '铝合金', '碳纤维'],
    '风筝面料': ['丝绸', '尼龙', 'Mylar膜'],
    '绳索材料': ['麻绳', '钢索', '凯夫拉']
}

st.title("🪁 风筝设计系统 - AI 图像生成")
st.caption("轻量版 + 智谱 AI 图像生成")


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
    """只提取绘图的元数据"""
    if canvas_data is None or canvas_data.image_data is None:
        return None
    
    objects = canvas_data.json_data.get('objects', []) if canvas_data.json_data else []
    
    metadata = {
        'object_count': len(objects),
        'timestamp': datetime.now().isoformat(),
        'has_drawing': True
    }
    
    if objects:
        metadata['object_types'] = list(set([obj.get('type', 'unknown') for obj in objects]))
    
    return metadata


def generate_ai_image(materials: dict) -> dict:
    """生成 AI 图像"""
    try:
        generator = ZhipuImageGenerator(ZHIPU_API_KEY)
        
        design_data = {'materials': materials}
        
        result = generator.generate_kite_image(design_data, size="1024x1024")
        
        return result
        
    except Exception as e:
        st.error(f"图像生成失败: {str(e)}")
        return None


def upload_design(canvas_data, materials, ai_image_url=None):
    """上传轻量级设计数据"""
    try:
        service = JSONBinService(JSONBIN_API_KEY)
        
        drawing_metadata = extract_drawing_metadata(canvas_data)
        
        # 创建轻量级设计对象
        new_design = {
            'design_id': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'drawing': drawing_metadata,
            'materials': materials,
            'ai_image_url': ai_image_url,  # 保存 AI 生成的图片 URL
            'created_at': datetime.now().isoformat()
        }
        
        if not st.session_state.fixed_bin_id:
            complete_data = {
                'designs': [new_design],
                'metadata': {
                    'created_at': datetime.now().isoformat(),
                    'last_updated': datetime.now().isoformat(),
                    'total_designs': 1,
                    'version': 'lightweight_ai'
                }
            }
            
            result = service.create_bin(complete_data, bin_name="kite_designs_ai")
            st.session_state.fixed_bin_id = result['metadata']['id']
            save_fixed_bin_id(st.session_state.fixed_bin_id)
            
            st.success(f"✅ 首次创建！Bin ID: {st.session_state.fixed_bin_id[:20]}...")
            
        else:
            existing_designs = get_existing_designs(service, st.session_state.fixed_bin_id)
            existing_designs.append(new_design)
            
            complete_data = {
                'designs': existing_designs,
                'metadata': {
                    'created_at': existing_designs[0]['created_at'] if existing_designs else datetime.now().isoformat(),
                    'last_updated': datetime.now().isoformat(),
                    'total_designs': len(existing_designs),
                    'version': 'lightweight_ai'
                }
            }
            
            data_size = len(json.dumps(complete_data))
            
            if data_size > 95000:
                st.error(f"❌ 数据接近100KB限制 (当前 {data_size/1024:.1f}KB)")
                st.warning("建议：重置Bin或删除旧设计")
                return False
            
            try:
                service.update_bin(st.session_state.fixed_bin_id, complete_data)
                st.success(f"✅ 设计已添加！当前共 {len(existing_designs)} 个设计")
                st.caption(f"数据大小: {data_size/1024:.1f}KB / 100KB")
            except Exception as update_error:
                if "404" in str(update_error) or "not found" in str(update_error).lower():
                    st.warning("⚠️ 原 Bin 已删除，正在创建新 Bin...")
                    st.session_state.fixed_bin_id = None
                    
                    result = service.create_bin(complete_data, bin_name="kite_designs_ai")
                    st.session_state.fixed_bin_id = result['metadata']['id']
                    save_fixed_bin_id(st.session_state.fixed_bin_id)
                    
                    st.success(f"✅ 新 Bin 已创建！")
                else:
                    raise
        
        st.session_state.last_upload_time = datetime.now().strftime("%H:%M:%S")
        st.session_state.design_count = len(get_existing_designs(service, st.session_state.fixed_bin_id))
        
        return True
        
    except Exception as e:
        error_msg = str(e)
        
        if "100kb" in error_msg.lower():
            st.error("❌ 超出免费版100KB限制！")
            st.info("点击侧边栏'重置 Bin ID'开始新的收藏集")
        else:
            st.error(f"❌ 上传失败: {error_msg}")
        
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
    
    st.divider()
    if st.button("🔄 重置 Bin ID"):
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
    if canvas_result.image_data is not None:
        st.write("**绘图预览:**")
        st.image(canvas_result.image_data, use_container_width=True)
        
        if canvas_result.json_data:
            obj_count = len(canvas_result.json_data.get('objects', []))
            st.metric("对象数", obj_count)
    else:
        st.info("👈 开始绘制")

# AI 图像生成区域
st.divider()
st.subheader("🎨 AI 图像生成")

col_ai1, col_ai2 = st.columns([1, 2])

with col_ai1:
    if st.button("🚀 生成 AI 风筝图片", type="primary", use_container_width=True,
                 disabled=not any(st.session_state.material_selections.values())):
        
        st.session_state.generating_image = True
        
        with st.spinner("🎨 AI 正在生成图片...（需要 10-30 秒）"):
            result = generate_ai_image(st.session_state.material_selections)
            
            if result:
                st.session_state.last_generated_image = result
                st.success("✅ 生成成功！")
            else:
                st.error("❌ 生成失败")
        
        st.session_state.generating_image = False

with col_ai2:
    if st.session_state.last_generated_image:
        st.image(
            st.session_state.last_generated_image['url'],
            caption="AI 生成的风筝效果图",
            use_container_width=True
        )

# 上传按钮
st.divider()
col_x, col_y, col_z = st.columns([1, 2, 1])

with col_y:
    st.subheader("☁️ 保存设计")
    
    has_drawing = canvas_result.image_data is not None
    has_materials = any(st.session_state.material_selections.values())
    
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
    
    with c3:
        if st.session_state.last_generated_image:
            st.success("✅ 已生成AI图")
        else:
            st.info("未生成")
    
    if st.button("💾 保存完整设计", type="secondary", use_container_width=True, 
                 disabled=not (has_drawing or has_materials)):
        
        ai_url = st.session_state.last_generated_image['url'] if st.session_state.last_generated_image else None
        
        with st.spinner("正在保存..."):
            if upload_design(canvas_result, st.session_state.material_selections, ai_url):
                st.balloons()
                st.success("🎉 设计已保存！")
                
                if ai_url:
                    st.info("💡 AI 图片URL已保存，评分系统可以显示")

# 使用说明
with st.expander("📖 使用指南 - AI 图像生成版"):
    st.markdown("""
    ### 🎯 完整流程
    
    **步骤 1：绘制草图**
    - 在画布上画出风筝的基本形状
    
    **步骤 2：选择材料**
    - 在左侧选择骨架、面料、绳索材料
    
    **步骤 3：生成 AI 图片**
    - 点击"🚀 生成 AI 风筝图片"
    - 等待 10-30 秒
    - AI 会根据你的材料选择生成逼真的风筝图片
    
    **步骤 4：保存设计**
    - 点击"💾 保存完整设计"
    - 草图、材料、AI图片 URL 都会保存
    
    ### ✨ AI 图像生成
    
    **智谱 AI CogView-4：**
    - 高质量 1024x1024 图片
    - 根据材料自动生成提示词
    - 真实的风筝效果展示
    
    **生成逻辑：**
    ```
    竹子 → "竹制骨架，自然的竹节纹理"
    丝绸 → "丝绸材质，柔软光滑，带有自然光泽"
    麻绳 → "天然麻绳，粗糙质感"
    
    组合成完整提示词 → AI 生成
    ```
    
    ### 💾 数据存储
    
    保存内容：
    - ✅ 绘图参数（轻量）
    - ✅ 材料选择
    - ✅ AI 图片 URL（智谱提供的链接）
    
    **注意：** AI 图片不保存在 JSONBin，只保存 URL
    
    ### 📊 评分系统
    
    评分系统会：
    1. 读取材料数据
    2. 计算评分
    3. 如果有 AI 图片 URL，可以显示效果图
    """)