import time
import requests
import pandas as pd
from tqdm import trange
import random
import traceback
from sqlalchemy import create_engine

def car(i):
    lst = []
    while True:
        try:
            data = {
                'adcode': '330100',
                'plateNo': '',
                'pageNum': i,
                'pageSize': 50,
                'testGroupFlag': '0',
            }
            res = sess.post("https://admin.yueyuechuxing.cn/bos/admin/v2/sv/vehicle/findSummaryList", headers=header, json=data).json()
            result = res['data']['items']
            for j in result:
                lst.append(j["carId"])
            time.sleep(0.5)
            code = detail(lst, "vehicleIdList")
            if code == 1:
                break
            else:
                print("返回的code不是1")
        except requests.exceptions.ConnectionError:
            print('连接超时')
            time.sleep(random.uniform(1, 2))
        except Exception:
            traceback.print_exc()
            time.sleep(random.uniform(2, 3))

def driver(i):
    dri_lst = []
    while True:
        try:
            data = {
                'adcode': '330100',
                'newTestGroupFlag': [0, 2],
                'plateNo': '',
                'pageNum': i,
                'pageSize': 50,
                'testGroupFlag': '0',
            }
            res = requests.post("https://admin.yueyuechuxing.cn/bos/admin/v2/sv/driver/findSummaryList", headers=header,
                            json=data).json()
            result = res['data']['items']
            for j in result:
                dri_lst.append(j["driverId"])
            time.sleep(0.5)
            code = detail(dri_lst, "driverIdList")
            if code == 1:
                break
            else:
                print("返回的code不是1")
        except requests.exceptions.ConnectionError:
            print('连接超时')
            time.sleep(random.uniform(1, 2))
        except Exception:
            traceback.print_exc()
            time.sleep(random.uniform(2, 3))
def detail(lst,leixing):
    while True:
        try:
            # 推送
            json_data = {
                'dockingId': 5305,
                'dmlType': 0,
                leixing: lst}
            # 广州更新报备
            # json_data = {
            #     'dmlSubType': 1,
            #     'dockingId': 330100,
            #     'dmlType': 0,
            #     leixing: lst}
            # 广州更新司机信息
            # json_data = {
            #     'dmlSubType': 2,
            #     'dockingId': 1150,
            #     'dmlType': 0,
            #     leixing: lst}
            res = sess.post("https://admin.yueyuechuxing.cn/bos/admin/v2/sv/real/staticSend", headers=header, json=json_data).json()
            print(res)
            time.sleep(0.5)
            if res['code'] == 1:
                return 1
            else:
                return 0
        except requests.exceptions.ConnectionError:
            print('连接超时')
            time.sleep(random.uniform(1, 2))
        except Exception:
            traceback.print_exc()
            time.sleep(random.uniform(2, 3))


if __name__ == '__main__':
    engine = create_engine('mssql+pymssql://sa:Xy202204@LAPTOP-HHMD1A48\XYCX/证件合规信息查询?charset=utf8', echo=False)
    url = 'https://admin.yueyuechuxing.cn/bos/admin/v1/sv/stat/queryTaskRece'
    ck = pd.read_sql("select * from 证件合规信息查询.dbo.小周账号信息配置表 where Account='admin'", con=engine)
    cookie = ck['cookie'][0]
    _admin_tk = ck['_admin_tk'][0]
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.54',
        'cookie': cookie,
        '_admin_eid': ck['eid'][0],
        '_admin_resource_key': 'personCarPush',
        '_admin_session_eid': ck['sesseid'][0],
        '_admin_sign': '76828b6260c0588b86dff532333faab9',
        '_admin_tk': _admin_tk,
        '_admin_ts': str(round(time.time())),
    }

    sess = requests.session()
    num = 117
    num2 = 117
    for i in trange(1, num):
        driver(i)
        time.sleep(random.uniform(0.5, 0.8))
    print("===========司机已推送完成============")
    for i in trange(1, num2):
        car(i)
        time.sleep(random.uniform(0.5, 0.8))
    print("===========车辆已推送完成============")

