"""
Canvas 绘图组件
负责生成前端 HTML/JavaScript 代码
"""

from typing import Dict


class CanvasComponent:
    """Canvas 绘图组件类"""
    
    @staticmethod
    def generate_html(
        width: int = 800,
        height: int = 600,
        pen_color: str = "#000000",
        pen_width: int = 3,
        bg_color: str = "#FFFFFF"
    ) -> str:
        """
        生成 Canvas HTML 代码
        
        Args:
            width: 画布宽度
            height: 画布高度
            pen_color: 笔触颜色
            pen_width: 笔触宽度
            bg_color: 背景颜色
            
        Returns:
            HTML 字符串
        """
        return f"""
<!DOCTYPE html>
<html>
<head>
<style>
    * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}
    
    body {{
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 20px;
    }}
    
    .container {{
        background: white;
        border-radius: 15px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        padding: 20px;
        max-width: {width + 40}px;
    }}
    
    #canvas {{
        border: 2px solid #e0e0e0;
        cursor: crosshair;
        display: block;
        margin: 0 auto;
        background-color: {bg_color};
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}
    
    .controls {{
        text-align: center;
        margin-top: 20px;
        display: flex;
        justify-content: center;
        gap: 15px;
        flex-wrap: wrap;
    }}
    
    button {{
        padding: 12px 24px;
        font-size: 16px;
        cursor: pointer;
        border: none;
        border-radius: 8px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}
    
    button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }}
    
    button:active {{
        transform: translateY(0);
    }}
    
    #clearBtn {{
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }}
    
    #undoBtn {{
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }}
    
    .info {{
        margin-top: 15px;
        text-align: center;
        color: #666;
        font-size: 14px;
    }}
    
    .status {{
        display: inline-block;
        padding: 8px 16px;
        background: #f0f0f0;
        border-radius: 20px;
        margin: 10px 5px;
        font-size: 13px;
    }}
</style>
</head>
<body>
<div class="container">
    <canvas id="canvas" width="{width}" height="{height}"></canvas>
    <div class="controls">
        <button onclick="undoLastPath()" id="undoBtn">↶ 撤销</button>
        <button onclick="clearCanvas()" id="clearBtn">🗑️ 清空</button>
        <button onclick="saveDrawing()">💾 保存并上传</button>
    </div>
    <div class="info">
        <span class="status" id="pathCount">笔画数: 0</span>
        <span class="status" id="pointCount">点数: 0</span>
    </div>
</div>

<script>
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
let drawing = false;
let paths = [];
let currentPath = [];
let totalPoints = 0;

// 设置画笔样式
ctx.strokeStyle = '{pen_color}';
ctx.lineWidth = {pen_width};
ctx.lineCap = 'round';
ctx.lineJoin = 'round';

// 鼠标事件
canvas.addEventListener('mousedown', startDrawing);
canvas.addEventListener('mousemove', draw);
canvas.addEventListener('mouseup', stopDrawing);
canvas.addEventListener('mouseleave', stopDrawing);

// 触摸事件支持
canvas.addEventListener('touchstart', handleTouch, {{passive: false}});
canvas.addEventListener('touchmove', handleTouch, {{passive: false}});
canvas.addEventListener('touchend', stopDrawing);

function getMousePos(e) {{
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    return {{
        x: (e.clientX - rect.left) * scaleX,
        y: (e.clientY - rect.top) * scaleY
    }};
}}

function handleTouch(e) {{
    e.preventDefault();
    const touch = e.touches[0];
    const mouseEvent = new MouseEvent(
        e.type === 'touchstart' ? 'mousedown' : 'mousemove',
        {{
            clientX: touch.clientX,
            clientY: touch.clientY
        }}
    );
    canvas.dispatchEvent(mouseEvent);
}}

function startDrawing(e) {{
    drawing = true;
    const pos = getMousePos(e);
    currentPath = [{{x: pos.x, y: pos.y, timestamp: Date.now()}}];
    ctx.beginPath();
    ctx.moveTo(pos.x, pos.y);
}}

function draw(e) {{
    if (!drawing) return;
    const pos = getMousePos(e);
    currentPath.push({{x: pos.x, y: pos.y, timestamp: Date.now()}});
    ctx.lineTo(pos.x, pos.y);
    ctx.stroke();
    updateStats();
}}

function stopDrawing() {{
    if (drawing && currentPath.length > 0) {{
        paths.push([...currentPath]);
        totalPoints += currentPath.length;
        updateStats();
    }}
    drawing = false;
}}

function clearCanvas() {{
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    paths = [];
    currentPath = [];
    totalPoints = 0;
    updateStats();
}}

function undoLastPath() {{
    if (paths.length > 0) {{
        const removed = paths.pop();
        totalPoints -= removed.length;
        redrawCanvas();
        updateStats();
    }}
}}

function redrawCanvas() {{
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    paths.forEach(path => {{
        if (path.length > 0) {{
            ctx.beginPath();
            ctx.moveTo(path[0].x, path[0].y);
            path.forEach(point => {{
                ctx.lineTo(point.x, point.y);
            }});
            ctx.stroke();
        }}
    }});
}}

function updateStats() {{
    document.getElementById('pathCount').textContent = `笔画数: ${{paths.length}}`;
    document.getElementById('pointCount').textContent = `点数: ${{totalPoints}}`;
}}

function saveDrawing() {{
    if (paths.length === 0) {{
        alert('画布为空，请先绘制内容！');
        return;
    }}
    
    // 获取 Base64 图像数据
    const imageData = canvas.toDataURL('image/png');
    
    // 计算绘制时长
    const timestamps = paths.flat().map(p => p.timestamp);
    const duration = timestamps.length > 0 
        ? Math.max(...timestamps) - Math.min(...timestamps)
        : 0;
    
    // 准备发送的数据
    const drawingData = {{
        image: imageData,
        paths: paths,
        statistics: {{
            pathCount: paths.length,
            totalPoints: totalPoints,
            drawingDuration: duration
        }},
        metadata: {{
            width: canvas.width,
            height: canvas.height,
            penColor: '{pen_color}',
            penWidth: {pen_width},
            backgroundColor: '{bg_color}',
            timestamp: new Date().toISOString()
        }}
    }};
    
    // 将数据转换为 JSON 字符串
    const dataStr = JSON.stringify(drawingData);
    
    // 创建下载链接
    const blob = new Blob([dataStr], {{ type: 'application/json' }});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'drawing_' + new Date().getTime() + '.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    // 同时存储到 sessionStorage，以便页面内使用
    try {{
        sessionStorage.setItem('drawing_data', dataStr);
        alert('✅ 数据已保存并下载！\\n\\n请使用页面上方的"数据上传"功能上传 JSON 文件。');
    }} catch(e) {{
        console.error('保存到 sessionStorage 失败:', e);
        alert('✅ 数据已下载！\\n\\n请使用页面上方的"数据上传"功能上传 JSON 文件。');
    }}
}}

// 初始化统计
updateStats();
</script>
</body>
</html>
"""