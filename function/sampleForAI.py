import base64
import json
from flask import Flask, request, jsonify
import datetime

from main import detect_objects

app = Flask(__name__)


@app.route('/detect', methods=['POST'])
def detect():
    # 接收客户端上传的图片
    file = request.files['image']

    # 将图像文件保存到临时目录
    temp_file_path = f'/predict/function/uploads/{file.filename}'
    file.save(temp_file_path)


    result = detect_objects(temp_file_path)


    # 将处理后的图像保存为bytes流
    if result["state"] == 1:
        with open(result["image"], 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
    elif result["state"] == 0:
        with open(temp_file_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')

    # 获取当前时间
    current_time = datetime.datetime.now()
    # 以字符串格式输出当前时间
    time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')


    # 返回处理后的图像和相关信息
    if result["state"] == 0:
        return jsonify({
            'image': image_data,
            'state': 0,
            'time': time_str
        })
    elif result["state"] == 1:
        # 将结果序列化为 JSON 格式
        conf_json_data = json.dumps(result['conf'])

        # 处理当前患病种类
        kinds = []
        for kind in result["type"]:
            if kind == "bacterial_leaf_blight":
                kinds.append("细菌性叶枯病")
            elif kind == "bacterial_leaf_streak":
                kinds.append("细菌性叶斑病")
            elif kind == "blast":
                kinds.append("稻瘟病")
            elif kind == "brown_spot":
                kinds.append("褐斑病")
            elif kind == "dead_heart":
                kinds.append("心腐病")
            elif kind == "downy_mildew":
                kinds.append("霜霉病")
            elif kind == "hispa":
                kinds.append("褐斑病")
            elif kind == "tungro":
                kinds.append("稻瘟病毒病")

        if result["type"][0] == "bacterial_leaf_blight":
            content = "患病现象：细菌性叶枯病初期叶片出现长条形、水浸状的病斑,呈灰绿色。病斑不断扩大,最终导致整个叶片枯萎。严重时,可导致稻穗不发育或者死亡。控制措施: 合理施肥,避免氮肥过量。及时清理田间作物残渣。适当防治,如喷洒杀菌剂。"
        elif result["type"][0] == "bacterial_leaf_streak":
            content = "患病现象: 在叶片上出现不规则形状的褐色或黄褐色斑点,斑点常沿叶脉延伸。严重时斑点会扩大,叶片出现大片死亡。病斑表面常有细菌状物质渗出。病叶常卷曲、枯萎。控制措施: 注意田间卫生,避免伤害植株。适时进行药剂防治,如使用铜制剂、多霉素等。配合农业措施,如轮作、施肥等。"
        elif result["type"][0] == "blast":
            content = "患病现象: 叶片上出现长椭圆形的白色或灰白色病斑,边缘褐色。病斑逐渐扩大,叶片枯萎死亡。严重时整个叶面积大量枯死,秆也会倒伏。颗粒满度降低,产量大幅下降。控制措施: 适时喷洒杀菌剂,如吡唑醚菌酯、戊唑醇等。合理施肥,增强作物抗病性。轮作或休耕等综合防控措施。"
        elif result["type"][0] == "brown_spot":
            content = "患病现象: 在叶片、茎秆上出现圆形或不规则的褐色或紫褐色斑点。病斑表面干燥,中间常有凹陷。严重时病斑会扩大,叶片枯萎脱落。在茎秆、花梗和块茎上也会出现类似病斑。块茎上的病斑往往不规则,严重时会全面腐烂。控制措施: 适时喷洒杀菌剂,如巴斯德菌素、多菌灵等。及时清理病株残体,保持田间卫生。采取轮作、合理施肥等综合防控措施。"
        elif result["type"][0] == "dead_heart":
            content = "患病现象: 病害首先发生在植株心叶部位,导致心叶枯黄、卷曲。进一步发展时,心叶会完全枯死,呈黑褐色。严重时,整个植株菜心部位全部腐烂,呈现烂心症状。受染植株生长受阻,株高明显矮小。还会引起糖分含量降低,严重影响产量和品质。控制措施: 适时喷洒铜制剂等杀菌剂进行药剂防治。保持良好的田间卫生,清理病株残体。合理施肥,增强植株抗病能力。"
        elif result["type"][0] == "downy_mildew":
            content = "患病现象: 初发时叶片上出现不规则的黄色或褐色斑点。斑点逐渐扩大,叶片变成灰白色或紫色,呈现霜霉样。严重时,整个叶片枯萎脱落,茎干也会出现病斑。在果实或块茎上也会出现类似症状,严重影响品质。潮湿天气下,病斑表面还会出现白色或灰色的霉状物。控制措施: 注重田间管理,保持良好通风透光条件。适时喷洒如噻菌灵、代森锰锌等杀菌剂。及时清理病株残体,避免病菌越冬传播。"
        elif result["type"][0] == "hispa":
            content = "患病现象: 叶片、茎秆上出现褐色或紫褐色的圆形或不规则斑点。病斑表面干燥,中间常有凹陷。严重时病斑扩大,叶片枯萎脱落茎秆、花梗和块茎上也会出现类似病斑。块茎病斑不规则,严重时腐烂。控制措施: 适时喷洒杀菌剂。清理病株残体,保持田间卫生。采取轮作、合理施肥等综合防控。"
        elif result["type"][0] == "tungro":
            content = "患病现象: 叶片出现淡绿色或黄绿色条纹或斑块。病叶呈现波浪状弯曲或卷曲。严重时植株矮化,分蘖受抑制。出现白化或枯死的病斑。稻穗畸形或不能抽出。控制措施: 切断病毒媒介的传播渠道,如合理用药防治白背飞虱。及时清除病株,保持良好的田间卫生。合理施肥,增强植株抗病力。对种子进行热处理或化学消毒。"

        return jsonify({
            'image': image_data,
            'state': 1,
            'type': kinds,
            'conf': conf_json_data,
            'content': content,
            'time': time_str
        })
    else:
        return jsonify({
            'msg': "error"
        })


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)


