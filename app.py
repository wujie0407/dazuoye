"""
手绘画板 + 材料选择系统
画图 + 选材料 + 一键上传
"""

import streamlit as st
import streamlit.components.v1 as components
import json
from datetime import datetime

from jsonbin import JSONBinService
from image_handler import ImageHandler

# 页面配置
st.set_page_config(
    page_title="风筝设计系统",
    page_icon="🪁",
    layout="wide"
)

# API 配置
API_KEY = "$2a$10$pleOacf0lQu1mvIU//jjfeYPUCb.kiFXX.08qupD/90UYKwHtU8e."
BIN_ID = ""

# 初始化 session state
if 'current_bin_id' not in st.session_state:
    st.session_state.current_bin_id = BIN_ID
if 'last_upload_time' not in st.session_state:
    st.session_state.last_upload_time = None
if 'drawing_data' not in st.session_state:
    st.session_state.drawing_data = None
if 'material_selections' not in st.session_state:
    st.session_state.material_selections = {
        '骨架材料': [],
        '风筝面料': [],
        '绳索材料': []
    }

# 材料数据库
MATERIALS = {
    '骨架材料': [
        '竹子',
        '铝合金',
        '碳纤维'
    ],
    '风筝面料': [
        '丝绸',
        '尼龙',
        'Mylar膜'
    ],
    '绳索材料': [
        '麻绳',
        '钢索',
        '凯夫拉'
    ]
}

# 标题
st.title("🪁 风筝设计系统")
st.caption("设计图形 + 选择材料 + 一键上传")

# 上传函数
def upload_complete_design(drawing_data, materials):
    """上传完整设计（图形+材料）"""
    try:
        # 合并数据
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
                result = service.update_bin(st.session_state.current_bin_id, complete_data)
                st.success(f"✅ 设计已更新！")
                st.session_state.last_upload_time = datetime.now().strftime("%H:%M:%S")
                return True
            except Exception as e:
                if "404" in str(e):
                    result = service.create_bin(complete_data)
                    st.session_state.current_bin_id = result['metadata']['id']
                    st.success(f"✅ 设计已保存！Bin ID: {st.session_state.current_bin_id[:20]}...")
                    st.session_state.last_upload_time = datetime.now().strftime("%H:%M:%S")
                    return True
                raise
        else:
            result = service.create_bin(complete_data)
            st.session_state.current_bin_id = result['metadata']['id']
            st.success(f"✅ 设计已保存！Bin ID: {st.session_state.current_bin_id[:20]}...")
            st.session_state.last_upload_time = datetime.now().strftime("%H:%M:%S")
            return True
            
    except Exception as e:
        st.error(f"❌ 上传失败: {str(e)}")
        return False

# 侧边栏 - 材料选择
with st.sidebar:
    st.header("📦 材料选择")
    
    for category, options in MATERIALS.items():
        st.subheader(f"• {category}")
        
        # 使用多选框
        selected = st.multiselect(
            f"选择{category}",
            options=options,
            default=st.session_state.material_selections[category],
            key=f"material_{category}"
        )
        
        st.session_state.material_selections[category] = selected
        
        # 显示已选材料
        if selected:
            st.success(f"已选: {', '.join(selected)}")
        else:
            st.info("未选择")
        
        st.divider()
    
    # 上传记录
    st.subheader("☁️ 上传记录")
    if st.session_state.current_bin_id:
        st.code(st.session_state.current_bin_id[:25] + "...", language="text")
        if st.session_state.last_upload_time:
            st.caption(f"最后上传: {st.session_state.last_upload_time}")
    else:
        st.info("还未上传")

