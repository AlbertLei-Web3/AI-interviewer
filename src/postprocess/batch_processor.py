from typing import List, Dict
import asyncio

class BatchProcessor:
    def __init__(self, processor):
        """初始化批量处理器"""
        # processor: 处理文本的处理器对象，应该具备一个process方法
        self.processor = processor
        self.batch_size = 5  # 每批处理的最大文本数，控制一次处理多少文本
        self.queue = asyncio.Queue()  # 异步队列，存放待处理的文本
        self.results = {}  # 存储处理结果的字典，key是text_id，value是处理结果
        self._processing = False  # 标志是否正在处理，防止重复启动处理

    async def add_text(self, text: str, text_id: str):
        """将文本添加到处理队列"""
        # 将文本与唯一标识符（text_id）放入队列中
        await self.queue.put((text_id, text))
        
        # 如果当前没有正在处理的批次，开始处理队列中的文本
        if not self._processing:
            self._processing = True
            # 启动一个异步任务来处理批次
            asyncio.create_task(self._process_batch())
    
    async def _process_batch(self):
        """批量处理队列中的文本"""
        while not self.queue.empty():  # 如果队列不为空，继续处理
            batch = []  # 当前批次的文本列表
            batch_ids = []  # 当前批次的文本ID列表
            
            # 收集一批文本，直到达到batch_size的数量
            while len(batch) < self.batch_size and not self.queue.empty():
                text_id, text = await self.queue.get()  # 从队列中获取文本
                batch.append(text)  # 将文本加入批次
                batch_ids.append(text_id)  # 将文本ID加入ID列表

            # 创建并发任务处理这批文本
            tasks = [
                asyncio.create_task(self.processor.process(text))  # 并行处理每个文本
                for text in batch
            ]
            
            # 等待所有任务完成，并返回处理结果
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 保存每个文本的处理结果
            for text_id, result in zip(batch_ids, results):
                if isinstance(result, Exception):  # 如果出现异常
                    print(f"处理文本 {text_id} 时出错: {str(result)}")
                    self.results[text_id] = None  # 将错误结果保存为None
                else:
                    self.results[text_id] = result  # 保存正确的处理结果
        
        self._processing = False  # 标记处理结束
    
    async def get_result(self, text_id: str, timeout: float = None) -> str:
        """获取某个文本的处理结果"""
        start_time = asyncio.get_event_loop().time()  # 获取当前时间，计算超时
        while timeout is None or asyncio.get_event_loop().time() - start_time < timeout:
            # 如果结果已经处理完成，返回结果并从results字典中删除
            if text_id in self.results:
                return self.results.pop(text_id)
            # 如果还没有结果，稍等再检查
            await asyncio.sleep(0.1)
        
        # 如果超时，抛出超时异常
        raise TimeoutError(f"获取文本 {text_id} 的结果超时")
