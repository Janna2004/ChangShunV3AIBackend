import base64
import json
from flask import Flask, request, jsonify
import datetime
import requests
import logging

from main import detect_objects

app = Flask(__name__)

# 配置日志
logging.basicConfig(level=logging.INFO)

diseases = [
    {
        "id": 1,
        "name": "细菌性叶枯病",
        "description": "患病现象：细菌性叶枯病初期叶片出现长条形、水浸状的病斑,呈灰绿色。病斑不断扩大,最终导致整个叶片枯萎。严重时,可导致稻穗不发育或者死亡。控制措施: 合理施肥,避免氮肥过量。及时清理田间作物残渣。适当防治,如喷洒杀菌剂。"
    },
    {
        "id": 2,
        "name": "细菌性叶斑病",
        "description": "患病现象: 在叶片上出现不规则形状的褐色或黄褐色斑点,斑点常沿叶脉延伸。严重时斑点会扩大,叶片出现大片死亡。病斑表面常有细菌状物质渗出。病叶常卷曲、枯萎。控制措施: 注意田间卫生,避免伤害植株。适时进行药剂防治,如使用铜制剂、多霉素等。配合农业措施,如轮作、施肥等。"
    },
    {
        "id": 3,
        "name": "稻瘟病",
        "description": "患病现象: 叶片上出现长椭圆形的白色或灰白色病斑,边缘褐色。病斑逐渐扩大,叶片枯萎死亡。严重时整个叶面积大量枯死,秆也会倒伏。颗粒满度降低,产量大幅下降。控制措施: 适时喷洒杀菌剂,如吡唑醚菌酯、戊唑醇等。合理施肥,增强作物抗病性。轮作或休耕等综合防控措施。"
    },
    {
        "id": 4,
        "name": "褐斑病",
        "description": "患病现象: 在叶片、茎秆上出现圆形或不规则的褐色或紫褐色斑点。病斑表面干燥,中间常有凹陷。严重时病斑会扩大,叶片枯萎脱落。在茎秆、花梗和块茎上也会出现类似病斑。块茎上的病斑往往不规则,严重时会全面腐烂。控制措施: 适时喷洒杀菌剂,如巴斯德菌素、多菌灵等。及时清理病株残体,保持田间卫生。采取轮作、合理施肥等综合防控措施。"
    },
    {
        "id": 5,
        "name": "心腐病",
        "description": "患病现象: 病害首先发生在植株心叶部位,导致心叶枯黄、卷曲。进一步发展时,心叶会完全枯死,呈黑褐色。严重时,整个植株菜心部位全部腐烂,呈现烂心症状。受染植株生长受阻,株高明显矮小。还会引起糖分含量降低,严重影响产量和品质。控制措施: 适时喷洒铜制剂等杀菌剂进行药剂防治。保持良好的田间卫生,清理病株残体。合理施肥,增强植株抗病能力。"
    },
    {
        "id": 6,
        "name": "霜霉病",
        "description": "患病现象: 初发时叶片上出现不规则的黄色或褐色斑点。斑点逐渐扩大,叶片变成灰白色或紫色,呈现霜霉样。严重时,整个叶片枯萎脱落,茎干也会出现病斑。在果实或块茎上也会出现类似症状,严重影响品质。潮湿天气下,病斑表面还会出现白色或灰色的霉状物。控制措施: 注重田间管理,保持良好通风透光条件。适时喷洒如噻菌灵、代森锰锌等杀菌剂。及时清理病株残体,避免病菌越冬传播。"
    },
    {
        "id": 7,
        "name": "褐飞虱",
        "description": "患病现象: 叶片、茎秆上出现褐色或紫褐色的圆形或不规则斑点。病斑表面干燥,中间常有凹陷。严重时病斑扩大,叶片枯萎脱落茎秆、花梗和块茎上也会出现类似病斑。块茎病斑不规则,严重时腐烂。控制措施: 适时喷洒杀菌剂。清理病株残体,保持田间卫生。采取轮作、合理施肥等综合防控。"
    },
    {
        "id": 8,
        "name": "稻瘟病毒病",
        "description": "患病现象: 叶片出现淡绿色或黄绿色条纹或斑块。病叶呈现波浪状弯曲或卷曲。严重时植株矮化,分蘖受抑制。出现白化或枯死的病斑。稻穗畸形或不能抽出。控制措施: 切断病毒媒介的传播渠道,如合理用药防治白背飞虱。及时清除病株,保持良好的田间卫生。合理施肥,增强植株抗病力。对种子进行热处理或化学消毒。"
    }
]


