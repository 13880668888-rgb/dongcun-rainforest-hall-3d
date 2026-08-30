# 可编辑 Blender 源模型

当前仓库已经保存参数化建模代码、OBJ、GLB白模和由Blender 4.0.2实际生成的
可编辑源模型：

`models/source/rainforest-hall-white-v1.blend`

需要重新生成时执行：

```bash
blender --background --python src/blender/build_white_model.py
```

运行前可执行：

```bash
python3 src/blender/build_white_model.py --check
```

屋顶高度与坡度、柱网、斜撑位置、右侧门洞高度和生命树均为可调占位，不作为施工尺寸。
