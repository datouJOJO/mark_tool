# coding=utf-8
import os
import cv2
import torch
import torch.nn as nn
import numpy as np
import json
from statistics import mode

data = {
    'Anger': 0,
    'Disgust': 0,
    'Fear': 0,
    'Happy': 0,
    'Surprise': 0,
    'Sad': 0,
    'Neutral': 0,
    'Unknown': 0
}


def preprocess_input(images):
    """ preprocess input by substracting the train mean
    # Arguments: images or image of any shape
    # Returns: images or image with substracted train mean (129)
    """
    images = images / 255.0
    return images


def gaussian_weights_init(m):
    classname = m.__class__.__name__
    # 字符串查找find，找不到返回-1，不等-1即字符串中含有该字符
    if classname.find('Conv') != -1:
        m.weight.data.normal_(0.0, 0.04)


class FaceCNN(nn.Module):
    # 初始化网络结构
    def __init__(self):
        super(FaceCNN, self).__init__()

        # 第一次卷积、池化
        self.conv1 = nn.Sequential(
            nn.Conv2d(in_channels=1, out_channels=64, kernel_size=3, stride=1, padding=1),  # 卷积层
            nn.BatchNorm2d(num_features=64),  # 归一化
            nn.RReLU(inplace=True),  # 激活函数
            nn.MaxPool2d(kernel_size=2, stride=2),  # 最大值池化
        )

        # 第二次卷积、池化
        self.conv2 = nn.Sequential(
            nn.Conv2d(in_channels=64, out_channels=128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(num_features=128),
            nn.RReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )

        # 第三次卷积、池化
        self.conv3 = nn.Sequential(
            nn.Conv2d(in_channels=128, out_channels=256, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(num_features=256),
            nn.RReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )

        # 参数初始化
        self.conv1.apply(gaussian_weights_init)
        self.conv2.apply(gaussian_weights_init)
        self.conv3.apply(gaussian_weights_init)

        # 全连接层
        self.fc = nn.Sequential(
            nn.Dropout(p=0.2),
            nn.Linear(in_features=256 * 6 * 6, out_features=4096),
            nn.RReLU(inplace=True),
            nn.Dropout(p=0.5),
            nn.Linear(in_features=4096, out_features=1024),
            nn.RReLU(inplace=True),
            nn.Linear(in_features=1024, out_features=256),
            nn.RReLU(inplace=True),
            nn.Linear(in_features=256, out_features=7),
        )

    # 前向传播
    def forward(self, x):
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        # 数据扁平化
        x = x.view(x.shape[0], -1)
        y = self.fc(x)
        return y


def machine_mark(video_dir, video_name):
    emotion_mode = ''
    labels = []
    detection_model_path = 'haarcascade_frontalface_default.xml'
    classification_model_path = 'model_net.pkl'
    frame_window = 10
    emotion_labels = {0: 'Angry', 1: 'Disgust', 2: 'Fear', 3: 'Happy', 4: 'Sad', 5: 'Surprise', 6: 'Neutral'}
    # 加载人脸检测模型
    face_detection = cv2.CascadeClassifier(detection_model_path)

    # 加载表情识别
    emotion_classifier = torch.load(classification_model_path)

    emotion_window = []

    video_capture = cv2.VideoCapture(video_dir)

    while video_capture.isOpened():
        # 读取一帧
        ret, frame = video_capture.read()
        if ret:
            frame = frame.copy()
            # 获得灰度图，并且在内存中创建一个图像对象
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # 获取当前帧中的全部人脸
            faces = face_detection.detectMultiScale(gray, 1.3, 5)
            # 对于所有发现的人脸
            for (x, y, w, h) in faces:
                # 在脸周围画一个矩形框，(255,0,0)是颜色，2是线宽
                # 获取人脸图像
                face = gray[y:y + h, x:x + w]
                try:
                    # shape变为(48,48)
                    face = cv2.resize(face, (48, 48))
                except:
                    continue

                # 扩充维度，shape变为(1,48,48,1)
                # 将（1，48，48，1）转换成为(1,1,48,48)
                face = np.expand_dims(face, 0)
                face = np.expand_dims(face, 0)
                # 人脸数据归一化，将像素值从0-255映射到0-1之间
                face = preprocess_input(face)
                new_face = torch.from_numpy(face)
                new_new_face = new_face.float().requires_grad_(False)

                # 调用我们训练好的表情识别模型，预测分类
                emotion_arg = np.argmax(emotion_classifier.forward(new_new_face).detach().numpy())
                emotion = emotion_labels[emotion_arg]

                emotion_window.append(emotion)

                if len(emotion_window) >= frame_window:
                    emotion_window.pop(0)

                try:
                    # 获得出现次数最多的分类
                    emotion_mode = mode(emotion_window)
                except:
                    continue

                # 在矩形框上部，输出分类文字
                labels.append(emotion_mode)

                cv2.rectangle(frame, (x, y), (x + w, y + h), (84, 255, 159), 2)
                cv2.putText(frame, emotion_mode, (x + 30, y + 30),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (255, 0, 255),
                            2)
                cv2.imshow('recognized machine', frame)

            if len(labels) == 0:
                labels.append(emotion_mode)
            else:
                if not emotion_mode in labels:
                    labels.append(emotion_mode)

        if cv2.waitKey(5) & 0xFF == 27:
            break

        if not ret:
            break

    res = data
    for i in labels:
        res[i] = 1

    json_res = json.dumps(res, sort_keys=True, indent=4, separators=(',', ':'))
    filename = 'machineTag/' + video_name + '.json'
    # filename = video_name + '.json'

    with open(filename, 'w') as f:
        f.write(json_res)
    for i in labels:
        res[i] = 0
    video_capture.release()
    cv2.destroyAllWindows()


def test_opencv(video_dir):
    capture = cv2.VideoCapture(video_dir)

    while capture.isOpened():
        ok, frame = capture.read()
        if not ok:
            break
        cv2.imshow('deme', frame)
        if cv2.waitKey(5) & 0xFF == 27:
            break

    capture.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    machine_mark('test.mp4', 'test.mp4')
    # test_opencv('test.mp4')
