import myframe
import cv2
from PySide2.QtCore import QTimer


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

# 疲劳判断变量
# Perclos模型
# perclos = (Rolleye / Roll) + (Rollmouth / Roll) * 0.2
Roll = 0  # 整个循环内的帧数
Rolleye = 0  # 循环内闭眼帧数
Rollmouth = 0  # 循环内打哈欠数


class CamDetector:
    def __init__(self):
        self.v_timer = QTimer()
        self.cap = cv2.VideoCapture(-1)
        if not self.cap:
            print('Open camera failed!')
            return

    def run_transfer_data(self):
        global EYE_AR_THRESH, EYE_AR_CONSEC_FRAMES, MAR_THRESH, MOUTH_AR_CONSEC_FRAMES, COUNTER, TOTAL, mCOUNTER, \
            mTOTAL, ActionCOUNTER, Roll, Rolleye, Rollmouth

        success, frame = self.cap.read()
        if success:
            ret, frame = myframe.frametest(frame)
            lab, eye, mouth = ret
            # ret和frame，为函数返回
            # ret为检测结果，ret的格式为[lab,eye,mouth],lab为yolo的识别结果包含'phone' 'smoke' 'drink',eye为眼睛的开合程度（长宽比），mouth为嘴巴的开合程度
            # frame为标注了识别结果的帧画面，画上了标识框

            # 分心行为判断
            # 分心行为检测以15帧为一个循环
            ActionCOUNTER += 1
            # 如果检测到分心行为，加ActionCOUNTER减1，以延长循环时间
            for i in lab:
                if (i == "phone"):
                    pass  # 传输数据phone
                    # print('using phone now')
                    if ActionCOUNTER > 0:
                        ActionCOUNTER -= 1
                elif (i == "smoke"):
                    pass  # 传输数据smoke
                    if ActionCOUNTER > 0:
                        ActionCOUNTER -= 1
                elif (i == "drink"):
                    pass  # 传输数据drink
                    if ActionCOUNTER > 0:
                        ActionCOUNTER -= 1
            # 如果超过15帧未检测到分心行为，将后端修改为平时状态
            if ActionCOUNTER == 15:
                # 重置数据库数据
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
                    pass
                    # 传输数据库数据eye_times
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
                    # 传输数据库数据
                    # 重置嘴帧计数器
                    mCOUNTER = 0

            # 疲劳模型
            # 疲劳模型以150帧为一个循环
            # 每一帧Roll加1
            Roll += 1
            # 当检测满150帧时，计算模型得分
            if Roll == 150:
                # 计算Perclos模型得分
                perclos = (Rolleye / Roll) + (Rollmouth / Roll) * 0.2
                # 当过去的150帧中，Perclos模型得分超过0.38时，判断为疲劳状态
                if perclos > 0.38:
                    pass
                    # 数据库传输数据fatigue，执行语音警告以及紧急拨号
                else:
                    pass  # 保持数据库fatigue为0
                # 归零
                # 将三个计数器归零
                # 重新开始新一轮的检测
                Roll = 0
                Rolleye = 0
                Rollmouth = 0
        else:
            print('Open camera failed!')


if __name__ == "__main__":
    exe_detect = CamDetector()
    exe_detect.run_transfer_data()
