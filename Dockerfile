# 使用官方的Python 3.8镜像作为基础镜像
FROM python:3.8
# 设置工作目录为 /function
WORKDIR /function
# 将当前目录中的 function 目录内容复制到容器的 /function 目录中
COPY function /function

# 安装任何需要的包
RUN echo "deb http://mirrors.aliyun.com/debian/ buster main non-free contrib" > /etc/apt/sources.list.d/aliyun.list
RUN echo "deb-src http://mirrors.aliyun.com/debian/ buster main non-free contrib" >> /etc/apt/sources.list.d/aliyun.list
RUN apt-get update && \
    apt-get install ffmpeg libsm6 libxext6  -y
RUN pip install  -i https://pypi.tuna.tsinghua.edu.cn/simple --upgrade pip
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 对外暴露的端口号
EXPOSE 5000
# 运行命令
CMD ["python", "function/sampleForAI.py"]
