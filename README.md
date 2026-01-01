# 🛡️ Jarvis WorldSense (LLaVA Edition)

<p align="center">
  <img src="docs/banner.png" alt="Jarvis WorldSense" width="600">
</p>

<p align="center">
  <b>Iron Man Style AR Assistant - Powered by Multimodal AI</b>
</p>

<p align="center">
  <a href="./README_CN.md">中文文档</a> | <b>English (Active Protocol)</b>
</p>

---

## ✨ Mission Briefing

**Jarvis WorldSense** transforms your computer into a fully interactive AI assistant with an **Iron Man Heads-Up Display (HUD)**. It sees what you see, hears what you say, and responds instantly.

### 🦾 Key Capabilities
- **👁️ AR Vision (HUD)**: Real-time **Iron Man interface** with eye-tracking targeting systems.
- **🧠 Kinetic Intelligence**: Powered by **TinyLLaVA-3.1B**, optimized for consumer hardware (Run on 8GB RAM!).
- **🗣️ Natural Voice**: "Always-On" continuous voice conversation (English Only Protocol).
- **🛡️ Pure Vision**: AI sees the raw world, while you enjoy the AR overlay (Vision Separation Technology).

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- macOS (M1/M2/M3) or NVIDIA GPU
- 8GB+ RAM (Thanks to TinyLLaVA)
- Webcam & Microphone

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/LLaVA-WorldSense.git
cd LLaVA-WorldSense
```

2. **Create virtual environment**
```bash
conda create -n jarvis python=3.10 -y
conda activate jarvis
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
pip install git+https://github.com/haotian-liu/LLaVA.git
```

4. **Install Audio Drivers (macOS)**
```bash
brew install portaudio
pip install pyaudio
```

### 🎮 Launch Jarvis

**Recommended Mode (TinyLLaVA + Web UI):**
```bash
python main.py --llava-model tinyllava/TinyLLaVA-Phi-2-SigLIP-3.1B --web
```

**Access the Interface:**
Open **http://localhost:8080** in your Chrome/Safari browser.

> **Note**: The first run will download the TinyLLaVA model (~6GB). Please be patient.

## 🕹️ Controls

| Action | Control |
|--------|---------|
| **Toggle HUD** | Click "Toggle Camera" to engage AR systems. |
| **Voice Command** | Click "🎙️" once. Continuous mode stays active. |
| **Snap & Analyze** | Say "What do you see?" for a quick scan. |
| **Deep Scan** | Say "Tell me details" for a full analysis. |

## 🧠 The Brain: TinyLLaVA-3.1B

Jarvis runs on **TinyLLaVA-Phi-2-SigLIP-3.1B**, a state-of-the-art small multimodal model that punches above its weight.

### Why this model?

| Component | Tech Stack | Benefit |
|-----------|------------|---------|
| **Vision Encoder** | **SigLIP-384** | Superior to CLIP. Understands fine-grained details and text in images better. |
| **Language Core** | **Microsoft Phi-2** | A 2.7B reasoning powerhouse. Performs mathematically and logically on par with much larger models. |
| **Connector** | **MLP Projection** | Efficiently translates visual features into language tokens. |

### Performance Stats
- **Memory Footprint**: ~4GB VRAM (FP16) / ~6GB RAM (MPS/CPU).
- **Inference Speed**: Real-time conversational latency on M1/M2/M3 chips.
- **Capabilities**: Strong at object recognition, OCR (reading text), and spatial reasoning.

## 🔧 Troubleshooting

- **Audio Error**: Ensure `portaudio` is installed via Homebrew.
- **AR Misalignment**: The HUD uses a mirror effect. Ensure you are facing the camera directly.
- **Model Load Fail**: Check your internet connection for HuggingFace downloads.

## 🤝 Contributing

We welcome Stark Industries engineers! Please read [CONTRIBUTING.md](CONTRIBUTING.md).

## 📄 License

MIT License. Built for the future of AI interaction.

---

<p align="center">
  <i>"Sometimes you gotta run before you can walk."</i>
</p>

