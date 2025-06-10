import io
import random
import traceback
import zipfile
import os
import pandas as pd
import time
from datetime import datetime, timedelta
import requests
import pymysql
import warnings
import emoji
import numpy
from sqlalchemy import create_engine, text
engine = create_engine('mysql+pymysql://root:M25xx%ycl@HgDataBase:4408/sophon?charset=utf8mb4', echo=False)
db = pymysql.connect(
    host='HgDataBase',
    port=4408,
    user='root',
    password='M25xx%ycl',
    database='sophon',
)
# 忽略特定类型的警告
warnings.filterwarnings("ignore", category=pd.errors.DtypeWarning)
with engine.connect() as connection:
    info = connection.execute(text("SELECT field_cn, field_en FROM `edsac`.`fields_info` WHERE table_name='orders'"))
    field_dict = {row[0]: row[1] for row in info.fetchall()}
print(field_dict)



def dec_zip(file, condition):
    """
    如果经营支付数据太大，下载的就是压缩包，此函数是下载压缩包然后解压并返回解压好的文件的所在路径
    """
    file_name = fr'D:\订单列表压缩包\{condition}.zip'
    print(file_name)
    with open(file_name, 'wb') as file_zip:
        for chunk in file.iter_content(chunk_size=1024):
            file_zip.write(chunk)
    f = zipfile.ZipFile(file_name, 'r')  # 压缩文件位置
    for p in f.namelist():
        f.extract(p, r"D:/订单列表/")  # 解压位置
    f.close()
    files = os.listdir(r"D:/订单列表/")
    return files


def field(field_datn):
    """
    处理字段
    """
    field_datn['订单号'] = field_datn['订单号'].apply(lambda x: x.replace('=', '').replace('"', ''))
    # field_datn['渠道打车订单号'] = field_datn['渠道打车订单号'].apply(lambda x: x.replace('=', '').replace('"', ''))
    field_datn['渠道打车订单号'] = field_datn['渠道打车订单号'].apply(
        lambda x: x.replace('=', '').replace('"', '') if isinstance(x, str) else x
    )
    field_datn['乘客编号'] = field_datn['乘客编号'].apply(lambda x: x.replace('=', '').replace('"', ''))
    field_datn['司机编号'] = field_datn['司机编号'].apply(lambda x: x.replace('=', '').replace('"', ''))
    field_datn['司机手机号'] = field_datn['司机手机号'].apply(lambda x: x.replace('=', '').replace('"', ''))
    field_datn['综合能耗费'] = field_datn['综合能耗费'].apply(lambda x: x.replace('=', '').replace('"', ''))
    field_datn['节假日服务费'] = field_datn['节假日服务费'].apply(lambda x: x.replace('=', '').replace('"', ''))
    field_datn['预估时间'] = field_datn['预估时间'].apply(
        lambda x: x.replace('=', '').replace('"', '') if isinstance(x, str) else x)
    field_datn['实际时长'] = field_datn['实际时长'].apply(
        lambda x: x.replace('=', '').replace('"', '') if isinstance(x, str) else x)
    field_datn['拼车行程ID'] = field_datn['拼车行程ID'].apply(
        lambda x: x.replace('=', '').replace('"', '') if isinstance(x, str) else x)
    return field_datn


