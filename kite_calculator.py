"""
风筝参数计算系统
根据绘图数据（点数、尺寸）和材料选择计算风筝的各项参数
"""

from typing import Dict, Any
import math


class KiteCalculator:
    """风筝参数计算器"""
    
    # 材料属性数据库
    MATERIAL_PROPERTIES = {
        # 骨架材料属性
        '骨架材料': {
            '竹子': {
                'density': 0.6,        # 密度 (g/cm³)
                'strength': 80,        # 强度指数
                'flexibility': 85,     # 柔韧性指数
                'cost': 1.0,          # 成本系数
                'weight_factor': 1.0   # 重量系数
            },
            '铝合金': {
                'density': 2.7,
                'strength': 150,
                'flexibility': 60,
                'cost': 3.5,
                'weight_factor': 0.8
            },
            '碳纤维': {
                'density': 1.6,
                'strength': 200,
                'flexibility': 70,
                'cost': 8.0,
                'weight_factor': 0.5
            }
        },
        
        # 风筝面料属性
        '风筝面料': {
            '丝绸': {
                'weight_per_sqm': 60,    # 克/平方米
                'wind_resistance': 70,   # 抗风性
                'durability': 60,        # 耐用性
                'cost': 2.0,
                'air_permeability': 15   # 透气性 (越低越好)
            },
            '尼龙': {
                'weight_per_sqm': 85,
                'wind_resistance': 95,
                'durability': 90,
                'cost': 1.5,
                'air_permeability': 5
            },
            'Mylar膜': {
                'weight_per_sqm': 50,
                'wind_resistance': 85,
                'durability': 75,
                'cost': 3.0,
                'air_permeability': 2
            }
        },
        
        # 绳索材料属性
        '绳索材料': {
            '麻绳': {
                'tensile_strength': 500,   # 拉伸强度 (N)
                'weight_per_meter': 8,     # 克/米
                'elasticity': 30,          # 弹性指数
                'cost': 0.5
            },
            '钢索': {
                'tensile_strength': 2000,
                'weight_per_meter': 15,
                'elasticity': 10,
                'cost': 2.0
            },
            '凯夫拉': {
                'tensile_strength': 3000,
                'weight_per_meter': 5,
                'elasticity': 20,
                'cost': 5.0
            }
        }
    }
    
    def __init__(self, design_data: Dict[str, Any]):
        """
        初始化计算器
        
        Args:
            design_data: 从 JSONBin 读取的完整设计数据
        """
        self.design_data = design_data
        self.drawing = design_data.get('drawing', {})
        self.materials = design_data.get('materials', {})
        
    def calculate_area(self) -> float:
        """
        计算风筝面积 (基于绘图点数估算)
        
        Returns:
            估算面积 (平方厘米)
        """
        stats = self.drawing.get('statistics', {})
        total_points = stats.get('totalPoints', 0)
        path_count = stats.get('pathCount', 0)
        
        # 基于点数估算面积
        # 假设每个点代表约 1 平方厘米的绘图区域
        if total_points > 0:
            # 考虑路径密度
            density_factor = total_points / max(path_count, 1)
            estimated_area = total_points * 0.8  # 0.8 是经验系数
            return round(estimated_area, 2)
        
        return 0.0
    
    def calculate_perimeter(self) -> float:
        """
        计算风筝周长 (基于绘图数据估算)
        
        Returns:
            估算周长 (厘米)
        """
        stats = self.drawing.get('statistics', {})
        path_count = stats.get('pathCount', 0)
        total_points = stats.get('totalPoints', 0)
        
        # 基于路径数和点数估算周长
        if path_count > 0:
            avg_path_length = total_points / path_count
            estimated_perimeter = path_count * avg_path_length * 0.5
            return round(estimated_perimeter, 2)
        
        return 0.0
    
    def calculate_frame_weight(self) -> float:
        """
        计算骨架重量
        
        Returns:
            骨架重量 (克)
        """
        frame_materials = self.materials.get('骨架材料', [])
        if not frame_materials:
            return 0.0
        
        perimeter = self.calculate_perimeter()
        
        # 假设骨架长度约为周长的 1.5 倍 (包括交叉支撑)
        frame_length = perimeter * 1.5
        
        # 假设骨架横截面积约为 0.5 cm²
        frame_volume = frame_length * 0.5  # cm³
        
        total_weight = 0.0
        for material in frame_materials:
            props = self.MATERIAL_PROPERTIES['骨架材料'].get(material, {})
            density = props.get('density', 1.0)
            weight_factor = props.get('weight_factor', 1.0)
            
            # 计算该材料的重量贡献
            material_weight = frame_volume * density * weight_factor / len(frame_materials)
            total_weight += material_weight
        
        return round(total_weight, 2)
    
    def calculate_surface_weight(self) -> float:
        """
        计算面料重量
        
        Returns:
            面料重量 (克)
        """
        surface_materials = self.materials.get('风筝面料', [])
        if not surface_materials:
            return 0.0
        
        area = self.calculate_area()
        area_sqm = area / 10000  # 转换为平方米
        
        total_weight = 0.0
        for material in surface_materials:
            props = self.MATERIAL_PROPERTIES['风筝面料'].get(material, {})
            weight_per_sqm = props.get('weight_per_sqm', 70)
            
            # 计算该材料的重量贡献
            material_weight = area_sqm * weight_per_sqm / len(surface_materials)
            total_weight += material_weight
        
        return round(total_weight, 2)
    
    def calculate_string_weight(self) -> float:
        """
        计算绳索重量 (假设标准长度 50 米)
        
        Returns:
            绳索重量 (克)
        """
        string_materials = self.materials.get('绳索材料', [])
        if not string_materials:
            return 0.0
        
        string_length = 50  # 标准长度 50 米
        
        total_weight = 0.0
        for material in string_materials:
            props = self.MATERIAL_PROPERTIES['绳索材料'].get(material, {})
            weight_per_meter = props.get('weight_per_meter', 8)
            
            # 计算该材料的重量贡献
            material_weight = string_length * weight_per_meter / len(string_materials)
            total_weight += material_weight
        
        return round(total_weight, 2)
    
    def calculate_total_weight(self) -> float:
        """
        计算风筝总重量
        
        Returns:
            总重量 (克)
        """
        frame_weight = self.calculate_frame_weight()
        surface_weight = self.calculate_surface_weight()
        string_weight = self.calculate_string_weight()
        
        total = frame_weight + surface_weight + string_weight
        return round(total, 2)
    
    def calculate_strength_index(self) -> float:
        """
        计算结构强度指数 (0-100)
        
        Returns:
            强度指数
        """
        frame_materials = self.materials.get('骨架材料', [])
        if not frame_materials:
            return 0.0
        
        total_strength = 0.0
        for material in frame_materials:
            props = self.MATERIAL_PROPERTIES['骨架材料'].get(material, {})
            strength = props.get('strength', 50)
            total_strength += strength
        
        avg_strength = total_strength / len(frame_materials)
        return round(avg_strength, 2)
    
    def calculate_wind_resistance(self) -> float:
        """
        计算抗风性能指数 (0-100)
        
        Returns:
            抗风性能指数
        """
        surface_materials = self.materials.get('风筝面料', [])
        if not surface_materials:
            return 0.0
        
        total_resistance = 0.0
        for material in surface_materials:
            props = self.MATERIAL_PROPERTIES['风筝面料'].get(material, {})
            resistance = props.get('wind_resistance', 50)
            total_resistance += resistance
        
        avg_resistance = total_resistance / len(surface_materials)
        return round(avg_resistance, 2)
    
    def calculate_flight_stability(self) -> float:
        """
        计算飞行稳定性指数 (0-100)
        综合考虑重量、面积、强度
        
        Returns:
            稳定性指数
        """
        area = self.calculate_area()
        weight = self.calculate_total_weight()
        strength = self.calculate_strength_index()
        
        # 重量面积比 (越接近理想值越好)
        if area > 0:
            weight_area_ratio = weight / area
            # 理想比例约为 0.5 克/cm²
            ratio_score = max(0, 100 - abs(weight_area_ratio - 0.5) * 100)
        else:
            ratio_score = 0
        
        # 综合稳定性
        stability = (ratio_score * 0.5 + strength * 0.5)
        return round(stability, 2)
    
    def calculate_optimal_wind_speed(self) -> Dict[str, float]:
        """
        计算最佳风速范围
        
        Returns:
            {'min': 最小风速(m/s), 'max': 最大风速(m/s)}
        """
        weight = self.calculate_total_weight()
        area = self.calculate_area()
        wind_resistance = self.calculate_wind_resistance()
        
        if area > 0:
            # 基础风速计算 (基于重量面积比)
            weight_area_ratio = weight / area
            
            # 最小起飞风速
            min_wind = 2 + weight_area_ratio * 2
            
            # 最大安全风速 (基于抗风性)
            max_wind = 5 + (wind_resistance / 10) * 3
            
            return {
                'min': round(min_wind, 1),
                'max': round(max_wind, 1)
            }
        
        return {'min': 0.0, 'max': 0.0}
    
    def calculate_cost(self) -> float:
        """
        计算制作成本估算 (相对值)
        
        Returns:
            成本估算 (元)
        """
        total_cost = 0.0
        
        # 骨架成本
        frame_materials = self.materials.get('骨架材料', [])
        perimeter = self.calculate_perimeter()
        for material in frame_materials:
            props = self.MATERIAL_PROPERTIES['骨架材料'].get(material, {})
            cost_factor = props.get('cost', 1.0)
            total_cost += (perimeter / 100) * cost_factor * 10
        
        # 面料成本
        surface_materials = self.materials.get('风筝面料', [])
        area = self.calculate_area()
        for material in surface_materials:
            props = self.MATERIAL_PROPERTIES['风筝面料'].get(material, {})
            cost_factor = props.get('cost', 1.0)
            total_cost += (area / 100) * cost_factor * 5
        
        # 绳索成本
        string_materials = self.materials.get('绳索材料', [])
        for material in string_materials:
            props = self.MATERIAL_PROPERTIES['绳索材料'].get(material, {})
            cost_factor = props.get('cost', 1.0)
            total_cost += 50 * cost_factor * 0.2
        
        return round(total_cost, 2)
    
    def calculate_all_parameters(self) -> Dict[str, Any]:
        """
        计算所有参数
        
        Returns:
            包含所有计算参数的字典
        """
        wind_speed = self.calculate_optimal_wind_speed()
        
        return {
            # 基础尺寸
            'dimensions': {
                'area': self.calculate_area(),
                'perimeter': self.calculate_perimeter(),
                'unit': 'cm/cm²'
            },
            
            # 重量分析
            'weight': {
                'frame': self.calculate_frame_weight(),
                'surface': self.calculate_surface_weight(),
                'string': self.calculate_string_weight(),
                'total': self.calculate_total_weight(),
                'unit': 'g'
            },
            
            # 性能指标
            'performance': {
                'strength_index': self.calculate_strength_index(),
                'wind_resistance': self.calculate_wind_resistance(),
                'flight_stability': self.calculate_flight_stability(),
                'unit': '指数 (0-100)'
            },
            
            # 飞行条件
            'flight_conditions': {
                'min_wind_speed': wind_speed['min'],
                'max_wind_speed': wind_speed['max'],
                'optimal_wind': round((wind_speed['min'] + wind_speed['max']) / 2, 1),
                'unit': 'm/s'
            },
            
            # 成本
            'cost': {
                'estimated_cost': self.calculate_cost(),
                'unit': '元'
            },
            
            # 材料清单
            'materials_used': self.materials
        }
    
    def generate_report(self) -> str:
        """
        生成人类可读的分析报告
        
        Returns:
            格式化的报告文本
        """
        params = self.calculate_all_parameters()
        
        report = f"""
╔══════════════════════════════════════════════╗
║         风筝设计参数分析报告                 ║
╚══════════════════════════════════════════════╝

【基础尺寸】
  • 面积: {params['dimensions']['area']} cm²
  • 周长: {params['dimensions']['perimeter']} cm

【重量分析】
  • 骨架重量: {params['weight']['frame']} g
  • 面料重量: {params['weight']['surface']} g
  • 绳索重量: {params['weight']['string']} g
  • 总重量: {params['weight']['total']} g

【性能指标】
  • 结构强度: {params['performance']['strength_index']}/100
  • 抗风性能: {params['performance']['wind_resistance']}/100
  • 飞行稳定性: {params['performance']['flight_stability']}/100

【飞行条件】
  • 最小风速: {params['flight_conditions']['min_wind_speed']} m/s
  • 最大风速: {params['flight_conditions']['max_wind_speed']} m/s
  • 最佳风速: {params['flight_conditions']['optimal_wind']} m/s

【成本估算】
  • 预计成本: ¥{params['cost']['estimated_cost']}

【材料清单】
"""
        
        for category, materials in params['materials_used'].items():
            if materials:
                report += f"  • {category}: {', '.join(materials)}\n"
        
        report += "\n" + "="*50 + "\n"
        
        return report


def analyze_kite_from_jsonbin(jsonbin_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    便捷函数：从 JSONBin 数据分析风筝参数
    
    Args:
        jsonbin_data: 从 JSONBin 获取的原始数据
        
    Returns:
        完整的参数分析结果
    """
    calculator = KiteCalculator(jsonbin_data)
    return calculator.calculate_all_parameters()