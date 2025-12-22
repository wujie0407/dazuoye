"""
手绘画板 Streamlit 应用 - 优化版
自动从 secrets 读取配置，绘制完成后自动上传
"""

import streamlit as st
import streamlit.components.v1 as components
import json
from datetime import datetime
import time

from canvas import CanvasComponent
from jsonbin import JSONBinService
from image_handler import ImageHandler

# 页面配置
st.set_page_config(
    page_title="手绘画板",
    page_icon="🎨",
    layout="wide"
)

# 从 secrets 加载配置（带容错处理）
def load_config():
    """尝试从 secrets 加载配置，如果失败则返回 None"""
    try:
        api_key = st.secrets["JSONBIN_API_KEY"]
        bin_id = st.secrets.get("JSONBIN_BIN_ID", "")
        return api_key, bin_id, True
    except:
        return None, None, False

API_KEY, BIN_ID, config_loaded = load_config()

# 如果没有加载到配置，显示输入框
if not config_loaded:
    st.error("❌ 未找到 secrets.toml 配置文件")
    
    with st.expander("📝 配置说明", expanded=True):
        st.markdown("""
        ### 方法 1: 创建 secrets.toml（推荐）
        
        1. 在项目根目录创建 `.streamlit` 文件夹
        2. 在 `.streamlit` 文件夹中创建 `secrets.toml` 文件
        3. 添加以下内容：
        
        ```toml
        JSONBIN_API_KEY = "你的Master_Key"
        JSONBIN_BIN_ID = ""
        ```
        
        4. 重启 Streamlit 应用
        
        ---
        
        ### 方法 2: 临时输入（快速测试）
        
        在下方输入框中输入 API Key 即可使用（仅当前会话有效）
        """)
    
    # 临时输入框
    st.subheader("🔑 临时 API Key 输入")
    
    if 'temp_api_key' not in st.session_state:
        st.session_state.temp_api_key = ""
    
    temp_api_key = st.text_input(
        "Master API Key",
        type="password",
        value=st.session_state.temp_api_key,
        help="输入你的 JSONBin Master Key",
        placeholder="$2a$10$..."
    )
    
    if temp_api_key:
        st.session_state.temp_api_key = temp_api_key
        API_KEY = temp_api_key
        BIN_ID = ""
        st.success("✅ 已设置临时 API Key，可以开始使用了！")
        st.info("💡 刷新页面后需要重新输入，建议创建 secrets.toml 文件")
    else:
        st.warning("⚠️ 请在上方输入 API Key 才能使用应用")
        st.stop()
else:
    # 成功加载配置
    pass

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

# 定义上传函数（必须在使用之前定义）
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
    
    st.info("💡 在画布上绘制完成后，数据会自动保存到右侧面板")
    
    # 数据接收区域（隐藏的）
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
    ### 🚀 快速开始（全自动）
    
    1. **开始绘画**：在画布上自由创作
    2. **点击"保存"**：点击画布下方的"💾 保存"按钮
    3. **自动上传**：系统会自动将作品上传到云端
    4. **实时预览**：右侧面板实时显示统计和预览
    
    ### ⚙️ 功能说明
    
    - **自动上传**：默认启用，可在左侧边栏关闭
    - **智能 Bin 管理**：
      - 第一次上传会创建新 Bin
      - 后续上传会自动更新到同一个 Bin
      - Bin ID 会自动保存
    - **手动上传**：关闭自动上传后，可使用底部"立即上传"按钮
    - **本地保存**：随时可以下载 JSON 或图像文件
    
    ### 📝 配置说明
    
    API Key 和 Bin ID 从 `secrets.toml` 自动读取：
    ```toml
    JSONBIN_API_KEY = "你的Master_Key"
    JSONBIN_BIN_ID = ""  # 留空让系统自动创建
    ```
    
    ### 💡 提示
    
    - 绘制时可以随时撤销和清空
    - 支持鼠标和触摸屏绘制
    - 自动保存的 Bin ID 会显示在左侧边栏
    """)