def order_list(header, brand, res_lst, number):
    """
    下载订单列表
    """
    global cookie_list
    q = 0
    while True:
        result = requests.post("https://admin.yueyuechuxing.cn/bos/admin/v1/base/export/task/list",
                               headers=header, json={'pageNum': 1, 'pageSize': 100, 'templateType': 'orderList'})
        response = result.json()
        if response['code'] == 7600:
            user_input = input(f"cookie已过期{emoji.emojize(':robot:')}，{emoji.emojize(':robot:')}y继续，n停止：")
            if user_input.lower() == 'y':
                cookie_list = pd.read_sql("select * from accounts where account='小周'", con=engine)
                header["_admin_eid"], header["_admin_session_eid"] = cookie_list["session_eid"][number], cookie_list["session_eid"][number]
                header["cookie"] = cookie_list["cookie"][number]
                header["_admin_tk"] = cookie_list["token"][number]
                continue
            elif user_input.lower() == 'n':
                quit()
            else:
                print("输入无效，请输入 'y' 表示继续或 'n' 表示停止。")
        if response["data"]["items"]:
            data_list = response["data"]["items"]
            # if str(start_Time)[:-9] in str(data_list[q]['taskContent'][1]):  # 先判断是否是我需要的时间段数据
            if brand not in res_lst:  # 判断是否已经下载过了
                print(f"{emoji.emojize(':enraged_face:')}已经存过了{emoji.emojize(':enraged_face:')}")
                time.sleep(20)
            elif data_list[q]['taskStatus'] == 3:  # 判断是否可以下载
                down_url = f"https://admin.yueyuechuxing.cn{data_list[q]['artifact']}"  # 下载链接
                file = requests.get(down_url, headers=headers)
                if '.zip' in down_url:  # 如果下载链接是压缩包的话则先下载再进行解压缩
                    filelist = dec_zip(file, brand)
                    print(f'{emoji.emojize(":rabbit::rabbit::rabbit:")}压缩包列表~{filelist}')
                    for new_file in filelist:
                        print(f'{emoji.emojize(":rabbit::rabbit::rabbit:")}{new_file}')
                        datn = pd.read_csv(fr'D:\订单列表\{new_file}')
                        datn =field(datn)
                        while True:
                            try:
                                datn = datn.rename(columns=field_dict)
                                datn.to_sql('orders', con=engine, if_exists='append', index=False)
                                break
                            except Exception as t:
                                print(f"写入错误, {t}")
                                datn.to_csv(rf"D:\双证合规\{brand}{str(start_Time)}.csv", index=False)
                                time.sleep(20)
                        os.remove(fr'D:\订单列表\{new_file}')
                else:
                    datn = pd.read_csv(io.BytesIO(file.content))
                    datn =field(datn)
                    while True:
                        try:
                            datn = datn.rename(columns=field_dict)
                            datn.to_sql('orders', con=engine, if_exists='append', index=False)
                            break
                        except Exception as o:
                            print(f"写入错误, {o}")
                            datn.to_csv(rf"D:\双证合规\{brand}{str(start_Time)}.csv", index=False)
                            time.sleep(20)
                res_lst.remove(f'{brand}')
            elif data_list[q]["taskStatus"] == 1:
                print(
                    f"{emoji.emojize(':ghost::ghost:')}{brand}提交中看一个品牌{emoji.emojize(':ghost::ghost:')}")
                time.sleep(20)
            elif data_list[q]["taskStatus"] == 2:
                print(f"{emoji.emojize(':clown_face:')}{brand}导出失败{emoji.emojize(':clown_face:')}")
                for index, item in enumerate(res_lst):
                    if item == f'{brand}':
                        res_lst[index] = f'{brand}(失败)'
            else:
                print(f"{brand}等待"
                      f"{emoji.emojize(':spouting_whale::spouting_whale::spouting_whale:')}审批~或者正在新建")
                time.sleep(60 * 5)
            time.sleep(random.uniform(3, 6))
            return res_lst
            # else:
            #     q += 1


def delete(s):
    cursor = db.cursor()
    cursor.execute(s)
    db.commit()


start_date_obj = datetime.now() - timedelta(days=1)
# start_obj = "2024-02-25"
# obj = datetime.strptime(start_obj, "%Y-%m-%d")
# u = 0
# while start_date_obj.month != 1 or start_date_obj.day != 1:
#     start_date_obj = obj - timedelta(days=u)
#     print(start_date_obj.month, start_date_obj.day, u)
start_Time = start_date_obj.strftime('%Y-%m-%d')
# 起始时间戳
start_date_obj = start_date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
startTime = int(start_date_obj.timestamp() * 1000)
# 截止时间戳
end_time_obj = start_date_obj.replace(hour=23, minute=59, second=59, microsecond=999999)
endTime = int(end_time_obj.timestamp() * 1000)
sql = f"""
DELETE FROM orders 
WHERE pay_time >= '{start_date_obj.replace(hour=0, minute=0, second=0, microsecond=0)}'
  AND pay_time < '{datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)}'
"""
delete(sql)
dit = {
    '喜行约车': {'file': 'Profile 1', 'user': '喜行约车', 'eid': '800432'},
    '神州专车': {'file': 'Profile 2', 'user': '神州专车', 'eid': '800447'},
    '蛋卷出行': {'file': 'Profile 5', 'user': '蛋卷出行', 'eid': '800761'},
    '星徽出行': {'file': 'Profile 4', 'user': '星徽出行', 'eid': '800161'},
    '江南出行': {'file': 'Profile 3', 'user': '江南出行', 'eid': '800188'},
}
headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
            '_admin_resource_key': 'driverAssessment-Data',
            '_admin_sign': '76828b6260c0588b86dff532333faab9',
            '_admin_ts': str(round(time.time())),
        }