# 主界面 - 三列布局
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🖌️ 设计绘图区")
    
    # 画笔设置
    pen_col1, pen_col2, pen_col3 = st.columns(3)
    with pen_col1:
        pen_width = st.slider("笔触粗细", 1, 20, 3)
    with pen_col2:
        pen_color = st.color_picker("笔触颜色", "#000000")
    with pen_col3:
        bg_color = st.color_picker("背景颜色", "#FFFFFF")
    
    # 画布
    canvas_width = 700
    canvas_height = 500
    
    canvas_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 15px;
            font-family: 'Segoe UI', sans-serif;
        }}
        .container {{
            background: white;
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }}
        #canvas {{
            border: 2px solid #ddd;
            cursor: crosshair;
            background: {bg_color};
            border-radius: 6px;
            display: block;
            margin: 0 auto;
        }}
        .controls {{
            margin-top: 15px;
            text-align: center;
            display: flex;
            justify-content: center;
            gap: 8px;
            flex-wrap: wrap;
        }}
        button {{
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }}
        button:hover {{ transform: translateY(-1px); }}
        #undoBtn {{ background: #4facfe; color: white; }}
        #clearBtn {{ background: #f5576c; color: white; }}
        #saveBtn {{ background: #43e97b; color: white; }}
        .info {{
            margin-top: 10px;
            text-align: center;
            color: #666;
            font-size: 13px;
        }}
    </style>
    </head>
    <body>
    <div class="container">
        <canvas id="canvas" width="{canvas_width}" height="{canvas_height}"></canvas>
        <div class="controls">
            <button id="undoBtn" onclick="undo()">↶ 撤销</button>
            <button id="clearBtn" onclick="clear()">🗑️ 清空</button>
            <button id="saveBtn" onclick="saveDrawing()">💾 保存图形</button>
        </div>
        <div class="info">
            <span id="stats">笔画: 0 | 点数: 0</span>
        </div>
    </div>
    
    <script>
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    let drawing = false, paths = [], currentPath = [], totalPoints = 0;
    
    ctx.strokeStyle = '{pen_color}';
    ctx.lineWidth = {pen_width};
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    
    function getPos(e) {{
        const rect = canvas.getBoundingClientRect();
        return {{
            x: (e.clientX - rect.left) * (canvas.width / rect.width),
            y: (e.clientY - rect.top) * (canvas.height / rect.height),
            timestamp: Date.now()
        }};
    }}
    
    canvas.addEventListener('mousedown', e => {{
        drawing = true;
        const p = getPos(e);
        currentPath = [p];
        ctx.beginPath();
        ctx.moveTo(p.x, p.y);
    }});
    
    canvas.addEventListener('mousemove', e => {{
        if (!drawing) return;
        const p = getPos(e);
        currentPath.push(p);
        ctx.lineTo(p.x, p.y);
        ctx.stroke();
        updateStats();
    }});
    
    canvas.addEventListener('mouseup', () => stop());
    canvas.addEventListener('mouseleave', () => stop());
    
    function stop() {{
        if (drawing && currentPath.length > 0) {{
            paths.push([...currentPath]);
            totalPoints += currentPath.length;
        }}
        drawing = false;
        updateStats();
    }}
    
    function updateStats() {{
        document.getElementById('stats').textContent = `笔画: ${{paths.length}} | 点数: ${{totalPoints}}`;
    }}
    
    function undo() {{
        if (paths.length > 0) {{
            totalPoints -= paths.pop().length;
            redraw();
        }}
    }}
    
    function clear() {{
        if (confirm('确定清空画布吗？')) {{
            paths = [];
            totalPoints = 0;
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            updateStats();
        }}
    }}
    
    function redraw() {{
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        paths.forEach(path => {{
            if (path.length > 0) {{
                ctx.beginPath();
                ctx.moveTo(path[0].x, path[0].y);
                path.forEach(pt => ctx.lineTo(pt.x, pt.y));
                ctx.stroke();
            }}
        }});
        updateStats();
    }}
    
    function saveDrawing() {{
        if (paths.length === 0) {{
            alert('画布为空！请先绘制内容');
            return;
        }}
        
        const btn = document.getElementById('saveBtn');
        btn.disabled = true;
        btn.textContent = '保存中...';
        
        try {{
            const timestamps = paths.flat().map(p => p.timestamp);
            const duration = timestamps.length > 0 ? Math.max(...timestamps) - Math.min(...timestamps) : 0;
            
            const data = {{
                image: canvas.toDataURL('image/png'),
                paths: paths,
                statistics: {{
                    pathCount: paths.length,
                    totalPoints: totalPoints,
                    drawingDuration: duration
                }},
                canvas_settings: {{
                    width: canvas.width,
                    height: canvas.height,
                    penColor: '{pen_color}',
                    penWidth: {pen_width},
                    backgroundColor: '{bg_color}'
                }},
                timestamp: new Date().toISOString()
            }};
            
            // 下载为 JSON 文件
            const dataStr = JSON.stringify(data, null, 2);
            const blob = new Blob([dataStr], {{ type: 'application/json' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'drawing_' + new Date().getTime() + '.json';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            btn.textContent = '✅ 已保存';
            btn.style.background = '#43e97b';
            
            setTimeout(() => {{
                btn.disabled = false;
                btn.textContent = '💾 保存图形';
                btn.style.background = '#43e97b';
            }}, 1500);
            
        }} catch (err) {{
            alert('保存失败: ' + err.message);
            btn.disabled = false;
            btn.textContent = '💾 保存图形';
        }}
    }}
    
    updateStats();
    </script>
    </body>
    </html>
    """
    
    # 显示画布
    components.html(canvas_html, height=canvas_height + 120)
    
    # 使用文件上传接收数据
    st.divider()
    uploaded_json = st.file_uploader(
        "📤 上传绘图数据",
        type=['json'],
        key='drawing_uploader',
        help="点击画布的'保存图形'按钮后，会自动下载 JSON 文件，把文件拖到这里"
    )
    
    if uploaded_json:
        try:
            data = json.load(uploaded_json)
            if 'image' in data or 'paths' in data:
                st.session_state.drawing_data = data
                st.success("✅ 图形已保存到内存")
            else:
                st.error("文件格式不正确")
        except Exception as e:
            st.error(f"读取失败: {str(e)}")

with col2:
    st.subheader("📋 设计预览")
    
    # 材料选择预览
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
    if st.session_state.drawing_data:
        st.divider()
        st.write("**绘图预览:**")
        try:
            if 'image' in st.session_state.drawing_data:
                image = ImageHandler.base64_to_image(st.session_state.drawing_data['image'])
                st.image(image, use_container_width=True)
                
                stats = st.session_state.drawing_data.get('statistics', {})
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("笔画数", stats.get('pathCount', 0))
                with col_b:
                    st.metric("总点数", stats.get('totalPoints', 0))
        except:
            st.error("图像加载失败")
    else:
        st.divider()
        st.info("👈 先在左侧绘制图形")

# 底部上传区
st.divider()

upload_col1, upload_col2, upload_col3 = st.columns([1, 2, 1])

with upload_col2:
    st.subheader("☁️ 上传完整设计")
    
    # 检查是否有数据
    has_drawing = st.session_state.drawing_data is not None
    has_materials = any(st.session_state.material_selections.values())
    
    # 状态指示
    status_col1, status_col2 = st.columns(2)
    with status_col1:
        if has_drawing:
            st.success("✅ 已绘制图形")
        else:
            st.warning("⚠️ 未绘制图形")
    
    with status_col2:
        if has_materials:
            st.success("✅ 已选择材料")
        else:
            st.warning("⚠️ 未选择材料")
    
    # 上传按钮
    if st.button("🚀 上传完整设计", type="primary", use_container_width=True, disabled=not (has_drawing or has_materials)):
        if not has_drawing and not has_materials:
            st.error("❌ 请先绘制图形或选择材料")
        else:
            with st.spinner("正在上传..."):
                if upload_complete_design(
                    st.session_state.drawing_data,
                    st.session_state.material_selections
                ):
                    st.balloons()
                    st.success("🎉 设计已成功上传到云端！")

# 使用说明
with st.expander("📖 使用指南"):
    st.markdown("""
    ### 🎯 完整流程
    
    **第一步：绘制设计图**
    - 在左侧画布上绘制风筝设计
    - 可以调整笔触粗细和颜色
    - 点击"💾 保存图形"按钮
    
    **第二步：选择材料**
    - 在左侧边栏选择各部件的材料
    - 材料面板：竹子、铝合金、碳纤维等
    - 骨架材料：轻质、耐热、柔韧等
    - 风筝面料：丝绸、尼龙、Mylar膜等
    
    **第三步：上传设计**
    - 确认图形和材料都已设置
    - 点击"🚀 上传完整设计"按钮
    - 完成！
    
    ### 💡 提示
    
    - 可以只绘图不选材料，也可以只选材料不绘图
    - 支持多选材料
    - 每次上传会保存完整的设计数据
    - Bin ID 显示在左侧边栏
    
    ### 📦 上传的数据包含
    
    - **drawing**: 绘图数据（图像、路径、统计）
    - **materials**: 材料选择（三类材料）
    - **metadata**: 元数据（时间戳、设计类型）
    """)