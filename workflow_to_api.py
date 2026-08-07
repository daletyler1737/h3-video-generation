#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ComfyUI UI workflow JSON -> API prompt 转换器 (2026-08-07)
用法: python workflow_to_api.py <ui_workflow.json> [覆盖参数: 节点id.参数名=值 ...]
示例: python workflow_to_api.py "workflows/H3-文生视频带音频-t2v.json" 5.prompt="A cat" 5.length=72
输出: 打印 API prompt JSON（可直接 POST /prompt）
"""
import json
import sys


def convert(ui_path: str, overrides: dict = None):
    with open(ui_path, encoding="utf-8") as f:
        ui = json.load(f)

    nodes = {n["id"]: n for n in ui.get("nodes", [])}
    # link: [link_id, from_id, from_slot, to_id, to_slot, type]
    link_map = {}
    for l in ui.get("links", []):
        # link_id -> (from_id, from_slot)
        link_map[l[0]] = (l[1], l[2])

    prompt = {}
    for nid, n in nodes.items():
        ctype = n.get("type")
        if not ctype or ctype == "MarkdownNote":
            continue
        inputs = {}
        wv = list(n.get("widgets_values", []) or [])
        wv_idx = 0
        for inp in n.get("inputs", []):
            name = inp.get("name")
            link = inp.get("link")
            if link is not None and link in link_map:
                src = link_map[link]
                # ComfyUI API 连接: [节点id(字符串), 输出槽位]
                inputs[name] = [str(src[0]), src[1]]
            else:
                # widget 值（顺序对应 widgets_values）
                if wv_idx < len(wv):
                    inputs[name] = wv[wv_idx]
                    wv_idx += 1
        # 处理 outputs 引用的 widget（如 SaveImage 的 filename_prefix 可能在 widgets_values 尾部）
        # 某些节点 inputs 里没有但 widgets_values 有的（如 prompt 在 widgets_values[0]）
        prompt[str(nid)] = {"class_type": ctype, "inputs": inputs}

    # 覆盖参数: "5.prompt=xxx" / "5.length=72" / "7.ref_image_0=" (空值=删除该参数)
    if overrides:
        for k, v in overrides.items():
            nid, _, pname = k.partition(".")
            if nid in prompt and pname:
                if v == "":
                    prompt[nid]["inputs"].pop(pname, None)
                    continue
                try:
                    prompt[nid]["inputs"][pname] = json.loads(v)
                except Exception:
                    prompt[nid]["inputs"][pname] = v
    # 检查节点是否用旧版参数名（UI JSON vs 当前节点接口不匹配时覆盖）
    # AUTOGROW 动态输入: 连接直接以 ["from_id", slot] 形式接到 ref_images 即可
    return prompt


if __name__ == "__main__":
    path = sys.argv[1]
    ov = {}
    for a in sys.argv[2:]:
        k, _, v = a.partition("=")
        ov[k.strip()] = v.strip()
    p = convert(path, ov)
    print(json.dumps({"prompt": p}, ensure_ascii=False, indent=1))
