import os

from ultralytics import YOLO
import cv2
import torch
import torch.nn.functional as F
import numpy as np
from torchvision import transforms
from PIL import Image


def detect_objects(image_path):
    # 加载 YOLO 模型
    model_path = "/predict/function/best.pt"
    model = YOLO(model_path)

    # 使用 cv2.imread() 读取图像文件
    image = cv2.imread(image_path)

    # 进行目标检测
    results = model.predict(source=image, save=True, save_txt=True)

    # 处理检测结果
    for result in results:
        # 获取边界框坐标 (归一化后的)
        boxes_xyxyn = result.boxes.xyxyn

        # 获取置信度和类别
        confs = result.boxes.conf
        classes = result.boxes.cls

        # 检查是否检测到任何目标
        if boxes_xyxyn.nelement() == 0:
            print("No objects detected.")
            return {
                 "state": 0,
            }
        else:
            # 打印检测到的目标数量
            num_boxes = len(boxes_xyxyn)
            print(f"Number of detected objects: {num_boxes}")

            # 获取保存预测结果的目录路径和图像文件名
            save_dir = result.save_dir
            image_name = os.path.basename(result.path)

            type, conf = classify_image(image_path)
            # 返回结果信息
            return {
                "state": 1,
                "image": save_dir + "\\" + image_name,
                "type": type,
                "conf": conf,
            }


def classify_image(img_path):
    # 选择设备
    device = 'cuda:0'
    device = torch.device(device if torch.cuda.is_available() else 'cpu')
    # 载入类别标签
    idx_to_labels = np.load(r"./idx_to_labels.npy", allow_pickle=True).item()

    # 导入训练好的模型
    model = torch.load(r"./dataset0_pytorch_C1.pth", map_location=device)
    model = model.eval().to(device)

    # 图像预处理
    test_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    # 载入测试图像
    img_pil = Image.open(img_path)
    input_img = test_transform(img_pil).unsqueeze(0).to(device)

    # 执行前向预测
    pre_logit = model(input_img)
    pre_softmax = F.softmax(pre_logit, dim=1)

    # 获取前 n 个预测结果
    n = 10
    top_n = torch.topk(pre_softmax, n)
    pre_ids = top_n[1].cpu().detach().numpy().squeeze()
    confs = (top_n[0].cpu().detach().numpy().squeeze()).tolist()

    pre=[]
    pre.append(idx_to_labels[pre_ids[0]])
    pre.append(idx_to_labels[pre_ids[1]])
    pre.append(idx_to_labels[pre_ids[2]])
    con=[]
    if confs[0] <= 0.01:
         con.append(0.01)
    else:
         con.append(confs[0])
    if confs[1] <= 0.01:
         con.append(0.01)
    else:
         con.append(confs[1])
    if confs[2] <= 0.01:
         con.append(0.01)
    else:
         con.append(confs[2])

    return pre,con
