import pyaudio
import wave
import time

def test_audio_routing():
    """测试音频路由并录制音频"""
    CHUNK = 4096   # 缓冲区大小，用于每次读取的音频数据块
    FORMAT = pyaudio.paInt32  # 音频格式，32 位整数
    CHANNELS = 1  # 声道数，单声道
    RATE = 44100  # 采样率，44100 Hz
    RECORD_SECONDS = 30  # 录制时间，单位秒
    
    p = pyaudio.PyAudio()  # 初始化 PyAudio 对象
    
    # 查找 CABLE Output 设备
    cable_index = None
    for i in range(p.get_device_count()):
        # 根据设备名称查找 CABLE Output 设备
        if 'CABLE Output' in p.get_device_info_by_index(i)['name']:
            cable_index = i
            break
    
    if cable_index is None:
        print("\n未找到 CABLE Output 设备")
        return
        
    # 提示开始录制音频
    print(f"\n开始从 CABLE Output (索引 {cable_index}) 录制 {RECORD_SECONDS} 秒音频...")
    print("请在腾讯会议中说话测试...")
    print("音量电平监测:")
    
    # 打开音频流进行录音
    stream = p.open(format=FORMAT, 
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    input_device_index=cable_index,
                    frames_per_buffer=CHUNK)
    
    frames = []  # 存储录音数据
    end_time = time.time() + RECORD_SECONDS  # 设定录音结束的时间
    
    while time.time() < end_time:
        try:
            # 读取音频数据块并存储
            data = stream.read(CHUNK, exception_on_overflow=True)
            frames.append(data)
            
            # 计算音量电平：取数据块中每对字节的最大绝对值作为音量值
            level = max(abs(int.from_bytes(data[i:i+2], byteorder='little', signed=True)) 
                       for i in range(0, len(data), 2))
            
            # 打印音量条，基于电平大小
            bars = int(level / 1000)  # 根据音量大小映射成等号数量
            print('\r' + '=' * bars + ' ' * (50 - bars), end='', flush=True)  # 动态显示音量条
            time.sleep(0.1)  # 每次更新间隔 0.1 秒
        
        except Exception as e:
            print(f"\n错误: {str(e)}")
            break
    
    print("\n\n录制完成")
    
    # 停止并关闭音频流
    stream.stop_stream()
    stream.close()
    
    # 保存录音文件
    wf = wave.open("test_recording.wav", 'wb')
    wf.setnchannels(CHANNELS)  # 设置声道数
    wf.setsampwidth(p.get_sample_size(FORMAT))  # 设置采样位宽
    wf.setframerate(RATE)  # 设置采样率
    wf.writeframes(b''.join(frames))  # 写入录制的音频数据
    wf.close()
    
    p.terminate()  # 终止 PyAudio 实例
    
    print("录音已保存为 test_recording.wav")
    print("请检查:")
    print("1. 你是否能在耳机中听到声音")
    print("2. 音量电平是否有变化")
    print("3. 生成的 test_recording.wav 是否包含声音")

if __name__ == "__main__":
    test_audio_routing()  # 执行音频路由测试
