# 主函数
import json
import sys
import time

import cv2
import requests
from PySide2 import QtWidgets
from PySide2.QtCore import QTimer
from PySide2.QtGui import QPixmap, QImage
from PySide2.QtWidgets import QMainWindow

import myframe
from ui_mainwindow import Ui_MainWindow


# 定义相应url
server_url = "https://www.xqstudy.top"
get_id_url = server_url + "/userInfo/getId"
upload_url = server_url + "/pic/upload"

# 定义传输危险行为的图片
def post_img_para(danger_type, img_path, user_id):
    img_path = "./" + img_path
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    files = {'file': (timestamp + '.png', open(img_path, 'rb'))}
    upload_info = {
        "id": user_id,
        "type": danger_type,
        "time": timestamp
    }
    upload_info_res = requests.post(url=upload_url, files=files, params=upload_info)  # 使用表单
    return upload_info_res.text


# 首先从数据库获取当前驾驶员id
# user_id = json.loads(requests.get(url=get_id_url).text)['data']
user_id = requests.get(url=get_id_url).text
print("Current user_id is ", user_id)


# 定义变量
# 眼睛闭合判断
EYE_AR_THRESH = 0.15  # 眼睛长宽比
EYE_AR_CONSEC_FRAMES = 2  # 闪烁阈值

# 嘴巴开合判断
MAR_THRESH = 0.65  # 打哈欠长宽比
MOUTH_AR_CONSEC_FRAMES = 3  # 闪烁阈值

# 定义检测变量，并初始化
COUNTER = 0  # 眨眼帧计数器
TOTAL = 0  # 眨眼总数
mCOUNTER = 0  # 打哈欠帧计数器
mTOTAL = 0  # 打哈欠总数
ActionCOUNTER = 0  # 分心行为计数器器
framecounter = 0  # 截帧上传计数器
drink_flag = 0
smoke_flag = 0
fatigue_flag = 0
phone_flag = 0

# 疲劳判断变量
# Perclos模型
# perclos = (Rolleye/Roll) + (Rollmouth/Roll)*0.2
Roll = 0  # 整个循环内的帧技术
Rolleye = 0  # 循环内闭眼帧数
Rollmouth = 0  # 循环内打哈欠数


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        # 打开文件类型，用于类的定义
        self.f_type = 0

    def window_init(self):
        # 设置控件属性
        # 设置label的初始值
        self.label.setText("请打开摄像头")
        self.label_2.setText("疲劳检测：")
        self.label_3.setText("眨眼次数：0")
        self.label_4.setText("哈欠次数：0")
        self.label_5.setText("行为检测：")
        self.label_6.setText("手机")
        self.label_7.setText("抽烟")
        self.label_8.setText("喝水")
        self.label_9.setText("是否存在分心行为")
        self.label_10.setText("是否为疲劳状态")
        self.menu.setTitle("打开")
        self.actionOpen_camera.setText("打开摄像头")
        # 菜单按钮 槽连接 到函数
        self.actionOpen_camera.triggered.connect(CamConfig_init)
        # 自适应窗口缩放
        self.label.setScaledContents(True)


