#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
终极修复版：文件夹按权重排序，文件按自然排序（1,2,3...10）
"""

import os
import re
from pathlib import Path
from datetime import datetime


# ==================== 配置 ====================

SKIP_DIRS = {'.git', '__pycache__', '.vscode', 'node_modules', '.idea', 'venv', 'env'}
RULE_FILE = "sort_order.txt"
FILTER_EXT = ".html"


# ==================== 排序逻辑 ====================

def load_sort_rules(rule_file):
    """加载排序规则"""
    rules = {}
    
    if not os.path.exists(rule_file):
        print(f"❌ 未找到规则文件: {rule_file}")
        return rules
    
    try:
        with open(rule_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split('|')
                if len(parts) >= 2:
                    name = parts[0].strip()
                    try:
                        weight = float(parts[1].strip())
                        rules[name] = weight
                    except ValueError:
                        pass
                        
    except Exception as e:
        print(f"❌ 读取规则文件失败: {e}")
        return {}
    
    print(f"✅ 已加载 {len(rules)} 条排序规则")
    return rules


def natural_sort_key(s):
    """自然排序：把字符串中的数字按数值排序"""
    return [int(t) if t.isdigit() else t.lower() 
            for t in re.split(r'(\d+)', str(s))]


def get_sort_key(item, rules):
    """
    获取排序键：
    1. 有规则的按权重值排序
    2. 无规则的按自然排序
    """
    name = item.name
    
    if name in rules:
        return (0, rules[name], "", "")
    
    return (1, 0, name.lower(), natural_sort_key(name))


# ==================== 树状生成 ====================

def make_tree(path, prefix="", rules=None):
    """生成树状结构"""
    if rules is None:
        rules = {}
    
    lines = []
    
    try:
        # 获取所有项目
        items = list(Path(path).iterdir())
        
        # 按规则排序（文件夹用权重，文件用自然排序）
        items.sort(key=lambda x: get_sort_key(x, rules))
        
        # 过滤系统文件夹
        items = [item for item in items 
                 if not (item.is_dir() and item.name in SKIP_DIRS)]
        
        # 分离文件夹和文件
        dirs = [d for d in items if d.is_dir()]
        files = [f for f in items if f.is_file()]
        
        # 过滤文件后缀
        if FILTER_EXT:
            files = [f for f in files if f.suffix.lower() == FILTER_EXT.lower()]
        
        # 关键修复：文件按自然排序（1.html, 2.html... 10.html）
        files.sort(key=lambda x: natural_sort_key(x.name))
        
        # 文件夹在前，文件在后
        all_items = dirs + files
        
        for i, item in enumerate(all_items):
            is_last = (i == len(all_items) - 1)
            connector = "└── " if is_last else "├── "
            child_prefix = prefix + ("    " if is_last else "│   ")
            
            lines.append(prefix + connector + item.name)
            
            if item.is_dir():
                lines.extend(make_tree(item, child_prefix, rules))
                
    except PermissionError:
        pass
    except Exception as e:
        lines.append(prefix + f"[错误: {e}]")
    
    return lines


# ==================== 主程序 ====================

def main():
    print("=" * 60)
    print("豆瓣小组存档 - 排序文件列表生成器（文件排序修复版）")
    print("=" * 60)
    
    current_dir = os.getcwd()
    print(f"\n📂 目标目录: {current_dir}")
    
    # 加载规则
    print(f"\n📋 加载规则文件: {RULE_FILE}")
    rules = load_sort_rules(RULE_FILE)
    
    if not rules:
        print("\n⚠️  未加载到任何规则，将使用默认排序")
        return 1
    
    # 生成文件
    timestamp = datetime.now().strftime("%m%d_%H%M%S")
    filename = f"list_sorted_{timestamp}.txt"
    
    header = [
        f"卷 {current_dir[:2].upper()} 的文件夹 PATH 列表",
        f"{current_dir[:2].upper()}:",
        current_dir[2:],
        "",
        f"【生成信息】",
        f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"规则文件: {RULE_FILE}",
        f"匹配规则: {len(rules)} 条",
        "-" * 50,
        ""
    ]
    
    print(f"\n🌲 正在生成树状结构...")
    tree_lines = make_tree(current_dir, rules=rules)
    
    all_lines = header + tree_lines
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(all_lines))
    
    print(f"\n✅ 生成成功: {filename}")
    print(f"   总行数: {len(all_lines)}")
    
    # 预览前50行
    print(f"\n📄 预览 (前50行):")
    print("-" * 50)
    for line in all_lines[:50]:
        print(line)
    if len(all_lines) > 50:
        print(f"... ({len(all_lines) - 50} 行省略)")
    print("-" * 50)
    
    return 0


if __name__ == "__main__":
    exit(main())