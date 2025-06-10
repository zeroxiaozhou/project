import requests
import time
import random
import execjs
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler  # 改用后台调度器
from threading import Event
from sqlalchemy import create_engine


def login(k, m):
    login_url = "http://112.48.134.15:5000/doLogin"
    header = {
        'Content-Type': 'application/json;charset=UTF-8',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'http://112.48.134.15:5001/',
        # "Token": "3a52d2b9849243c4843a73f7da16913e",
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.31'
    }

    with open(r'./厦门加密.js', 'r', encoding='utf-8') as f:
        decrypt = f.read()
    ctx = execjs.compile(decrypt)
    data = {"account": k, "password": ctx.call("passwd", m)}
    print(data)
    while True:
        try:
            res = requests.post(login_url, headers=header, json=data)
            print(res.json())
            token = res.json()['data']['token']
            return token
        except Exception as e:
            print(f'登录失败{e}')
            time.sleep(random.uniform(3, 5))

def State(state):
    x = state
    if x == '营运' or x == '审验通过':
        x = '有效'
    return x
def driver():
    df = pd.DataFrame()
    headers["Token"] = login("91350203MACBRPWX89", 'Xx202505')
    while True:
        try:
            url = "http://112.48.134.15:5000/jpBsdriver/queryPage"
            new_data = {"page": {"showAll": False, "pageStart": 1, "pageSize": 100, "rowsCount": 0, "currentPage": 1,
                                 "totalPage": 0,
                                 "returnFields": "keyno;sadminareaname;qlsapprovestatusname;qlsreqkindname;sapplyman;sidcardno;sidadd;qlsreqtypename;dcardreceivedate1;scardsenddate;dworkenddate;scarno;scorpname;saldrivetype;dfsendnodate;smobiltele;dauditdate;qlsiccardmacno;qldiccarddate;dcreatedate;qlscardadminarea;sremark"},
                        "queryVo": {"quickQryApprovestatusno": "003", "quickQryArea": "3502", "quickQryType": "A",
                                    "quickQryInclueLower": True, "pageType": "0", "loginAdminarea": "3502"}}
            new_result = requests.post(url, headers=headers, json=new_data, timeout=None)
            # 页数
            page = new_result.json()["data"]["page"]["totalPage"]
            # 条数
            size = new_result.json()["data"]["page"]["rowsCount"]
            print(f'\033[1;36m页数==>{page} 条数==>{size}\033[0m')
            new_data["page"]["pageSize"] = size
            result = requests.post(url, headers=headers, json=new_data, timeout=None)
            lst = result.json()['data']['list']
            result.close()
            df = pd.concat([df, pd.DataFrame(lst)], ignore_index=True)
            time.sleep(random.uniform(0.8, 1))
            df = df[['sidcardno', 'sapplyman', "smobiltele", "scardsenddate", "dworkenddate",
                     "qlsapprovestatusname", "qlsreqtypename", "qlsreqkindname"]]
            df.rename(columns={'sidcardno': '身份证号', 'sapplyman': '司机姓名', "smobiltele": "手机号",
                               "scardsenddate": "发证日期", "dworkenddate": "有效期至", "qlsapprovestatusname": "从业状态", "qlsreqtypename": "从业资格类别",
                               "qlsreqkindname": "业务类型"}, inplace=True)
            df.to_excel(r'D:\双证合规\厦门市\厦门运政平台人证%s.xlsx' % today[5::], index=False)
            # 两表匹配
            # merged_data = pd.merge(table, df, on='身份证号', how="left")
            # merged_data['从业状态'] = merged_data['从业状态'].fillna('无效')
            # merged_data = merged_data.drop_duplicates()
            # merged_data['人证'] = merged_data['从业状态'].apply(State)
            # merged_data.to_excel(r'D:\双证合规\厦门市\厦门市人证%s.xlsx' % today[5::], index=False)
            print('人证写入完成')
            break
        except requests.exceptions.ConnectionError:
            print('连接超时')
            time.sleep(random.uniform(1, 2))
        except Exception as e:
            print(e)
            time.sleep(random.uniform(3, 5))


