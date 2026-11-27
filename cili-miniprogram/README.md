# 刺梨农事助手 — 微信小程序

面向个体户农民与买家的刺梨（Rosa roxburghii）微信小程序首版。  
原生小程序结构，全部页面可用模拟数据跑通；AI / 定位 / 相机能力以 Mock API 占位。

## 功能一览

| Tab | 能力 |
| --- | --- |
| 首页 | 定位、种植方案、拍照诊病、语音问答、今日农事建议 |
| 行情 | 视觉分级估价、对版验货、去挂售、附近行情 |
| 商城 | 农药/肥料/树苗/刺梨产品分类、比价与用量、下单 |
| 我的 | 订单入口、私信、农民/买家身份切换 |

子页面：诊病结果、对版验货、商品详情、订单列表、私信、种植方案、挂售。

## 用微信开发者工具预览

1. 安装并打开 [微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)。
2. **导入项目** → 目录选择本仓库下的：
   ```
   cili-miniprogram/
   ```
3. AppID 可选「测试号」或使用项目内 `touristappid`（游客模式即可预览 UI）。
4. 打开后即可在模拟器切换四个 Tab，点击拍照/语音会走 Mock 流程（真机需授权相机/麦克风）。
5. Mock 接口形状见 `utils/mock-api.js`，静态数据见 `data/mock.js`。

## 目录结构

```
cili-miniprogram/
├── app.js / app.json / app.wxss
├── project.config.json
├── data/mock.js
├── utils/mock-api.js
├── images/          # Tab 图标
└── pages/
    ├── home / market / mall / profile
    ├── diagnose-result / verify / product-detail
    ├── orders / messages / planting-plan / listing
```

## 说明

- 本目录独立于博客前后端，不改动 `frontend/`、`backend/`。
- 接真服务时，将 `utils/mock-api.js` 中各函数替换为 `wx.request` 即可，请求/响应字段已写在文件头注释中。
