# 照片处理工具

一个基于Web的照片处理应用程序，支持图片上传、多种图像处理功能和下载功能。

## 功能特点

- **图片上传**: 支持点击选择或拖拽上传
- **图片处理**:
  - 黑白照片 - 转换为灰度图像
  - 放大 - 120% 尺寸放大
  - 缩小 - 80% 尺寸缩小
  - 左右互换 - 水平翻转图片
- **实时预览**: 上传后可预览原图，处理后显示结果
- **图片下载**: 一键下载处理后的图片
- **响应式设计**: 适配桌面端和移动端

## 技术栈

- **后端**: Flask (Python Web框架)
- **图片处理**: Pillow (PIL)
- **前端**: HTML5 + CSS3 + JavaScript

## 项目结构

```
photo_processor/
├── app.py              # Flask后端应用
├── requirements.txt    # Python依赖
├── README.md          # 说明文档
├── SPEC.md            # 规范文档
├── templates/
│   └── index.html     # 前端页面模板
└── static/
    ├── style.css      # 样式文件
    └── app.js         # 前端脚本
```

## 环境要求

- Python 3.8 或更高版本
- 支持的操作系统: Windows, macOS, Linux

## 安装步骤

1. **克隆或下载项目**

2. **创建虚拟环境（推荐）**

   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **安装依赖**

   ```bash
   pip install -r requirements.txt
   ```

## 运行应用

1. **启动服务器**

   ```bash
   python app.py
   ```

2. **访问应用**

   打开浏览器访问: http://localhost:5000

## 使用说明

### 上传图片

1. 点击上传区域的虚线框或直接将图片拖拽到上传区域
2. 支持的格式: JPG, JPEG, PNG, GIF, BMP, WEBP
3. 文件大小限制: 10MB

### 处理图片

1. 上传图片后，下方的处理按钮将变为可用状态
2. 点击需要的处理功能按钮:
   - 黑白照片 - 将图片转换为灰度
   - 放大 - 将图片放大120%
   - 缩小 - 将图片缩小80%
   - 左右互换 - 水平翻转图片
3. 处理完成后，右侧区域将显示处理结果

### 下载图片

1. 处理完成后，点击"下载处理后的图片"按钮
2. 图片将自动下载到本地

## 错误处理

- 不支持的文件格式会提示错误信息
- 文件过大时会提示文件大小限制
- 上传或处理失败时会显示错误信息并允许重试

## 注意事项

1. 所有图片数据存储在临时目录中，关闭应用后会清除
2. 请确保上传的图片格式正确
3. 建议使用现代浏览器（Chrome, Firefox, Edge, Safari）以获得最佳体验

## 许可证

MIT License