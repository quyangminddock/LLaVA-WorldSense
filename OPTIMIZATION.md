# LLaVA 轻量级优化方案

## 当前问题
- LLaVA-v1.5-7b 模型太重 (~13GB)
- 推理速度慢,不适合实时视频应用
- 服务器响应缓慢

## 优化方案

### 方案 1: 优化推理参数 (最快实现)
在 `llava_engine.py` 中调整生成参数:

```python
# 当前参数
max_new_tokens=512  # 减少到 128 或更少
temperature=0.2     # 使用贪婪解码 temperature=0
do_sample=True      # 改为 False (贪婪解码更快)

# 优化后
max_new_tokens=64   # 只生成简短描述
temperature=0
do_sample=False
num_beams=1         # 单beam搜索
```

### 方案 2: 使用 4-bit 量化 (推荐)
使用 BitsAndBytes 量化,减少内存和加速推理:

```python
from transformers import BitsAndBytesConfig

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16
)

model = LlavaLlamaForCausalLM.from_pretrained(
    model_path,
    quantization_config=quantization_config,
    device_map="auto"
)
```

**速度提升**: ~2-3x 更快  
**内存减少**: ~75% (13GB → 3.5GB)

### 方案 3: 切换到更小的模型 (✅ 推荐)
- **TinyLLaVA-Phi-2-SigLIP-3.1B** (3.1B参数) - 最新推荐 ⭐
  - 内存占用: ~4GB
  - 基于Microsoft Phi-2
  - 使用命令: `python main.py --llava-model tinyllava/TinyLLaVA-Phi-2-SigLIP-3.1B`
- **MobileVLM** (1.7B/3B) - 移动端优化
- **LLaVA-Phi** (2.7B) - 基于 Phi-2

### 方案 4: 图像预处理优化
```python
# 降低图像分辨率
image = image.resize((224, 224))  # 从 336x336降到 224x224

# 跳过不必要的帧
frame_skip = 2  # 每处理1帧跳过2帧
```

### 方案 5: 批处理和缓存
- 缓存最近的视觉特征
- 只在场景变化时重新编码

## 推荐组合 (实时性能++)

1. **启用 4-bit 量化**
2. **减少 max_tokens 到 64**  
3. **使用贪婪解码** (temperature=0)
4. **降低图像分辨率到 224x224**

预计速度: **3-5x 提升**

## 实施步骤

我可以帮你:
1. 修改 `llava_engine.py` 添加量化支持
2. 调整生成参数
3. 添加配置选项切换"快速模式"

你想尝试哪个方案?我推荐先试方案2(量化)+ 优化参数,基本不影响质量但速度提升明显。