# 定义摄像头类
class CamConfig:
    def __init__(self):
        Ui_MainWindow.printf(window, "正在打开摄像头请稍后...")
        # 设置时钟
        self.v_timer = QTimer()
        # 打开摄像头
        self.cap = cv2.VideoCapture(0)
        if not self.cap:
            Ui_MainWindow.printf(window, "打开摄像头失败")
            return
        # 设置定时器周期，单位毫秒
        self.v_timer.start(20)
        # 连接定时器周期溢出的槽函数，用于显示一帧视频
        self.v_timer.timeout.connect(self.show_pic)
        # 在前端UI输出提示信息
        Ui_MainWindow.printf(window, "载入成功，开始运行程序")
        Ui_MainWindow.printf(window, "")
        Ui_MainWindow.printf(window, "开始执行疲劳检测...")
        window.statusbar.showMessage("正在使用摄像头...")

    def show_pic(self):
        # 全局变量
        # 在函数中引入定义的全局变量
        global EYE_AR_THRESH, EYE_AR_CONSEC_FRAMES, MAR_THRESH, MOUTH_AR_CONSEC_FRAMES, COUNTER, TOTAL, mCOUNTER, \
            mTOTAL, ActionCOUNTER, Roll, Rolleye, Rollmouth, framecounter, drink_flag, phone_flag, fatigue_flag, \
            smoke_flag

        # 读取摄像头的一帧画面
        success, frame = self.cap.read()
        if success:
            # 检测
            # 将摄像头读到的frame传入检测函数myframe.frametest()
            ret, frame = myframe.frametest(frame)
            lab, eye, mouth = ret
            # ret和frame，为函数返回
            # ret为检测结果，ret的格式为[lab,eye,mouth],lab为yolo的识别结果包含'phone' 'smoke' 'drink',eye为眼睛的开合程度（长宽比），mouth为嘴巴的开合程度
            # frame为标注了识别结果的帧画面，画上了标识框

            # 分心行为判断
            # 分心行为检测以15帧为一个循环，截图上传15帧一个循环
            ActionCOUNTER += 1
            framecounter += 1
            # 如果检测到分心行为
            # 将信息返回到前端ui，使用红色字体来体现
            # 并加ActionCOUNTER减1，以延长循环时间
            for i in lab:
                # print(framecounter)
                if (i == "phone"):
                    # dager_type = 3
                    window.label_6.setText("<font color=red>正在用手机</font>")
                    if phone_flag == 0:
                        phone_img_path = r"using_phone.png"
                        cv2.imwrite(phone_img_path, frame)
                        
                        upload_result = post_img_para(danger_type=3, img_path=phone_img_path, user_id=user_id)
                        print("phone upload: ", upload_result)
                        if upload_result == "true":
                            phone_flag = 1
                            window.label_9.setText("<font color=red>UsingPhone已报备云端</font>")
                        # else:
                        #     window.label_9.setText("<font color=red>UploadFailed</font>")
                    else:
                        window.label_9.setText("<font color=red>最近帧内已报备云端</font>")
                        if framecounter >= 45:  # 若为规定帧数循环后，全部置零
                            phone_flag = 0
                            framecounter = 0
                    if ActionCOUNTER > 0:
                        ActionCOUNTER -= 1
                elif (i == "smoke"):
                    # danger_type = 1
                    smoke_img_path = r"smoking.png"
                    window.label_7.setText("<font color=red>正在抽烟</font>")
                    if smoke_flag == 0:
                        cv2.imwrite(smoke_img_path, frame)
                        upload_result = post_img_para(danger_type=1, img_path=smoke_img_path, user_id=user_id)
                        print("smoke upload: ", upload_result)
                        print(type(upload_result))
                        if upload_result == "true":
                            smoke_flag = 1
                            window.label_9.setText("<font color=red>Smoking已报备云端</font>")
                        # else:
                        #     window.label_9.setText("<font color=red>UploadFailed</font>")
                    else:
                        window.label_9.setText("<font color=red>最近帧内已报备云端</font>")
                        if framecounter >= 45:  # 若为规定帧数循环后，全部置零
                            smoke_flag = 0
                            framecounter = 0
                    if ActionCOUNTER > 0:
                        ActionCOUNTER -= 1
                elif (i == "drink"):
                    # danger_type = 2
                    drink_img_path = r"drinking.png"
                    window.label_8.setText("<font color=red>正在用喝水</font>")
                    if drink_flag == 0:
                        cv2.imwrite(drink_img_path, frame)
                        upload_result = post_img_para(danger_type=2, img_path=drink_img_path, user_id=user_id)
                        print("drink upload: ", upload_result)
                        print(type(upload_result))
                        if upload_result == "true":
                            drink_flag = 1
                            window.label_9.setText("<font color=red>Drinking已报备云端</font>")
                        # else:
                        #     window.label_9.setText("<font color=red>UploadFailed</font>")
                    else:
                        window.label_9.setText("<font color=red>最近帧内已报备云端</font>")
                        if framecounter >= 45:
                            drink_flag = 0
                            framecounter = 0
                    if ActionCOUNTER > 0:
                        ActionCOUNTER -= 1

            # 如果超过15帧未检测到分心行为，将label修改为平时状态
            if ActionCOUNTER == 15:
                window.label_6.setText("手机")
                window.label_7.setText("抽烟")
                window.label_8.setText("喝水")
                window.label_9.setText("")
                ActionCOUNTER = 0

            # 疲劳判断
            # 眨眼判断
            if eye < EYE_AR_THRESH:
                # 如果眼睛开合程度小于设定好的阈值
                # 则两个和眼睛相关的计数器加1
                COUNTER += 1
                Rolleye += 1
            else:
                # 如果连续2次都小于阈值，则表示进行了一次眨眼活动
                if COUNTER >= EYE_AR_CONSEC_FRAMES:
                    TOTAL += 1
                    window.label_3.setText("眨眼次数：" + str(TOTAL))
                    # 重置眼帧计数器
                    COUNTER = 0

            # 哈欠判断，同上
            if mouth > MAR_THRESH:
                mCOUNTER += 1
                Rollmouth += 1
            else:
                # 如果连续3次都小于阈值，则表示打了一次哈欠
                if mCOUNTER >= MOUTH_AR_CONSEC_FRAMES:
                    mTOTAL += 1
                    window.label_4.setText("哈欠次数：" + str(mTOTAL))
                    # 重置嘴帧计数器
                    mCOUNTER = 0

            # 将画面显示在前端UI上
            show = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            showImage = QImage(show.data, show.shape[1], show.shape[0], QImage.Format_RGB888)
            window.label.setPixmap(QPixmap.fromImage(showImage))

            # 疲劳模型
            # 疲劳模型以150帧为一个循环
            # 每一帧Roll加1
            Roll += 1
            # 当检测满150帧时，计算模型得分
            if Roll == 150:
                # 计算Perclos模型得分
                perclos = (Rolleye / Roll) + (Rollmouth / Roll) * 0.2
                # 在前端UI输出perclos值
                Ui_MainWindow.printf(window, "过去150帧中，Perclos得分为" + str(round(perclos, 3)))
                # 当过去的150帧中，Perclos模型得分超过0.38时，判断为疲劳状态
                if perclos > 0.38:
                    Ui_MainWindow.printf(window, "当前处于疲劳状态")
                    window.label_10.setText("<font color=red>疲劳！！！</font>")
                    # danger_type = 4
                    fatigue_img_path = r"fatigue.png"
                    cv2.imwrite(fatigue_img_path, frame)
                    post_img_para(danger_type=4, img_path=fatigue_img_path, user_id=user_id)
                    Ui_MainWindow.printf(window, "")
                else:
                    Ui_MainWindow.printf(window, "当前处于清醒状态")
                    window.label_10.setText("清醒")
                    Ui_MainWindow.printf(window, "")

                # 归零
                # 将三个计数器归零
                # 重新开始新一轮的检测
                Roll = 0
                Rolleye = 0
                Rollmouth = 0
                Ui_MainWindow.printf(window, "重新开始执行疲劳检测...")


def CamConfig_init():
    window.f_type = CamConfig()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.window_init()
    window.show()
    sys.exit(app.exec_())
