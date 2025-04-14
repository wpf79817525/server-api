from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
import os
import shutil
import subprocess

app = FastAPI()

# 设置 Conda 环境名
transfer_conda_env_name = "stargan-v2"  # 替换为你需要激活的环境名

TRANSFER_SOURCE_DIR = "/home/wpf/code/stargan-v2-master/assets/representative/weary/src"
TRANSFER_REFERENCE_DIR = "/home/wpf/code/stargan-v2-master/assets/representative/weary/ref"
TRANSFER_OUTPUT_DIR = "/home/wpf/code/stargan-v2-master/expr/results/weary"
# TRANSFER_SOURCE_DIR = "./input_images/source/"
# TRANSFER_REFERENCE_DIR = "./input_images/reference/"
# TRANSFER_OUTPUT_DIR = "./output_images/"

os.makedirs(TRANSFER_SOURCE_DIR, exist_ok=True)
os.makedirs(TRANSFER_REFERENCE_DIR, exist_ok=True)
os.makedirs(TRANSFER_OUTPUT_DIR, exist_ok=True)

@app.post("/style-transfer")
async def style_transfer(source: UploadFile = File(...), reference: UploadFile = File(...)):
    try:
        # 清空文件夹
        for dir_path in [TRANSFER_SOURCE_DIR, TRANSFER_REFERENCE_DIR]:
            for filename in os.listdir(dir_path):
                file_path = os.path.join(dir_path, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)

        # 保存图像
        source_path = os.path.join(TRANSFER_SOURCE_DIR, "source.jpg")
        reference_path = os.path.join(TRANSFER_REFERENCE_DIR, "reference.jpg")

        with open(source_path, "wb") as f:
            shutil.copyfileobj(source.file, f)

        with open(reference_path, "wb") as f:
            shutil.copyfileobj(reference.file, f)

        # 执行脚本
        args = "--mode sample --num_domains 3 --resume_iter 100000 --w_hpf 1 --checkpoint_dir expr/checkpoints/weary_transform_multi --result_dir expr/results/weary --src_dir assets/representative/weary/src --ref_dir assets/representative/weary/ref --img_size 128"
        args = ""
        result = subprocess.run(
            f"bash -c 'source ~/anaconda3/etc/profile.d/conda.sh && conda activate {transfer_conda_env_name} && python main.py {args}'",
            shell=True,  # 使用 shell 来执行 bash 脚本
            # ["python", "test.py", args],
            cwd="/home/wpf/code/stargan-v2-master/",  # 可换成你的实际脚本目录
            # cwd=".",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode == 0:
            # 假设脚本执行完后，在 output_images/weary 目录下生成了风格转换后的图像
            output_image_path = os.path.join(TRANSFER_OUTPUT_DIR, "reference.jpg")
            if os.path.exists(output_image_path):
                return FileResponse(output_image_path, media_type='image/jpeg')
            else:
                return JSONResponse(content={"message": "生成的图像不存在"}, status_code=500)
        else:
            return JSONResponse(content={
                "message": "风格转换失败",
                "stderr": result.stderr
            }, status_code=500)

    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)
