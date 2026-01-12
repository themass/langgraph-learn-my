#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
运行所有推理范式的 Demo
"""

import sys
import importlib.util

def run_demo(module_name, demo_func_name="demo"):
    """运行指定的 demo"""
    try:
        spec = importlib.util.spec_from_file_location(module_name, f"{module_name}.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if hasattr(module, demo_func_name):
            demo_func = getattr(module, demo_func_name)
            demo_func()
            return True
        else:
            print(f"❌ {module_name} 中没有找到 {demo_func_name} 函数")
            return False
    except Exception as e:
        print(f"❌ 运行 {module_name} 时出错: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("大模型驱动智能体的 5 大核心推理范式 Demo")
    print("=" * 60)
    
    demos = [
        ("01_cot_chain_of_thought", "demo_cot"),
        ("02_react_reasoning_acting", "demo_react"),
        ("03_tot_tree_of_thoughts", "demo_tot"),
        ("04_self_consistency", "demo_self_consistency"),
        ("05_self_reflection", "demo_self_reflection"),
    ]
    
    results = []
    
    for module_name, func_name in demos:
        print(f"\n{'='*60}")
        print(f"运行: {module_name}")
        print(f"{'='*60}\n")
        
        success = run_demo(module_name, func_name)
        results.append((module_name, success))
        
        print("\n")
    
    # 显示总结
    print("=" * 60)
    print("运行总结")
    print("=" * 60)
    
    for module_name, success in results:
        status = "✅ 成功" if success else "❌ 失败"
        print(f"{status}: {module_name}")
    
    success_count = sum(1 for _, success in results if success)
    print(f"\n总计: {success_count}/{len(results)} 个 Demo 运行成功")


if __name__ == "__main__":
    main()
