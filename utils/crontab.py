#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import schedule

def clear_session():
    os.chdir(os.path.dirname(os.path.dirname(__file__)))
    ret = os.system('python manage.py clearsessions')
    if ret == 0:
        print('清理过期session完成！')

# clear_session()

# schedule.every(10).minutes.do(job)    # 每隔十分钟执行一次任务
# schedule.every().hour.do(job)     # 每隔一小时执行一次任务
# schedule.every().day.at("10:30").do(job)  # 每天的10:30执行一次任务
# schedule.every(5).to(10).days.do(job)     # 每隔5到10天执行一次任务
# schedule.every().monday.do(job)       # 每周一的这个时候执行一次任务
# schedule.every().wednesday.at("13:15").do(job)    # 每周三13:15执行一次任务

schedule.every().day.at("23:00").do(clear_session)
if __name__ == '__main__':
    while True:
        schedule.run_pending()  # 运行所有可以运行的任务

