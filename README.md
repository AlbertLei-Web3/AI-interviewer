  # AI Interviewer
+ # AI 面试助手
  
- AI面试助手 - 实时语音识别和回答系统
+ Real-time Speech Recognition and Response System
+ 实时语音识别和回答系统
  
  ## 快速开始
+ ## Quick Start
  
  ### 安装
+ ### Installation
  ```bash
  # 克隆项目
+ # Clone the repository
  git clone https://github.com/AlbertLei-Web3/AI-interviewer.git
  cd ai-interviewer
  
  # 安装依赖
+ # Install dependencies
  pip install -r requirements.txt
  
  # 配置环境
+ # Configure environment
  cp .env.example .env
  # 编辑 .env 文件，填入你的 API 密钥
+ # Edit .env file and fill in your API key
  ```
  
  ### 运行
+ ### Running
  ```bash
  # 运行命令行版本
+ # Run command line version
  python src/main.py
  
  # 运行GUI版本
+ # Run GUI version
  python src/run_gui.py
  ```
  
  ## 功能特点
+ ## Features
  
  ### 1. 语音交互
+ ### 1. Voice Interaction
  - 实时录音和语音识别
+ - Real-time recording and speech recognition
  - 使用 OpenAI Whisper 进行语音转文字
+ - Speech-to-text using OpenAI Whisper
  - 支持自定义麦克风设备
+ - Custom microphone device support
  - 自动音频质量优化
+ - Automatic audio quality optimization
  
  ### 2. 文本后处理系统
+ ### 2. Text Post-processing System
  - 拼写检查和自动修正
+ - Spell check and auto-correction
  - Web3 行业术语标准化
+ - Web3 industry terminology standardization
  - 语法检查和优化
+ - Grammar check and optimization
  - 语义分析和改进
+ - Semantic analysis and improvement
  
  ### 3. AI 对话功能
+ ### 3. AI Conversation Features
  - 使用 GPT-3.5 生成回答
+ - Response generation using GPT-3.5
  - 中英文对照输出
+ - Bilingual output (Chinese-English)
  - 面试场景定制化
+ - Interview scenario customization
  - 上下文感知对话
+ - Context-aware conversation
  
  ## 使用说明
+ ## Usage Guide
  
  ### 键盘快捷键
+ ### Keyboard Shortcuts
  - `F2`: 开始录音
+ - `F2`: Start recording
  - `F3`: 停止录音并处理
+ - `F3`: Stop recording and process
  - `Ctrl+Q`: 退出程序
+ - `Ctrl+Q`: Exit program
  
  ### 配置文件
+ ### Configuration Files
  - `.env`: 环境变量配置
+ - `.env`: Environment variables
  - `config.json`: 系统配置
+ - `config.json`: System configuration
  
  ### 音频设置
+ ### Audio Settings
  - 支持多种音频输入设备
+ - Multiple audio input device support
  - 默认使用系统默认麦克风
+ - Uses system default microphone
  - 可在配置中自定义音频参数
+ - Customizable audio parameters
  
  ## 项目结构
+ ## Project Structure
  ```
  ai-interviewer/
  ├── src/
  │   ├── main.py           # 主程序 / Main program
  │   ├── getMic.py         # 麦克风处理 / Microphone handling
  │   ├── config/           # 配置管理 / Configuration management
  │   ├── postprocess/      # 文本处理 / Text processing
  │   └── gui/              # 图形界面 / Graphical interface
  ├── tests/                # 测试文件 / Test files
  ├── docs/                 # 文档 / Documentation
  ├── requirements.txt      # 依赖清单 / Dependencies list
  └── .env                  # 环境配置 / Environment configuration
  ```
  
  ## 依赖项
+ ## Dependencies
  - Python 3.8+
  - OpenAI Whisper
  - PyAudio
  - Language Tool
  - SpaCy
  
  ## 常见问题
+ ## Common Issues
  1. **麦克风未找到**
+ 1. **Microphone Not Found**
     - 检查系统音频设置
+    - Check system audio settings
     - 确认麦克风权限
+    - Verify microphone permissions
  
  2. **API 错误**
+ 2. **API Error**
     - 验证 API 密钥
+    - Verify API key
     - 检查网络连接
+    - Check network connection
  
  ## 贡献指南
+ ## Contribution Guide
  1. Fork 项目
+ 1. Fork the project
  2. 创建特性分支
+ 2. Create feature branch
  3. 提交更改
+ 3. Commit changes
  4. 发起 Pull Request
+ 4. Create Pull Request
  
  ## 许可证
+ ## License
  MIT License