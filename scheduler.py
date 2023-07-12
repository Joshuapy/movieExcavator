
# 任务调度器初始化

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.background import BlockingScheduler

# tasks
from gather import dytt_gather
from judgment import run as judge_movie


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

    sch = BlockingScheduler(**config)
    sch.add_job(dytt_gather, "cron", hour="21", day="*")
    sch.add_job(judge_movie(), "cron", minutes="30", hour="21", day="*")
    return sch
