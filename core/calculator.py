"""
风筝参数计算器
根据绘图数据和材料选择计算风筝的各项参数
"""

from typing import Dict, Any, List
from dataclasses import dataclass
import math

from config import get_config


@dataclass
class KiteParameters:
    """风筝参数数据类"""
    # 尺寸
    area: float = 0.0
    perimeter: float = 0.0
    
    # 重量
    frame_weight: float = 0.0
    surface_weight: float = 0.0
    string_weight: float = 0.0
    total_weight: float = 0.0
    
    # 性能
    strength_index: float = 0.0
    wind_resistance: float = 0.0
    flight_stability: float = 0.0
    
    # 飞行条件
    min_wind_speed: float = 0.0
    max_wind_speed: float = 0.0
    optimal_wind_speed: float = 0.0
    
    # 成本
    estimated_cost: float = 0.0
    
    # 材料
    materials_used: Dict[str, List[str]] = None
    
    def __post_init__(self):
        if self.materials_used is None:
            self.materials_used = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式（兼容旧接口）"""
        return {
            'dimensions': {
                'area': self.area,
                'perimeter': self.perimeter,
                'unit': 'cm/cm²'
            },
            'weight': {
                'frame': self.frame_weight,
                'surface': self.surface_weight,
                'string': self.string_weight,
                'total': self.total_weight,
                'unit': 'g'
            },
            'performance': {
                'strength_index': self.strength_index,
                'wind_resistance': self.wind_resistance,
                'flight_stability': self.flight_stability,
                'unit': '指数 (0-100)'
            },
            'flight_conditions': {
                'min_wind_speed': self.min_wind_speed,
                'max_wind_speed': self.max_wind_speed,
                'optimal_wind': self.optimal_wind_speed,
                'unit': 'm/s'
            },
            'cost': {
                'estimated_cost': self.estimated_cost,
                'unit': '元'
            },
            'materials_used': self.materials_used
        }


class KiteCalculator:
    """风筝参数计算器"""
    
    def __init__(self, design_data: Dict[str, Any]):
        """
        初始化计算器
        
        Args:
            design_data: 设计数据，包含 drawing 和 materials
        """
        self.design_data = design_data
        self.drawing = design_data.get('drawing', {})
        self.materials = design_data.get('materials', {})
        self.config = get_config()
    
    def calculate_area(self) -> float:
        """计算风筝面积（基于绘图点数估算）"""
        stats = self.drawing.get('statistics', {})
        total_points = stats.get('totalPoints', 0)
        path_count = stats.get('pathCount', 0)
        
        # 兼容不同的数据格式
        if total_points == 0:
            total_points = self.drawing.get('object_count', 0) * 50
        
        if total_points > 0:
            estimated_area = total_points * 0.8
            return round(estimated_area, 2)
        
        return 0.0
    
    def calculate_perimeter(self) -> float:
        """计算风筝周长（基于绘图数据估算）"""
        stats = self.drawing.get('statistics', {})
        path_count = stats.get('pathCount', 0)
        total_points = stats.get('totalPoints', 0)
        
        if total_points == 0:
            total_points = self.drawing.get('object_count', 0) * 50
            path_count = self.drawing.get('object_count', 0)
        
        if path_count > 0:
            avg_path_length = total_points / path_count
            estimated_perimeter = path_count * avg_path_length * 0.5
            return round(estimated_perimeter, 2)
        
        return 0.0
    
    def calculate_frame_weight(self) -> float:
        """计算骨架重量"""
        frame_materials = self.materials.get('骨架材料', [])
        if not frame_materials:
            return 0.0
        
        perimeter = self.calculate_perimeter()
        frame_length = perimeter * 1.5  # 包括交叉支撑
        frame_volume = frame_length * 0.5  # 假设横截面积 0.5 cm²
        
        material_props = self.config.materials.FRAME_MATERIALS
        
        total_weight = 0.0
        for material in frame_materials:
            if material in material_props:
                props = material_props[material]
                material_weight = frame_volume * props.density * props.weight_factor / len(frame_materials)
                total_weight += material_weight
        
        return round(total_weight, 2)
    
    def calculate_surface_weight(self) -> float:
        """计算面料重量"""
        surface_materials = self.materials.get('风筝面料', [])
        if not surface_materials:
            return 0.0
        
        area = self.calculate_area()
        area_sqm = area / 10000  # 转换为平方米
        
        material_props = self.config.materials.SURFACE_MATERIALS
        
        total_weight = 0.0
        for material in surface_materials:
            if material in material_props:
                props = material_props[material]
                material_weight = area_sqm * props.weight_per_sqm / len(surface_materials)
                total_weight += material_weight
        
        return round(total_weight, 2)
    
    def calculate_string_weight(self) -> float:
        """计算绳索重量"""
        string_materials = self.materials.get('绳索材料', [])
        if not string_materials:
            return 0.0
        
        string_length = self.config.system.DEFAULT_STRING_LENGTH
        material_props = self.config.materials.STRING_MATERIALS
        
        total_weight = 0.0
        for material in string_materials:
            if material in material_props:
                props = material_props[material]
                material_weight = string_length * props.weight_per_meter / len(string_materials)
                total_weight += material_weight
        
        return round(total_weight, 2)
    
    def calculate_total_weight(self) -> float:
        """计算总重量"""
        return round(
            self.calculate_frame_weight() +
            self.calculate_surface_weight() +
            self.calculate_string_weight(),
            2
        )
    
    def calculate_strength_index(self) -> float:
        """计算结构强度指数（0-100）"""
        frame_materials = self.materials.get('骨架材料', [])
        if not frame_materials:
            return 0.0
        
        material_props = self.config.materials.FRAME_MATERIALS
        
        total_strength = 0.0
        for material in frame_materials:
            if material in material_props:
                total_strength += material_props[material].strength
        
        return round(total_strength / len(frame_materials), 2)
    
    def calculate_wind_resistance(self) -> float:
        """计算抗风性能指数（0-100）"""
        surface_materials = self.materials.get('风筝面料', [])
        if not surface_materials:
            return 0.0
        
        material_props = self.config.materials.SURFACE_MATERIALS
        
        total_resistance = 0.0
        for material in surface_materials:
            if material in material_props:
                total_resistance += material_props[material].wind_resistance
        
        return round(total_resistance / len(surface_materials), 2)
    
    def calculate_flight_stability(self) -> float:
        """计算飞行稳定性指数（0-100）"""
        area = self.calculate_area()
        weight = self.calculate_total_weight()
        strength = self.calculate_strength_index()
        
        if area > 0:
            weight_area_ratio = weight / area
            # 理想比例约为 0.5 克/cm²
            ratio_score = max(0, 100 - abs(weight_area_ratio - 0.5) * 100)
        else:
            ratio_score = 0
        
        stability = ratio_score * 0.5 + strength * 0.5
        return round(stability, 2)
    
    def calculate_optimal_wind_speed(self) -> Dict[str, float]:
        """计算最佳风速范围"""
        weight = self.calculate_total_weight()
        area = self.calculate_area()
        wind_resistance = self.calculate_wind_resistance()
        
        if area > 0:
            weight_area_ratio = weight / area
            min_wind = 2 + weight_area_ratio * 2
            max_wind = 5 + (wind_resistance / 10) * 3
            
            return {
                'min': round(min_wind, 1),
                'max': round(max_wind, 1)
            }
        
        return {'min': 0.0, 'max': 0.0}
    
    def calculate_cost(self) -> float:
        """计算制作成本估算"""
        total_cost = 0.0
        perimeter = self.calculate_perimeter()
        area = self.calculate_area()
        
        # 骨架成本
        frame_props = self.config.materials.FRAME_MATERIALS
        for material in self.materials.get('骨架材料', []):
            if material in frame_props:
                total_cost += (perimeter / 100) * frame_props[material].cost * 10
        
        # 面料成本
        surface_props = self.config.materials.SURFACE_MATERIALS
        for material in self.materials.get('风筝面料', []):
            if material in surface_props:
                total_cost += (area / 100) * surface_props[material].cost * 5
        
        # 绳索成本
        string_props = self.config.materials.STRING_MATERIALS
        for material in self.materials.get('绳索材料', []):
            if material in string_props:
                total_cost += 50 * string_props[material].cost * 0.2
        
        return round(total_cost, 2)
    
    def calculate_all(self) -> KiteParameters:
        """计算所有参数"""
        wind_speed = self.calculate_optimal_wind_speed()
        
        return KiteParameters(
            area=self.calculate_area(),
            perimeter=self.calculate_perimeter(),
            frame_weight=self.calculate_frame_weight(),
            surface_weight=self.calculate_surface_weight(),
            string_weight=self.calculate_string_weight(),
            total_weight=self.calculate_total_weight(),
            strength_index=self.calculate_strength_index(),
            wind_resistance=self.calculate_wind_resistance(),
            flight_stability=self.calculate_flight_stability(),
            min_wind_speed=wind_speed['min'],
            max_wind_speed=wind_speed['max'],
            optimal_wind_speed=round((wind_speed['min'] + wind_speed['max']) / 2, 1),
            estimated_cost=self.calculate_cost(),
            materials_used=self.materials
        )
    
    def calculate_all_parameters(self) -> Dict[str, Any]:
        """计算所有参数（兼容旧接口）"""
        return self.calculate_all().to_dict()
    
    def generate_report(self) -> str:
        """生成人类可读的分析报告"""
        params = self.calculate_all()
        
        report = f"""
╔══════════════════════════════════════════════╗
║         风筝设计参数分析报告                 ║
╚══════════════════════════════════════════════╝

【基础尺寸】
  • 面积: {params.area} cm²
  • 周长: {params.perimeter} cm

【重量分析】
  • 骨架重量: {params.frame_weight} g
  • 面料重量: {params.surface_weight} g
  • 绳索重量: {params.string_weight} g
  • 总重量: {params.total_weight} g

【性能指标】
  • 结构强度: {params.strength_index}/100
  • 抗风性能: {params.wind_resistance}/100
  • 飞行稳定性: {params.flight_stability}/100

【飞行条件】
  • 最小风速: {params.min_wind_speed} m/s
  • 最大风速: {params.max_wind_speed} m/s
  • 最佳风速: {params.optimal_wind_speed} m/s

【成本估算】
  • 预计成本: ¥{params.estimated_cost}

【材料清单】
"""
        
        for category, materials in params.materials_used.items():
            if materials:
                report += f"  • {category}: {', '.join(materials)}\n"
        
        report += "\n" + "=" * 50 + "\n"
        
        return report
