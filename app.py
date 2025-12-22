"""
手绘画板 Streamlit 应用 - 简化版（内置配置）
"""

import streamlit as st
import streamlit.components.v1 as components
import json
from datetime import datetime

from canvas import CanvasComponent
from jsonbin import JSONBinService
from image_handler import ImageHandler

# 页面配置
st.set_page_config(
    page_title="手绘画板",
    page_icon="🎨",
    layout="wide"
)

# ==========================================
# 直接设置 API Key（临时方案）
# ==========================================
API_KEY = "$2a$10$pleOacf0lQU1mvIU//jjfeYPUCb.kdFXX.08qupD/90UYKwHtU8e."
BIN_ID = ""

# 初始化 session state
if 'drawing_data' not in st.session_state:
    st.session_state.drawing_data = None
if 'last_upload_time' not in st.session_state:
    st.session_state.last_upload_time = None
if 'current_bin_id' not in st.session_state:
    st.session_state.current_bin_id = BIN_ID
if 'auto_upload' not in st.session_state:
    st.session_state.auto_upload = True

# 标题
st.title("🎨 手绘画板 - 自动云端存储")

# 定义上传函数
def upload_to_jsonbin(data):
    """自动上传到 JSONBin"""
    try:
        service = JSONBinService(API_KEY)
        
        if st.session_state.current_bin_id:
            # 更新已有 Bin
            try:
                result = service.update_bin(st.session_state.current_bin_id, data)
                st.success(f"✅ 已更新到 Bin: {st.session_state.current_bin_id}")
                st.session_state.last_upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            except Exception as update_error:
                # 如果 404，创建新的
                if "404" in str(update_error):
                    result = service.create_bin(data)
                    new_bin_id = result['metadata']['id']
                    st.session_state.current_bin_id = new_bin_id
                    st.success(f"✅ 已创建新 Bin: {new_bin_id}")
                    st.session_state.last_upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                else:
                    raise
        else:
            # 创建新 Bin
            result = service.create_bin(data)
            new_bin_id = result['metadata']['id']
            st.session_state.current_bin_id = new_bin_id
            st.success(f"✅ 已创建新 Bin: {new_bin_id}")
            st.info("💡 Bin ID 已保存，下次会自动更新到同一个 Bin")
            st.session_state.last_upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
    except Exception as e:
        st.error(f"❌ 上传失败: {str(e)}")
        import traceback
        with st.expander("查看详细错误"):
            st.code(traceback.format_exc())

# 侧边栏配置
with st.sidebar:
    st.header("⚙️ 画布配置")
    
    # 画笔设置
    pen_width = st.slider("笔触粗细", 1, 20, 3)
    pen_color = st.color_picker("笔触颜色", "#000000")
    bg_color = st.color_picker("背景颜色", "#FFFFFF")
    
    # 画布尺寸
    st.subheader("画布尺寸")
    canvas_width = st.number_input("宽度", 400, 1200, 800, step=50)
    canvas_height = st.number_input("高度", 300, 800, 600, step=50)
    
    st.divider()
    
    # 自动上传设置
    st.header("☁️ 自动上传")
    st.session_state.auto_upload = st.checkbox(
        "启用自动上传",
        value=st.session_state.auto_upload,
        help="绘制完成后自动上传到 JSONBin"
    )
    
    if st.session_state.auto_upload:
        st.success("✅ 自动上传已启用")
    else:
        st.info("ℹ️ 自动上传已禁用")
    
    st.divider()
    
    # 当前 Bin ID
    st.subheader("📦 当前 Bin")
    if st.session_state.current_bin_id:
        st.code(st.session_state.current_bin_id, language="text")
    else:
        st.info("尚未创建 Bin")
    
    # 最后上传时间
    if st.session_state.last_upload_time:
        st.caption(f"上次上传: {st.session_state.last_upload_time}")

# 主内容区域
col_main, col_side = st.columns([2, 1])

