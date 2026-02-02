import subprocess
import json
import os
import re
import shutil
from services.history_service import HistoryService

GS_PYTHON = r"D:\Anaconda\envs\improving_3dgs\python.exe"
GS_ROOT = r"G:\xf\Improving-ADC-3DGS"

def run_metric(model_path: str):
    """
    调用 Improving-ADC-3DGS/evaluate.py
    计算 PSNR / SSIM / LPIPS
    """

    eval_script = os.path.join(GS_ROOT, "evaluate.py")

    if not os.path.exists(eval_script):
        raise RuntimeError(f"evaluate.py 不存在: {eval_script}")

    cmd = [
        GS_PYTHON,
        eval_script,
        "--model_path",
        model_path
    ]

    print("\n[Metric CMD]")
    print(" ".join(cmd))

    result = subprocess.run(
        cmd,
        cwd=GS_ROOT,                 # ⭐ 非常重要
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="ignore"
    )

    print("\n[Metric STDOUT]")
    print(result.stdout)

    if result.stderr:
        print("\n[Metric STDERR]")
        print(result.stderr)

    if result.returncode != 0:
        raise RuntimeError("evaluate.py 执行失败")

    # ===============================
    # 解析 evaluate.py 输出
    # ===============================

    """
    强约定（你 evaluate.py 里要做的事）：
    最后 print 一行 JSON，例如：
    {
        "PSNR": 28.31,
        "SSIM": 0.912,
        "LPIPS": 0.084
    }
    """

    for line in result.stdout.splitlines():
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            try:
                metrics = json.loads(line)
                # 基本字段校验
                if all(k in metrics for k in ("PSNR", "SSIM", "LPIPS")):
                    # 保存 metrics.md
                    try:
                        md_path = os.path.join(model_path, "metrics.md")
                        with open(md_path, "w", encoding="utf-8") as f:
                            f.write("# 训练评估报告\n\n")
                            f.write("| 指标 | 数值 |\n")
                            f.write("| :--- | :--- |\n")
                            f.write(f"| PSNR | {metrics['PSNR']} |\n")
                            f.write(f"| SSIM | {metrics['SSIM']} |\n")
                            f.write(f"| LPIPS | {metrics['LPIPS']} |\n")
                        print(f"[Metric] Saved report to {md_path}")

                        history_service = HistoryService()
                        record = history_service.get_record_by_model_path(model_path)
                        eval_output_path = md_path
                        if record and record.get("dataset_path"):
                            try:
                                dataset_md_path = os.path.join(record["dataset_path"], "metrics.md")
                                shutil.copyfile(md_path, dataset_md_path)
                                eval_output_path = dataset_md_path
                                print(f"[Metric] Copied report to {dataset_md_path}")
                            except Exception as e:
                                print(f"[Metric] Copy report failed: {e}")

                        try:
                            history_service.update_eval_record(
                                train_model_path=model_path,
                                eval_output_path=eval_output_path
                            )
                        except Exception as e:
                            print(f"[History Error] Failed to update eval record: {e}")
                    except Exception as e:
                        print(f"[Metric] Failed to save report: {e}")

                    return metrics
            except json.JSONDecodeError:
                continue

    # 如果没解析到
    raise RuntimeError("未在 evaluate.py 输出中找到评估结果 JSON")
