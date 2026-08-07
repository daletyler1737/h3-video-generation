# MiniMax H3 本地视频生成 / Local AI Video Generation with MiniMax H3

用 MiniMax H3（FL2VA 文生视频带音频）在 ComfyUI 中本地生成 AI 视频。
Generate AI videos locally with MiniMax H3 (FL2VA text-to-video with audio) in ComfyUI.

> 无需 API、无需联网生成、断网也能用 / No API keys, fully local, works offline.

---

## 特性 / Features

- **文生视频带音频** (Text-to-Video with Audio, t2v)：一句话生成带对白/音效的视频，适合短剧、动漫、短视频 / Generate videos with dialogue & sound effects from a prompt — great for short dramas, anime, and shorts
- **参考图生视频** (Reference Image to Video, ref2va)：让角色说话/动作，保持形象一致 / Make a character speak & move while keeping identity consistent
- **首尾帧过渡** (First-Last Frame, fl2v)：首帧 + 尾帧 → 运镜/转场 / Camera moves & transitions between two frames
- **伪图像生成** (Pseudo Image, pseudo)：文字 → 静态分镜图/海报 / Text-to-image for storyboards & posters
- **API 自动化** (API Automation)：`h3_t2v.py` 脚本直接提交生成任务，无需打开网页 / Submit jobs via script — no browser needed

## 硬件要求 / Hardware Requirements

| 组件 / Component | 最低要求 / Minimum | 推荐 / Recommended |
|---|---|---|
| GPU 显存 / VRAM | 8 GB (CPU offload) | 16 GB+ |
| 内存 / RAM | 32 GB | 48 GB+ |
| 硬盘 / Disk | 60 GB 可用 | 100 GB+ |
| 系统 / OS | Windows 10/11, Linux | — |

> 显存不足会自动 CPU offload，生成速度变慢但可用。 / Low VRAM falls back to CPU offload — slower but works.

## 模型下载 / Model Downloads

模型约 45 GB（GGUF 量化版），任选一个镜像 / ~45 GB quantized GGUF, pick any mirror:

- **ModelScope（国内快）**：https://www.modelscope.cn/models/Abiray/MiniMax-H3-GGUF
- **HF Mirror（国内镜像）**：https://hf-mirror.com/Abiray/MiniMax-H3-GGUF

放到对应目录 / Place into:

| 模型 / Model | 目录 / Directory |
|---|---|
| `MiniMax-H3-FL2VA-Q4_K_M.gguf` | `ComfyUI/models/unet/` |
| `MiniMax-H3-Ref2VA-Q4_K_S.gguf` | `ComfyUI/models/unet/` |
| `qwen3vl_32b_minimax_h3-Q4_K_M.gguf` (CLIP) | `ComfyUI/models/text_encoders/` |
| `minimax_h3_video_vae_fp16.safetensors` | `ComfyUI/models/vae/` |
| `minimax_h3_audio_vae_fp32.safetensors` | `ComfyUI/models/audio/` |

## 安装 / Installation

1. 安装 ComfyUI（Windows 便携版或官方版）/ Install ComfyUI
2. 安装 H3 节点（GGUF 支持）/ Install H3 custom nodes:
   - `ComfyUI-GGUF`（需 h3-mmproj 分支）/ with the h3-mmproj branch
   - MiniMax H3 核心节点（含 `MiniMaxH3ImageToVideo`、`MiniMaxH3SigmaShift`、`VAEDecodeAudio`、`CreateVideo`）
3. 下载模型放入对应目录 / Download models into the folders above
4. 把 `workflows/` 下的 JSON 导入 ComfyUI（拖入画布即可）/ Drag the JSON files from `workflows/` into ComfyUI canvas

## 使用 / Usage

### 方式一：网页 / Web UI

启动 ComfyUI → 打开 http://127.0.0.1:8188 → 拖入工作流 JSON → Queue。

### 方式二：脚本（推荐自动化）/ Script (recommended)

```bash
# 文生视频带音频 / text-to-video with audio
python h3_t2v.py "A young anime girl walks through a neon-lit street at night, rain falling, cinematic lighting" h3_anime_girl 768 768 72 30

# 参数 / Args: 提示词 输出名 宽 高 帧数(24fps) 步数
#                prompt  out_name  w   h   length   steps
```

输出到 `ComfyUI/output/<out_name>_00001.mp4`（带音频轨 / with audio track）。

**提示词要点 / Prompt tips**（对 H3 效果显著 / works well with H3）：

- 用英文效果更好 / English prompts work best
- 结构：主体 + 动作 + 场景 + 风格 + 情绪 / Subject + action + scene + style + mood
- 运动描述要具体：走路方向、镜头运动、物理规律 / Be specific about motion: walking direction, camera movement, physics

## 性能参考 / Performance Reference

- 768×768 / 3 秒 (72帧) / 30 步：约 20 分钟（中端显卡 + CPU offload）
- 分辨率、时长、步数线性放大 / Scales linearly with resolution, length, and steps
- 提速建议：降步数到 20、用 512×512、或先用 pseudo 出图再 ref2va（分镜图→视频更可控）/ Speed tips: 20 steps, 512×512, or storyboard-image → ref2va pipeline

## 工作流说明 / Workflows

| 文件 / File | 用途 / Purpose |
|---|---|
| `H3-文生视频带音频-t2v.json` | 文字→视频+对白音频（短剧/动漫主力）/ Text → video with dialogue (main pipeline) |
| `H3-参考图视频-ref2va.json` | 角色参考图→说话/动作 / Character image → speaking & moving |
| `H3-首尾帧图生视频-fl2v.json` | 首帧+尾帧→过渡（转场/运镜）/ First+last frame → transition |
| `H3-伪图像生成-pseudo.json` | 文字→静态图（分镜/海报）/ Text → still image (storyboard/poster) |

## 常见坑 / Pitfalls

- **`MiniMaxH3ImageToVideo` 输出是 [CONDITIONING, LATENT] 两个槽位**：`KSampler.positive` 接 output_0（节点自带条件，不需要额外 CLIPTextEncode positive），`latent_image` 接 output_1。接反报 `return_type_mismatch`。 / The node outputs TWO slots: positive ← output_0 (CONDITIONING, built-in), latent_image ← output_1 (LATENT)
- UI 工作流 JSON 不能直接提交 API，要用脚本里的手写 prompt（节点链固定） / UI workflow JSON can't be POSTed directly; use the hand-built prompt in the script
- t2v 带音频必须用 FL2VA 模型，ref2va 用 Ref2VA 模型，别选错 / Use FL2VA for t2v-with-audio, Ref2VA for reference-image jobs
- 提示词 cfg=1.0、sampler=euler、scheduler=normal 是 H3 的标准配置 / cfg 1.0 + euler + normal is the H3 standard

## 脚本 / Scripts

- `h3_t2v.py` — 文生视频带音频 API 提交 + 进度轮询 / Text-to-video-with-audio API submit + progress polling

## License

MIT
