
# 任务调度器初始化

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler


def make_scheduler():
    """
    make scheduler
    :return:
    """
    config = {
        'timezone': "Asia/Shanghai",
        'executors': {
            'default': ThreadPoolExecutor(2)
        },
        'job_defaults': {
            'max_instances': 3,
            'coalesce': True,
            'misfire_grace_time': 5
        }
    }

    sch = BackgroundScheduler(**config)
    return sch
