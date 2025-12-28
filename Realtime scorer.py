"""
单Bin版实时评分系统
监控一个 Bin 中的所有设计，只对新设计评分
"""

import time
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional, List
from jsonbin import JSONBinService
from kite_calculator import KiteCalculator


class SingleBinRealtimeScorer:
    """单Bin版实时评分系统"""
    
    def __init__(self, api_key: str, check_interval: int = 3):
        """
        初始化
        
        Args:
            api_key: JSONBin API Key
            check_interval: 检查间隔（秒）
        """
        self.api_key = api_key
        self.check_interval = check_interval
        self.jsonbin = JSONBinService(api_key)
        
        # 已评分的设计 ID 集合
        self.scored_design_ids = set()
        
        # 当前 Bin ID
        self.bin_id = None
        
        # 评分概要
        self.score_summary = []
    
    def _get_bin_id(self) -> Optional[str]:
        """
        获取固定的 Bin ID
        
        优先级：
        1. fixed_bin_id.txt（设计器使用）
        2. latest_bin.txt（兼容旧版）
        
        Returns:
            Bin ID 或 None
        """
        # 尝试读取固定 Bin ID
        for filename in ['fixed_bin_id.txt', 'latest_bin.txt']:
            try:
                with open(filename, 'r') as f:
                    bin_id = f.read().strip()
                    if bin_id:
                        return bin_id
            except FileNotFoundError:
                continue
            except Exception as e:
                print(f"⚠️ 读取 {filename} 失败: {str(e)}")
        
        return None
    
    def fetch_all_designs(self) -> Optional[List[Dict[str, Any]]]:
        """
        获取 Bin 中的所有设计
        
        Returns:
            设计列表 或 None
        """
        # 获取 Bin ID
        bin_id = self._get_bin_id()
        
        if not bin_id:
            return None
        
        # 更新当前 Bin ID
        if bin_id != self.bin_id:
            print(f"\n📂 加载 Bin: {bin_id[:20]}...")
            self.bin_id = bin_id
        
        # 读取数据
        try:
            response = self.jsonbin.read_bin(self.bin_id)
            data = response.get('record', response)
            
            # 提取设计列表
            designs = data.get('designs', [])
            
            return designs
            
        except Exception as e:
            print(f"❌ 读取失败: {str(e)}")
            return None
    
    def get_new_designs(self, all_designs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        筛选出未评分的新设计
        
        Args:
            all_designs: 所有设计列表
            
        Returns:
            新设计列表
        """
        new_designs = []
        
        for design in all_designs:
            design_id = design.get('design_id', design.get('created_at', 'unknown'))
            
            if design_id not in self.scored_design_ids:
                new_designs.append(design)
                self.scored_design_ids.add(design_id)
        
        return new_designs
    
    def calculate_score(self, design: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算单个设计的评分
        
        Args:
            design: 设计数据
            
        Returns:
            评分结果
        """
        try:
            # 构造 KiteCalculator 需要的数据格式
            calculator_data = {
                'drawing': design.get('drawing'),
                'materials': design.get('materials'),
                'metadata': {
                    'created_at': design.get('created_at')
                }
            }
            
            calculator = KiteCalculator(calculator_data)
            params = calculator.calculate_all_parameters()
            
            score = self._calculate_comprehensive_score(params)
            
            return {
                'design_id': design.get('design_id', 'unknown'),
                'timestamp': datetime.now().isoformat(),
                'created_at': design.get('created_at'),
                'score': score,
                'parameters': params,
                'success': True
            }
            
        except Exception as e:
            print(f"❌ 计算评分失败: {str(e)}")
            return {
                'design_id': design.get('design_id', 'unknown'),
                'timestamp': datetime.now().isoformat(),
                'score': 0,
                'error': str(e),
                'success': False
            }
    
    def _calculate_comprehensive_score(self, params: Dict[str, Any]) -> float:
        """计算综合评分（0-100）"""
        weights = {
            'performance': 0.40,
            'feasibility': 0.30,
            'cost': 0.20,
            'innovation': 0.10
        }
        
        # 性能评分
        performance_score = (
            params['performance']['flight_stability'] * 0.5 +
            params['performance']['strength_index'] * 0.3 +
            params['performance']['wind_resistance'] * 0.2
        )
        
        # 可行性评分
        weight = params['weight']['total']
        area = params['dimensions']['area']
        
        if area > 0:
            weight_area_ratio = weight / area
            if 0.3 <= weight_area_ratio <= 0.7:
                feasibility_score = 100
            elif 0.2 <= weight_area_ratio <= 1.0:
                feasibility_score = 70
            else:
                feasibility_score = 40
        else:
            feasibility_score = 0
        
        # 成本评分
        cost = params['cost']['estimated_cost']
        if cost < 50:
            cost_score = 100
        elif cost < 100:
            cost_score = 80
        elif cost < 150:
            cost_score = 60
        else:
            cost_score = 30
        
        # 创新性评分
        materials_count = sum(len(mats) for mats in params['materials_used'].values())
        innovation_score = min(materials_count * 20, 100)
        
        # 综合评分
        final_score = (
            performance_score * weights['performance'] +
            feasibility_score * weights['feasibility'] +
            cost_score * weights['cost'] +
            innovation_score * weights['innovation']
        )
        
        return round(final_score, 1)
    
    def display_score(self, score_data: Dict[str, Any]):
        """显示评分"""
        print("\n" + "="*60)
        print(f"🎯 设计评分 - {score_data.get('design_id', 'unknown')}")
        print("="*60)
        
        print(f"\n⭐ 综合评分: {score_data['score']}/100")
        print(f"📅 创建时间: {score_data.get('created_at', 'unknown')[:19]}")
        
        if score_data.get('success') and 'parameters' in score_data:
            params = score_data['parameters']
            
            print(f"\n📏 面积: {params['dimensions']['area']:.1f} cm²")
            print(f"⚖️  重量: {params['weight']['total']:.1f} g")
            print(f"💰 成本: ¥{params['cost']['estimated_cost']:.1f}")
            
            print(f"\n🎯 性能:")
            print(f"   稳定性: {params['performance']['flight_stability']:.0f}/100")
            print(f"   强度: {params['performance']['strength_index']:.0f}/100")
            
            # 材料
            materials = []
            for category, items in params['materials_used'].items():
                if items:
                    materials.extend(items)
            
            if materials:
                print(f"\n📦 材料: {', '.join(materials)}")
        
        print("\n" + "="*60 + "\n")
    
    def save_score_summary(self, score_data: Dict[str, Any]):
        """保存评分概要"""
        summary = {
            'design_id': score_data.get('design_id'),
            'timestamp': score_data['timestamp'],
            'created_at': score_data.get('created_at'),
            'score': score_data['score']
        }
        
        self.score_summary.append(summary)
        
        # 追加到文件
        try:
            with open('scores_summary.jsonl', 'a', encoding='utf-8') as f:
                f.write(json.dumps(summary, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"⚠️ 保存概要失败: {str(e)}")
    
    def run_once(self) -> int:
        """
        执行一次检查
        
        Returns:
            新评分的设计数量
        """
        current_time = datetime.now().strftime('%H:%M:%S')
        print(f"[{current_time}] 检查更新...", end='')
        
        # 获取所有设计
        all_designs = self.fetch_all_designs()
        
        if all_designs is None:
            print(" 无法读取数据")
            return 0
        
        # 筛选新设计
        new_designs = self.get_new_designs(all_designs)
        
        if not new_designs:
            print(f" 无新设计 (共 {len(all_designs)} 个)")
            return 0
        
        print(f" 发现 {len(new_designs)} 个新设计！")
        
        # 逐个评分
        for design in new_designs:
            score_result = self.calculate_score(design)
            self.display_score(score_result)
            self.save_score_summary(score_result)
        
        return len(new_designs)
    
    def run_continuous(self):
        """持续监控模式"""
        print("="*60)
        print("   🚀 单Bin版实时评分系统")
        print("="*60)
        print("\n特性:")
        print("  ✅ 监控单个 Bin 中的所有设计")
        print("  ✅ 自动识别新设计")
        print("  ✅ 只对每个设计评分一次")
        print("  ✅ 支持批量评分")
        print(f"\n⏱️  检查间隔: {self.check_interval} 秒")
        print("💡 在设计器中添加新设计会自动评分")
        print("\n按 Ctrl+C 停止\n")
        print("="*60)
        
        try:
            while True:
                self.run_once()
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print("\n\n" + "="*60)
            print("⏹️  监控已停止")
            print(f"📊 共评分 {len(self.score_summary)} 个设计")
            
            if self.score_summary:
                print("\n最近评分:")
                for summary in self.score_summary[-5:]:
                    print(f"  • {summary['design_id']}: {summary['score']}/100")
            
            print("="*60)


def main():
    """主函数"""
    API_KEY = "$2a$10$pleOacf0lQu1mvIU//jjfeYPUCb.kiFXX.08qupD/90UYKwHtU8e."
    
    # 创建评分系统
    scorer = SingleBinRealtimeScorer(API_KEY, check_interval=3)
    
    # 持续监控
    scorer.run_continuous()


if __name__ == "__main__":
    main()