def addDetInfo(data):
    url = "http://chang-shun-v3-backend:9003/ai/detInfo"  # 替换为你的服务器地址和API端点
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, json=data)
    return response.status_code, response.json()

def addAlert(data):
    url = "http://chang-shun-v3-backend:9003/ai/alert"  # 替换为你的服务器地址和API端点
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, json=data)
    return response.status_code, response.json()

@app.route('/detect', methods=['POST'])
def detect():
    try:
        if 'image' not in request.files:
            logging.error("No image file in request")
            return jsonify({"msg": "No image file in request"}), 400

        # 接收客户端上传的图片
        file = request.files['image']

        # 将图像文件保存到临时目录
        temp_file_path = f'uploads/{file.filename}'
        file.save(temp_file_path)

        result = detect_objects(temp_file_path)

        # 获取当前时间
        current_time = datetime.datetime.now()
        time_str = current_time.strftime('%Y-%m-%dT%H:%M:%S+08:00')

        # 返回处理后的图像和相关信息
        if result["state"] == 0:
            return jsonify({
                'state': 0,
                'time': time_str
            })
        elif result["state"] == 1:
            with open(result["image"], 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            # 获取第一个患病种类
            disease_type = result["type"][0] if result["type"] else None
            # 获取第一个患病概率
            pest_probability = result["conf"][0] if result["conf"] else None
            # 查找对应的病害描述和 pest_type_id
            content = None
            pest_type_id = None
            for disease in diseases:
                if disease_type == disease["name"]:
                    content = disease["description"]
                    pest_type_id = disease["id"]
                    break

            # 将结果返回给服务器
            message_data = {
                "image_paths": [
                    {
                        "path": "/function/"+temp_file_path
                    }
                ],
                "field_id": None,
                "drone_id": None,
                "detection_time": time_str,
                "pest_type_id": pest_type_id,
                "pest_probability": pest_probability
            }
            print(message_data)
            status_code, response_data = addDetInfo(message_data)
            if status_code != 200:
                return jsonify({"msg": "Failed to send message to server", "status_code": status_code})

            detection_info_id = response_data['data']['detection_info_id']
            return jsonify({
                'image': image_data,
                'state': 1,
                'type': disease_type,
                'conf': pest_probability,
                'content': content,
                'time': time_str,
                'detection_info_id': detection_info_id
            })
        else:
            return jsonify({
                'msg': "error"
            })
    except Exception as e:
        logging.error(f"Error during processing: {e}")
        return jsonify({"msg": "An error occurred", "error": str(e)}), 400


@app.route('/detectByDrone', methods=['POST'])
def detectByDrone():
    try:
        # 接收客户端上传的图片
        if 'image' not in request.files:
            logging.error("No image file in request")
            return jsonify({"msg": "No image file in request"}), 400
        file = request.files['image']

        # 将图像文件保存到临时目录
        temp_file_path = f'uploads/{file.filename}'
        file.save(temp_file_path)

        result = detect_objects(temp_file_path)

        # 获取当前时间
        current_time = datetime.datetime.now()
        time_str = current_time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
        # 获取第一个患病种类
        disease_type = result["type"][0] if result["type"] else None
        # 获取第一个患病概率
        pest_probability = result["conf"][0] if result["conf"] else None
        # 查找对应的pest_type_id
        pest_type_id = None
        for disease in diseases:
            if disease_type == disease["name"]:
                pest_type_id = disease["id"]
                break

        # 将结果返回给服务器
        message_data = {
            "image_paths": [
                {
                    "path": "tempor"
                }
            ],
            "field_id": None,
            "drone_id": None,
            "detection_time": time_str,
            "pest_type_id": pest_type_id,
            "pest_probability": pest_probability
        }
        status_code, response_data = addDetInfo(message_data)
        if status_code != 200:
            return jsonify({"msg": "Failed to send message to server", "status_code": status_code})

        # 获取 detection_info_id 并发送 alert 请求
        detection_info_id = response_data['data']['detection_info_id']
        data = {
            "handled": False,
            "alert_time": time_str,
            "detection_info_id": detection_info_id
        }
        alert_status_code, alert_response_data = addAlert(data)
        if alert_status_code != 200:
            return jsonify({"msg": "Failed to send alert to server", "status_code": alert_status_code})

        return jsonify({
            'msg': "success",
        })
    except Exception as e:
        logging.error(f"Error during processing: {e}")
        return jsonify({"msg": "An error occurred", "error": str(e)}), 400


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)


