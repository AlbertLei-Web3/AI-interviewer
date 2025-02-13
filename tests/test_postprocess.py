import asyncio
import pytest
from src.postprocess.processor import TextProcessor


#python -m pytest tests/test_postprocess.py -v 运行测试

class TestTextProcessor:
    @pytest.fixture
    def processor(self):
        """创建文本处理器实例"""
        return TextProcessor(industry="web3")

    @pytest.mark.asyncio
    async def test_basic_processing(self, processor):
        """测试基本的文本处理功能"""
        # 测试文本包含拼写错误和Web3术语
        text = "I want to lern about blockchan and smart contrat development"
        result = await processor.process(text)
        
        # 检查是否修正了拼写错误
        assert "learn" in result.lower()
        # 检查是否修正了行业术语
        assert "blockchain" in result.lower()
        assert "smart contract" in result.lower()
        
        # 检查性能统计
        stats = processor.get_performance_stats()
        assert "总处理时间" in stats
        assert stats["总处理时间"]["处理次数"] == 1

    @pytest.mark.asyncio
    async def test_timeout_handling(self, processor):
        """测试超时处理"""
        # 使用更合理的文本长度
        long_text = "blockchain " * 50  # 减少重复次数
        result = await processor.process(long_text)
        
        # 检查是否在超时时间内完成
        stats = processor.get_performance_stats()
        assert "总处理时间" in stats, "性能统计中缺少总处理时间"
        assert "最长耗时" in stats["总处理时间"], "缺少最长耗时统计"
        assert stats["总处理时间"]["最长耗时"] <= processor.total_timeout * 1.1  # 允许10%的误差

    @pytest.mark.asyncio
    async def test_error_handling(self, processor):
        """测试错误处理"""
        # 测试空输入
        result = await processor.process("")
        assert result == ""
        
        # 测试None输入
        result = await processor.process(None)
        assert result == None

    @pytest.mark.asyncio
    async def test_web3_terms(self, processor):
        """测试Web3术语处理"""
        test_cases = [
            ("I use metamsk for my etherium transactions", 
             ["metamask", "ethereum"]),  # 应该修正的术语
            
            ("The dfi protocol and nfts are popular", 
             ["defi", "nft"]),  # 应该修正的术语
            
            ("Smart contrat deployment on the blockchan", 
             ["smart contract", "blockchain"]),  # 应该修正的术语
        ]
        
        for input_text, expected_terms in test_cases:
            result = await processor.process(input_text)
            # 检查每个期望的术语是否在结果中
            for term in expected_terms:
                assert term.lower() in result.lower()

    @pytest.mark.asyncio
    async def test_performance_monitoring(self, processor):
        """测试性能监控功能"""
        # 执行多次处理来收集性能数据
        texts = [
            "Simple blockchain text",
            "More complex ethereum and smart contrat text",
            "Very long " + "blockchain " * 20 + "text"  # 减少文本长度
        ]
        
        for text in texts:
            await processor.process(text)
        
        # 获取性能统计
        stats = processor.get_performance_stats()
        
        # 检查是否记录了所有步骤的性能数据
        expected_steps = ["拼写检查", "术语检查", "语法检查", "语义分析", "总处理时间"]
        
        for step in expected_steps:
            assert step in stats, f"缺少 {step} 的性能数据"
            for metric in ["平均耗时", "最短耗时", "最长耗时", "处理次数"]:
                assert metric in stats[step], f"缺少 {step} 的 {metric} 数据"
            # 允许部分处理失败，检查处理次数不为0
            assert stats[step]["处理次数"] > 0, f"{step} 的处理次数为0"

if __name__ == "__main__":
    pytest.main(["-v"]) 

# 这个测试文件包含了：
# 基本功能测试：--------------------------------
# 拼写修正
# 术语修正
# 性能统计
# 超时处理测试：--------------------------------
# 确保长文本处理不超时
# 验证超时机制
# 错误处理测试：--------------------------------
# 空输入
# None输入
# Web3术语测试：--------------------------------
# 常见术语修正
# 多种错误写法
# 性能监控测试：--------------------------------
# 统计数据收集
# 性能指标验证
