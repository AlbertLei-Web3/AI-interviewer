# 导入必要的库
import os                  # 用于文件和目录操作
import pytest             # 测试框架
import whisper            # OpenAI的语音识别模型
from src.postprocess.processor import TextProcessor  # 导入文本后处理器
import asyncio            # 异步操作支持
import time
from tqdm import tqdm  # 添加进度条
from src.config.config_manager import ConfigManager
from pydub import AudioSegment
import tempfile

class TestAudioFileProcessing:
    # 使用 fixture 替代 __init__
    @pytest.fixture(autouse=True)
    def setup(self):
        """在每个测试前自动运行"""
        self.config = ConfigManager()
    
    @pytest.fixture
    def whisper_model(self):
        """初始化并加载 Whisper 模型（这个只会执行一次）"""
        print("正在加载 Whisper 模型...")
        model_path = r"D:\web3codework\AI-interviwer\models\whisper\medium.pt"
        if not os.path.exists(model_path):
            print(f"错误: 模型文件不存在: {model_path}")
            print("尝试下载模型...")
            model = whisper.load_model("medium")
        else:
            print(f"使用本地模型: {model_path}")
            model = whisper.load_model("medium", download_root=os.path.dirname(model_path))
        print("Whisper 模型加载完成")
        return model
    
    @pytest.fixture
    def text_processor(self):
        """初始化文本处理器（这个只会执行一次）"""
        return TextProcessor(industry="web3", enable_postprocess=False)  # 禁用后处理
    
    def get_audio_files(self, directory):
        """扫描目录获取所有音频文件"""
        if not os.path.exists(directory):
            print(f"\n错误: 目录不存在: {directory}")
            return []
        
        # 列出目录中的所有文件
        all_files = os.listdir(directory)
        print(f"\n目录 {directory} 中的所有文件:")
        for file in all_files:
            print(f"- {file}")
        
        audio_files = []  # 存储找到的音频文件路径
        supported_formats = ['.m4a', '.mp3', '.wav']  # 支持的音频格式
        
        for file in all_files:  # 遍历目录中的所有文件
            file_lower = file.lower()  # 转换为小写进行比较
            if any(file_lower.endswith(fmt) for fmt in supported_formats):
                full_path = os.path.join(directory, file)
                print(f"\n检查文件: {full_path}")
                print(f"文件是否存在: {os.path.exists(full_path)}")
                print(f"文件大小: {os.path.getsize(full_path)} 字节")
                audio_files.append(full_path)
            else:
                print(f"跳过非音频文件: {file}")
        
        if not audio_files:
            print(f"\n警告: 在目录 {directory} 中没有找到支持的音频文件")
            print(f"支持的格式: {supported_formats}")
        else:
            print(f"\n找到以下音频文件:")
            for file in audio_files:
                print(f"- {os.path.basename(file)}")
            print(f"总计: {len(audio_files)} 个文件")
        
        return audio_files

    def convert_to_wav(self, m4a_file):
        """将 M4A 文件转换为 WAV 格式"""
        try:
            print(f"转换文件格式: {os.path.basename(m4a_file)}")
            # 创建临时文件
            temp_dir = tempfile.mkdtemp()
            wav_path = os.path.join(temp_dir, "temp.wav")
            
            # 转换格式
            audio = AudioSegment.from_file(m4a_file, format="m4a")
            audio.export(wav_path, format="wav")
            
            return wav_path
        except Exception as e:
            print(f"转换格式失败: {str(e)}")
            return None

    async def process_single_file(self, audio_file, whisper_model, text_processor, timeout=120):
        """处理单个音频文件，带超时控制"""
        try:
            print(f"\n开始处理: {os.path.basename(audio_file)}")
            
            # 设置超时
            async with asyncio.timeout(timeout):
                # 1. Whisper 转写
                print("转写中...")
                print(f"正在处理文件: {audio_file}")
                print(f"文件大小: {os.path.getsize(audio_file)} 字节")
                result = await asyncio.to_thread(
                    whisper_model.transcribe,
                    audio_file,  # 直接使用 m4a 文件
                    language='en',
                    fp16=False,
                    verbose=True,  # 显示更多处理信息
                    initial_prompt="This is a short interview answer in English."
                )
                
                original_text = result["text"].strip()
                print(f"转写完成: {original_text}")
                
                print("后处理中...")
                processed_text = await text_processor.process(original_text)
                print(f"处理完成: {processed_text}")
                
                return {
                    'original': original_text,
                    'processed': processed_text,
                    'success': True
                }
        except asyncio.TimeoutError:
            print(f"\n处理文件超时: {os.path.basename(audio_file)}")
            return {'success': False, 'error': 'timeout'}
        except Exception as e:
            print(f"\n处理文件出错: {os.path.basename(audio_file)} - {str(e)}")
            return {'success': False, 'error': str(e)}

    @pytest.mark.asyncio
    async def test_audio_transcription(self, whisper_model, text_processor, capsys):
        """主测试函数：处理音频文件并分析结果"""
        # 完全禁用 pytest 的输出捕获
        with capsys.disabled():
            # 设置较短的超时时间
            timeout = 120  # 每个文件最多120秒
            
            # 指定音频文件目录
            audio_dir = r"D:\CloudMusic\interview-question"
            
            print("\n=== 开始音频文件处理测试 ===")
            
            # 检查目录是否存在
            if not os.path.exists(audio_dir):
                print(f"\n请确认音频文件目录是否正确: {audio_dir}")
                print("当前工作目录:", os.getcwd())
                return
            
            # 获取所有音频文件
            audio_files = self.get_audio_files(audio_dir)
            
            if not audio_files:
                print("\n没有找到可处理的音频文件，请检查:")
                print(f"1. 目录 {audio_dir} 是否存在")
                print("2. 目录中是否有 .m4a 文件")
                return
            
            print(f"\n找到 {len(audio_files)} 个音频文件")
            start_time = time.time()
            
            # 并行处理所有文件
            tasks = [
                self.process_single_file(
                    audio_file, 
                    whisper_model, 
                    text_processor, 
                    timeout=timeout
                ) 
                for audio_file in audio_files
            ]
            
            results = []
            for audio_file, task in zip(audio_files, asyncio.as_completed(tasks)):
                try:
                    result = await task
                    results.append((audio_file, result))
                except Exception as e:
                    print(f"处理失败: {os.path.basename(audio_file)} - {e}")
            
            # 输出统计信息
            total_time = time.time() - start_time
            success_count = sum(1 for _, r in results if r['success'])
            print(f"\n处理完成:")
            print(f"总时间: {total_time:.2f}秒")
            print(f"成功: {success_count}/{len(audio_files)}")
            
            # 输出详细结果
            for audio_file, result in results:
                if result['success']:
                    print(f"\n文件: {os.path.basename(audio_file)}")
                    print(f"原始文本: {result['original']}")
                    print(f"处理后文本: {result['processed']}")

# 如果直接运行此文件（而不是通过 pytest 运行）
if __name__ == "__main__":
    # 使用 pytest 运行测试
    pytest.main(["-v", "-s", "test_audio_files.py"])  # -v 参数显示详细输出，-s 参数强制显示所有输出 