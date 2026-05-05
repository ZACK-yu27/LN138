# -*- coding: utf-8 -*-
"""
照片处理网页应用 - Flask后端
提供图片上传、处理和下载功能
"""

import os
import uuid
import math
import tempfile
from flask import Flask, render_template, request, jsonify, send_file, after_this_request
from PIL import Image

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024

TEMP_DIR = tempfile.mkdtemp()


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_size(file):
    """获取文件大小"""
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    return size


def generate_unique_filename(original_filename):
    """生成唯一文件名"""
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'jpg'
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    return unique_name


@app.route('/')
def index():
    """渲染主页面"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_image():
    """处理图片上传"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '没有选择文件'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'success': False, 'error': '未选择文件'}), 400

        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': '不支持的文件格式'}), 400

        file_size = get_file_size(file)
        if file_size > MAX_FILE_SIZE:
            return jsonify({'success': False, 'error': '文件大小超过10MB限制'}), 400

        unique_filename = generate_unique_filename(file.filename)
        filepath = os.path.join(TEMP_DIR, unique_filename)
        file.save(filepath)

        with Image.open(filepath) as img:
            width, height = img.size

        return jsonify({
            'success': True,
            'filename': unique_filename,
            'width': width,
            'height': height
        })

    except Exception as e:
        return jsonify({'success': False, 'error': f'上传失败: {str(e)}'}), 500


@app.route('/process', methods=['POST'])
def process_image():
    """处理图片"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        process_type = data.get('processType')

        if not filename or not process_type:
            return jsonify({'success': False, 'error': '缺少必要参数'}), 400

        source_path = os.path.join(TEMP_DIR, filename)

        if not os.path.exists(source_path):
            return jsonify({'success': False, 'error': '文件不存在，请重新上传'}), 404

        with Image.open(source_path) as img:
            original_mode = img.mode
            processed_img = img.copy()

            if process_type == 'grayscale':
                processed_img = processed_img.convert('L')

            elif process_type == 'scale':
                scale_value = data.get('scaleValue', 100)
                if not isinstance(scale_value, (int, float)) or scale_value < 10 or scale_value > 500:
                    return jsonify({'success': False, 'error': '缩放比例必须在10-500之间'}), 400
                
                width, height = processed_img.size
                scale_factor = scale_value / 100.0
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                processed_img = processed_img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            elif process_type == 'flip':
                processed_img = processed_img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

            elif process_type == 'emboss':
                emboss_depth = data.get('embossDepth', 5)
                emboss_direction = data.get('embossDirection', 0)
                
                if not isinstance(emboss_depth, int) or emboss_depth < 1 or emboss_depth > 10:
                    return jsonify({'success': False, 'error': '浮雕深度必须在1-10之间'}), 400
                
                width, height = processed_img.size
                original_mode = processed_img.mode
                
                if original_mode != 'L':
                    processed_img = processed_img.convert('L')
                
                pixels = processed_img.load()
                output_img = Image.new('L', (width, height))
                output_pixels = output_img.load()
                
                angle_rad = math.radians(emboss_direction + 45)
                dx = int(round(emboss_depth * math.cos(angle_rad)))
                dy = int(round(emboss_depth * math.sin(angle_rad)))
                
                for y in range(height):
                    for x in range(width):
                        x1 = max(0, min(width - 1, x - dx))
                        y1 = max(0, min(height - 1, y - dy))
                        x2 = max(0, min(width - 1, x + dx))
                        y2 = max(0, min(height - 1, y + dy))
                        
                        val_center = pixels[x, y]
                        val_x = pixels[x1, y1]
                        
                        diff = val_center - val_x
                        new_val = 128 + diff * emboss_depth
                        new_val = max(0, min(255, new_val))
                        
                        output_pixels[x, y] = new_val
                
                if original_mode == 'RGB':
                    output_img = output_img.convert('RGB')
                elif original_mode == 'RGBA':
                    output_img = output_img.convert('RGBA')
                
                processed_img = output_img

            else:
                return jsonify({'success': False, 'error': '未知的处理类型'}), 400

            base_name = os.path.splitext(filename)[0]
            ext = os.path.splitext(filename)[1][1:] or 'png'
            output_filename = f"{base_name}_{process_type}.{ext}"
            output_path = os.path.join(TEMP_DIR, output_filename)

            if processed_img.mode in ('RGBA', 'LA') or (processed_img.mode == 'P' and 'transparency' in processed_img.info):
                processed_img = processed_img.convert('RGBA')
                output_filename = f"{base_name}_{process_type}.png"
                output_path = os.path.join(TEMP_DIR, output_filename)
                processed_img.save(output_path, 'PNG')
            else:
                processed_img.save(output_path)

        return jsonify({
            'success': True,
            'filename': output_filename,
            'processType': process_type
        })

    except Exception as e:
        return jsonify({'success': False, 'error': f'处理失败: {str(e)}'}), 500


@app.route('/download/<filename>')
def download_image(filename):
    """下载处理后的图片"""
    try:
        filepath = os.path.join(TEMP_DIR, filename)

        if not os.path.exists(filepath):
            return jsonify({'success': False, 'error': '文件不存在'}), 404

        return send_file(
            filepath,
            as_attachment=True,
            download_name=f"processed_{filename}"
        )

    except Exception as e:
        return jsonify({'success': False, 'error': f'下载失败: {str(e)}'}), 500


@app.route('/temp/<filename>')
def get_temp_image(filename):
    """获取临时图片用于预览"""
    try:
        filepath = os.path.join(TEMP_DIR, filename)

        if not os.path.exists(filepath):
            return '', 404

        return send_file(filepath)

    except Exception as e:
        return '', 500


@app.route('/cleanup', methods=['POST'])
def cleanup_temp():
    """清理临时文件"""
    try:
        data = request.get_json()
        filename = data.get('filename')

        if filename:
            filepath = os.path.join(TEMP_DIR, filename)
            if os.path.exists(filepath):
                os.remove(filepath)

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)