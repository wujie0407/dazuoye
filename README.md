# 🪁 风筝设计评估系统

一个完整的风筝设计、评分和可视化反馈系统。

## 📁 项目结构

```
kite_project/
├── config/                 # 配置模块
│   ├── __init__.py
│   └── settings.py         # 所有配置项（API密钥、评分权重、材料属性等）
│
├── services/               # 外部服务模块
│   ├── __init__.py
│   ├── jsonbin_service.py  # JSONBin 云存储服务
│   └── zhipu_service.py    # 智谱 AI 图像生成服务
│
├── core/                   # 核心业务逻辑
│   ├── __init__.py
│   ├── calculator.py       # 风筝参数计算器
│   └── scorer.py           # 评分系统
│
├── utils/                  # 工具模块
│   ├── __init__.py
│   └── image_handler.py    # 图像处理工具
│
├── ui/                     # 用户界面
│   ├── __init__.py
│   └── streamlit_app.py    # Streamlit 前端应用
│
├── scripts/                # 脚本
│   └── realtime_scorer.py  # 实时评分监控脚本
│
├── static/                 # 静态文件
│   └── kite_crossing.html  # 渡河动画页面
│
├── __init__.py             # 包入口
├── requirements.txt        # 依赖包
└── README.md               # 项目说明
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动 Streamlit 前端

```bash
cd kite_project
streamlit run ui/streamlit_app.py
```

### 3. 启动实时评分监控

```bash
python scripts/realtime_scorer.py
```

### 4. 打开渡河动画

```bash
# 使用本地服务器
python -m http.server 8000

# 然后访问 http://localhost:8000/static/kite_crossing.html
```

## 📊 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    用户界面层 (UI)                           │
│  ├── Streamlit 前端（设计输入）                              │
│  └── P5.js 动画（渡河反馈）                                  │
├─────────────────────────────────────────────────────────────┤
│                    核心业务层 (Core)                         │
│  ├── KiteCalculator（参数计算）                              │
│  └── KiteScorer（评分系统）                                  │
├─────────────────────────────────────────────────────────────┤
│                    服务层 (Services)                         │
│  ├── JSONBinService（云存储）                                │
│  └── ZhipuImageService（AI 图像生成）                        │
├─────────────────────────────────────────────────────────────┤
│                    配置层 (Config)                           │
│  └── settings.py（集中配置管理）                             │
└─────────────────────────────────────────────────────────────┘
```

## 📈 评分系统

### 评分维度

| 维度 | 权重 | 说明 |
|------|------|------|
| 性能 | 40% | 飞行稳定性、结构强度、抗风能力 |
| 可行性 | 30% | 重量/面积比是否合理 |
| 成本 | 20% | 材料成本越低越好 |
| 创新 | 10% | 材料组合多样性 |

### 评分等级

| 等级 | 分数范围 | 渡河结果 |
|------|----------|----------|
| SUCCESS | ≥80 | 🎉 渡河成功 |
| STRUGGLE | 50-79 | 😅 勉强渡河 |
| FAIL | <50 | 💦 渡河失败 |

## 🔧 配置说明

所有配置集中在 `config/settings.py`：

```python
from config import get_config

cfg = get_config()

# API 配置
cfg.api.JSONBIN_API_KEY
cfg.api.ZHIPU_API_KEY

# 评分权重
cfg.scoring.WEIGHT_PERFORMANCE  # 0.40
cfg.scoring.SCORE_SUCCESS_THRESHOLD  # 80

# 材料属性
cfg.materials.FRAME_MATERIALS['竹子'].strength  # 80
```

## 📦 模块说明

### config - 配置模块

集中管理所有配置，支持从环境变量加载敏感信息。

### services - 服务模块

- `JSONBinService`: 封装 JSONBin API，提供 CRUD 操作
- `DesignRepository`: 设计数据仓库，高级抽象
- `ZhipuImageService`: 智谱 AI 图像生成，支持多模型回退

### core - 核心模块

- `KiteCalculator`: 根据绘图和材料计算各项参数
- `KiteScorer`: 根据参数计算综合评分
- `KiteParameters`: 参数数据类
- `ScoreResult`: 评分结果数据类

### utils - 工具模块

- `ImageHandler`: 图像处理工具（Base64 转换、缩放等）

## 🔄 数据流

```
用户绘图 + 选择材料
        ↓
  保存到 JSONBin
        ↓
  实时评分系统监听
        ↓
  KiteCalculator 计算参数
        ↓
  KiteScorer 计算评分
        ↓
  渡河动画展示结果
```

## 📝 开发指南

### 添加新材料

在 `config/settings.py` 的 `MaterialsConfig` 中添加：

```python
FRAME_MATERIALS: Dict[str, MaterialProperty] = {
    '新材料': MaterialProperty(
        name='新材料',
        density=1.0,
        strength=100,
        cost=5.0
    ),
    # ...
}
```

### 调整评分权重

修改 `config/settings.py` 的 `ScoringConfig`：

```python
WEIGHT_PERFORMANCE: float = 0.40
WEIGHT_FEASIBILITY: float = 0.30
# ...
```

### 添加新的评分维度

1. 在 `core/scorer.py` 添加计算方法
2. 在 `ScoreResult` 添加新字段
3. 更新 `score()` 方法

## 📄 License

MIT License
