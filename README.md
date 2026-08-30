# 东村半日闲｜雨林厅 3D 模型

本仓库以已确认尺寸建立雨林厅白模：

- 净宽 14.80 米
- 净长 25.00 米，全长等宽
- 本阶段高度 4.00 米
- A 门厅玻璃入口框架净宽 4.80 米
- 双扇门全开净宽 2.20 米

旧的 13 米、12 米、24.5 米及“中段收窄”数据已作废。

## 直接查看

- `models/exports/rainforest-hall-white-v1.glb`：网页及多数三维查看器
- `models/exports/rainforest-hall-white-v1.obj`：酷家乐、SketchUp、Blender 等软件的交换模型
- `models/source/rainforest-hall-white-v1.blend`：Blender 4.0.2实际生成的可编辑源模型
- `docs/dimensions/white-model-v1.json`：机器校验尺寸报告

本地打开网页预览：

```bash
python3 -m http.server 8000
```

然后访问 `http://localhost:8000/web-preview/`。

## 重新生成和检查

```bash
python3 -m unittest discover -s tests -v
python3 scripts/build_white_model.py --output-root .
python3 src/blender/build_white_model.py --check
```

在已安装 Blender 的电脑上生成可编辑源模型：

```bash
blender --background --python src/blender/build_white_model.py
```

输出：`models/source/rainforest-hall-white-v1.blend`

## 当前阶段

这是尺寸白模，不是最终效果图。沙地、左侧半封闭可开关界面、原右侧门洞、
坡屋顶和入口关系已进入模型；屋顶精确高度、柱网、斜撑、消防机电和生命树
必须等待现场复测后锁定。

## V2 材质概念模型

V2 替代 V1 作为材质概念评审入口，但不替代 V1 的锁定尺寸白模基线；
`rainforest-hall-white-v1.blend` 保留且不得覆盖。V2 由 Blender 5.1.2
直接打开该 V1 文件后增量生成：

- `models/source/rainforest-hall-material-concept-v2.blend`：可编辑源文件
- `models/exports/rainforest-hall-material-concept-v2.glb`：可旋转预览模型
- `renders/concept-v2/entrance-to-rainforest-hall-v2.png`：入口看向雨林厅
- `renders/concept-v2/middle-life-tree-v2.png`：中部生命树概念
- `renders/concept-v2/rainforest-hall-to-banquet-hall-v2.png`：看向宴会厅方向
- `docs/dimensions/material-concept-v2.json`：Blender 独立重开校验报告

V2 保留 2.20 米顾客主通道，不设置正餐或宴会桌阵。屋顶与主体结构、
右侧原门洞、生命树、现场相关家具/灯具位置及宴会厅过渡导向框仍是复测前
可调占位，不得作为施工尺寸。
