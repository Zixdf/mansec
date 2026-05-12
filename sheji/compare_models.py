import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2, VGG16, ResNet50
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout, Input
from tensorflow.keras.models import Model
from sklearn.metrics import f1_score, accuracy_score
import time
import os
import numpy as np

# 1. 全局严格控制变量
IMG_SIZE = (224, 224)
BATCH_SIZE = 16  # 为了防止 VGG16 和 ResNet50 爆显存，统一调小到 16
EPOCHS = 10  # 实验跑 10 轮就能看出明显差距，节省你的时间


# 2. 准备统一的数据集管道
def get_datasets():
    print("🚀 正在加载统一下游数据集...")
    train_ds = tf.keras.utils.image_dataset_from_directory(
        'dataset/train', validation_split=0.2, subset="training",
        seed=42, image_size=IMG_SIZE, batch_size=BATCH_SIZE
    )
    val_ds = tf.keras.utils.image_dataset_from_directory(
        'dataset/train', validation_split=0.2, subset="validation",
        seed=42, image_size=IMG_SIZE, batch_size=BATCH_SIZE
    )
    AUTOTUNE = tf.data.AUTOTUNE
    return train_ds.cache().prefetch(buffer_size=AUTOTUNE), val_ds.cache().prefetch(buffer_size=AUTOTUNE)


# 3. 核心训练与构建逻辑
def build_and_train(model_name, base_model_class, preprocess_func, train_ds, val_ds):
    print(f"\n{'=' * 50}\n开始训练并评估模型: {model_name}\n{'=' * 50}")

    # 加载骨干网络，冻结底层特征提取层
    base_model = base_model_class(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    base_model.trainable = True
    for layer in base_model.layers[:-20]:
        layer.trainable = False

    # 组装网络
    inputs = Input(shape=(224, 224, 3))
    x = preprocess_func(inputs)  # 使用各自专属的预处理
    x = base_model(x, training=False)
    x = GlobalAveragePooling2D()(x)
    x = Dense(128, activation='relu')(x)
    x = Dropout(0.4)(x)
    predictions = Dense(1, activation='sigmoid')(x)

    model = Model(inputs=inputs, outputs=predictions)
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
                  loss='binary_crossentropy', metrics=['accuracy'])

    # 训练模型
    model.fit(train_ds, epochs=EPOCHS, validation_data=val_ds, verbose=1)

    # 存盘计算大小
    model_path = f'{model_name}_temp.keras'
    model.save(model_path)
    return model, model_path


# 4. 测评提取指标
def evaluate_metrics(model_name, model, model_path, val_ds):
    print(f"\n📊 正在计算 {model_name} 的论文指标...")

    params_m = model.count_params() / 1e6
    model_size_mb = os.path.getsize(model_path) / (1024 * 1024)

    # 取一批数据测试单张推理速度
    sample_images, _ = next(iter(val_ds))
    model.predict(sample_images[:1], verbose=0)  # 预热

    infer_start = time.time()
    for _ in range(100):
        model.predict(sample_images[:1], verbose=0)
    inference_time_ms = ((time.time() - infer_start) / 100) * 1000

    # 计算 F1 和 Accuracy
    y_true, y_pred_probs = [], []
    for images, labels in val_ds:
        preds = model.predict(images, verbose=0)
        y_true.extend(labels.numpy())
        y_pred_probs.extend(preds)

    y_pred = (np.array(y_pred_probs) > 0.5).astype(int)
    acc = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)

    print(f"\n✅ {model_name} 最终成绩单 (可直接填入论文表 6-1)：")
    print(f"参数量: {params_m:.2f} M")
    print(f"模型大小: {model_size_mb:.2f} MB")
    print(f"单张推理耗时: {inference_time_ms:.2f} ms")
    print(f"准确率 (Accuracy): {acc * 100:.2f}%")
    print(f"F1-Score: {f1 * 100:.2f}%\n")


# 5. 主执行入口
if __name__ == "__main__":
    train_ds, val_ds = get_datasets()

    models_dict = {
        'MobileNetV2': (MobileNetV2, tf.keras.applications.mobilenet_v2.preprocess_input),
        'ResNet50': (ResNet50, tf.keras.applications.resnet50.preprocess_input),
        'VGG16': (VGG16, tf.keras.applications.vgg16.preprocess_input)
    }

    for name, (base_class, prep_func) in models_dict.items():
        trained_model, saved_path = build_and_train(name, base_class, prep_func, train_ds, val_ds)
        evaluate_metrics(name, trained_model, saved_path, val_ds)

        # 跑完清理掉临时模型文件，防止占用硬盘
        if os.path.exists(saved_path):
            os.remove(saved_path)

    print("🎉 所有对比实验执行完毕，请将终端输出的数据填入你的论文表格中！")