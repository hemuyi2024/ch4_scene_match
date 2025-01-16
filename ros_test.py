#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
from std_msgs.msg import String


def talker():
    # 创建一个发布者，向名为 "chatter" 的话题发送 String 类型消息
    pub = rospy.Publisher('chatter', String, queue_size=10)

    # 初始化 ROS 节点，节点名称为 "test_pycharm_talker"
    rospy.init_node('test_pycharm_talker', anonymous=True)

    # 设置发布频率为 1Hz (每秒1次)
    rate = rospy.Rate(1)

    while not rospy.is_shutdown():
        # 构造要发布的字符串消息
        hello_str = f"Hello from PyCharm! Current time: {rospy.get_time():.4f}"

        # 在日志里打印该消息
        rospy.loginfo(hello_str)

        # 发布到 chatter 话题
        pub.publish(hello_str)

        # 休眠，维持发布频率
        rate.sleep()


if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
