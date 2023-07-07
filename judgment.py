
# 23/7/3
# 读取待评估记录，根据评分和类别判断是否下载，将判断结果回写数据
# 库



from model.movie import MoviveDbManager




def run():
    """
    # 获得状态是「待评审」(0)的数据
    """
    manager = MoviveDbManager()
    rows = manager.query_status(status=0)
    print(rows)
