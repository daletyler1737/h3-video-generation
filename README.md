# MiniMax H3 本地视频生成 / Local AI Video Generation with MiniMax H3

用 MiniMax H3 在 ComfyUI 中本地生成带原生立体声的 AI 视频：文生视频、参考图生视频、首尾帧过渡、**无限长度长视频**。
Generate AI videos with native stereo audio locally in ComfyUI — text-to-video, reference-image-to-video, first/last-frame transitions, and **infinite-length long video**.

> 无需 API、无需联网生成、断网也能用 / No API keys, fully local, works offline.

---

## 特性 / Features

- **无限长度长视频** (Infinite-Length, Continuum)：突破 H3 单次 15 秒上限 —— 把上一段的 latent 潜空间 + 音频尾巴接力进下一段继续去噪，音画都连续，5 秒分段任意拼接成几分钟成片 / Break the 15-second single-pass limit: carry the previous segment's latent + audio tail into the next denoising pass, then join 5s segments into multi-minute videos
- **文生视频带音频** (Text-to-Video with Audio, t2v)：一句话生成带对白/音效的视频，适合短剧、动漫、短视频 / Generate videos with dialogue & sound effects from a prompt
- **参考图生视频** (Reference Image to Video, ref2va)：让角色说话/动作，保持形象一致 / Make a character speak & move while keeping identity consistent
- **首尾帧过渡** (First-Last Frame, fl2v)：首帧 + 尾帧 → 运镜/转场 / Camera moves & transitions between two frames
- **伪图像生成** (Pseudo Image, pseudo)：文字 → 静态分镜图/海报 / Text-to-image for storyboards & posters
- **6GB 低显存版** (Low-VRAM)：每类流程都有 6G / 8G 优化版，在 6GB 显卡上也能跑 / Every pipeline has a 6G / 8G tuned variant that runs on a 6 GB GPU
- **API 自动化** (API Automation)：`h3_t2v.py` 脚本直接提交生成任务，无需打开网页 / Submit jobs via script — no browser needed

## 无限长度长视频 / Infinite-Length Video

H3 单次生成上限约 15 秒。想更长，只有三条路，本仓库都提供了工作流：

| 方案 / Method | 原理 / How it works | 画质连续性 / Continuity | 工作流 / Workflow |
|---|---|---|---|
| **Continuum 潜空间接力**（推荐）| 上一段的 **latent 潜空间 + 音频尾巴** 直接作为下一段的输入继续去噪，不是重新出片 | ★★★ 音画都连续，当前最连贯 | `H3无限长度-Continuum潜空间接力.json` |
| Motion Context 接力 | 把上一段尾部运动作为上下文传给下一段 | ★★ 画面稳，但音轨要另接 | `H3无限长度-MotionContext接力.json` |
| 有限分段 / TimelineDirector | 按时间轴切段，每段独立生成后拼接，段落提示词可控 | ★ 段落切换处可能有跳变，但**分镜完全可控** | `H3无限-TimelineDirector-有限分段.json` |

**使用步骤 / How to use**

1. 打开工作流 → 找到 **MASTER / 主控节点**（设置总时长、分段数） / Open the workflow, find the **MASTER** node (total duration / segment count)
2. 填全局提示词 + 每段（S1/S2/S3…）各自的提示词 / Fill a global prompt + per-segment prompts
3. 点 ▶ 运行 → 自动逐段生成并拼接 / Click Run — segments generate and join automatically
4. 完成后输出完整长视频 / Get the full-length video

**关键参数 / Key parameters**

- **分段时长**：建议 5 秒 / 段（120 帧 @24fps），段数决定总长 / 5s per segment, count decides total length
- **Continuation Backend**：`Standard`（默认）/ default
- **Audio Continuity**：开启 → 音画一起接力 / on = audio carries too
- **显存**：默认配置用 int8（20GB）主模型，6–8GB 显卡请换 Q4_K_M GGUF（18.5GB，用 `UnetLoaderGGUF`）或 int4（10.6GB，用 `UNETLoader`）/ Default config loads the int8 20GB model; on a 6–8 GB card switch to Q4_K_M GGUF (UnetLoaderGGUF) or int4 (UNETLoader)

**系列文件 / Variants**

