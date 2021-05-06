# coding=utf-8
import os
import json
import sys
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QApplication, QFileDialog
from PyQt5.QtCore import QTimer, QCoreApplication, QThread, pyqtSignal

from analy import MainWindow as MainWindow4
# from machine import MainWindow as MainWindow3
from manual_marking import Ui_MainWindow
from pre import MainWindow as MainWindow5
from machine import *
# from test import MainWindow as MainWindow1
import cv2
import time

is_play = True
is_stop = False
is_move = False

curFrame = 0
totalFrame = 0
# 视频开始的位置
videoStart = 0

# 选择列表下的操作
# 以字典的形式保存文件名称
videoName = {}
# 控制当前播放的视频
curVideo = ''
# 如果点击了换片的话
is_change = False
# 视频是否结束
is_finish = False
# 当前选择的行数
curVideoIndex = 0

name_list = []
# 写入文件的json文件
jsonRes = None
tagJson = None
# 文件tagging记录
tagRes = {}
# 保存的tag文件
tagFile = ''
# tag记录文件
tagRFile = ''

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

isAnger = False
isDisgust = False
isFear = False
isHappy = False
isSurprise = False
isSad = False
isNeutral = False

# 如果是一个不知道的
isUnknown = False

# 当前的根文件夹路径
dir_path = ''
# 对于没有标注的文件 文件列表颜色标红
# 对于点击了确认按钮的文件标绿
# 存放标记结果的文件夹
docPath = ''

