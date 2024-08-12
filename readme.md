### 长顺三期ai后端接口文档

**请求URL：** http://1.14.125.238/chang-shun/ai/detect

**请求类型：** POST

**Body：** form-data

- 参数名：image

- 参数值：图片（jpg）

- 类型：file

**返回示例：**

- 有病：

```json
{
    "conf": 0.9999895095825195,
    "content": "患病现象：细菌性叶枯病初期叶片出现长条形、水浸状的病斑,呈灰绿色。病斑不断扩大,最终导致整个叶片枯萎。严重时,可导致稻穗不发育或者死亡。控制措施: 合理施肥,避免氮肥过量。及时清理田间作物残渣。适当防治,如喷洒杀菌剂。",
    "detection_info_id": 22,
    "image": "这是一个base64串",
    "state": 1,
    "time": "2024-08-13T03:40:08+08:00",
    "type": "bacterial_leaf_blight"
}
```

- 无病：

```json
{
    "state": 0,
    "time": "2024-08-13T03:45:12+08:00"
}
```



如果有病，拿到detection_info_id去请求后端/ai/alert接口（文档详见apifox）