| 文件 / File | 说明 / Notes |
|---|---|
| `H3无限长度-Continuum潜空间接力-LoRA-turbo加速.json` | Continuum + lightx2v turbo LoRA，步数 20→8，**速度与质量的平衡点** / with turbo LoRA, 20→8 steps |
| `H3无限长度-Continuum潜空间接力-LoRA修正.json` | 同上，LoRA 强度修正版 / corrected LoRA strengths |
| `H3无限长度-Continuum潜空间接力.json` | 基础版，不带加速 LoRA / baseline, no accel LoRA |
| `H3无限长度-Continuum-V34-turbo-5秒接力.json` | V34 turbo 配置，5 秒一段 / V34 turbo, 5s segments |
| `H3无限-CL-T2V多场景5秒接力.json` | 纯文生多场景接力，不需要参考图 / multi-scene, text-only |
| `H3无限-TimelineDirector-导演台.json` | 时间轴导演台（带 UI）/ timeline director with UI |
| `H3无限-TimelineDirector-有限分段.json` | 时间轴 + 有限分段数 / timeline with fixed segment count |
| `H3无限-Director导演台-3段5秒接力.json` | 最简示例：3 段 × 5 秒 / minimal example: 3 × 5s |
| `H3无限长度-MotionContext接力.json` | Motion Context 方案 / motion-context variant |

## 低显存优化 / Low-VRAM (6 GB)

同一套流程的显存压缩版：更低的文本编码器占用 + 更小的主模型 + CPU offload，**最低 6GB 显存可跑**（480p 起）。

Same pipelines tuned down: smaller text encoder footprint + smaller main model + CPU offload, **runs from 6 GB VRAM** (start at 480p).

| 文件 / File | 用途 / Purpose |
|---|---|
| `H3-文生视频带音频-t2v-6G.json` | 文字 → 视频+对白音频（6G 版）/ t2v with audio, 6G |
| `H3-首尾帧图生视频-fl2v-6G.json` | 首帧+尾帧过渡（6G 版）/ fl2v, 6G |
| `H3-首尾帧图生视频-8G-低显存优化.json` | fl2v，8G 显存进一步优化 / fl2v, 8G |
| `H3-t2v-Spectrum加速-6G.json` | t2v + Spectrum 加速（6G 版）/ t2v + Spectrum, 6G |
| `H3-fl2v-Spectrum加速-6G.json` | fl2v + Spectrum 加速（6G 版）/ fl2v + Spectrum, 6G |
| `H3-伪图像生成-pseudo-6G.json` | 文字 → 分镜图（6G 版）/ pseudo, 6G |

> 6G 版默认按 480p / 较短时长配置，改大参数会 OOM。 / 6G variants default to 480p / shorter length; raising them may OOM.

## 硬件要求 / Hardware Requirements

| 组件 / Component | 最低 / Minimum | 推荐 / Recommended |
|---|---|---|
| GPU 显存 / VRAM | **6 GB**（用 6G 版工作流 / use the 6G workflows）| 16 GB+ |
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

**加速 LoRA（可选，但强烈建议）/ Acceleration LoRAs (optional)**

无限长度与 turbo 工作流引用了 lightx2v turbo LoRA，放到 `ComfyUI/models/loras/minimax/`：

- 4-step: https://hf-mirror.com/lightx2v/MiniMax-H3-Distill-LoRA
- 8-step: 同上仓库的 `8step` 变体 / same repo, `8step` variant

## 安装 / Installation

1. 安装 ComfyUI（Windows 便携版或官方版）/ Install ComfyUI
2. 安装 H3 节点 / Install H3 custom nodes:
   - `ComfyUI-GGUF`（需 h3-mmproj 分支）/ with the h3-mmproj branch
   - MiniMax H3 核心节点（含 `MiniMaxH3ImageToVideo`、`MiniMaxH3SigmaShift`、`VAEDecodeAudio`、`CreateVideo`）
   - **无限长度系列**还需 `MiniMaxH3LongVideo` 系列节点（Continuum / MotionContext / TimelineDirector），见报错提示里给出的插件名 / the infinite-length workflows additionally need the `MiniMaxH3LongVideo` node pack
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
- 带音频的流程可以在提示词里用 `Sound:` / `声音：` 分段写对白与音效 / For audio pipelines, write dialogue & SFX in `Sound:` lines

## 性能参考 / Performance Reference