with col_main:
    st.subheader("🖌️ 绘图区域")
    
    # 生成带自动上传功能的画布
    canvas_html = CanvasComponent.generate_html_with_auto_upload(
        width=canvas_width,
        height=canvas_height,
        pen_color=pen_color,
        pen_width=pen_width,
        bg_color=bg_color,
        auto_upload=st.session_state.auto_upload
    )
    
    components.html(canvas_html, height=canvas_height + 100)
    
    st.info("💡 在画布上绘制完成后，点击'保存'按钮，数据会自动保存")
    
    # 数据接收区域
    uploaded_json = st.file_uploader(
        "📤 或手动上传 JSON 文件",
        type=['json'],
        key="json_uploader",
        help="如果自动保存失败，可以手动上传"
    )
    
    if uploaded_json is not None:
        try:
            data = json.load(uploaded_json)
            if isinstance(data, dict) and 'image' in data:
                st.session_state.drawing_data = data
                
                # 如果启用自动上传，立即上传
                if st.session_state.auto_upload:
                    with st.spinner("正在自动上传..."):
                        upload_to_jsonbin(data)
                else:
                    st.success("✅ 数据已加载！")
            else:
                st.error("❌ JSON 文件格式不正确")
        except Exception as e:
            st.error(f"❌ 读取文件失败: {str(e)}")

with col_side:
    st.subheader("📊 数据信息")
    
    if st.session_state.drawing_data:
        data = st.session_state.drawing_data
        
        if isinstance(data, dict):
            stats = data.get('statistics', {})
            st.metric("笔画数", stats.get('pathCount', 0))
            st.metric("总点数", stats.get('totalPoints', 0))
            
            duration = stats.get('drawingDuration', 0)
            st.metric("绘制时长", f"{duration / 1000:.1f} 秒")
            
            st.divider()
            
            # 图像预览
            st.subheader("🖼️ 预览")
            try:
                if 'image' in data:
                    image = ImageHandler.base64_to_image(data['image'])
                    st.image(image, use_container_width=True)
            except Exception as e:
                st.error(f"图像加载失败: {str(e)}")

# 底部操作区
st.divider()

if st.session_state.drawing_data:
    data = st.session_state.drawing_data
    
    if isinstance(data, dict):
        col1, col2, col3 = st.columns(3)
        
        # 下载选项
        with col1:
            st.subheader("💾 本地保存")
            
            json_str = json.dumps(data, indent=2, ensure_ascii=False)
            st.download_button(
                label="📥 下载 JSON",
                data=json_str,
                file_name=f"drawing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
            
            # 下载图像
            if 'image' in data:
                try:
                    image = ImageHandler.base64_to_image(data['image'])
                    image_bytes = ImageHandler.image_to_bytes(image)
                    st.download_button(
                        label="📥 下载图像",
                        data=image_bytes,
                        file_name=f"drawing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                        mime="image/png",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"图像处理失败: {str(e)}")
        
        # 手动上传
        with col2:
            st.subheader("☁️ 手动上传")
            
            if st.button("🚀 立即上传到 JSONBin", type="primary", use_container_width=True):
                with st.spinner("上传中..."):
                    upload_to_jsonbin(data)
        
        # 数据查看
        with col3:
            st.subheader("🔍 数据查看")
            
            if st.button("📖 查看完整数据", use_container_width=True):
                with st.expander("完整 JSON 数据", expanded=True):
                    st.json(data)

else:
    st.info("👆 请在画布上绘制，数据会自动显示在右侧")

# 使用说明
with st.expander("📖 使用指南"):
    st.markdown("""
    ### 🚀 使用步骤
    
    1. **开始绘画**：在画布上自由创作
    2. **点击保存**：点击画布下方的"💾 保存"按钮
    3. **自动处理**：
       - JSON 文件会自动下载
       - 数据会自动上传到云端（如果启用）
    4. **查看结果**：右侧面板显示统计和预览
    
    ### 💡 提示
    
    - 绘制时可以随时撤销和清空
    - 支持鼠标和触摸屏绘制
    - 自动保存的 Bin ID 会显示在左侧边栏
    - 可以下载 JSON 和图像文件
    """)