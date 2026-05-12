import os
import io
import sqlite3
import csv
from datetime import datetime
import numpy as np
from PIL import Image
from flask import Flask, render_template, request, jsonify, Response
import tensorflow as tf
import cv2
import base64
import numpy as np
import tensorflow as tf

# 基础路径配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
MODEL_PATH = os.path.join(BASE_DIR, 'phishing_cv_model.keras')
DB_PATH = os.path.join(BASE_DIR, 'history.db')

app = Flask(__name__, template_folder=TEMPLATE_DIR)


# ----------------- 数据库初始化 -----------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
              CREATE TABLE IF NOT EXISTS predictions
              (
                  id
                  INTEGER
                  PRIMARY
                  KEY
                  AUTOINCREMENT,
                  filename
                  TEXT,
                  result
                  TEXT,
                  confidence
                  TEXT,
                  timestamp
                  TEXT
              )
              ''')
    conn.commit()
    conn.close()


init_db()

# ----------------- 加载模型 -----------------
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    print(f"✅ 检测模型加载成功！路径为: {MODEL_PATH}")
except Exception as e:
    model = None
    print(f"❌ 警告：未找到模型。报错详情: {e}")


def preprocess_image(img_bytes):
    img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
    img = img.resize((224, 224))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    return img_array


# ==========================================
# 🌟 核心科技：Grad-CAM 热力图生成引擎 (全网最强除虫净版)
def generate_gradcam(img_bytes, model):
    try:
        # 1. 读取原图并强制转为 3 通道 (彻底解决透明图、黑白图导致的报错)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None: return None

        # 拿到最纯净的宽度和高度
        h, w = img.shape[:2]
        original_size = (int(w), int(h))  # 👈 预存好 OpenCV 喜欢的尺寸格式

        # 2. 图像预处理
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_resized = cv2.resize(img_rgb, (224, 224))
        img_tensor = tf.cast(tf.expand_dims(img_resized, axis=0), tf.float32)

        # 3. 寻找 MobileNetV2 基础模型
        base_model = None
        for layer in model.layers:
            if isinstance(layer, tf.keras.Model) and layer.name != 'data_augmentation':
                base_model = layer
                break
        if base_model is None: return None

        # 4. 构建梯度模型并计算
        last_conv_layer = base_model.get_layer('out_relu')
        grad_model = tf.keras.Model(inputs=base_model.inputs, outputs=[last_conv_layer.output, base_model.output])

        with tf.GradientTape() as tape:
            x = img_tensor
            # 跳过预处理层，直接把输入传给基础模型
            for layer in model.layers:
                if layer == base_model: break
                if layer.__class__.__name__ == 'InputLayer': continue
                x = layer(x, training=False)

            conv_outputs, base_out = grad_model(x, training=False)
            tape.watch(conv_outputs)

            # 后半部分分类层逻辑
            y = base_out
            found = False
            for layer in model.layers:
                if layer == base_model: found = True; continue
                if found: y = layer(y, training=False)
            loss = y[:, 0]

        # 5. 生成热力图矩阵
        grads = tape.gradient(loss, conv_outputs)
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        conv_outputs = conv_outputs  # 👈 关键点：去掉批次维度
        heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)
        heatmap = tf.maximum(heatmap, 0) / (tf.math.reduce_max(heatmap) + 1e-10)

        # 6. 最终融合 (🌟 核心修复：使用预存好的 original_size，绝对不报错)
        heatmap_np = heatmap.numpy()
        heatmap_res = cv2.resize(heatmap_np, original_size)
        heatmap_res = np.uint8(255 * heatmap_res)
        heatmap_color = cv2.applyColorMap(heatmap_res, cv2.COLORMAP_JET)

        # 此时 img 和 heatmap_color 都是 3 通道彩色图，且尺寸毫厘不差
        superimposed_img = cv2.addWeighted(img, 0.6, heatmap_color, 0.4, 0)
        _, buffer = cv2.imencode('.jpg', superimposed_img)
        return base64.b64encode(buffer).decode('utf-8')

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ 热力图引擎终极报错: {e}")
        return None
@app.route('/')
def index():
    return render_template('index.html')


# ====================== 接口 1：单张识别 (保持原有逻辑) ======================
# ====================== 接口 1：单张识别 (修复报错版) ======================
@app.route('/api/detect', methods=['POST'])
def predict():
    # 1. 拦截异常情况（注意：这里千万不能漏掉 return！）
    if 'file' not in request.files:
        return jsonify({'error': '未收到文件'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '文件名为空'}), 400

    try:
        img_bytes = file.read()

        # 2. 模型推理
        processed_img = preprocess_image(img_bytes)
        raw_pred = model(processed_img, training=False)
        prediction = float(np.squeeze(raw_pred.numpy()))

        # 3. 判定逻辑
        is_phishing = prediction > 0.5
        result_type = "phishing" if is_phishing else "normal"
        result_text = "钓鱼邮件 (Phishing)" if is_phishing else "正常邮件 (Normal)"

        conf_num = prediction if is_phishing else (1.0 - prediction)
        confidence_str = f"{conf_num * 100:.1f}%"
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 4. 生成热力图
        raw_heatmap_b64 = generate_gradcam(img_bytes, model)
        heatmap_base64 = f"data:image/jpeg;base64,{raw_heatmap_b64}" if raw_heatmap_b64 else ""

        # 5. 模拟风险标签
        risk_tags = ["仿冒标题", "可疑按钮", "异常表单"] if is_phishing else ["未见异常"]

        # 6. 写入数据库并获取最新 ID
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO predictions (filename, result, confidence, timestamp) VALUES (?, ?, ?, ?)",
                  (file.filename, result_text, confidence_str, current_time))
        new_id = c.lastrowid
        conn.commit()
        conn.close()

        # 7. 成功完成，返回完整数据（千万不能漏掉 return！）
        return jsonify({
            'status': 'success',
            'id': new_id,
            'result_type': result_type,
            'result_text': result_text,
            'confidence': confidence_str,
            'heatmap_base64': heatmap_base64,
            'risk_tags': risk_tags,
            'process_time': current_time
        })

    except Exception as e:
        print(f"❌ 识别失败: {e}")
        # 8. 代码如果在 try 里面报错了，也必须 return 回去！
        return jsonify({'error': str(e)}), 500


# ====================== 接口 3：历史记录 (增加 result_type 供前端判断颜色) ======================
@app.route('/history', methods=['GET'])
def get_history():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        # 👈 修改：SELECT 语句中加上 id，按 id 倒序
        c.execute("SELECT id, filename, result, confidence, timestamp FROM predictions ORDER BY id DESC LIMIT 15")
        rows = c.fetchall()
        conn.close()

        history_list = []
        for row in rows:
            res_type = "phishing" if "Phishing" in row[2] else "normal"
            history_list.append({
                'id': row,             # 👈 新增：把数据库 ID 塞进列表
                'filename': row[1],
                'result_text': row[2],
                'result_type': res_type,
                'confidence': row[3],
                'timestamp': row[4]
            })
        return jsonify({'history': history_list})
    except Exception as e:
        return jsonify({'error': str(e)})


# ====================== 接口 4：删除单条记录 ======================
@app.route('/delete_history', methods=['POST'])
def delete_history():
    try:
        data = request.get_json()
        record_id = data.get('id')
        if not record_id:
            return jsonify({'error': '未提供记录ID'}), 400

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        # 从数据库中硬删除该条记录
        c.execute("DELETE FROM predictions WHERE id = ?", (record_id,))
        conn.commit()
        conn.close()

        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
# ====================== 接口 2：批量识别 (独立逻辑修复版) ======================
# ====================== 接口 2：批量识别 ======================
@app.route('/api/detect_batch', methods=['POST'])
def predict_batch():
    # 1. 核心：用 getlist 拿到前端发来的文件数组
    files = request.files.getlist('file')

    if not files or len(files) == 0 or files[0].filename == '':
        return jsonify({'error': '未收到任何文件'}), 400

    batch_results = []
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # 2. 循环处理每一个文件
        for f in files:
            img_bytes = f.read()
            if not img_bytes: continue

            # 模型预处理与推理
            processed_img = preprocess_image(img_bytes)
            raw_pred = model(processed_img, training=False)
            prediction = float(np.squeeze(raw_pred.numpy()))

            # 判定结论
            is_phishing = prediction > 0.5
            result_type = "phishing" if is_phishing else "normal"
            result_text = "钓鱼邮件 (Phishing)" if is_phishing else "正常邮件 (Normal)"

            conf_num = prediction if is_phishing else (1.0 - prediction)
            confidence_str = f"{conf_num * 100:.1f}%"
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 存入数据库
            c.execute("INSERT INTO predictions (filename, result, confidence, timestamp) VALUES (?, ?, ?, ?)",
                      (f.filename, result_text, confidence_str, now))

            batch_results.append({
                'filename': f.filename,
                'result_type': result_type,
                'confidence': confidence_str
            })

        conn.commit()
        conn.close()

        # 3. 返回成功信息与处理总数
        return jsonify({'status': 'success', 'total': len(batch_results), 'results': batch_results})

    except Exception as e:
        print(f"❌ 批量识别出错: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ====================== 接口 3：历史记录与导出 ======================
@app.route('/export_csv', methods=['GET'])
def export_csv():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, filename, result, confidence, timestamp FROM predictions ORDER BY id DESC")
        rows = c.fetchall()
        conn.close()

        si = io.StringIO()
        cw = csv.writer(si)
        cw.writerow(['ID', '文件名', '结果', '置信度', '时间'])
        cw.writerows(rows)
        output = '\ufeff' + si.getvalue()
        return Response(output, mimetype="text/csv",
                        headers={"Content-disposition": "attachment; filename=history.csv"})
    except Exception as e:
        return str(e)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True, threaded=False)