- 768×768 / 3 秒 (72帧) / 30 步：约 20 分钟（中端显卡 + CPU offload） / ~20 min on a mid-range GPU with CPU offload
- 分辨率、时长、步数线性放大 / Scales linearly with resolution, length, and steps
- 提速建议：降步数到 20、用 turbo LoRA（20→8 步）、512×512、或先用 pseudo 出图再 ref2va（分镜图→视频更可控）/ Speed tips: 20 steps, turbo LoRA (20→8), 512×512, or storyboard-image → ref2va pipeline

## 工作流说明 / Workflows

**基础流程 / Basics**

| 文件 / File | 用途 / Purpose |
|---|---|
| `H3-文生视频带音频-t2v.json` | 文字→视频+对白音频（短剧/动漫主力）/ Text → video with dialogue (main pipeline) |
| `H3-参考图视频-ref2va.json` | 角色参考图→说话/动作 / Character image → speaking & moving |
| `H3-参考图视频-ref2va-safetensors版.json` | 同上，safetensors（非 GGUF）模型版 / same, safetensors model variant |
| `H3-首尾帧图生视频-fl2v.json` | 首帧+尾帧→过渡（转场/运镜）/ First+last frame → transition |
| `H3-伪图像生成-pseudo.json` | 文字→静态图（分镜/海报）/ Text → still image (storyboard/poster) |
| `H3-Multishot-多镜头-safetensors版.json` | 一次生成多个镜头 / multi-shot in one run |
| `H3-Turbo加速-480p-8步-最佳.json` | 480p / 8 步最快出片配置 / fastest 480p / 8-step preset |

**加速 / Acceleration**

| 文件 / File | 用途 / Purpose |
|---|---|
| `H3-t2v-Spectrum加速.json` | t2v + Spectrum 加速节点 / t2v with Spectrum (~2x faster sampling) |
| `H3-ref2va-Spectrum加速.json` | ref2va + Spectrum 加速 / ref2va with Spectrum |
| `H3-fl2v-Spectrum加速.json` | fl2v + Spectrum 加速 / fl2v with Spectrum |

**无限长度 / Infinite-length** — 见上文《无限长度长视频》章节 / see the Infinite-Length section above（9 个变体 / 9 variants）

**低显存 6G/8G / Low-VRAM** — 见上文《低显存优化》章节 / see the Low-VRAM section above（6 个变体 / 6 variants）

**后处理 / Post-processing**

| 文件 / File | 用途 / Purpose |
|---|---|
| `超分-RealESRGAN-逐帧4x.json` | 逐帧 4 倍超分 / per-frame 4x upscale |
| `超分-FlashVSR-480p到1080p.json` | FlashVSR 视频超分 480p → 1080p / FlashVSR video upscaling |

## 子目录工作流 / Subfolder Workflows

`workflows/` 下还有三个文件夹，按用途分类收录，共 84 个：

Three extra folders under `workflows/`, 84 files in total:

| 文件夹 / Folder | 数量 | 内容 / Contents |
|---|---|---|
| `6G备份/` | 5 | 早期 6G 版备份（与根目录 6G 版基本一致，留档用）/ early 6G backups |
| `低显存/` | 18 | 熊猫怪兽分享的 4G / 6G / 8G 工作流拆包，每条流程独立自包含 / unpacked 4G-6G-8G pipelines, self-contained |
| `熊猫怪兽分享/` | 61 | 社区分享包（含 H3 各项工作流与笔记）/ community-shared pack |

> `低显存/` 里三个 `加LoRA` 工作流的 LoRA 节点**已清空**（原作者关联的 LoRA 与内容不符，公开仓库不保留该引用）：打开后自己在 `LoraLoaderModelOnly` 节点选你自己的 LoRA 即可，`strength_model = 0` 即关闭。
>
> The LoRA node inside the three `加LoRA` workflows under `低显存/` is **cleared on purpose** — the original reference didn't belong in a public repo. Pick your own LoRA in the `LoraLoaderModelOnly` node; `strength_model = 0` disables it.

## 加速方案 / Acceleration

