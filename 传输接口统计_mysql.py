import traceback
import requests
import pandas as pd
import time
from datetime import datetime, timedelta
import random
import io
from sqlalchemy import create_engine, text
import emoji
import pymysql


def parse(header):
    while True:
        try:
            json_data = {
                'desens': 0,
                'desensitizeFieldInfos': '[]',
                'statType': 0,
                'ignorePlatform': 2,
                'pageNum': 1,
                'pageSize': 10,
                'statStartDate': f"{formatted_date}",
                'statEndDate': f"{formatted_date}",
            }
            response = requests.post('https://admin.yueyuechuxing.cn/bos/admin/v2/sv/stat/interfaceSendExport',
                                     headers=header, json=json_data).json()
            return response
        except Exception as e:
            print(f'程序报错{e}')
            traceback.print_exc()
            time.sleep(random.uniform(2, 3))


def detail(header, brand):
    """
    爬取导出列表，下载文件
    :return:
    """
    k = 0
    while True:
        try:
            js_data = {"pageNum": 1, "pageSize": 50, "pageFlag": "interfaceDailySendJobExport", "configName": "",
                       "downloadStatus": None}
            response = requests.post(
                'https://admin.yueyuechuxing.cn/bos/admin/v2/ai/common/export/server/getExportRecords', headers=header,
                json=js_data).json()
            if response["code"] == 1:
                task_list = response["data"]["list"]
                # if str(for_date) in str(task_list[k]["condition"]):
                if task_list[k]["status"] == 3:
                    file_url = "https://admin.yueyuechuxing.cn" + task_list[k]["artifact"]
                    file = requests.get(file_url, headers=headers, timeout=None)
                    # 将获取的内容转换为 DataFrame
                    datn = pd.read_csv(io.StringIO(file.text))
                    datn.insert(0, '品牌', brand)
                    # 同时处理所有列，避免循环
                    for column in datn.columns[0:]:
                        datn[column] = datn[column].replace({'="0"': '0', '-': '0'})  # 替换为字符串 '0'
                    datn = datn.rename(columns=field_dict)
                    datn.to_sql('push_order_tally_stats', con=engine, if_exists='append', index=False)
                    print(f'\033[31m{account}写入数据库完成(✿◡‿◡){emoji.emojize(":partying_face:")}\033[0m')
                    time.sleep(random.uniform(2, 3))
                    return None
                print("数据还没能下载")
                time.sleep(random.uniform(10, 15))
                # else:
                #     print(f'{emoji.emojize(":ghost::ghost::ghost:")}不是我要的日期数据')
                #     k += 1
                #     time.sleep(20)
            else:
                print(response)
        except requests.exceptions.ConnectionError:
            print(f'连接超时{emoji.emojize(":dizzy::dizzy::dizzy::dizzy:")}')
            time.sleep(random.uniform(3, 6))
        except Exception as f:
            print(f'写入异常正在重新写入{emoji.emojize(":loudly_crying_face:")}======>>>{f}')
            # traceback.print_exc()
            time.sleep(random.uniform(3, 6))


def delete(s):
    db = pymysql.connect(
        host='HgDataBase',
        port=4408,
        user='root',
        password='M25xx%ycl',
        database='sophon',
        charset='utf8mb4'
    )
    cursor = db.cursor()
    cursor.execute(s)
    db.commit()
    db.close()


if __name__ == '__main__':
    dist = {
        '喜行约车': {'file': 'Profile 1', 'user': '喜行约车', 'eid': '800432'},
        '神州专车': {'file': 'Profile 2', 'user': '神州专车', 'eid': '800447'},
        '蛋卷出行': {'file': 'Profile 5', 'user': '蛋卷出行', 'eid': '800761'},
        '星徽出行': {'file': 'Profile 4', 'user': '星徽出行', 'eid': '800161'},
        '江南出行': {'file': 'Profile 3', 'user': '江南出行', 'eid': '800188'},
    }
    engine = create_engine('mysql+pymysql://root:M25xx%ycl@HgDataBase:4408/sophon?utf8mb4', echo=False)
    with engine.connect() as connection:
        info = connection.execute(
            text("SELECT field_cn, field_en FROM `edsac`.`fields_info` WHERE table_name='push_order_tally_stats'"))
        field_dict = {row[0]: row[1] for row in info.fetchall()}
    print(field_dict)
    # 格式化输出为指定格式
    date = datetime.now() - timedelta(days=1)
    # start_obj = "2025-05-12"
    # obj = datetime.strptime(start_obj, "%Y-%m-%d")
    # u = 2
    # while date.month != 1 or date.day != 1:
    #     date = obj - timedelta(days=u)
    #     print(date.month, date.day, u)
    formatted_date = date.strftime('%Y%m%d')
    # formatted_date = "20250601"
    # formatted_end_date = "20250603"
    for_date = date.strftime('%Y-%m-%d')
    sql = f"""DELETE FROM push_order_tally_stats WHERE date_time = '{for_date}'"""
    delete(sql)
    num = 0
    while True:
        if num == 3:
            print(f'{emoji.emojize(":ghost::ghost::ghost:")}全部搞定啦~')
            break
        for account in dist:  # 先导出
            ck = pd.read_sql("select * from accounts where account='小周'and brand='%s'" % dist[account]['user'], con=engine)
            cookie = ck['cookie'][0]
            _admin_tk = ck['token'][0]
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36',
                'cookie': cookie,
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Connection': 'keep-alive',
                'Content-Type': 'application/json',
                '_admin_eid': dist[account]['eid'],
                'Origin': 'https://admin.yueyuechuxing.cn',
                '_admin_mask': '0',
                # '_admin_resource_key': 'personCarPush',
                '_admin_resource_key': 'newDataPanelTransmitted',
                '_admin_session_eid': dist[account]['eid'],
                '_admin_sign': '76828b6260c0588b86dff532333faab9',
                '_admin_tk': _admin_tk,
                '_admin_ts': str(round(time.time())),
            }
            if num == 1:
                detail(headers, account)
            else:
                print(parse(headers))
                # print("已导出")
            if account == "江南出行" and num == 0:  # 当导出完成后，把num改成1重新循环进行爬取导出列表
                num = 1
                time.sleep(5)
            elif account == "江南出行" and num == 1:  # 当爬取导出列表页循环完后把num改成3退出while循环
                num = 3
import 经营支付导出_mysql
