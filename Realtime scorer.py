"""
智能实时评分系统
自动追踪设计器创建的最新 Bin ID
"""

import time
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from jsonbin import JSONBinService
from kite_calculator import KiteCalculator


class SmartRealtimeScorer:
    """智能实时评分系统"""
    
    def __init__(self, api_key: str, check_interval: int = 5, tracker_file: str = "latest_bin.txt"):
        """
        初始化智能实时评分系统
        
        Args:
            api_key: JSONBin API Key
            check_interval: 检查间隔（秒）
            tracker_file: 用于跟踪最新 Bin ID 的文件
        """
        self.api_key = api_key
        self.check_interval = check_interval
        self.tracker_file = tracker_file
        self.jsonbin = JSONBinService(api_key)
        
        self.current_bin_id = None
        self.last_update_time = None
        self.score_history = []
        
        # 加载上次的 Bin ID
        self._load_latest_bin()
    
    def _load_latest_bin(self):
        """从文件加载最新的 Bin ID"""
        if os.path.exists(self.tracker_file):
            try:
                with open(self.tracker_file, 'r') as f:
                    self.current_bin_id = f.read().strip()
                print(f"📂 加载上次的 Bin ID: {self.current_bin_id[:20]}...")
            except:
                pass
    
    def _save_latest_bin(self, bin_id: str):
        """保存最新的 Bin ID 到文件"""
        try:
            with open(self.tracker_file, 'w') as f:
                f.write(bin_id)
        except:
            pass
    
    def set_bin_id(self, bin_id: str):
        """
        手动设置要监控的 Bin ID
        
        Args:
            bin_id: Bin ID
        """
        self.current_bin_id = bin_id
        self._save_latest_bin(bin_id)
        print(f"✅ 已设置监控 Bin: {bin_id[:20]}...")
    
    def fetch_latest_data(self) -> Optional[Dict[str, Any]]:
        """获取当前 Bin 的最新数据"""
        if not self.current_bin_id:
            print("⚠️ 未设置 Bin ID")
            return None
        
        try:
            response = self.jsonbin.read_bin(self.current_bin_id)
            return response.get('record', response)
        except Exception as e:
            print(f"❌ 获取数据失败: {str(e)}")
            return None
    
    def check_for_updates(self, current_data: Dict[str, Any]) -> bool:
        """检查数据是否更新"""
        # 检查多个时间戳来源
        timestamps = [
            current_data.get('metadata', {}).get('created_at'),
            current_data.get('drawing', {}).get('timestamp'),
        ]
        
        for ts in timestamps:
            if ts and ts != self.last_update_time:
                self.last_update_time = ts
                return True
        
        return False
    
    def calculate_score(self, design_data: Dict[str, Any]) -> Dict[str, Any]:
        """计算设计评分"""
        try:
            calculator = KiteCalculator(design_data)
            params = calculator.calculate_all_parameters()
            
            score = self._calculate_comprehensive_score(params)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'bin_id': self.current_bin_id,
                'score': score,
                'parameters': params,
                'design_id': design_data.get('metadata', {}).get('created_at', 'unknown'),
                'success': True
            }
            
        except Exception as e:
            print(f"❌ 计算评分失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'timestamp': datetime.now().isoformat(),
                'bin_id': self.current_bin_id,
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
        print("🎯 风筝设计评分结果")
        print("="*60)
        
        print(f"\n⭐ 综合评分: {score_data['score']}/100")
        print(f"📅 评分时间: {score_data['timestamp']}")
        
        if score_data.get('success') and 'parameters' in score_data:
            params = score_data['parameters']
            
            print("\n【基础参数】")
            print(f"  面积: {params['dimensions']['area']} cm²")
            print(f"  总重量: {params['weight']['total']} g")
            
            print("\n【性能指标】")
            print(f"  飞行稳定性: {params['performance']['flight_stability']}/100")
            print(f"  结构强度: {params['performance']['strength_index']}/100")
            print(f"  抗风性能: {params['performance']['wind_resistance']}/100")
            
            print("\n【成本】")
            print(f"  预估成本: ¥{params['cost']['estimated_cost']}")
            
            print("\n【材料】")
            for category, materials in params['materials_used'].items():
                if materials:
                    print(f"  {category}: {', '.join(materials)}")
        
        print("\n" + "="*60 + "\n")
    
    def save_score(self, score_data: Dict[str, Any]):
        """保存评分结果"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"score_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(score_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 评分已保存: {filename}")
        except Exception as e:
            print(f"❌ 保存失败: {str(e)}")
    
    def run_once(self) -> Optional[Dict[str, Any]]:
        """执行一次评分"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 检查更新...")
        
        # 获取最新数据
        data = self.fetch_latest_data()
        if not data:
            return None
        
        # 检查是否更新
        if not self.check_for_updates(data):
            print("  无更新")
            return None
        
        print("  ✨ 发现新数据！开始评分...")
        
        # 计算评分
        score_result = self.calculate_score(data)
        
        # 保存到历史
        self.score_history.append(score_result)
        
        # 显示结果
        self.display_score(score_result)
        
        # 保存到文件
        self.save_score(score_result)
        
        return score_result
    
    def run_continuous(self):
        """持续监控模式"""
        print("🚀 智能实时评分系统启动")
        print(f"📊 监控 Bin ID: {self.current_bin_id[:20] if self.current_bin_id else '未设置'}...")
        print(f"⏱️  检查间隔: {self.check_interval} 秒")
        print("\n💡 提示: 在设计器中上传新设计会自动更新此 Bin")
        print("按 Ctrl+C 停止监控\n")
        
        try:
            while True:
                self.run_once()
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print("\n\n⏹️  监控已停止")
            print(f"📈 共完成 {len(self.score_history)} 次评分")


def main():
    """主函数"""
    import sys
    
    API_KEY = "$2a$10$pleOacf0lQu1mvIU//jjfeYPUCb.kiFXX.08qupD/90UYKwHtU8e."
    
    print("="*60)
    print("   智能实时评分系统")
    print("="*60)
    
    # 创建评分系统
    scorer = SmartRealtimeScorer(API_KEY, check_interval=5)
    
    # 检查是否有保存的 Bin ID
    if not scorer.current_bin_id:
        print("\n📋 首次运行，请输入 Bin ID:")
        print("   (从设计器上传后，在左侧边栏复制)")
        
        if len(sys.argv) > 1:
            bin_id = sys.argv[1]
        else:
            bin_id = input("\nBin ID: ").strip()
        
        if not bin_id:
            print("❌ 错误: 未提供 Bin ID")
            return
        
        scorer.set_bin_id(bin_id)
    
    print("\n选择运行模式:")
    print("1. 单次评分")
    print("2. 持续监控")
    mode = input("> ").strip()
    
    if mode == "1":
        result = scorer.run_once()
        if result:
            print("\n✅ 评分完成！")
        else:
            print("\n⚠️ 未找到数据或数据未更新")
    
    elif mode == "2":
        scorer.run_continuous()
    
    else:
        print("❌ 无效选项")


if __name__ == "__main__":
    main()