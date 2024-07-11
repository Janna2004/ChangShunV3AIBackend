# 使用官方的Python 3.8镜像作为基础镜像
FROM python:3.8
# 设置工作目录
WORKDIR /predict
# 将当前目录内容复制到容器的/app目录下
COPY . /predict
# 安装任何需要的包
RUN pip install --no-cache-dir -r requirements.txt
# 对外暴露的端口号
EXPOSE 5000
# 运行命令
CMD ["python", "function/sampleForAI.py"]
