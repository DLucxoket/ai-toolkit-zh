# AI Toolkit 项目指南

## 项目概述

AI Toolkit 是一个用于训练扩散模型（Diffusion Models）的工具套件，支持 LoRA/LoKr 微调。支持多种图像和视频模型，可通过 Web UI 或命令行使用。

## 项目结构

```
ai-toolkit-zh/
├── run.py                    # 命令行入口
├── start_ui.bat              # Windows UI 启动脚本
├── .env                      # 环境变量（HF 缓存路径等）
├── requirements.txt          # Python 依赖
│
├── config/                   # 训练配置文件
│   └── examples/             # 示例配置（YAML）
│
├── toolkit/                  # 核心代码库
│   ├── config_modules.py     # 配置数据结构定义
│   ├── stable_diffusion_model.py  # SD 模型基类
│   ├── models/               # 各模型实现
│   │   ├── base_model.py     # 模型基类
│   │   ├── wan21/            # Wan 2.1 模型
│   │   └── ...
│   ├── data_loader.py        # 数据加载器
│   ├── dataloader_mixins.py  # 数据增强/缓存逻辑
│   ├── lora_special.py       # LoRA 网络实现
│   ├── train_tools.py        # 训练工具函数
│   ├── samplers/             # 采样器
│   │   └── custom_flowmatch_sampler.py  # Flow Matching 采样器
│   └── optimizers/           # 优化器实现
│
├── extensions_built_in/      # 内置扩展
│   ├── diffusion_models/     # 模型注册
│   │   ├── krea2/            # Krea 2 模型
│   │   ├── flux2/            # FLUX 2 模型
│   │   ├── qwen_image/       # Qwen Image 模型
│   │   └── ...               # 其他模型
│   ├── sd_trainer/           # SD 训练器（主训练逻辑）
│   ├── captioner/            # 图片打标工具
│   └── dataset_tools/        # 数据集工具
│
├── jobs/                     # 任务系统
│   ├── BaseJob.py            # 任务基类
│   ├── ExtensionJob.py       # 扩展任务
│   ├── process/              # 训练进程
│   │   └── BaseSDTrainProcess.py  # 训练主循环
│   └── ...
│
├── ui/                       # Web UI（Next.js）
│   └── src/
│       └── app/
│           └── jobs/
│               └── new/
│                   ├── SimpleJob.tsx      # 训练配置界面
│                   └── options.ts         # 模型架构选项定义
│
├── datasets/                 # 训练数据集存放目录
└── output/                   # 训练输出目录
```

## 核心概念

### 模型架构（arch）

每个模型在 `extensions_built_in/diffusion_models/` 下有独立目录，通过 `__init__.py` 中的 `AI_TOOLKIT_MODELS` 列表注册。

模型加载流程：
1. 配置文件中的 `model.arch` 匹配模型类的 `arch` 属性
2. `toolkit/util/get_model.py` 中的 `get_model_class()` 查找对应模型类
3. 模型类继承自 `toolkit/models/base_model.py`

### LoRA 训练流程

```
1. 加载模型权重（Transformer + Text Encoder + VAE）
2. 构建 LoRA 网络（挂载到 Transformer）
3. 数据预处理（编码图片 → latent，缓存到硬盘）
4. 训练循环：
   a. 加载 latent
   b. 采样时间步 t
   c. 加噪声
   d. 模型预测
   e. 计算 loss
   f. 反向传播更新 LoRA 权重
5. 保存 LoRA 权重
```

### 关键配置参数

| 参数 | 位置 | 说明 |
|------|------|------|
| `model.arch` | 模型配置 | 模型架构标识（如 `krea2`、`flux`） |
| `model.name_or_path` | 模型配置 | 模型权重路径（本地文件或 HF repo） |
| `model.quantize` | 模型配置 | 是否 8bit 量化（省显存） |
| `model.low_vram` | 模型配置 | 低显存模式（组件移 CPU） |
| `model.layer_offloading` | 模型配置 | 层卸载（部分层放 CPU） |
| `network.type` | 网络配置 | `lora` 或 `lokr` |
| `network.linear` | 网络配置 | LoRA rank |
| `train.batch_size` | 训练配置 | 批大小 |
| `train.gradient_accumulation` | 训练配置 | 梯度累积步数 |
| `train.cache_text_embeddings` | 训练配置 | 缓存文本 embedding 到硬盘 |
| `datasets.cache_latents_to_disk` | 数据集配置 | 缓存 latent 到硬盘 |

## 环境配置

### .env 文件

```bash
# HuggingFace 缓存目录
HF_HOME=D:\huggingface_cache
HF_HUB_ENABLE_HF_TRANSFER=1
```

### 启动命令

```bash
# 命令行训练
python run.py config/your_config.yml

# 启动 Web UI
cd ui && npm run dev
```

## 常见问题

### safetensors 加载卡住

Windows 上 `mmap` 后端可能导致加载卡住，需要修改 `extensions_built_in/diffusion_models/krea2/krea2.py`：

```python
# 将所有 load_file 调用改为：
load_file(path, backend="pread")
```

### 8GB 显存配置建议

```yaml
model:
  quantize: true
  qtype: "qfloat8"
  quantize_te: true
  qtype_te: "qfloat8"
  low_vram: true
  layer_offloading: true
  layer_offloading_transformer_percent: 0.5

train:
  batch_size: 1
  gradient_accumulation: 4
  gradient_checkpointing: true
  optimizer: "adamw8bit"
  cache_text_embeddings: true  # 缓存到硬盘，释放 Text Encoder 显存

datasets:
  - cache_latents_to_disk: true
```

## 模型文件说明

- **Transformer 权重**：模型核心，LoRA 挂载位置
- **Text Encoder**：编码 prompt 为 embedding，训练时可缓存后卸载
- **VAE**：图片 ↔ latent 转换，训练时可缓存后卸载
- **Assistant LoRA**：Turbo 版本需要的训练适配器（如 krea2_turbo）