# 记录一下已经标签的字符串
tagString = ''


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        # 添加鼠标点击事件
        # 菜单项的点击事件是triggered
        self.backToWelcome.triggered.connect(self.jump_to_1)
        self.backToMachine.triggered.connect(self.jump_to_2)
        self.backToAnalysis.triggered.connect(self.jump_to_3)

        # 按钮点击事件
        self.selectVideo.clicked.connect(self.selectVideoDocument)
        self.playVideoB.clicked.connect(self.playVideo)
        self.pauseVideoB.clicked.connect(self.pauseVideo)

        # 播放列表
        self.play_list.doubleClicked.connect(self.selectV)
        self.preVideoB.clicked.connect(self.preVideo)
        self.nextVideoB.clicked.connect(self.nextVideo)
        # 进度条
        self.videoSlider.setMinimum(0)

        # 最大值晚点设置
        self.videoSlider.valueChanged.connect(self.setPlayPlace)

        # 情感标注
        # 添加标签
        self.isAnger.clicked.connect(self.is_anger)
        self.isDisgust.clicked.connect(self.is_disgust)
        self.isSad.clicked.connect(self.is_sad)
        self.isNeutral.clicked.connect(self.is_neutral)
        self.isUnknow.clicked.connect(self.is_unknown)
        self.isFear.clicked.connect(self.is_fear)
        self.isSurprise.clicked.connect(self.is_surprise)
        self.isHappy.clicked.connect(self.is_happy)

        # 提交
        self.subVideo.clicked.connect(self.submit)

        # 给标记列表添加一个单击响应函数
        self.mark_list.clicked.connect(self.remove_mark)

        #一键机器标注
        self.machine_reg.clicked.connect(self.machineReg)


    #机器标注
    def machineReg(self):
        # 机器标注时就暂停当前的视频
        global is_stop
        global is_play

        is_play = False
        is_stop = True
        machine_mark(curVideo, self.play_list.item(curVideoIndex).text())

    def selectV(self):
        global curVideo, curVideoIndex
        item = self.play_list.currentItem()
        curVideoIndex = self.play_list.currentRow()
        # print(item.text())
        curVideo = videoName[item.text()]
        # print('click')
        global is_change
        is_change = True
        self.videoSlider.setValue(curFrame)
        self.mark_list.clear()
        fPath = os.path.join(docPath, item.text() + '.json')
        self.checkAndShowTag(fPath)

    def PrepSliders(self):
        self.horizontalSlider.valueChanged.connect()

    # 帮助文档
    def help(self):
        msgBox = QMessageBox(QMessageBox.NoIcon, '帮助', '视频情感数据标注系统帮助文档')
        msgBox.exec_()

    # 关于
    def about_us(self):
        msgBox = QMessageBox(QMessageBox.NoIcon, '关于', '视频情感数据标注系统')
        msgBox.setIconPixmap(QPixmap("./YYY.jpg"))
        msgBox.exec_()

    # 跳转到主界面
    def jump_to_1(self):
        self.ui_1 = MainWindow1()
        self.ui_1.show()

    # 跳转到机器标注界面
    def jump_to_2(self):
        self.ui_2 = MainWindow3()
        self.ui_2.show()

    # 跳转到分析界面
    def jump_to_3(self):
        self.ui_3 = MainWindow4()
        self.ui_3.show()

    # 跳转到机器标注界面
    def jump_to_4(self):
        self.ui_4 = MainWindow5()
        self.ui_4.show()

    # 下一条视频
    def nextVideo(self):
        allRow = self.play_list.count()
        allRow -= 1
        # 如果下一个视频没有了
        global curVideo, is_change, videoName, curVideoIndex

        if curVideoIndex + 1 > allRow:
            is_change = True
            return
        else:
            curVideoIndex += 1
            is_change = True
            curVideo = videoName[self.play_list.item(curVideoIndex).text()]
        self.mark_list.clear()
        fPath = os.path.join(docPath, self.play_list.item(curVideoIndex).text() + '.json')
        self.checkAndShowTag(fPath)

    # 上一条视频
    def preVideo(self):
        # print(index)
        # 如果下一个视频没有了
        global curVideo, is_change, videoName, curVideoIndex

        if curVideoIndex == 0:
            is_change = True
            return
        else:
            is_change = True
            curVideoIndex -= 1
            curVideo = videoName[self.play_list.item(curVideoIndex).text()]
        self.mark_list.clear()
        fPath = os.path.join(docPath, self.play_list.item(curVideoIndex).text() + '.json')
        self.checkAndShowTag(fPath)

    # 暂停
    def pauseVideo(self):
        # print('pause')
        global is_stop
        global is_play

        is_play = False
        is_stop = True

    # 播放
    def playVideo(self):
        # print('play')
        global is_stop
        global is_play

        is_play = True
        is_stop = False

    # 提交
    def submit(self):
        global name_list, cur_vid, tagRes, tagFile, tagRFile, jsonRes, tagJson
        global isUnknown, isNeutral, isSad, isSurprise, isHappy, isFear, isDisgust, isAnger

        allRow = self.mark_list.count()
        if allRow == 0:
            # print('empty')
            QMessageBox.warning(self, '错误', '您没有选择任何标签标记', QMessageBox.Yes, QMessageBox.Cancel)
            return

        tagFile = os.path.join(dir_path, 'tagResult')
        tagFile = os.path.join(tagFile, self.play_list.item(curVideoIndex).text() + '.json')
        tagData = self.readJson(tagFile)
        if isUnknown:
            tagData['Unknown'] += 1
        if isNeutral:
            tagData['Neutral'] += 1
        if isSad:
            tagData['Sad'] += 1
        if isSurprise:
            tagData['Surprise'] += 1
        if isHappy:
            tagData['Happy'] += 1
        if isFear:
            tagData['Fear'] += 1
        if isDisgust:
            tagData['Disgust'] += 1
        if isAnger:
            tagData['Anger'] += 1

        json_res = json.dumps(tagData, sort_keys=True, indent=4, separators=(',', ':'))
        self.writeJson(json_res, tagFile)

        if isUnknown:
            tagRes[self.play_list.item(curVideoIndex).text()] = 2
            self.play_list.item(curVideoIndex).setForeground(QColor('black'))
            self.play_list.item(curVideoIndex).setBackground(QColor('black'))
            isUnknown = False
        else:
            tagRes[self.play_list.item(curVideoIndex).text()] = 1
            self.play_list.item(curVideoIndex).setForeground(QColor('green'))
        jsonRes = None
        jsonRes = json.dumps(tagRes, sort_keys=True, indent=4, separators=(',', ':'))
        self.writeJson(jsonRes, tagRFile)
        # 视频标签选择
        self.mark_list.clear()
        # 标签初始化
        self.tagInit()

    def is_anger(self):
        global isAnger
        global tagString
        if isNeutral:
            megInfo = '您已经选择Neutral标签了,不能再标记anger了'
            QMessageBox.warning(self, '错误', megInfo, QMessageBox.Yes, QMessageBox.Cancel)
            return
        if isUnknown:
            megInfo = '您已经选择Unknown标签了,不能再标记anger了'
            QMessageBox.warning(self, '错误', megInfo, QMessageBox.Yes, QMessageBox.Cancel)
            return
        if isHappy:
            megInfo = '您已经选择Happy标签了,不能再标记anger了'
            QMessageBox.warning(self, '错误', megInfo, QMessageBox.Yes, QMessageBox.Cancel)
            return
        if isAnger is False:
            self.add_mark_item("Anger")
            isAnger = True
            tagString += 'Anger,'

    def is_disgust(self):
        global isDisgust
        global tagString
        if isNeutral:
            megInfo = '您已经选择Neutral标签了,不能再标记disgust了'
            QMessageBox.warning(self, '错误', megInfo, QMessageBox.Yes, QMessageBox.Cancel)
            return
        if isUnknown:
            megInfo = '您已经选择Unknown标签了,不能再标记disgust了'
            QMessageBox.warning(self, '错误', megInfo, QMessageBox.Yes, QMessageBox.Cancel)
            return
        if isHappy:
            megInfo = '您已经选择Happy标签了,不能再标记disgust了'
            QMessageBox.warning(self, '错误', megInfo, QMessageBox.Yes, QMessageBox.Cancel)
            return
        if isDisgust is False:
            self.add_mark_item("Disgust")
            isDisgust = True
            tagString += 'Disgust,'

    def is_fear(self):
        global isFear
        global tagString
        if isNeutral:
            megInfo = '您已经选择Neutral标签了,不能再标记fear了'
            QMessageBox.warning(self, '错误', megInfo, QMessageBox.Yes, QMessageBox.Cancel)
            return
        if isUnknown:
            megInfo = '您已经选择Unknown标签了,不能再标记fear了'
            QMessageBox.warning(self, '错误', megInfo, QMessageBox.Yes, QMessageBox.Cancel)
            return
        if isHappy:
            megInfo = '您已经选择Happy标签了,不能再标记fear了'
            QMessageBox.warning(self, '错误', megInfo, QMessageBox.Yes, QMessageBox.Cancel)
            return
        if isFear is False:
            self.add_mark_item("Fear")
            isFear = True
            tagString += 'Fear,'

    def is_happy(self):
        global isHappy
        global tagString
        if isNeutral:
            megInfo = '您已经选择Neutral标签了,不能再标记happy了'
            QMessageBox.warning(self, '错误', megInfo, QMessageBox.Yes, QMessageBox.Cancel)
            return
        if isUnknown:
            megInfo = '您已经选择Unknown标签了,不能再标记happy了'
            QMessageBox.warning(self, '错误', megInfo, QMessageBox.Yes, QMessageBox.Cancel)
            return
        if isSad:
            megInfo = '您已经选择Sad标签了,不能再标记happy了'
            QMessageBox.warning(self, '错误', megInfo, QMessageBox.Yes, QMessageBox.Cancel)
            return
        if isDisgust:
            megInfo = '您已经选择Disgust标签了,不能再标记happy了'
            QMessageBox.warning(self, '错误', megInfo, QMessageBox.Yes, QMessageBox.Cancel)
            return
        if isFear:
            megInfo = '您已经选择Fear标签了,不能再标记happy了'
            QMessageBox.warning(self, '错误', megInfo, QMessageBox.Yes, QMessageBox.Cancel)
            return
        if isAnger:
            megInfo = '您已经选择Anger标签了,不能再标记happy了'
            QMessageBox.warning(self, '错误', megInfo, QMessageBox.Yes, QMessageBox.Cancel)
            return
        if isHappy is False:
            self.add_mark_item("Happy")
            isHappy = True
            tagString += 'Happy,'

    def is_surprise(self):
        global isSurprise
        global tagString
        if isNeutral:
            megInfo = '您已经选择Neutral标签了,不能再标记surprise了'
            QMessageBox.warning(self, '错误', megInfo, QMessageBox.Yes, QMessageBox.Cancel)
            return
        if isUnknown:
            megInfo = '您已经选择Unknown标签了,不能再标记surprise了'
            QMessageBox.warning(self, '错误', megInfo, QMessageBox.Yes, QMessageBox.Cancel)
            return
        if isSurprise is False:
            self.add_mark_item("Surprise")
            isSurprise = True
            tagString += 'Surprise,'

    def is_sad(self):
        global isSad
        global tagString
        if isNeutral:
            megInfo = '您已经选择Neutral标签了,不能再标记sad了'
            QMessageBox.warning(self, '错误', megInfo, QMessageBox.Yes, QMessageBox.Cancel)
            return
        if isUnknown:
            megInfo = '您已经选择Unknown标签了,不能再标记sad了'
            QMessageBox.warning(self, '错误', megInfo, QMessageBox.Yes, QMessageBox.Cancel)
            return
        if isHappy:
            megInfo = '您已经选择Happy标签了,不能再标记sad了'
            QMessageBox.warning(self, '错误', megInfo, QMessageBox.Yes, QMessageBox.Cancel)
            return
        if isSad is False:
            self.add_mark_item("Sad")
            isSad = True
            tagString += 'Sad,'

    def is_neutral(self):
        global isNeutral
        global tagString
        if isAnger | isDisgust | isFear | isHappy | isSurprise | isSad | isUnknown:
            megInfo = '您已经选择'+tagString+'标签了,不能再标记Neutral了'
            QMessageBox.warning(self, '错误', megInfo, QMessageBox.Yes, QMessageBox.Cancel)
            return
        if isNeutral is False:
            self.add_mark_item("Neutral")
            isNeutral = True
            tagString += 'Neutral,'

    def is_unknown(self):
        global isUnknown
        global tagString
        if isAnger | isDisgust | isFear | isHappy | isSurprise | isSad | isNeutral:
            megInfo = '您已经选择'+tagString+'标签了,不能再标记Unknown了'
            QMessageBox.warning(self, '错误', megInfo, QMessageBox.Yes, QMessageBox.Cancel)
            return
        if isUnknown is False:
            self.add_mark_item("Unknown")
            tagString += 'Unknown,'
            isUnknown = True

    # 标签初始化
    def tagInit(self):
        global isAnger
        global isDisgust
        global isFear
        global isHappy
        global isSurprise
        global isSad
        global isNeutral
        global isUnknown

        isAnger = False
        isDisgust = False
        isFear = False
        isHappy = False
        isSurprise = False
        isSad = False
        isNeutral = False
        isUnknown = False

    def add_mark_item(self, mark):
        self.mark_list.addItem(mark)

    def remove_mark(self):
        global isAnger
        global isDisgust
        global isFear
        global isHappy
        global isSurprise
        global isSad
        global isNeutral
        global isUnknown
        global tagString

        i = self.mark_list.currentItem()
        tag = i.text()
        print(tag)
        self.mark_list.takeItem(self.mark_list.row(i))
        if tag == 'Disgust':
            isDisgust = False
            tagString = tagString.replace('Disgust,', '')
        if tag == 'Fear':
            isFear = False
            tagString = tagString.replace('Fear,', '')
        if tag == 'Happy':
            isHappy = False
            tagString = tagString.replace('Happy,', '')
        if tag == 'Anger':
            isAnger = False
            tagString = tagString.replace('Anger,', '')
        if tag == 'Surprise':
            isSurprise = False
            tagString = tagString.replace('Surprise,', '')
        if tag == 'Sad':
            isSad = False
            tagString = tagString.replace('Sad,', '')
        if tag == 'Neutral':
            isNeutral = False
            tagString = tagString.replace('Neutral,', '')
        if tag == 'Unknown':
            isUnknown = False
            tagString = tagString.replace('Unknown,', '')

    # 选择文件夹的内容
    def selectVideoDocument(self):
        global videoName  # 在这里设置全局变量以便在线程中使用
        global curFrame
        global curVideo
        global tagFile
        global dir_path
        global docPath
        # videoName, videoType = QFileDialog.getOpenFileName(self,
        #                                                     "打开视频",
        #                                                     "",
        #                                                     # " *.jpg;;*.png;;*.jpeg;;*.bmp",
        #                                                     " *.jpg;;*.png;;*.jpeg;;*.bmp;;*.mp4;;*.avi;;All Files (*)")
        dir_path = QFileDialog.getExistingDirectory(self, "choose directory", "")
        # print(dir_path)
        # 打开这个路径 将所有视频文件、图片都保存到videoName中
        # files = os.listdir(dir_path)
        dir_path = dir_path.replace('/', '\\')
        docPath = os.path.join(dir_path, "tagResult")
        # 如果存放标签的结果的文件夹不存在
        # 就创建一个新的文件夹
        if os.path.exists(docPath) is False:
            os.mkdir(docPath)
        if dir_path:
            index = 0
            for root, dirs, names in os.walk(dir_path):
                for f in names:
                    if f.endswith('jpg') | f.endswith('png') | f.endswith('jpeg') | \
                            f.endswith('bmp') | f.endswith('mp4') | f.endswith('avi') | f.endswith('flv'):
                        fPath = os.path.join(root, f)
                        # print(f)
                        # print(fPath)
                        # 路径和文件名连接构成完整路径
                        # 根据创建的json文件来设置item的颜色
                        self.play_list.insertItem(index, f)
                        videoName[f] = fPath

                        # 万一有新的文件加入？
                        # 判断是否存在保存标签的文件
                        fPath = os.path.join(docPath, f + '.json')
                        if os.path.exists(fPath) is False:
                            tag = json.dumps(data, sort_keys=True, indent=4, separators=(',', ':'))
                            self.writeJson(tag, fPath)
                        index += 1
            self.taggingRecord()
            # 读入tagging记录文件进行记录
            for i in range(0, index):
                if tagRes[self.play_list.item(i).text()] == 0:
                    self.play_list.item(i).setForeground(QColor('red'))
                elif tagRes[self.play_list.item(i).text()] == 1:
                    self.play_list.item(i).setForeground(QColor('green'))
                else:
                    self.play_list.item(i).setForeground(QColor('black'))
                    self.play_list.item(i).setBackground(QColor('black'))
            curVideo = videoName[self.play_list.item(0).text()]
            fPath = os.path.join(docPath, self.play_list.item(0).text() + '.json')
            self.checkAndShowTag(fPath)
            # 视频显示
            th = Thread1(self)
            th.changePixmap.connect(self.showPic)
            th.start()

    # 判断并显示已经标记的标签
    def checkAndShowTag(self, filePath):
        tagRecord = self.readJson(filePath)
        for key in tagRecord:
            # print(str(key)+" : "+str(tagRecord[key]))
            if tagRecord[key] is not 0:
                self.mark_list.addItem(key)

    # 判断是否存在记录 不存在标记记录就新建标记文件
    # 如果存在就读入json文件
    def taggingRecord(self):
        global json_res, tagRes, tagRFile
        tagRFile = os.path.join(dir_path, "tagging.json")
        files = os.listdir(dir_path)
        if 'tagging.json' in files:
            # 如果存在就读入这个文件 保存到一个字典里面
            print('exist')
            tagRes = self.readJson(tagRFile)
            # print('tagRes:')
            # print(tagRes)
        else:
            # 创建一个tagging文件在当前视频文件夹中
            print('you should create a new json file')
            tagRes = {}
            for key in videoName:
                tagRes[key] = 0

            json_res = json.dumps(tagRes, sort_keys=True, indent=4, separators=(',', ':'))
            self.writeJson(json_res, tagRFile)

    # 修改播放位置
    def setPlayPlace(self):
        global videoStart
        global is_move
        is_move = True
        videoStart = self.videoSlider.value()

        # print(videoStart)

    def showPic(self, image):
        # print('pic')
        self.hereIsVideo.setPixmap(QPixmap.fromImage(image))
        self.hereIsVideo.setScaledContents(True)  # 图片自适应LABEL大小
        global curFrame
        curFrame += 1
        self.frameNumber.display(curFrame)
        self.videoSlider.setMaximum(totalFrame)
        self.videoSlider.setValue(curFrame)
        # print('totalFrame: '+str(totalFrame))
        # print('curFrame: '+str(curFrame))

    # 读入json文件
    def readJson(self, file):
        with open(file, 'r', encoding='UTF-8') as f:
            return json.load(f)

    # 写入json文件
    def writeJson(self, tagData, file):
        with open(file, 'w') as f:
            f.write(tagData)


