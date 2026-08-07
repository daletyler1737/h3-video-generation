#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H3 文生视频带音频 (t2v) - ComfyUI API 提交 + 轮询 (2026-08-07 验证通过)
用法: python h3_t2v.py "<英文提示词>" [输出名] [width] [height] [length帧] [steps]
示例: python h3_t2v.py "A young anime girl ..." h3_anime_girl 768 768 72 30
输出: ComfyUI/output/<输出名>_00001.mp4 (带音频轨)
"""
import json
import sys
import time
import urllib.request

API = "http://127.0.0.1:8188"


def submit(prompt_text: str, out_name: str, width=768, height=768, length=72, steps=30, seed=42):
    # 关键坑: MiniMaxH3ImageToVideo 输出 [CONDITIONING, LATENT] 两个槽位
    #   KSampler.positive <- output_0 (CONDITIONING, 节点自带, 不需要额外 CLIPTextEncode positive)
    #   KSampler.latent_image <- output_1 (LATENT)
    p = {
        "1": {"class_type": "UnetLoaderGGUF", "inputs": {"unet_name": "MiniMax-H3-FL2VA-Q4_K_M.gguf"}},
        "2": {"class_type": "CLIPLoaderGGUF", "inputs": {"clip_name": "qwen3vl_32b_minimax_h3-Q4_K_M.gguf", "type": "minimax"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_video_vae_fp16.safetensors"}},
        "4": {"class_type": "VAELoader", "inputs": {"vae_name": "minimax_h3_audio_vae_fp32.safetensors"}},
        "5": {"class_type": "MiniMaxH3SigmaShift", "inputs": {"model": ["1", 0], "shift_video": 12.0, "shift_audio": 3.0}},
        "6": {"class_type": "MiniMaxH3ImageToVideo", "inputs": {
            "clip": ["2", 0], "vae": ["3", 0],
            "prompt": prompt_text,
            "width": width, "height": height, "length": length,
        }},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": ""}},
        "8": {"class_type": "KSampler", "inputs": {
            "model": ["5", 0], "seed": seed, "steps": steps, "cfg": 1.0,
            "sampler_name": "euler", "scheduler": "normal", "denoise": 1.0,
            "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["6", 1],
        }},
        "9": {"class_type": "VAEDecode", "inputs": {"samples": ["8", 0], "vae": ["3", 0]}},
        "10": {"class_type": "VAEDecodeAudio", "inputs": {"samples": ["8", 0], "vae": ["4", 0]}},
        "11": {"class_type": "CreateVideo", "inputs": {"images": ["9", 0], "fps": 24.0, "audio": ["10", 0]}},
        "12": {"class_type": "SaveVideo", "inputs": {"video": ["11", 0], "filename_prefix": out_name, "format": "auto", "codec": "auto"}},
    }
    payload = json.dumps({"prompt": p}).encode()
    req = urllib.request.Request(f"{API}/prompt", data=payload, headers={"Content-Type": "application/json"})
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        r = json.loads(resp.read())
        pid = r.get("prompt_id")
        if r.get("node_errors"):
            print("节点错误:", json.dumps(r["node_errors"], ensure_ascii=False)[:300])
            return None
        print(f"提交成功 prompt_id={pid}")
        return pid
    except urllib.error.HTTPError as e:
        print("HTTP", e.code, e.read().decode()[:600])
        return None


def poll(pid: str, timeout_min=60):
    t0 = time.time()
    last = -1
    while time.time() - t0 < timeout_min * 60:
        try:
            r = json.loads(urllib.request.urlopen(f"{API}/history/{pid}", timeout=10).read())
            if pid in r:
                status = r[pid].get("status", {})
                if status.get("completed"):
                    outs = r[pid].get("outputs", {})
                    print("✅ 完成! 输出:", json.dumps(outs, ensure_ascii=False)[:300])
                    return True
                if status.get("status_str") == "error":
                    print("❌ 失败:", json.dumps(status, ensure_ascii=False)[:400])
                    return False
            try:
                q = json.loads(urllib.request.urlopen(f"{API}/queue", timeout=10).read())
                cur = q.get("queue_running", [])
                if cur:
                    cur = cur[0][1]
                    prog = cur.get("progress", {})
                    if cur.get("prompt_id") == pid and prog:
                        v = prog.get("value", 0) / max(prog.get("max", 1), 1) * 100
                        if int(v) != last:
                            last = int(v)
                            print(f"  进度: {v:.0f}% ({time.time()-t0:.0f}s)", flush=True)
            except Exception:
                pass
        except Exception:
            pass
        time.sleep(10)
    print("超时")
    return False


if __name__ == "__main__":
    prompt_text = sys.argv[1]
    out_name = sys.argv[2] if len(sys.argv) > 2 else "h3_gen"
    w = int(sys.argv[3]) if len(sys.argv) > 3 else 768
    h = int(sys.argv[4]) if len(sys.argv) > 4 else 768
    ln = int(sys.argv[5]) if len(sys.argv) > 5 else 72
    st = int(sys.argv[6]) if len(sys.argv) > 6 else 30
    pid = submit(prompt_text, out_name, w, h, ln, st)
    if pid:
        poll(pid)
