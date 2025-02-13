# 导入所需的库
import pyaudio  # 用于处理音频流
import wave  # 用于保存音频文件
import time  # 用于处理时间
import whisper  # 用于语音识别模型
import json  # 用于处理JSON数据
import asyncio  # 用于处理异步编程
import keyboard  # 用于处理键盘输入
import http.client  # 用于发送HTTP请求
import os  # 用于处理文件和操作系统功能
import numpy as np  # 用于处理数值计算
import subprocess
import sys
import shutil
from src.config.settings import OPENAI_API_KEY  # 从配置文件导入API密钥
from src.postprocess.processor import TextProcessor

class InterviewAssistant:
    def __init__(self, config_path: str = "config.json"):
        # 设置 Whisper 模型下载路径
        whisper_dir = os.path.join("D:", "web3codework", "AI-interviwer", "models", "whisper")
        os.makedirs(whisper_dir, exist_ok=True)
        os.environ["XDG_CACHE_HOME"] = whisper_dir
        
        # 加载配置文件，默认路径为"config.json"
        self.config = self._load_config(config_path)
        
        # 初始化Whisper模型，使用更大的模型提高精度
        print(f"正在加载Whisper模型... (保存路径: {whisper_dir})")
        self.whisper_model = whisper.load_model("medium")  # 改用medium模型
        print("Whisper模型加载完成")
        
        # 设置音频参数，适配pyaudio的音频流
        self.CHUNK = 4096  # 每次读取的音频块大小
        self.FORMAT = pyaudio.paInt32  # 音频格式为32位
        self.CHANNELS = 1  # 单声道音频
        self.RATE = 48000    # 音频采样率
        self.p = pyaudio.PyAudio()  # 初始化PyAudio实例
        
        # 查找"CABLE Output"设备
        self.cable_index = None
        for i in range(self.p.get_device_count()):
            try:
                device_info = self.p.get_device_info_by_index(i)
                if 'CABLE Output' in device_info['name']:
                    self.cable_index = i  # 找到设备，保存索引
                    print(f"找到 CABLE Output 设备 (索引: {i})")
                    break
            except Exception as e:
                continue
        
        # 如果没有找到CABLE Output设备，打印警告并使用默认设备
        if self.cable_index is None:
            print("警告: 未找到 CABLE Output 设备，请检查设置")
            self.cable_index = 0
        
        # 初始化状态变量
        self.start_time = None  # 记录按下 F2 时的时间戳
        self.end_time = None    # 记录按下 F3 时的时间戳
        self.is_recording = False  # 录音状态
        self.is_running = True  # 程序运行状态
        self.stream = None  # 音频流对象
        self.audio_data = []  # 存储录音数据
        self.text_processor = TextProcessor(industry="web3")

    def _load_config(self, config_path: str):
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)  # 返回配置内容
        except FileNotFoundError:
            return {"language": "en-US"}  # 默认语言为英语

    def print_audio_level(self, stream, duration):
        """监控并打印音频电平"""
        end_time = time.time() + duration  # 计算结束时间
        while time.time() < end_time:
            try:
                # 读取音频流数据
                data = stream.read(self.CHUNK, exception_on_overflow=False)
                # 计算音量电平（读取音频数据并计算最大值）
                level = max(abs(int.from_bytes(data[i:i+2], byteorder='little', signed=True)) 
                           for i in range(0, len(data), 2))
                # 打印音量条
                bars = int(level / 1000)  # 将音量值转为条数
                print('\r' + '=' * bars + ' ' * (50 - bars), end='', flush=True)  # 实时更新音量条
                time.sleep(0.1)  # 延时0.1秒
            except Exception as e:
                print(f"\n错误: {str(e)}")  # 如果出错，打印错误信息
                break

    def start_recording(self):
        """开始录音"""
        if self.is_recording:  # 如果已经在录音，则不再启动
            return
            
        try:
            self.start_time = time.time()  # 记录按下 F2 时的时间
            self.stream = self.p.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                input_device_index=self.cable_index,
                frames_per_buffer=self.CHUNK
            )
            self.is_recording = True
            self.audio_data = []
            print("\n开始录音...")
            
        except Exception as e:
            print(f"\n开始录音时出错: {str(e)}")  # 如果出错，打印错误信息
            self.is_recording = False

    async def stop_recording(self):
        """停止录音并处理音频"""
        if not self.is_recording:
            return
            
        try:
            self.end_time = time.time()
            recording_duration = self.end_time - self.start_time
            self.is_recording = False
            print(f"\n停止录音，录制时长: {recording_duration:.2f}秒")
            print(f"录音数据长度: {len(self.audio_data)}")

            if not self.audio_data:
                print("没有录到音频数据")
                return

            # 保存音频文件
            temp_wav = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"temp_recording_{int(time.time())}.wav")
            with wave.open(temp_wav, 'wb') as wf:
                wf.setnchannels(self.CHANNELS)
                wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
                wf.setframerate(self.RATE)
                wf.writeframes(b''.join(self.audio_data))

            # 验证文件是否创建成功
            if not os.path.exists(temp_wav):
                raise FileNotFoundError(f"临时文件创建失败: {temp_wav}")
            
            print(f"临时文件已创建: {temp_wav}")
            print(f"文件大小: {os.path.getsize(temp_wav)} 字节")

            # 关闭音频流
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None

            # 使用 Whisper 进行语音识别
            try:
                print("开始语音识别...")
                result = self.whisper_model.transcribe(
                    temp_wav,
                    language='en',
                    fp16=False,
                    initial_prompt="This is an interview conversation in English."
                )
                print("语音识别完成")

                text = result["text"].strip()
                if text:
                    print(f"\n原始识别文本: {text}")
                    
                    # 执行后处理
                    processed_text = await self.text_processor.process(text)
                    print(f"后处理文本: {processed_text}")
                    
                    # 获取AI回答
                    self._getResponse(processed_text)
                else:
                    print("\n未能识别到有效的语音内容")

            finally:
                # 保存临时文件到指定目录
                try:
                    # 指定保存路径
                    save_dir = os.path.join("D:", "web3codework", "AI-interviwer", "src", "testvoice")
                    
                    # 使用时间戳创建唯一的文件名
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    save_path = os.path.join(save_dir, f"recording_{timestamp}.wav")
                    
                    # 确保目标目录存在
                    os.makedirs(save_dir, exist_ok=True)
                    
                    # 复制文件到目标位置
                    shutil.copy2(temp_wav, save_path)
                    print(f"录音文件已保存到: {save_path}")
                    
                    # 删除原始临时文件
                    os.remove(temp_wav)
                    
                except Exception as e:
                    print(f"保存录音文件失败: {str(e)}")
                    import traceback
                    traceback.print_exc()

        except Exception as e:
            print(f"\n处理录音时出错: {str(e)}")
            import traceback
            traceback.print_exc()

    def _getResponse(self, text):
        """根据识别的文本获取AI的回答"""
        conn = http.client.HTTPSConnection("kg-api.cloud")
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {OPENAI_API_KEY}',  # 使用环境变量中的API密钥
            'Content-Type': 'application/json'
        }

        # 构建请求体
        payload = json.dumps({
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个面试者，你需要用英文回答我的问题，并一句中文一句英语的给出对照的翻译"
                },
                {
                    "role": "user",
                    "content": text  # 用户的问题
                }
            ]
        })

        try:
            # 发送POST请求
            conn.request("POST", "/v1/chat/completions", payload, headers)
            res = conn.getresponse()  # 获取响应
            data = res.read()  # 读取响应数据
            response = json.loads(data.decode("utf-8"))  # 解析JSON数据

            message = response["choices"][0]["message"]["content"]  # 获取AI回答

            print("\n=== AI回答 ===")
            print(message)
            print("============")

        except Exception as e:
            print(f"\nAI响应错误: {str(e)}")  # 如果AI响应错误，打印错误信息

    async def run(self):
        """主运行循环"""
        print("\n=== AI面试助手 ===")
        print("按 F2 开始录音")
        print("按 F3 停止录音")
        print("输入 'quit' 退出程序")
        
        # 绑定F2和F3键，用于开始和停止录音
        keyboard.on_press_key("F2", lambda e: self.start_recording())
        keyboard.on_press_key("F3", lambda e: self._stop_recording_callback(e))

        # 主循环，保持程序运行
        while self.is_running:
            try:
                if self.is_recording and self.stream:
                    data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                    self.audio_data.append(data)
            except Exception as e:
                if self.is_recording:
                    print(f"\n录音错误: {str(e)}")
            await asyncio.sleep(0.01)

    def _stop_recording_callback(self, e):
        """F3按键回调"""
        if self.is_recording:
            asyncio.create_task(self.stop_recording())

if __name__ == "__main__":
    print("AI 面试助手启动...")  # 程序启动提示
    assistant = InterviewAssistant()  # 创建助手对象

    try:
        asyncio.run(assistant.run())  # 启动主运行循环
    except KeyboardInterrupt:
        print("\n程序已退出")  # 捕获键盘中断并退出程序
    finally:
        if assistant.stream:  # 停止音频流并清理资源
            assistant.stream.stop_stream()
            assistant.stream.close()
        assistant.p.terminate()  # 关闭PyAudio实例