class Thread1(QThread):  # 采用线程来播放视频
    changePixmap = pyqtSignal(QtGui.QImage)

    def run(self):
        while is_finish is False:
            global totalFrame
            cap = cv2.VideoCapture(curVideo)
            # 总帧数
            totalFrame = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            # print(str(totalFrame))
            # 保存所有帧
            allFrames = []
            # print(totalFrame)
            # print('play video:  '+curVideo)
            while cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    allFrames.append(frame)

                else:
                    cap.release()
                    break

            global videoStart
            i = videoStart
            # print('videoStart:' + str(videoStart))
            while i < len(allFrames):
                rgbImage = cv2.cvtColor(allFrames[i], cv2.COLOR_BGR2RGB)
                convertToQtFormat = QtGui.QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0],
                                                 QtGui.QImage.Format_RGB888)  # 在这里可以对每帧图像进行处理，
                self.changePixmap.emit(convertToQtFormat)
                time.sleep(0.1)  # 控制视频播放的速度
                i += 1
                # 如果按下暂停键
                # 那么就进入while循环
                # 等待按下播放键
                # print("play state is:"+str(is_play))
                # print("stop state is:"+str(is_stop))
                if is_stop:
                    while is_stop:
                        # print('stop')
                        continue
                # 如果移动了进度条
                global is_move
                global curFrame
                if is_move:
                    is_move = False
                    i = videoStart
                    curFrame = i

                # 如果点击了切换视频
                # 播放上一条或者下一条视频
                # 不过要先清空缓存
                # 退出循环进行下一个视频的载入
                global is_change
                if is_change:
                    cap.release()
                    curFrame = 0
                    videoStart = 0
                    is_change = False
                    break


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
