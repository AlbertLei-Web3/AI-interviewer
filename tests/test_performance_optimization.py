import pytest
import asyncio
import time
from src.postprocess.processor import TextProcessor
from src.postprocess.batch_processor import BatchProcessor

class TestPerformanceOptimization:
    @pytest.fixture
    def processor(self):
        return TextProcessor(industry="web3")
        
    @pytest.fixture
    def batch_processor(self, processor):
        return BatchProcessor(processor)

    @pytest.mark.asyncio
    async def test_cache_effectiveness(self, processor):
        """测试缓存机制的有效性"""
        # 准备测试文本
        test_text = "Testing smart contrat and blockchan technology"
        
        # 第一次处理（无缓存）
        start_time = time.time()
        result1 = await processor.process(test_text)
        first_run_time = time.time() - start_time
        
        # 第二次处理（应该使用缓存）
        start_time = time.time()
        result2 = await processor.process(test_text)
        second_run_time = time.time() - start_time
        
        # 验证结果
        assert result1 == result2  # 结果应该一致
        assert second_run_time < first_run_time  # 缓存应该更快
        assert second_run_time < 0.1  # 缓存访问应该非常快

    @pytest.mark.asyncio
    async def test_grammar_checker_singleton(self):
        """测试语法检查器的单例模式"""
        processor1 = TextProcessor()
        processor2 = TextProcessor()
        
        # 验证两个实例使用相同的语法检查器
        assert processor1.grammar_checker is processor2.grammar_checker

    @pytest.mark.asyncio
    async def test_batch_processing(self, batch_processor):
        """测试批处理功能"""
        # 准备多个测试文本
        texts = [
            ("id1", "Testing smart contrat"),
            ("id2", "Using blockchan technology"),
            ("id3", "Learning etherium basics"),
            ("id4", "Understanding dfi protocols"),
            ("id5", "Working with nfts")
        ]
        
        # 添加所有文本到批处理器
        start_time = time.time()
        for text_id, text in texts:
            await batch_processor.add_text(text, text_id)
        
        # 获取所有结果
        results = {}
        for text_id, _ in texts:
            try:
                results[text_id] = await batch_processor.get_result(text_id, timeout=5.0)
            except TimeoutError as e:
                print(f"获取结果超时: {e}")
        
        total_time = time.time() - start_time
        
        # 验证结果
        assert len(results) == len(texts)  # 所有文本都应该处理完成
        assert all(results.values())  # 没有处理失败的文本
        assert total_time < (len(texts) * 2.9)  # 批处理应该比顺序处理快

    @pytest.mark.asyncio
    async def test_cache_size_limit(self, processor):
        """测试缓存大小限制"""
        # 生成超过缓存限制的文本
        texts = [f"Test text {i}" for i in range(processor.cache_size + 10)]
        
        # 处理所有文本
        for text in texts:
            await processor.process(text)
        
        # 验证缓存大小不超过限制
        assert len(processor.cache) <= processor.cache_size

    @pytest.mark.asyncio
    async def test_performance_comparison(self, processor):
        """比较优化前后的性能"""
        test_cases = [
            "Short text with smart contrat",
            "Medium length text about blockchan and etherium technology",
            "Long text " + "with multiple terms " * 10 + "including nfts and dfi"
        ]
        
        for text in test_cases:
            # 第一次运行（无缓存）
            start = time.time()
            result1 = await processor.process(text)
            time1 = time.time() - start
            
            # 第二次运行（有缓存）
            start = time.time()
            result2 = await processor.process(text)
            time2 = time.time() - start
            
            print(f"\n文本长度: {len(text)}")
            print(f"首次处理时间: {time1:.3f}秒")
            print(f"缓存处理时间: {time2:.3f}秒")
            print(f"性能提升: {((time1 - time2) / time1 * 100):.1f}%")
            
            # 验证性能提升
            assert time2 < time1
            assert result1 == result2 