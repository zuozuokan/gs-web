# services/dataset_service.py
import os
import subprocess

# 3DGS 专用 Python 环境
GS_PYTHON = r"D:\Anaconda\envs\improving_3dgs\python.exe"

# 3DGS 项目根目录
GS_ROOT = r"G:\xf\Improving-ADC-3DGS"


class DatasetService:

    def create_from_video(self, video_path: str):
        """
        从视频生成数据集
        """
        video_path = os.path.abspath(video_path)

        if not os.path.isfile(video_path):
            return False, "视频文件不存在"

        base_dir = os.path.dirname(video_path)
        input_dir = os.path.join(base_dir, "input")
        distorted_dir = os.path.join(base_dir, "distorted")

        # 1️⃣ 创建 input / distorted 目录
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(distorted_dir, exist_ok=True)

        # 2️⃣ ffmpeg 抽帧（✅ list 参数，完美支持空格路径）
        ffmpeg_cmd = [
            "ffmpeg",
            "-y",
            "-i", video_path,
            "-r", "1.5",
            "-vf", "scale=1280:720",
            os.path.join(input_dir, "input_%04d.png")
        ]

        try:
            subprocess.run(
                ffmpeg_cmd,
                check=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            return False, f"ffmpeg 执行失败:\n{e.stderr}"

        print("抽帧完成")

        # 3️⃣ 调用 convert.py（3DGS 专用 Python）
        convert_cmd = [
            GS_PYTHON,
            os.path.join(GS_ROOT, "convert.py"),
            "-s",
            base_dir
        ]

        try:
            subprocess.run(
                convert_cmd,
                check=True,
                cwd=GS_ROOT,    
                text=True
            )
        except subprocess.CalledProcessError as e:
            return False, f"convert.py 执行失败:\n{e.stderr}"

        return True, "数据集生成成功"


dataset_service = DatasetService()