columns_list = ['订单号', '渠道打车订单号', '乘客编号', '司机编号', '司机手机号', '实际时长', '综合能耗费', '节假日服务费']
cookie_list = pd.read_sql("select * from accounts where account='小周'", con=engine)
# 申请导出订单列表
for account in dit:
    ck = pd.read_sql("select * from accounts where account='小周'and brand='%s'" % dit[account]['user'], con=engine)
    url = 'https://admin.yueyuechuxing.cn/bos/admin/v2/order/seniorExport/addFileDownload'
    while True:
        headers["cookie"] = ck['cookie'][0]
        headers["_admin_tk"] = ck['token'][0]
        headers["_admin_eid"], headers["_admin_session_eid"] = dit[account]['eid'], dit[account]['eid']
        try:
            data = {
                    "desensitizeFieldInfos": '[{"fieldName":"driverName","fieldTitle":"司机姓名","selected":1},{"fieldName":"driverNumber","fieldTitle":"司机手机号","selected":1},{"fieldName":"carNumber","fieldTitle":"车牌","selected":1},{"fieldName":"startAddress","fieldTitle":"出发地","selected":1},{"fieldName":"endAddress","fieldTitle":"目的地","selected":1}]',
                    "exportSourceType": 2,
                    "description": f"支付时间{start_Time}, {startTime}, {endTime}",
                    "desensType": 0,
                    "pageFlag": "orderList",
                    "agreementId": 10,
                    "agreementVersion": 1679563874669,
                    "agreementFlag": 1,
                    "orderPayStartDate": startTime,
                    "orderPayEndDate": endTime,
                    "pageNum": 1,
                    "pageSize": 10,
                    "showEtravelCancelOrderFlag": 0,
                    "exportTenantIds": [dit[account]['eid']]
                }
            res = requests.post(url, headers=headers, json=data)
            print(f'当前品牌{account} {res.json()}')
            if res.json()['code'] == 1:
                time.sleep(random.uniform(2, 3))
                break
            elif res.json()['code'] == 7600:
                user_input = input(f"cookie已过期{emoji.emojize(':robot:')}，{emoji.emojize(':robot:')}y继续，n停止：")
                if user_input.lower() == 'y':
                    ck = pd.read_sql("select * from accounts where account='小周'and brand='%s'" % dit[account]['user'], con=engine)
                    continue
                elif user_input.lower() == 'n':
                    quit()
                else:
                    print("输入无效，请输入 'y' 表示继续或 'n' 表示停止。")
            elif res.json()['code'] == -99999:
                print(f'系统问题，等待十分钟{emoji.emojize(":carp_streamer::carp_streamer::carp_streamer:")}')
                time.sleep(300)
            else:
                print(f'导出失败，重来{emoji.emojize(":carp_streamer::carp_streamer::carp_streamer:")}')
                time.sleep(random.uniform(2, 3))
        except requests.exceptions.ConnectionError:
            print(f'连接超时{emoji.emojize(":dizzy::dizzy::dizzy::dizzy:")}')
            traceback.print_exc()
            time.sleep(random.uniform(1, 2))
        except Exception as e:
            traceback.print_exc()
            print(f'程序异常{emoji.emojize(":hear_no_evil_monkey::hear_no_evil_monkey:")}{e}')
            time.sleep(random.uniform(2, 5))
print(f'=====订单列表已申请导出{emoji.emojize(":partying_face::partying_face::partying_face:")}=====')
time.sleep(60*4)
brand_list = ["神州专车", "星徽出行", "江南出行", "蛋卷出行", "喜行约车"]
num = 0
while True:
    if not any("失败" not in item for item in brand_list):  # 如果列表为空或者只有失败的城市的话就可以退出循环了
        # print(brand_list)
        print(f'{emoji.emojize(":ghost::ghost::ghost:")}收工下班~{emoji.emojize(":ghost::ghost::ghost:")}')
        break
    try:
        headers["_admin_eid"], headers["_admin_session_eid"] = cookie_list["session_eid"][num], cookie_list["session_eid"][num]
        headers["cookie"] = cookie_list["cookie"][num]
        headers["_admin_tk"] = cookie_list["token"][num]
        print(f'{emoji.emojize(":partying_face:")}{cookie_list["brand"][num]}开始{emoji.emojize(":partying_face:")}')
        result_list = order_list(headers, cookie_list['brand'][num], brand_list, num)
        print(result_list)
        num = (num + 1) % 5
    except Exception as f:
        print(f"程序错误，{f}")
        traceback.print_exc()
import update_order_driver_info
update_order_driver_info.main(1)
# u += 1