def car(user):
    df = pd.DataFrame()
    while True:
        try:
            url = "http://112.48.134.15:5000/taCarWy/queryPage"
            new_data = {"page": {"showAll": False, "pageStart": 1, "pageSize": 100, "rowsCount": 0, "currentPage": 1,
                                 "totalPage": 0,
                                 "returnFields": "keyno;sadminareaname;scarsign;slockstatus;scarcolorname;scarno;strafficard;scorpname;nchecktonx;sengineno;scarbodyno;sfactcardmodel;svectypename;sfueltype;dtrifficsenddate;dtrifficenddate;sporttype;dcheckdate;dcheckenddate;sendnogblook;sendnogbremark;dcreatedate;screateusername;sremark;corpslicense;corpsaddr;corpsprofessiontype;scartlevelname;dcartleveldate;nlength;nwidth;nheight;nmassseat;nnullmass;scarboxtype;dsendjoindate;djoindate;stele;straffickind;scarsource;denddate;dburdenfeeend;scarname"},
                        "queryVo": {"quickQryCarsignArray": [], "quickQryArea": "3502", "quickQryType": "A",
                                    "quickQryInclueLower": True, "pageType": "0", "loginAdminarea": "3502",
                                    "quickQryTag": "1"}}
            new_result = sess.post(url, headers=headers, json=new_data, timeout=30)
            # 页数
            page = new_result.json()["data"]["page"]["totalPage"]
            # 条数
            size = new_result.json()["data"]["page"]["rowsCount"]
            print(f'\033[1;36m页数==>{page} 条数==>{size}\033[0m')
            new_data["page"]["pageSize"] = size
            result = sess.post(url, headers=headers, json=new_data, timeout=None)
            lst = result.json()['data']['list']
            result.close()
            df = df._append(pd.DataFrame(lst), ignore_index=True)
            # df = pd.concat([df, pd.DataFrame(lst)], ignore_index=True)
            time.sleep(random.uniform(0.8, 1))
            df = df[['scarno', "scarcolorname", "strafficard", "sporttype", "dtrifficsenddate",
                     "dcheckenddate", "scarname", "scarsign"]]
            df.rename(columns={'scarno': '车牌号', "scarcolorname": "车牌颜色", "strafficard": "运输证号",
                               "sporttype": "运输类型", "dtrifficsenddate": "年审日期", "dcheckenddate": "年审有效期", "scarname": "车辆所有人",
                               "scarsign": "营运状态"}, inplace=True)
            df.to_excel(rf'D:\双证合规\厦门市\{user}厦门运政平台车证%s.xlsx' % today[5::], index=False)
            print(f'{user}车证完成')
            # 两表匹配
            # table.rename(columns={"人证": "车证"}, inplace=True)
            # merged_data = pd.merge(table, df, on='车牌号', how="left")
            # merged_data['营运状态'] = merged_data['营运状态'].fillna('无效')
            # merged_data = merged_data.drop_duplicates()
            # merged_data['车证'] = merged_data['营运状态'].apply(State)
            # merged_data.to_excel(r'D:\双证合规\厦门市\厦门市车证%s.xlsx' % today[5::], index=False)
            # print('车证写入完成')
            quit()
        except requests.exceptions.ConnectionError:
            print('连接超时')
            time.sleep(random.uniform(1, 2))
        except Exception as e:
            print(e)
            time.sleep(random.uniform(3, 5))

def Transfe():
    df = pd.DataFrame()
    while True:
        try:
            url = "http://112.48.134.15:5000/taCarWyPlateLog/queryPage"
            new_data = {
                "page": {
                    "showAll": False,
                    "pageStart": 1,
                    "pageSize": 20,
                    "rowsCount": 3272,
                    "currentPage": 1,
                    "totalPage": 164,
                    "returnFields": "keyno;sadminareaname;soperkind;scarno;scarcolorname;scorpname;dcreatedate;sremark"
                },
                "queryVo": {
                    "quickQryArea": "3502",
                    "quickQryType": "A",
                    "quickQryInclueLower": True,
                    "pageType": "0",
                    "loginAdminarea": "3502",
                    "quickQryTag": "1"
                }
            }
            new_result = sess.post(url, headers=headers, json=new_data, timeout=30)
            # 页数
            page = new_result.json()["data"]["page"]["totalPage"]
            # 条数
            size = new_result.json()["data"]["page"]["rowsCount"]
            print(f'\033[1;36m页数==>{page} 条数==>{size}\033[0m')
            new_data["page"]["pageSize"] = size
            result = sess.post(url, headers=headers, json=new_data, timeout=300)
            lst = result.json()['data']['list']
            result.close()
            df = df._append(pd.DataFrame(lst), ignore_index=True)
            # df = pd.concat([df, pd.DataFrame(lst)], ignore_index=True)
            time.sleep(random.uniform(0.8, 1))
            df.to_excel(r'D:\双证合规\厦门市\运政平台转出车证%s.xlsx' % today[5::], index=False)
            print('车辆转出记录导出完成')
            break
        except Exception as e:
            print(e)
            headers["Token"] = login()
            time.sleep(random.uniform(3, 5))


if __name__ == '__main__':
    sess = requests.session()
    engine = create_engine('mssql+pymssql://sa:Xy202204@LAPTOP-HHMD1A48\XYCX/证件合规信息查询?charset=utf8', echo=False)
    sql = "select * from [证件合规信息查询].[dbo].[每日需要查询数据] where 城市='厦门市'"
    table = pd.read_sql(sql, con=engine)
    table.insert(table.columns.get_loc('更新日期'), '人证', '')
    today = str(time.strftime('%Y-%m-%d', time.localtime()))
    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'http://112.48.134.15:5001/',
        # "Token": login("91350128315352588H", 'Sz202305'),
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.31'
    }
    # time.sleep(60*60*12)
    driver()
    # scheduler.shutdown()  # 主线程中安全关闭调度器
    # car('神州')
    # Transfe()
    # headers["Token"] = login('91350203MACBRPWX89', 'Hx202409')
    # car('喜行')
    # Transfe()
