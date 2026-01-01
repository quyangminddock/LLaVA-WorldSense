# 🌋 LLaVA WorldSense

<p align="center">
  <b>多模态 AI 助手 - 看见并听懂世界</b>
</p>

<p align="center">
  中文 | <a href="./README.md">English</a>
</p>

---

## ✨ 功能特点

- 🔮 **视觉理解** - 基于 LLaVA-1.5-7B 多模态模型
- 🎤 **语音输入** - OpenAI Whisper 语音转文字
- 📷 **摄像头捕获** - 实时摄像头集成
- 💬 **多轮对话** - 上下文感知对话
- 🌐 **网页界面** - 美观的 Gradio UI

## 🚀 快速开始

### 环境要求

- Python 3.10+
- macOS / Linux / Windows
- 16GB+ 内存（运行 LLaVA-1.5-7B）
- 摄像头（可选）
- 麦克风（可选）

### 安装步骤

1. **克隆仓库**

```bash
git clone https://github.com/yourusername/LLaVA-WorldSense.git
cd LLaVA-WorldSense
```

2. **创建虚拟环境**

```bash
conda create -n worldsense python=3.10 -y
conda activate worldsense
```

3. **安装 LLaVA**

```bash
git clone https://github.com/haotian-liu/LLaVA.git
cd LLaVA
pip install -e .

# macOS 用户
pip install torch==2.1.2 torchvision==0.16.2
pip uninstall bitsandbytes  # macOS 不支持

cd ..
```

4. **安装依赖**

```bash
pip install -r requirements.txt
```

5. **安装音频依赖（macOS）**

```bash
brew install portaudio
pip install pyaudio
```

### 使用方法

**启动演示：**

```bash
python main.py
```

**带参数启动：**

```bash
# 使用更大的 LLaVA 模型
python main.py --llava-model liuhaotian/llava-v1.5-13b

# 使用更大的 Whisper 模型以获得更好的准确性
python main.py --whisper-model small

# 创建公共分享链接
python main.py --share
```

**访问界面：**

在浏览器中打开 http://127.0.0.1:7860

## 💡 使用指南

1. **捕获图像**：点击"📸 从摄像头捕获"或上传图片
2. **提问**：
   - 🎤 使用麦克风录制语音
   - ⌨️ 在文本框中输入问题
3. **获取回复**：点击"🚀 询问 LLaVA"获取 AI 回复

### 示例问题

- "你在这张图片中看到了什么？"
- "详细描述这个场景"
- "图中有哪些物体？"
- "这里有什么危险的东西吗？"
- "图中人物的情绪是什么？"

## ⚙️ 配置选项

| 参数 | 默认值 | 描述 |
|------|--------|------|
| `--llava-model` | `liuhaotian/llava-v1.5-7b` | LLaVA 模型路径 |
| `--whisper-model` | `base` | Whisper 模型大小 |
| `--device` | `auto` | 设备 (auto/cuda/mps/cpu) |
| `--camera-id` | `0` | 摄像头设备 ID |
| `--share` | `False` | 创建公共链接 |

## 🔧 常见问题

### macOS 问题

**问题**：`bitsandbytes` 错误
```bash
pip uninstall bitsandbytes
```

**问题**：PyAudio 安装失败
```bash
brew install portaudio
pip install pyaudio
```

### 内存问题

如果内存不足，可以尝试：
- 使用更小的 LLaVA 模型
- 使用 `--device cpu`（较慢但内存占用少）
- 关闭其他应用程序

## 🤝 贡献

欢迎贡献代码！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [LLaVA](https://github.com/haotian-liu/LLaVA) - 视觉指令微调
- [OpenAI Whisper](https://github.com/openai/whisper) - 语音识别
- [Gradio](https://gradio.app/) - 网页界面框架
- [OpenCV](https://opencv.org/) - 计算机视觉库

---

<p align="center">
  Made with ❤️ by minddock.ai
</p>
