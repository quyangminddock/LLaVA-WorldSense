# 🛡️ Jarvis WorldSense

<p align="center">
  <img src="docs/banner.png" alt="Jarvis WorldSense" width="600">
</p>

<p align="center">
  <b>Iron Man 风格 AR 助手 - 由多模态 AI 驱动</b>
</p>

<p align="center">
  中文文档 | <a href="./README.md">English (Active Protocol)</a>
</p>

---

## ✨ 任务简报

**Jarvis WorldSense** 将你的电脑变身为一个完全交互式的 AI 助手，配备 **钢铁侠抬头显示器 (HUD)**。它能看到你所见，听懂你所说，并即时回应。

### 🦾 核心能力
- **👁️ AR 视觉 (HUD)**: 实时 **钢铁侠界面**，具备眼球追踪锁定系统。
- **🧠 动力核心**: 由 **TinyLLaVA-3.1B** 驱动，专为消费级硬件优化 (8GB 内存即可运行!)。
- **🗣️ 自然语音**: "Always-On" 连续语音对话 (目前仅限英语协议)。
- **🛡️ 纯净视觉**: AI 看到的是纯净的真实世界，而你享受酷炫的 AR 界面 (视觉分离技术)。

## 🚀 快速开始

### 前置要求
- Python 3.10+
- macOS (M1/M2/M3) 或 NVIDIA 显卡
- 8GB+ 内存 (感谢 TinyLLaVA)
- 摄像头 & 麦克风

### 安装步骤

1. **克隆仓库**
```bash
git clone https://github.com/quyangminddock/LLaVA-WorldSense.git
cd LLaVA-WorldSense
```

2. **创建虚拟环境**
```bash
conda create -n jarvis python=3.10 -y
conda activate jarvis
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

> **注意**: 如果你想使用旧版 `LLaVA-1.5` 7B/13B 模型，你需要单独安装原版 LLaVA 库。对于默认的 TinyLLaVA 体验，这是**不需要**的。

4. **安装音频驱动 (macOS)**
```bash
brew install portaudio
pip install pyaudio
```

### 🎮 启动 Jarvis

**推荐模式 (TinyLLaVA + Web UI):**
```bash
python main.py --llava-model tinyllava/TinyLLaVA-Phi-2-SigLIP-3.1B --web
```

**访问界面:**
在 Chrome/Safari 浏览器中打开 **http://localhost:8080**。

> **提示**: 首次运行会自动下载 TinyLLaVA 模型 (~6GB)，请耐心等待。

## 🕹️ 操作指南

| 动作 | 控制 |
|--------|---------|
| **开启 HUD** | 点击 "Toggle Camera" 启动 AR 系统。 |
| **语音指令** | 点击 "🎙️" 一次即可。连续对话模式将保持激活。 |
| **快速分析** | 说 "What do you see?" 进行快速扫描。 |
| **深度扫描** | 说 "Tell me details" 进行全面分析。 |

## ⚙️ 配置 (J.A.R.V.I.S. 协议)

系统预设为 **全英文模式 (English Mode)**。

| 组件 | 设置 | 说明 |
|-----------|---------|-------------|
| **语音输入** | `en-US` | 仅响应英语指令。 |
| **系统人设** | `Jarvis` | 简洁、乐于助人、专业。 |
| **视觉模型** | `TinyLLaVA` | 3.1B 参数, FP16 精度。 |

## 🧠 大脑：TinyLLaVA-3.1B

Jarvis 运行在 **TinyLLaVA-Phi-2-SigLIP-3.1B** 之上，这是一个小而强大的多模态模型。

### 为什么选择它？

| 组件 | 技术栈 | 优势 |
|-----------|------------|---------|
| **视觉编码器** | **SigLIP-384** | 优于 CLIP。能更好地理解图片中的细节和文字。 |
| **语言核心** | **Microsoft Phi-2** | 2.7B 推理强者。逻辑和数学能力媲美大模型。 |
| **连接器** | **MLP Projection** | 高效地将视觉特征转化为语言 Token。 |

### 性能指标
- **显存占用**: ~4GB VRAM (FP16) / ~6GB RAM (MPS/CPU)。
- **推理速度**: 在 M1/M2/M3 芯片上实现实时对话。
- **能力**: 擅长物体识别、OCR (文字阅读) 和空间推理。

## 🔧 故障排除

- **音频错误**: 确保通过 Homebrew 安装了 `portaudio`。
- **AR 对齐问题**: HUD 使用镜像效果。确保你正对摄像头。
- **模型加载失败**: 检查网络连接是否能访问 HuggingFace。

## 🤝 参与贡献

欢迎斯塔克工业的工程师们！详情请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 📄 许可证

MIT 许可证。为 AI 交互的未来而构建。

---

<p align="center">
  <i>"Sometimes you gotta run before you can walk."</i>
</p>
