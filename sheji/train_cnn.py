import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout, RandomFlip, RandomRotation, RandomZoom, \
    RandomTranslation
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
import os

# 基础配置
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 20  # 有了数据增强，模型更不容易过拟合，可以稍微多跑几轮


def train_model():
    print("🚀 正在初始化现代 TensorFlow 数据管道...")

    # 1. 准备数据
    train_ds = tf.keras.utils.image_dataset_from_directory(
        'dataset/train',
        validation_split=0.2,
        subset="training",
        seed=42,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE
    )

    val_ds = tf.keras.utils.image_dataset_from_directory(
        'dataset/train',
        validation_split=0.2,
        subset="validation",
        seed=42,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE
    )

    # 🚀 新增性能优化：将图片放进内存缓存，利用 CPU 提前准备数据，训练速度起飞！
    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

    # 🚀 新增核心模块：数据增强流水线 (Data Augmentation)
    # 每次训练时，图片都会被随机轻微改变，让模型学会认“本质”而不是“死记硬背”
    data_augmentation = tf.keras.Sequential([
        RandomFlip("horizontal"),
        RandomRotation(0.05),  # 随机旋转一点点
        RandomZoom(0.1),  # 随机缩放 10%
        RandomTranslation(0.1, 0.1)  # 随机平移 10%
    ], name="data_augmentation")

    # 2. 构建模型：专家级微调 (Fine-tuning)
    print("🧠 正在构建并解封部分 MobileNetV2 大脑...")
    base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))

    # 解冻最后 20 层，让它专门学习邮件 UI 特征
    base_model.trainable = True
    for layer in base_model.layers[:-20]:
        layer.trainable = False

    # 组装完整的神经网络
    inputs = tf.keras.Input(shape=(224, 224, 3))

    # 🚀 将数据增强层无缝接入 (只在训练时生效，预测时会自动关闭)
    x = data_augmentation(inputs)

    # 必须加入内置的预处理层
    x = tf.keras.applications.mobilenet_v2.preprocess_input(x)

    # training=False 非常重要！保证底层的 BatchNormalization 层不被破坏
    x = base_model(x, training=False)
    x = GlobalAveragePooling2D()(x)
    x = Dense(128, activation='relu')(x)
    x = Dropout(0.4)(x)
    predictions = Dense(1, activation='sigmoid')(x)

    model = Model(inputs=inputs, outputs=predictions)

    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
                  loss='binary_crossentropy',
                  metrics=['accuracy'])

    # 3. 配置智能监控回调函数
    callbacks = [
        ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, verbose=1),
        EarlyStopping(monitor='val_accuracy', patience=5, restore_best_weights=True, verbose=1)
    ]

    # 4. 执行训练
    print("🔥 开始专家级炼丹！(请盯紧 val_accuracy 的飙升)")
    model.fit(
        train_ds,
        epochs=EPOCHS,
        validation_data=val_ds,
        callbacks=callbacks
    )

    # 5. 保存结果
    model.save('phishing_cv_model.keras')
    print("🎉 模型训练完美结束！已保存为 phishing_cv_model.keras")


if __name__ == "__main__":
    if not os.path.exists('dataset/train'):
        print("请确保已在 dataset/train 下准备好图片分类文件夹。")
    else:
        train_model()