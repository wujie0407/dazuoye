"""
手绘画板 Streamlit 应用
"""

import streamlit as st
import streamlit.components.v1 as components
import json
from datetime import datetime

from components.canvas import CanvasComponent
from services.jsonbin import JSONBinService
from utils.image_handler import ImageHandler

# 页面配置
st.set_page_config(
    page_title="手绘画板",
    page_icon="🎨",
    layout="wide"
)

# 初始化 session state
if 'drawing_data' not in st.session_state:
    st.session_state.drawing_data = None

# 标题
st.title("🎨 手绘画板 - 云端存储")

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
    
    # JSONBin 配置
    st.header("☁️ JSONBin 配置")
    api_key = st.text_input(
        "API Key",
        value=st.secrets.get("JSONBIN_API_KEY", ""),
        type="password",
        help="从 jsonbin.io 获取你的 API Key"
    )
    
    bin_id = st.text_input(
        "Bin ID (可选)",
        value=st.secrets.get("JSONBIN_BIN_ID", ""),
        help="留空则创建新 Bin，填写则更新已有 Bin"
    )
    
    # 验证 API Key
    if api_key:
        if JSONBinService.validate_api_key(api_key):
            st.success("✅ API Key 有效")
        else:
            st.warning("⚠️ API Key 可能无效")

# 主内容区域
col_main, col_side = st.columns([2, 1])

with col_main:
    st.subheader("🖌️ 绘图区域")
    
    # 生成并渲染 Canvas
    canvas_html = CanvasComponent.generate_html(
        width=canvas_width,
        height=canvas_height,
        pen_color=pen_color,
        pen_width=pen_width,
        bg_color=bg_color
    )
    
    drawing_data = components.html(canvas_html, height=canvas_height + 200)
    
    # 处理接收到的绘图数据
    if drawing_data:
        try:
            data = json.loads(drawing_data)
            st.session_state.drawing_data = data
        except json.JSONDecodeError:
            st.error("❌ 数据解析失败")

with col_side:
    st.subheader("📊 数据信息")
    
    if st.session_state.drawing_data:
        data = st.session_state.drawing_data
        
        # 显示统计信息
        stats = data.get('statistics', {})
        st.metric("笔画数", stats.get('pathCount', 0))
        st.metric("总点数", stats.get('totalPoints', 0))
        
        duration = stats.get('drawingDuration', 0)
        st.metric("绘制时长", f"{duration / 1000:.1f} 秒")
        
        st.divider()
        
        # 图像预览
        st.subheader("🖼️ 预览")
        try:
            image = ImageHandler.base64_to_image(data['image'])
            st.image(image, use_container_width=True)
            
            # 显示图像信息
            with st.expander("图像详情"):
                info = ImageHandler.get_image_info(image)
                st.json(info)
        except Exception as e:
            st.error(f"图像加载失败: {str(e)}")

# 底部操作区
st.divider()

if st.session_state.drawing_data:
    col1, col2, col3 = st.columns(3)
    
    # 下载选项
    with col1:
        st.subheader("💾 本地保存")
        
        data = st.session_state.drawing_data
        
        # 下载 JSON
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        st.download_button(
            label="📥 下载 JSON",
            data=json_str,
            file_name=f"drawing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
        
        # 下载图像
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
    
    # JSONBin 上传
    with col2:
        st.subheader("☁️ 云端上传")
        
        if st.button("🚀 上传到 JSONBin", type="primary", use_container_width=True):
            if not api_key:
                st.error("❌ 请先配置 API Key")
            else:
                try:
                    with st.spinner("上传中..."):
                        service = JSONBinService(api_key)
                        
                        if bin_id:
                            # 更新已有 Bin
                            result = service.update_bin(bin_id, data)
                            st.success(f"✅ 已更新 Bin: {bin_id}")
                        else:
                            # 创建新 Bin
                            result = service.create_bin(data)
                            new_bin_id = result['metadata']['id']
                            st.success(f"✅ 已创建新 Bin")
                            st.code(f"Bin ID: {new_bin_id}")
                            st.info("💡 保存此 Bin ID 以便后续更新")
                        
                        with st.expander("查看响应"):
                            st.json(result)
                
                except Exception as e:
                    st.error(f"❌ 上传失败: {str(e)}")
    
    # 数据查看
    with col3:
        st.subheader("🔍 数据查看")
        
        if st.button("📖 查看完整数据", use_container_width=True):
            st.json(st.session_state.drawing_data)

else:
    st.info("👆 请在画布上绘制，然后点击'保存并上传'按钮")

# 使用说明
with st.expander("📖 使用指南"):
    st.markdown("""
    ### 快速开始
    
    1. **调整设置**：在左侧边栏配置画笔和画布
    2. **开始绘画**：在画布上自由创作
    3. **保存作品**：点击"保存并上传"按钮
    4. **选择操作**：
       - 本地保存：下载 JSON 或图像文件
       - 云端上传：上传到 JSONBin 永久保存
    
    ### JSONBin 设置
    
    1. 访问 [jsonbin.io](https://jsonbin.io) 注册账号
    2. 获取 API Key 并填入侧边栏
    3. 首次上传会创建新 Bin，记住 Bin ID
    4. 后续可使用 Bin ID 更新同一个存储空间
    
    ### 数据格式
```json
    {
        "image": "base64图像数据",
        "paths": [路径点数组],
        "statistics": {统计信息},
        "metadata": {元数据}
    }
```
    """)