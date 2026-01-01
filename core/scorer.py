"""
风筝设计评分系统
根据设计参数计算综合评分
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

from config import get_config
from .calculator import KiteCalculator, KiteParameters

logger = logging.getLogger(__name__)


class ScoreLevel(Enum):
    """评分等级"""
    SUCCESS = "success"      # 成功
    STRUGGLE = "struggle"    # 勉强
    FAIL = "fail"           # 失败


@dataclass
class ScoreResult:
    """评分结果"""
    total_score: float
    level: ScoreLevel
    
    # 分项得分
    performance_score: float
    feasibility_score: float
    cost_score: float
    innovation_score: float
    
    # 参数详情
    parameters: Optional[KiteParameters] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'total_score': self.total_score,
            'level': self.level.value,
            'breakdown': {
                'performance': self.performance_score,
                'feasibility': self.feasibility_score,
                'cost': self.cost_score,
                'innovation': self.innovation_score
            },
            'parameters': self.parameters.to_dict() if self.parameters else None
        }


class KiteScorer:
    """风筝评分器"""
    
    def __init__(self):
        self.config = get_config()
    
    def calculate_performance_score(self, params: KiteParameters) -> float:
        """
        计算性能得分
        
        基于：稳定性 50% + 强度 30% + 抗风 20%
        """
        score = (
            params.flight_stability * 0.5 +
            params.strength_index * 0.3 +
            params.wind_resistance * 0.2
        )
        return round(score, 2)
    
    def calculate_feasibility_score(self, params: KiteParameters) -> float:
        """
        计算可行性得分
        
        基于重量/面积比
        """
        if params.area <= 0:
            return 0.0
        
        ratio = params.total_weight / params.area
        
        # 理想比例区间
        if 0.3 <= ratio <= 0.7:
            return 100.0
        elif 0.2 <= ratio <= 1.0:
            return 70.0
        else:
            return 40.0
    
    def calculate_cost_score(self, params: KiteParameters) -> float:
        """
        计算成本得分
        
        成本越低，得分越高
        """
        cost = params.estimated_cost
        cfg = self.config.scoring
        
        if cost < cfg.COST_EXCELLENT:
            return 100.0
        elif cost < cfg.COST_GOOD:
            return 80.0
        elif cost < cfg.COST_FAIR:
            return 60.0
        else:
            return 30.0
    
    def calculate_innovation_score(self, params: KiteParameters) -> float:
        """
        计算创新得分
        
        基于材料种类数
        """
        materials_count = sum(
            len(mats) for mats in params.materials_used.values()
        )
        return min(materials_count * 20, 100)
    
    def determine_level(self, score: float) -> ScoreLevel:
        """根据分数确定等级"""
        cfg = self.config.scoring
        
        if score >= cfg.SCORE_SUCCESS_THRESHOLD:
            return ScoreLevel.SUCCESS
        elif score >= cfg.SCORE_STRUGGLE_THRESHOLD:
            return ScoreLevel.STRUGGLE
        else:
            return ScoreLevel.FAIL
    
    def score(self, design_data: Dict[str, Any]) -> ScoreResult:
        """
        计算设计评分
        
        Args:
            design_data: 设计数据
            
        Returns:
            评分结果
        """
        # 计算参数
        calculator = KiteCalculator(design_data)
        params = calculator.calculate_all()
        
        # 计算各项得分
        performance = self.calculate_performance_score(params)
        feasibility = self.calculate_feasibility_score(params)
        cost = self.calculate_cost_score(params)
        innovation = self.calculate_innovation_score(params)
        
        # 加权计算总分
        cfg = self.config.scoring
        total = (
            performance * cfg.WEIGHT_PERFORMANCE +
            feasibility * cfg.WEIGHT_FEASIBILITY +
            cost * cfg.WEIGHT_COST +
            innovation * cfg.WEIGHT_INNOVATION
        )
        total = round(total, 1)
        
        # 确定等级
        level = self.determine_level(total)
        
        return ScoreResult(
            total_score=total,
            level=level,
            performance_score=performance,
            feasibility_score=feasibility,
            cost_score=cost,
            innovation_score=innovation,
            parameters=params
        )
    
    def score_simple(self, design_data: Dict[str, Any]) -> float:
        """简化评分，只返回总分"""
        return self.score(design_data).total_score


class RealtimeScorer:
    """实时评分监控器"""
    
    def __init__(self):
        from services import DesignRepository
        
        self.scorer = KiteScorer()
        self.repository = DesignRepository()
        self.processed_ids: set = set()
        self.results: list = []
    
    def check_new_designs(self) -> list:
        """
        检查新设计并评分
        
        Returns:
            新设计的评分结果列表
        """
        all_designs = self.repository.get_all_designs()
        new_results = []
        
        for design in all_designs:
            design_id = design.get('design_id', design.get('created_at', 'unknown'))
            
            if design_id not in self.processed_ids:
                self.processed_ids.add(design_id)
                
                try:
                    result = self.scorer.score(design)
                    
                    score_record = {
                        'design_id': design_id,
                        'score': result.total_score,
                        'level': result.level.value,
                        'design': design,
                        'result': result
                    }
                    
                    self.results.append(score_record)
                    new_results.append(score_record)
                    
                    logger.info(f"评分完成: {design_id} = {result.total_score}")
                    
                except Exception as e:
                    logger.error(f"评分失败 {design_id}: {e}")
        
        return new_results
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取评分统计"""
        if not self.results:
            return {
                'total': 0,
                'average': 0,
                'success_rate': 0,
                'level_distribution': {}
            }
        
        scores = [r['score'] for r in self.results]
        levels = [r['level'] for r in self.results]
        
        level_dist = {}
        for level in ScoreLevel:
            level_dist[level.value] = levels.count(level.value)
        
        return {
            'total': len(self.results),
            'average': round(sum(scores) / len(scores), 1),
            'success_rate': round(level_dist.get('success', 0) / len(self.results) * 100, 1),
            'level_distribution': level_dist
        }
