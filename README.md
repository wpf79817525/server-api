# 🌐 Style Transfer API 服务端

本项目为风格转换的后端服务，基于 FastAPI 构建，用于接收图像、执行风格转换脚本并返回生成结果图像。

---

## 🧱 环境准备

### 1. 创建服务端环境

项目中提供了 `server_env.yml` 环境配置文件，请执行以下命令：

```bash
conda env create -f server_env.yml
conda activate api-server
```
## 🧱 启动API服务

确保你当前位于服务端项目目录中，例如 ~/code/api-server/：
```
uvicorn hello:app --host 0.0.0.0 --port 8000
```
此时服务会监听所有 IP 地址，端口为 8000，终端输出类似如下：
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```
## 🧱 编写API服务
假设想添加一个新功能，可以参考style_transfer方法。编写完毕以后可以在Linux/Windows端进行测试：
如果是在Linux端测试可以执行：
```
curl -X POST http://localhost:8000
```