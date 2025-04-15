from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
import os
import shutil
import subprocess

app = FastAPI()

# 设置 Conda 环境名
transfer_conda_env_name = "stargan-v2"  # 替换为你需要激活的环境名

def clear_all_files(dir_path):
    """递归删除指定目录下所有文件，保留目录结构"""
    print(f"🧹 清空目录中的所有文件（保留文件夹）：{dir_path}")
    if not os.path.exists(dir_path):
        print(f"❌ 路径不存在：{dir_path}")
        return

    for root, dirs, files in os.walk(dir_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            try:
                print(f"尝试删除文件：{file_path}")
                os.remove(file_path)
            except Exception as e:
                print(f"⚠️ 无法删除 {file_path}: {e}")

@app.post("/style-transfer")
async def style_transfer(source: UploadFile = File(...), reference: UploadFile = File(...), source_label: str = Form(...), reference_label: str = Form(...)):
    transfer_source_dir = "/home/wpf/code/stargan-v2-master/assets/representative/weary/src"
    transfer_reference_dir = "/home/wpf/code/stargan-v2-master/assets/representative/weary/ref"
    transfer_output_dir = "/home/wpf/code/stargan-v2-master/expr/results/weary"

    os.makedirs(transfer_source_dir, exist_ok=True)
    os.makedirs(transfer_reference_dir, exist_ok=True)
    os.makedirs(transfer_output_dir, exist_ok=True)

    try:
        for dir_path in [transfer_source_dir, transfer_reference_dir]:
            clear_all_files(dir_path)

        transfer_source_dir = os.path.join(transfer_source_dir, source_label)
        transfer_reference_dir = os.path.join(transfer_reference_dir, reference_label)

        # 保存图像
        source_path = os.path.join(transfer_source_dir, "source.jpg")
        reference_path = os.path.join(transfer_reference_dir, "reference.jpg")

        with open(source_path, "wb") as f:
            shutil.copyfileobj(source.file, f)

        with open(reference_path, "wb") as f:
            shutil.copyfileobj(reference.file, f)

        # 执行脚本
        args = "--mode sample --num_domains 3 --resume_iter 100000 --w_hpf 1 --checkpoint_dir expr/checkpoints/weary_transform_multi --result_dir expr/results/weary --src_dir assets/representative/weary/src --ref_dir assets/representative/weary/ref --img_size 128"
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
            output_image_path = os.path.join(transfer_output_dir, "reference.jpg")
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
