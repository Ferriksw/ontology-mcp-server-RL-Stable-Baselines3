#!/usr/bin/env python3
"""修复版权信息位置，确保 from __future__ import annotations 在正确位置"""
from pathlib import Path
import re

def fix_file(file_path: Path):
    """修复单个文件的版权信息位置"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 如果没有版权信息，跳过
    if 'Copyright (c) 2025 shark8848' not in content:
        return False
    
    lines = content.split('\n')
    
    # 查找各个部分
    shebang = None
    copyright_start = -1
    copyright_end = -1
    future_import_line = -1
    
    for i, line in enumerate(lines):
        if i == 0 and line.startswith('#!/'):
            shebang = line
        if '"""' in line and 'Copyright (c) 2025 shark8848' in lines[i:i+10]:
            copyright_start = i
        if copyright_start >= 0 and copyright_end < 0 and i > copyright_start and '"""' in line:
            copyright_end = i
        if 'from __future__ import annotations' in line:
            future_import_line = i
    
    # 如果没有 from __future__ import，不需要修复
    if future_import_line < 0:
        return False
    
    # 如果 from __future__ import 已经在版权之前，不需要修复
    if future_import_line < copyright_start:
        return False
    
    # 需要重新组织
    new_lines = []
    
    # 1. Shebang
    if shebang:
        new_lines.append(shebang)
    
    # 2. from __future__ import (必须在最前)
    if future_import_line >= 0:
        new_lines.append(lines[future_import_line])
    
    # 3. 版权信息 (作为注释而非 docstring)
    if copyright_start >= 0:
        new_lines.append('# Copyright (c) 2025 shark8848')
        new_lines.append('# MIT License')
        new_lines.append('#')
        new_lines.append('# Ontology MCP Server - 电商 AI 助手系统')
        new_lines.append('# 本体推理 + 电商业务逻辑 + 对话记忆 + 可视化 UI')
        new_lines.append('#')
        new_lines.append('# Author: shark8848')
        new_lines.append('# Repository: https://github.com/shark8848/ontology-mcp-server')
    
    # 4. 其余内容 (跳过旧的版权 docstring 和 future import)
    skip_until = copyright_end + 1 if copyright_end >= 0 else copyright_start
    in_old_docstring = False
    added_content = False
    
    for i, line in enumerate(lines):
        # 跳过 shebang
        if i == 0 and shebang:
            continue
        # 跳过版权 docstring
        if copyright_start >= 0 and copyright_start <= i <= copyright_end:
            continue
        # 跳过 future import (已经添加了)
        if i == future_import_line:
            continue
        # 跳过版权 docstring 后面的空行
        if i <= skip_until + 2 and not line.strip():
            continue
        
        new_lines.append(line)
        added_content = True
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print(f"✅ 已修复: {file_path}")
    return True

def main():
    """主函数"""
    src_dir = Path('src')
    py_files = list(src_dir.rglob('*.py'))
    
    print(f"🔍 检查 {len(py_files)} 个文件\n")
    
    fixed = 0
    for py_file in sorted(py_files):
        if fix_file(py_file):
            fixed += 1
    
    print(f"\n📊 修复完成: {fixed} 个文件")

if __name__ == '__main__':
    main()
