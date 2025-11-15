#!/usr/bin/env python3
"""
Copyright (c) 2025 shark8848
MIT License

Ontology MCP Server - 电商 AI 助手系统
Author: shark8848
Repository: https://github.com/shark8848/ontology-mcp-server
"""

"""测试记忆配置系统"""
import os
import sys
from typing import Callable, Dict, List, Optional, Tuple

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agent.memory_config import (
    get_memory_config,
    is_memory_enabled,
    use_chromadb,
    use_similarity_search,
    get_persist_directory,
    get_max_results,
)
from agent.react_agent import LangChainAgent


def test_config_loading():
    """测试配置加载"""
    print("=" * 60)
    print("测试 1: 配置加载")
    print("=" * 60)
    
    config = get_memory_config()
    
    tests: List[Tuple[str, object, object]] = [
        ("记忆启用", config.enabled, True),
        ("后端类型", config.backend, "chromadb"),
        ("检索模式", config.strategy.retrieval_mode, "recent"),
        ("最大记录数", config.strategy.max_recent_turns, 10),
        ("存储目录", config.chromadb.persist_directory, "data/chroma_memory"),
        ("Collection", config.chromadb.collection_name, "conversation_memory"),
        ("LLM摘要", config.strategy.enable_llm_summary, True),
        ("摘要触发", config.summary.trigger, "threshold"),
        ("缓存启用", config.performance.enable_cache, True),
    ]
    
    mismatches: List[Tuple[str, object, object]] = []
    for name, actual, expected in tests:
        status = "✓" if actual == expected else "✗"
        print(f"{status} {name}: {actual}")
        if actual != expected:
            mismatches.append((name, actual, expected))
    
    print(f"\n通过: {len(tests) - len(mismatches)}/{len(tests)}")
    assert not mismatches, f"配置项不匹配: {mismatches}"


def test_convenience_functions():
    """测试便捷函数"""
    print("\n" + "=" * 60)
    print("测试 2: 便捷函数")
    print("=" * 60)
    
    tests: List[Tuple[str, object, object]] = [
        ("is_memory_enabled()", is_memory_enabled(), True),
        ("use_chromadb()", use_chromadb(), True),
        ("use_similarity_search()", use_similarity_search(), False),
        ("get_persist_directory()", get_persist_directory(), "data/chroma_memory"),
        ("get_max_results()", get_max_results(), 10),
    ]
    
    mismatches: List[Tuple[str, object, object]] = []
    for name, actual, expected in tests:
        status = "✓" if actual == expected else "✗"
        print(f"{status} {name} = {actual}")
        if actual != expected:
            mismatches.append((name, actual, expected))
    
    print(f"\n通过: {len(tests) - len(mismatches)}/{len(tests)}")
    assert not mismatches, f"便捷函数返回值异常: {mismatches}"


def test_agent_initialization():
    """测试 Agent 初始化"""
    print("\n" + "=" * 60)
    print("测试 3: Agent 初始化")
    print("=" * 60)
    
    agent = LangChainAgent()

    checks: List[Tuple[str, object, object]] = [
        ("记忆启用", agent.use_memory, True),
        ("相似度搜索", agent.use_similarity_search, False),
        ("记忆对象存在", agent.memory is not None, True),
        ("工具数量 > 0", len(agent.tools) > 0, True),
    ]

    mismatches: List[Tuple[str, object, object]] = []
    for name, actual, expected in checks:
        status = "✓" if actual == expected else "✗"
        print(f"{status} {name}: {actual}")
        if actual != expected:
            mismatches.append((name, actual, expected))

    if agent.memory:
        print(f"  会话ID: {agent.memory.session_id}")
        print(f"  存储目录: {agent.memory.persist_directory}")

    print(f"\n通过: {len(checks) - len(mismatches)}/{len(checks)}")
    assert not mismatches, f"Agent 初始化检查未通过: {mismatches}"


def test_parameter_override():
    """测试参数覆盖"""
    print("\n" + "=" * 60)
    print("测试 4: 参数覆盖配置")
    print("=" * 60)
    
    agent = LangChainAgent(
        use_memory=True,
        session_id="test_session_override",
        use_similarity_search=True,
        max_results=20,
    )

    checks: List[Tuple[str, object, object]] = [
        ("记忆启用", agent.use_memory, True),
        ("相似度搜索", agent.use_similarity_search, True),
        ("会话ID", agent.memory.session_id if agent.memory else None, "test_session_override"),
        ("最大结果数", agent.memory.max_results if agent.memory else None, 20),
    ]

    mismatches: List[Tuple[str, object, object]] = []
    for name, actual, expected in checks:
        status = "✓" if actual == expected else "✗"
        print(f"{status} {name}: {actual}")
        if actual != expected:
            mismatches.append((name, actual, expected))

    print(f"\n通过: {len(checks) - len(mismatches)}/{len(checks)}")
    assert not mismatches, f"参数覆盖结果不符合预期: {mismatches}"


def test_config_hierarchy():
    """测试配置层级（环境变量 > YAML > 默认值）"""
    print("\n" + "=" * 60)
    print("测试 5: 配置层级")
    print("=" * 60)
    
    # 保存原始环境变量
    original_env: Dict[str, Optional[str]] = {}
    env_vars = ['MEMORY_ENABLED', 'MEMORY_BACKEND', 'MEMORY_RETRIEVAL_MODE']
    for var in env_vars:
        original_env[var] = os.environ.get(var)  # type: ignore[assignment]

    from agent.memory_config import MemoryConfigLoader
    loader = MemoryConfigLoader()
    original_config = loader.config

    try:
        # 设置环境变量
        os.environ['MEMORY_RETRIEVAL_MODE'] = 'similarity'

        # 重新加载配置
        config = loader.reload()

        status = "✓" if config.strategy.retrieval_mode == 'similarity' else "✗"
        print(f"{status} 环境变量覆盖: retrieval_mode = {config.strategy.retrieval_mode}")
        assert config.strategy.retrieval_mode == 'similarity', "环境变量未正确覆盖检索模式"

    finally:
        # 恢复环境变量
        for var, value in original_env.items():
            if value is None:
                os.environ.pop(var, None)
            else:
                os.environ[var] = value

        # 再次重新加载确保恢复
        restored = loader.reload()
        print(f"✓ 恢复配置: retrieval_mode = {restored.strategy.retrieval_mode}")
        assert (
            restored.strategy.retrieval_mode == original_config.strategy.retrieval_mode
        ), "配置恢复后的检索模式与原始配置不一致"


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("记忆配置系统测试")
    print("=" * 60 + "\n")
    
    tests: List[Tuple[str, Callable[[], None]]] = [
        ("配置加载", test_config_loading),
        ("便捷函数", test_convenience_functions),
        ("Agent初始化", test_agent_initialization),
        ("参数覆盖", test_parameter_override),
        ("配置层级", test_config_hierarchy),
    ]

    results: Dict[str, bool] = {}
    for name, func in tests:
        try:
            func()
        except AssertionError as exc:
            print(f"❌ {name}: {exc}")
            results[name] = False
        except Exception as exc:  # pragma: no cover - manual invocation fallback
            print(f"❌ {name}: {exc}")
            results[name] = False
        else:
            results[name] = True
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for name, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {name}")
    
    total_passed = sum(1 for passed in results.values() if passed)
    total_tests = len(results)
    
    print(f"\n总计: {total_passed}/{total_tests} 通过")
    
    if total_passed == total_tests:
        print("\n🎉 所有测试通过!")
        return 0
    else:
        print(f"\n⚠️  {total_tests - total_passed} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
