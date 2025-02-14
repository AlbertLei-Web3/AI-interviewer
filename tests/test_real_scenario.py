import pytest
import time
from src.postprocess.processor import TextProcessor

@pytest.mark.asyncio
async def test_interview_scenario():
    """模拟真实面试场景的测试"""
    processor = TextProcessor(industry="web3")
    
    # 模拟典型的面试问答
    interview_texts = [
        "Can you explain what blockchain is?",  # 简短问题
        "I have experience with smart contracts and dfi protocols",  # 中等长度
        "I worked on several blockchan projects using etherium and implemented smart contrat solutions"  # 较长回答
    ]
    
    print("\n=== 面试场景性能测试 ===")
    
    # 首次运行（包含初始化时间）
    print("\n第一轮（首次运行，包含初始化）:")
    for text in interview_texts:
        start = time.time()
        result = await processor.process(text)
        process_time = time.time() - start
        
        print(f"\n输入文本: {text}")
        print(f"处理时间: {process_time:.3f}秒")
        print(f"处理结果: {result}")
        
        assert process_time < 1.5, f"处理时间过长: {process_time:.3f}秒"
    
    # 第二轮（使用缓存）
    print("\n第二轮（使用缓存）:")
    for text in interview_texts:
        start = time.time()
        result = await processor.process(text)
        process_time = time.time() - start
        
        print(f"\n输入文本: {text}")
        print(f"处理时间: {process_time:.3f}秒")
        print(f"处理结果: {result}")
        
        # 缓存访问应该很快
        assert process_time < 0.1, f"缓存访问时间过长: {process_time:.3f}秒" 