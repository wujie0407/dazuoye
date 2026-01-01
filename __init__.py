"""
风筝设计评估系统
Kite Design Evaluation System

一个完整的风筝设计、评分和可视化反馈系统
"""

__version__ = "2.0.0"
__author__ = "Kite Design Team"

# 方便导入的快捷方式
from config import config, get_config
from services import JSONBinService, DesignRepository, ZhipuImageService
from core import KiteCalculator, KiteScorer, ScoreLevel

__all__ = [
    'config',
    'get_config',
    'JSONBinService',
    'DesignRepository', 
    'ZhipuImageService',
    'KiteCalculator',
    'KiteScorer',
    'ScoreLevel'
]
