
# 23/7/3
# 根据评分和列表标签判断电影是否要下载



from model.movie import MoviveDbManager




def run():
    """
    # 获得状态是「待评审」(0)的数据
    """
    manager = MoviveDbManager()
    rows = manager.query_status(status=0)
    print(rows)
