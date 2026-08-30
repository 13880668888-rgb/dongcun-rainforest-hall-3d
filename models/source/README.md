# 可编辑 Blender 源模型

当前仓库已经保存参数化建模代码、OBJ 与 GLB 白模。由于自动执行环境没有安装
Blender，二进制 `.blend` 文件需要在装有 Blender 的电脑上执行以下命令生成：

```bash
blender --background --python src/blender/build_white_model.py
```

生成文件：

`models/source/rainforest-hall-white-v1.blend`

运行前可执行：

```bash
python3 src/blender/build_white_model.py --check
```

屋顶高度与坡度、柱网、斜撑位置、右侧门洞高度和生命树均为可调占位，不作为施工尺寸。
