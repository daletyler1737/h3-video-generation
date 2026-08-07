#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""给 H3 工作流插入 Spectrum 加速节点，生成新工作流 (2026-08-07)
用法: python insert_spectrum.py <输入工作流.json> <输出工作流.json> [sigma_shift_node_id] [sampler_node_id]
原理: 在原链 SigmaShift -> KSampler 之间插入 SpectrumApplyMiniMaxH3(model)
"""
import json
import sys

WF_DIR = "F:/ai-tu/ComfyUI_windows_portable_nvidia/ComfyUI_windows_portable/ComfyUI/user/default/workflows"


def insert(ui_path: str, out_path: str, sigma_id=2, sampler_id=7):
    with open(ui_path, encoding="utf-8") as f:
        ui = json.load(f)

    nodes = ui["nodes"]
    links = ui["links"]
    last_node = max(n["id"] for n in nodes)
    last_link = max(l[0] for l in links)

    # 找 SigmaShift -> KSampler 的连接 (sigma输出 -> sampler的model输入)
    old_link = None
    for l in links:
        # l: [link_id, from_id, from_slot, to_id, to_slot, type]
        if l[1] == sigma_id and l[3] == sampler_id and l[2] == 0 and l[4] == 0:
            old_link = l
            break
    if not old_link:
        # 宽松匹配: 任意 sigma->sampler 的 MODEL 连接
        for l in links:
            if l[1] == sigma_id and l[3] == sampler_id:
                old_link = l
                break
    if not old_link:
        print("❌ 未找到 SigmaShift -> KSampler 连接")
        return False

    print(f"找到原连接: {old_link}")

    # 1. 删除原连接
    links.remove(old_link)

    # 2. 新建 Spectrum 节点
    new_id = last_node + 1
    new_link_a = last_link + 1  # sigma -> spectrum
    new_link_b = last_link + 2  # spectrum -> sampler

    spectrum_node = {
        "id": new_id,
        "type": "SpectrumApplyMiniMaxH3",
        "pos": [1000, 500],
        "size": [254.77, 298],
        "flags": {},
        "order": 50,
        "mode": 0,
        "inputs": [
            {"name": "model", "type": "MODEL", "link": new_link_a},
            {"name": "enabled", "type": "BOOLEAN", "widget": {"name": "enabled"}, "link": None},
            {"name": "blend_weight", "type": "FLOAT", "widget": {"name": "blend_weight"}, "link": None},
            {"name": "degree", "type": "INT", "widget": {"name": "degree"}, "link": None},
            {"name": "ridge_lambda", "type": "FLOAT", "widget": {"name": "ridge_lambda"}, "link": None},
            {"name": "window_size", "type": "FLOAT", "widget": {"name": "window_size"}, "link": None},
            {"name": "flex_window", "type": "FLOAT", "widget": {"name": "flex_window"}, "link": None},
            {"name": "warmup_steps", "type": "INT", "widget": {"name": "warmup_steps"}, "link": None},
            {"name": "tail_actual_steps", "type": "INT", "widget": {"name": "tail_actual_steps"}, "link": None},
            {"name": "max_history", "type": "INT", "widget": {"name": "max_history"}, "link": None},
            {"name": "debug", "type": "BOOLEAN", "widget": {"name": "debug"}, "link": None},
        ],
        "outputs": [{"name": "model", "type": "MODEL", "links": [new_link_b]}],
        "properties": {"Node name for S&R": "SpectrumApplyMiniMaxH3"},
        "widgets_values": [True, 0.5, 1, 0.1, 2.0, 0.75, 1, 1, 8, False],
    }
    nodes.append(spectrum_node)

    # 3. 新建两条连接: sigma->spectrum, spectrum->sampler
    links.append([new_link_a, old_link[1], old_link[2], new_id, 0, "MODEL"])
    links.append([new_link_b, new_id, 0, old_link[3], old_link[4], "MODEL"])

    # 4. 更新 sampler 节点的 model input 指向新连接
    for n in nodes:
        if n["id"] == sampler_id:
            for inp in n.get("inputs", []):
                if inp["name"] == "model":
                    inp["link"] = new_link_b
            break

    # 5. 更新元数据
    ui["last_node_id"] = new_id
    ui["last_link_id"] = new_link_b

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(ui, f, ensure_ascii=False, indent=1)
    print(f"✅ 已生成: {out_path}")
    print(f"   Spectrum 节点 id={new_id}, 连接 {old_link[1]}->{new_id}->{old_link[3]}")
    return True


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else f"{WF_DIR}/H3-文生视频带音频-t2v.json"
    dst = sys.argv[2] if len(sys.argv) > 2 else f"{WF_DIR}/H3-t2v-Spectrum加速.json"
    sigma = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    sampler = int(sys.argv[4]) if len(sys.argv) > 4 else 7
    insert(src, dst, sigma, sampler)
