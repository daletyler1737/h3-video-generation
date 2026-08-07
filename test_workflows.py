#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试所有 H3 工作流: 转换 -> 提交 -> 轮询 (2026-08-07)
用法: python test_workflows.py <ui_workflow.json> <输出前缀> [额外覆盖参数...]
示例: python test_workflows.py "workflows/H3-伪图像生成-pseudo.json" h3_pseudo_test "5.prompt=xxx"
"""
import json
import sys
import time
import urllib.request
import urllib.error

API = "http://127.0.0.1:8188"
sys.path.insert(0, ".")
from workflow_to_api import convert


def submit(prompt: dict):
    payload = json.dumps({"prompt": prompt}).encode()
    req = urllib.request.Request(f"{API}/prompt", data=payload, headers={"Content-Type": "application/json"})
    try:
        r = json.loads(urllib.request.urlopen(req, timeout=30).read())
        if r.get("node_errors"):
            print("❌ 节点错误:", json.dumps(r["node_errors"], ensure_ascii=False)[:500])
            return None
        print("✅ 提交成功 prompt_id:", r.get("prompt_id"))
        return r.get("prompt_id")
    except urllib.error.HTTPError as e:
        print("❌ HTTP", e.code, e.read().decode()[:500])
        return None


def poll(pid: str, timeout_min=90):
    t0 = time.time()
    last = -1
    while time.time() - t0 < timeout_min * 60:
        try:
            r = json.loads(urllib.request.urlopen(f"{API}/history/{pid}", timeout=10).read())
            if pid in r:
                status = r[pid].get("status", {})
                if status.get("completed"):
                    outs = r[pid].get("outputs", {})
                    print("✅ 完成! 输出:", json.dumps(outs, ensure_ascii=False)[:400])
                    return True
                if status.get("status_str") == "error":
                    print("❌ 失败:", json.dumps(status, ensure_ascii=False)[:500])
                    return False
            q = json.loads(urllib.request.urlopen(f"{API}/queue", timeout=10).read())
            for item in q.get("queue_running", []):
                cur = item[1]
                if cur.get("prompt_id") == pid:
                    prog = cur.get("progress", {})
                    if prog:
                        v = prog.get("value", 0) / max(prog.get("max", 1), 1) * 100
                        if int(v) != last:
                            last = int(v)
                            print(f"  进度: {v:.0f}% ({time.time()-t0:.0f}s)", flush=True)
        except Exception:
            pass
        time.sleep(10)
    print("⏰ 超时")
    return False


if __name__ == "__main__":
    wf = sys.argv[1]
    out_prefix = sys.argv[2]
    overrides = {}
    for a in sys.argv[3:]:
        k, _, v = a.partition("=")
        overrides[k.strip()] = v.strip()
    # 自动注入输出名前缀覆盖 (找 SaveVideo/SaveImage 节点的 filename_prefix)
    p = convert(wf, overrides)
    for nid, n in p.items():
        ct = n["class_type"]
        if ct in ("SaveVideo", "SaveImage") and "filename_prefix" in n["inputs"]:
            n["inputs"]["filename_prefix"] = out_prefix
    pid = submit(p)
    if pid:
        poll(pid)
