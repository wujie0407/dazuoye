#!/usr/bin/env python3
"""
实时评分监控脚本
监控 JSONBin 中的新设计，自动评分并显示结果
"""

import time
import json
import sys
from datetime import datetime

# 添加项目路径
sys.path.insert(0, '.')

from config import get_config
from services import DesignRepository
from core import KiteScorer, ScoreLevel


class RealtimeScorerCLI:
    """命令行版实时评分监控"""
    
    def __init__(self, check_interval: int = 3):
        self.config = get_config()
        self.check_interval = check_interval
        self.repository = DesignRepository()
        self.scorer = KiteScorer()
        
        self.processed_ids: set = set()
        self.score_history: list = []
    
    def display_score(self, design_id: str, result, design: dict):
        """显示评分结果"""
        print("\n" + "=" * 60)
        print(f"🎯 设计评分 - {design_id}")
        print("=" * 60)
        
        # 总分和等级
        level_emoji = {
            ScoreLevel.SUCCESS: "🎉",
            ScoreLevel.STRUGGLE: "😅", 
            ScoreLevel.FAIL: "💦"
        }
        
        print(f"\n⭐ 综合评分: {result.total_score}/100 {level_emoji.get(result.level, '')}")
        print(f"📊 等级: {result.level.value}")
        
        # 分项得分
        print(f"\n📈 分项得分:")
        print(f"   性能: {result.performance_score:.1f}")
        print(f"   可行性: {result.feasibility_score:.1f}")
        print(f"   成本: {result.cost_score:.1f}")
        print(f"   创新: {result.innovation_score:.1f}")
        
        # 参数详情
        if result.parameters:
            params = result.parameters
            print(f"\n📏 面积: {params.area:.1f} cm²")
            print(f"⚖️  重量: {params.total_weight:.1f} g")
            print(f"💰 成本: ¥{params.estimated_cost:.1f}")
            
            # 材料
            materials = []
            for category, items in params.materials_used.items():
                if items:
                    materials.extend(items)
            
            if materials:
                print(f"\n📦 材料: {', '.join(materials)}")
        
        # AI 图片
        if design.get('ai_image_url'):
            print(f"\n🎨 AI效果图: {design['ai_image_url'][:60]}...")
        
        print("\n" + "=" * 60 + "\n")
    
    def save_summary(self, design_id: str, result):
        """保存评分概要"""
        summary = {
            'design_id': design_id,
            'timestamp': datetime.now().isoformat(),
            'score': result.total_score,
            'level': result.level.value
        }
        
        self.score_history.append(summary)
        
        try:
            with open(self.config.system.SCORES_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps(summary, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"⚠️ 保存概要失败: {e}")
    
    def run_once(self) -> int:
        """执行一次检查"""
        current_time = datetime.now().strftime('%H:%M:%S')
        print(f"[{current_time}] 检查更新...", end='')
        
        designs = self.repository.get_all_designs()
        
        if not designs:
            print(" 无法读取数据或无设计")
            return 0
        
        new_count = 0
        
        for design in designs:
            design_id = design.get('design_id', design.get('created_at', 'unknown'))
            
            if design_id not in self.processed_ids:
                self.processed_ids.add(design_id)
                new_count += 1
                
                print(f" 发现新设计！")
                
                try:
                    result = self.scorer.score(design)
                    self.display_score(design_id, result, design)
                    self.save_summary(design_id, result)
                except Exception as e:
                    print(f"❌ 评分失败: {e}")
        
        if new_count == 0:
            print(f" 无新设计 (共 {len(designs)} 个)")
        
        return new_count
    
    def run(self):
        """持续监控模式"""
        print("=" * 60)
        print("   🚀 风筝设计实时评分系统")
        print("=" * 60)
        print("\n特性:")
        print("  ✅ 监控 JSONBin 中的所有设计")
        print("  ✅ 自动识别新设计")
        print("  ✅ 实时计算评分")
        print("  ✅ 显示详细参数")
        print(f"\n⏱️  检查间隔: {self.check_interval} 秒")
        print("💡 在设计系统中添加新设计会自动评分")
        print("\n按 Ctrl+C 停止\n")
        print("=" * 60)
        
        try:
            while True:
                self.run_once()
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print("\n\n" + "=" * 60)
            print("⏹️  监控已停止")
            print(f"📊 共评分 {len(self.score_history)} 个设计")
            
            if self.score_history:
                print("\n最近评分:")
                for summary in self.score_history[-5:]:
                    print(f"  • {summary['design_id']}: {summary['score']}/100 ({summary['level']})")
            
            print("=" * 60)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='风筝设计实时评分系统')
    parser.add_argument(
        '-i', '--interval',
        type=int,
        default=3,
        help='检查间隔（秒），默认 3'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='只运行一次'
    )
    
    args = parser.parse_args()
    
    scorer = RealtimeScorerCLI(check_interval=args.interval)
    
    if args.once:
        scorer.run_once()
    else:
        scorer.run()


if __name__ == "__main__":
    main()