| 方案 / Method | 原理 / How | 提速 / Speedup | 来源 / Source |
|---|---|---|---|
| **Spectrum**（推荐）| 切比雪夫谱特征预测，跳过部分 transformer 计算 / Chebyshev spectral prediction skips part of the transformer | ~2x | https://github.com/xmarre/ComfyUI-Spectrum-MiniMax-H3 |
| **turbo LoRA**（lightx2v）| 蒸馏少步 LoRA，20 步 → 8 步 / distilled few-step LoRA, 20 → 8 steps | ~2-3x | https://hf-mirror.com/lightx2v/MiniMax-H3-Distill-LoRA |
| NB-H3-HyperStep | 复用中间 transformer block 结果 / reuses intermediate blocks | ~60% | https://github.com/biyuhe3442-cmd/ComfyUI-NB-H3-HyperStep |
| MiniMax-H3-Turbo | 4 步少步采样器 / 4-step sampler | 数倍 / several× | ComfyUI-Manager 搜 "MiniMax-H3 Turbo" |
| INT8 量化 + nunchaku | pruned_int8_convrot 模型 / int8 pruned model | ~2-3x | ComfyUI-nunchaku |
| TE fp16_accumulation | FP16 累积计算 / fp16 accumulation | 45%（显存充足时 / when VRAM is ample）| TE 启动器 |

**Spectrum 安装与使用 / Install & use**（本仓库已含加速工作流）:
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/xmarre/ComfyUI-Spectrum-MiniMax-H3.git
# 重启 ComfyUI 后，用 workflows/H3-t2v-Spectrum加速.json
```
节点插在 `MiniMaxH3SigmaShift` 和 `KSampler` 之间（MODEL→MODEL）。默认参数即用；`enabled=false` 可关闭。注意：Spectrum 是近似加速，快速动作时细节（眼睛/手指）可能变形，质量敏感场景请 A/B 对比。

## 常见坑 / Pitfalls

- **`MiniMaxH3ImageToVideo` 输出是 [CONDITIONING, LATENT] 两个槽位**：`KSampler.positive` 接 output_0（节点自带条件，不需要额外 CLIPTextEncode positive），`latent_image` 接 output_1。接反报 `return_type_mismatch`。 / The node outputs TWO slots: positive ← output_0 (CONDITIONING, built-in), latent_image ← output_1 (LATENT)
- UI 工作流 JSON 不能直接提交 API，要用脚本里的手写 prompt（节点链固定） / UI workflow JSON can't be POSTed directly; use the hand-built prompt in the script
- **API 连接的节点 id 必须是字符串**：`["1", 0]` 而不是 `[1, 0]`，否则报 KeyError / API link node ids must be strings
- **ref2va 旧版参数坑**：老工作流 JSON 用 `ref_image_0` 参数名，新版节点接口是 AUTOGROW 的 `ref_images`，API 格式为 `[["1", 0]]`（数组套数组）。旧名会报 `unexpected keyword argument 'ref_image_0'` / Old workflows use `ref_image_0`, new node API uses `ref_images` in `[["1",0]]` format
- t2v 带音频必须用 FL2VA 模型，ref2va 用 Ref2VA 模型，别选错 / Use FL2VA for t2v-with-audio, Ref2VA for reference-image jobs
- 提示词 cfg=1.0、sampler=euler、scheduler=normal 是 H3 的标准配置 / cfg 1.0 + euler + normal is the H3 standard
- pseudo 伪图像工作流 length=8 太短时提示词引导力弱，出图可能与提示词不符；要出图可用更长 length（如 17-34）再取帧 / pseudo with length=8 may ignore the prompt; use longer length for better control
- **无限长度工作流缺节点报错**：缺 `MiniMaxH3LongVideo` 系列节点时请按报错提示安装对应插件；Continuum 接力必须保证每段模型/VAE/LoRA 完全一致，换模型会导致接力处跳变 / install the `MiniMaxH3LongVideo` node pack; keep model/VAE/LoRA identical across segments
- **段数越多耗时越线性增长**：Continuum 每段都要完整采样，10 段 ≈ 单段耗时 ×10 / each segment is a full sampling pass

## 内容说明 / Content Policy

仓库内工作流的提示词均为**通用示例**（风景、人物动作、产品、剧情类），不含成人内容。

All prompts shipped in this repository are **generic examples** (landscape, character motion, product, narrative) and contain no adult content.

请遵守所在地法律与模型许可协议使用。 / Use in compliance with your local laws and the model license.

## 脚本 / Scripts

- `h3_t2v.py` — 文生视频带音频 API 提交 + 进度轮询 / Text-to-video-with-audio API submit + progress polling
- `workflow_to_api.py` — UI 工作流 JSON → API prompt 转换器（支持覆盖参数、空值删除参数）/ Convert UI workflow JSON to API prompt with overrides
- `test_workflows.py` — 一键测试任意工作流：转换→提交→轮询，自动注入输出名前缀 / Test any workflow: convert → submit → poll

## License

MIT
