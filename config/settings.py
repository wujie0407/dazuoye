"""
风筝设计评估系统 - 配置模块
集中管理所有配置项，便于维护和部署
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class APIConfig:
    """API 配置"""
    # JSONBin 配置
    JSONBIN_API_KEY: str = "$2a$10$pleOacf0lQu1mvIU//jjfeYPUCb.kiFXX.08qupD/90UYKwHtU8e."
    JSONBIN_BASE_URL: str = "https://api.jsonbin.io/v3"
    
    # 智谱 AI 配置
    ZHIPU_API_KEY: str = "b91a0c07fd0640f488491d6bd0fa4e7f.z5j8U7iiyrWkO5sc"
    ZHIPU_BASE_URL: str = "https://open.bigmodel.cn/api/paas/v4"
    ZHIPU_MODEL: str = "cogView-4-250304"


@dataclass
class ScoringConfig:
    """评分配置"""
    # 权重配置
    WEIGHT_PERFORMANCE: float = 0.40
    WEIGHT_FEASIBILITY: float = 0.30
    WEIGHT_COST: float = 0.20
    WEIGHT_INNOVATION: float = 0.10
    
    # 分数区间
    SCORE_SUCCESS_THRESHOLD: int = 80
    SCORE_STRUGGLE_THRESHOLD: int = 50
    
    # 成本评分阈值
    COST_EXCELLENT: float = 50
    COST_GOOD: float = 100
    COST_FAIR: float = 150


@dataclass
class MaterialProperty:
    """单个材料属性"""
    name: str
    density: float = 0.0          # 密度 g/cm³
    strength: float = 0.0         # 强度指数
    flexibility: float = 0.0      # 柔韧性
    cost: float = 0.0             # 成本系数
    weight_factor: float = 1.0    # 重量系数
    wind_resistance: float = 0.0  # 抗风性
    weight_per_sqm: float = 0.0   # 克/平方米
    air_permeability: float = 0.0 # 透气性
    tensile_strength: float = 0.0 # 拉伸强度
    weight_per_meter: float = 0.0 # 克/米
    elasticity: float = 0.0       # 弹性


@dataclass
class MaterialsConfig:
    """材料配置"""
    
    # 骨架材料
    FRAME_MATERIALS: Dict[str, MaterialProperty] = field(default_factory=lambda: {
        '竹子': MaterialProperty(
            name='竹子',
            density=0.6,
            strength=80,
            flexibility=85,
            cost=1.0,
            weight_factor=1.0
        ),
        '铝合金': MaterialProperty(
            name='铝合金',
            density=2.7,
            strength=150,
            flexibility=60,
            cost=3.5,
            weight_factor=0.8
        ),
        '碳纤维': MaterialProperty(
            name='碳纤维',
            density=1.6,
            strength=200,
            flexibility=70,
            cost=8.0,
            weight_factor=0.5
        )
    })
    
    # 风筝面料
    SURFACE_MATERIALS: Dict[str, MaterialProperty] = field(default_factory=lambda: {
        '丝绸': MaterialProperty(
            name='丝绸',
            weight_per_sqm=60,
            wind_resistance=70,
            cost=2.0,
            air_permeability=15
        ),
        '尼龙': MaterialProperty(
            name='尼龙',
            weight_per_sqm=85,
            wind_resistance=95,
            cost=1.5,
            air_permeability=5
        ),
        'Mylar膜': MaterialProperty(
            name='Mylar膜',
            weight_per_sqm=50,
            wind_resistance=85,
            cost=3.0,
            air_permeability=2
        )
    })
    
    # 绳索材料
    STRING_MATERIALS: Dict[str, MaterialProperty] = field(default_factory=lambda: {
        '麻绳': MaterialProperty(
            name='麻绳',
            tensile_strength=500,
            weight_per_meter=8,
            elasticity=30,
            cost=0.5
        ),
        '钢索': MaterialProperty(
            name='钢索',
            tensile_strength=2000,
            weight_per_meter=15,
            elasticity=10,
            cost=2.0
        ),
        '凯夫拉': MaterialProperty(
            name='凯夫拉',
            tensile_strength=3000,
            weight_per_meter=5,
            elasticity=20,
            cost=5.0
        )
    })
    
    # 材料视觉描述（用于 AI 图像生成）
    MATERIAL_DESCRIPTIONS: Dict[str, str] = field(default_factory=lambda: {
        '竹子': '竹制骨架，自然的竹节纹理',
        '铝合金': '银色金属骨架，现代工业感',
        '碳纤维': '黑色碳纤维骨架，科技感十足',
        '丝绸': '丝绸材质，柔软光滑，带有自然光泽',
        '尼龙': '尼龙布料，色彩鲜艳，现代感',
        'Mylar膜': '镭射膜材质，反光效果，未来科技感',
        '麻绳': '天然麻绳，粗糙质感',
        '钢索': '金属钢索，坚固有力',
        '凯夫拉': '黑色凯夫拉纤维，高科技材质'
    })
    
    @property
    def categories(self) -> Dict[str, List[str]]:
        """获取材料分类列表"""
        return {
            '骨架材料': list(self.FRAME_MATERIALS.keys()),
            '风筝面料': list(self.SURFACE_MATERIALS.keys()),
            '绳索材料': list(self.STRING_MATERIALS.keys())
        }


@dataclass
class SystemConfig:
    """系统配置"""
    # 文件路径
    BIN_ID_FILE: str = "fixed_bin_id.txt"
    SCORES_FILE: str = "scores_summary.jsonl"
    
    # 监控配置
    CHECK_INTERVAL: int = 3  # 秒
    
    # 动画配置
    ANIMATION_DURATION: int = 6000  # 毫秒
    
    # 绳索默认长度
    DEFAULT_STRING_LENGTH: float = 50  # 米


@dataclass
class AppConfig:
    """应用总配置"""
    api: APIConfig = field(default_factory=APIConfig)
    scoring: ScoringConfig = field(default_factory=ScoringConfig)
    materials: MaterialsConfig = field(default_factory=MaterialsConfig)
    system: SystemConfig = field(default_factory=SystemConfig)


# 全局配置实例
config = AppConfig()


def get_config() -> AppConfig:
    """获取配置实例"""
    return config


def load_config_from_env() -> AppConfig:
    """从环境变量加载配置（用于生产环境）"""
    cfg = AppConfig()
    
    # 从环境变量覆盖敏感配置
    if os.getenv('JSONBIN_API_KEY'):
        cfg.api.JSONBIN_API_KEY = os.getenv('JSONBIN_API_KEY')
    
    if os.getenv('ZHIPU_API_KEY'):
        cfg.api.ZHIPU_API_KEY = os.getenv('ZHIPU_API_KEY')
    
    return cfg
