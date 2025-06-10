import traceback
import requests
import pandas as pd
from tqdm import trange
import time
from datetime import datetime, timedelta
import random
import io
import os
import zipfile
import pymysql
from sqlalchemy import create_engine, text
import emoji
engine = create_engine('mysql+pymysql://root:M25xx%ycl@HgDataBase:4408/sophon?charset=utf8mb4', echo=False)
with engine.connect() as connection:
    info = connection.execute(
        text("SELECT field_cn, field_en FROM `edsac`.`fields_info` WHERE table_name='push_orders'"))
    field_dict = {row[0]: row[1] for row in info.fetchall()}
print(field_dict)


def dec_zip(file, condition):
    """
    如果经营支付数据太大，下载的就是压缩包，此函数是下载压缩包然后解压并返回解压好的文件的所在路径
    """
    file_name = fr'D:\经营支付压缩包\{condition[3][3::]}.zip'
    print(file_name)
    with open(file_name, 'wb') as file_zip:
        for chunk in file.iter_content(chunk_size=1024):
            file_zip.write(chunk)
    f = zipfile.ZipFile(file_name, 'r')  # 压缩文件位置
    for p in f.namelist():
        f.extract(p, r"D:/经营支付/")  # 解压位置
    f.close()
    files = os.listdir(r"D:/经营支付/")
    return files


def input_info(zcode, header, start_data, end_data):
    url = 'https://admin.yueyuechuxing.cn/bos/admin/v2/sv/exportJob/addJob'
    # 经营支付
    data = {
        "applyReason": '',
        "desensType": 0,
        "agentTenantId": '',
        "adcode": f"{zcode}",
        "agreementId": 10,
        "agreementVersion": 1679563874669,
        "agreementFlag": True,
        "platformType": "0",
        "startDate": f"{start_data}",
        "endDate": f"{end_data}",
        "fieldConfig": "field_config_6_5",
        "exportFields": [
            {"OrderId": "订单号"},
            {"DriverName": "机动车驾驶员姓名"},
            {"LicenseId": "机动车驾驶证号"},
            {"VehicleNo": "车辆号牌"},
            {"DepArea": "上车地点"},
            {"DepTime": "上车时间"},
            {"DestArea": "下车地点"},
            {"DestTime": "下车时间"},
            {"FactPrice": "实收金额"},
            {"Price": "应收金额"},
            {"PayTime": "乘客结算时间"},
            {"OrderMatchTime": "订单完成时间"},
            {"driverId": "司机编号"}
        ],
        "sendStatus": "1"
    }
    while True:
        res = requests.post(url, json=data, headers=header).json()
        if res['code'] == 1:
            break
        print(res)


def writer_file(file_data, brand, export_date, city):
    """
    读取文件后进行数据清洗然后写入数据库
    :return:
    """
    # 将时间列转换为正确的时间格式
    file_data['上车时间'] = pd.to_datetime(file_data['上车时间'], format='%Y%m%d%H%M%S')
    file_data['下车时间'] = pd.to_datetime(file_data['下车时间'], format='%Y%m%d%H%M%S')
    file_data['订单完成时间'] = pd.to_datetime(file_data['订单完成时间'], format='%Y%m%d%H%M%S')
    file_data['乘客结算时间'] = pd.to_datetime(file_data['乘客结算时间'], format='%Y%m%d%H%M%S')
    file_last = file_data[["司机编号", "订单号", "机动车驾驶员姓名", "机动车驾驶证号", "车辆号牌", "上车地点", "上车时间",
                           "下车地点", "下车时间", "订单完成时间", "乘客结算时间", "实收金额", "应收金额"]].copy()
    file_last.insert(0, '品牌', brand)
    file_last.insert(1, '城市', city)
    file_last['数据日期'] = str(start_time)[:-9]
    file_last = file_last.rename(columns=field_dict)
    file_last = file_last.drop_duplicates()
    file_last.to_sql('push_orders', con=engine, if_exists='append', index=False)
    time.sleep(random.uniform(1, 2))
    return True


def detail(header, brand, lst, n):
    global city_list
    global cookie_list
    url = 'https://admin.yueyuechuxing.cn/bos/admin/v2/sv/exportJob/pageList'
    j = 0
    data = {
        "pageNum": 1,
        "pageSize": 100,
        "template": "regulatoryTransmissionExport"
    }
    while True:
        try:
            response = requests.post(url, headers=header, json=data).json()
            if response['code'] == 7600:
                user_input = input(f"cookie已过期{emoji.emojize(':robot:')}，{emoji.emojize(':robot:')}y继续，n停止：")
                if user_input.lower() == 'y':
                    city_list = pd.read_sql(sql2, con=engine)
                    cookie_list = city_list.groupby('brand', as_index=False).first()[['brand', 'cookie', 'token', 'eid']]
                    header["cookie"] = cookie_list["cookie"][n]
                    header["_admin_tk"] = cookie_list["token"][n]
                    header["_admin_eid"], header["_admin_session_eid"] = cookie_list["eid"][n], cookie_list["eid"][n]
                    continue
                elif user_input.lower() == 'n':
                    quit()
                else:
                    print("输入无效，请输入 'y' 表示继续或 'n' 表示停止。")
            if response["data"]["items"]:
                response = response["data"]["items"]
                condition = response[j]["condition"]
                if str(start_time)[:-9] in str(condition[2]):  # 判断是不是我导出的时间段数据
                    if str(brand + condition[0][5::]) not in lst:
                        # print(f'{brand + condition[0][5::]}已经存了')
                        j += 1
                        # time.sleep(random.uniform(2, 3))
                    elif response[j]["status"] == 3:  # 3则表示审批结束，可以下载
                        file_url = "https://admin.yueyuechuxing.cn" + response[j]["artifact"]  # 下载链接
                        file = requests.get(file_url, headers=header, timeout=None)
                        if '.zip' in file_url:  # 如果下载链接是压缩包的话则先下载再进行解压缩
                            print("压缩包")
                            filelist = dec_zip(file, condition)
                            print(f'{emoji.emojize(":rabbit::rabbit::rabbit:")}压缩包列表~{filelist}')
                            for new_file in filelist:
                                datn = pd.read_excel(fr'D:\经营支付\{new_file}',
                                                     dtype={'司机编号': str, '订单号': str, '机动车驾驶证号': str})
                                writer_file(datn, brand, response[j]["createDate"], condition[0][5::])
                                os.remove(fr'D:\经营支付\{new_file}')
                        else:
                            datn = pd.read_excel(io.BytesIO(file.content),
                                                 dtype={'司机编号': str, '订单号': str, '机动车驾驶证号': str})
                            writer_file(datn, brand, response[j]["createDate"], condition[0][5::])
                        j += 1
                        lst.remove(f'{brand+condition[0][5::]}')
                    elif response[j]["status"] == 1:
                        print(f"{emoji.emojize(':ghost::ghost:')}{condition[0][5::]}提交中，"
                              f"看下一个任务{emoji.emojize(':ghost::ghost:')}")
                        j += 1
                        time.sleep(20)
                    elif response[j]["status"] == 2:
                        print(f"{emoji.emojize(':clown_face:')}{condition[0][5::]}导出失败{emoji.emojize(':clown_face:')}")
                        for index, item in enumerate(lst):
                            if item == f'{brand + condition[0][5::]}':
                                lst[index] = f'{brand + condition[0][5::]}(失败)'
                        j += 1
                    else:
                        print(f"{condition[0][5::]}等待"
                              f"{emoji.emojize(':spouting_whale::spouting_whale::spouting_whale:')}审批~或者正在新建")
                        j += 1
                        time.sleep(60*10)
                else:
                    print(f"{emoji.emojize(':enraged_face:')}下一个品牌{emoji.emojize(':enraged_face:')}")
                    return lst
            time.sleep(random.uniform(2, 3))
        except requests.exceptions.ConnectionError:
            print(f'连接超时{emoji.emojize(":dizzy::dizzy::dizzy::dizzy:")}')
            time.sleep(random.uniform(1, 2))
        except Exception as r:
            print(f'程序异常{emoji.emojize(":loudly_crying_face:")}======>>>{r}')
            traceback.print_exc()
            quit()


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


# if __name__ == '__main__':
sql2 = """SELECT 
    DISTINCT a.brand,
    a.city,
    b.adcode,
    c.cookie,
    c.token,
    c.eid,
    SUM(CAST(pay_order_count AS SIGNED)) AS pay_order_count
FROM push_order_tally_stats a
LEFT JOIN (SELECT DISTINCT city, adcode FROM `edsac`.push_city_info) b 
    ON a.city = b.city
LEFT JOIN accounts c 
    ON a.brand = c.brand
WHERE 
    a.date_time = CURDATE() - INTERVAL 1 DAY 
    AND platform = '交通部' 
    AND pay_order_count > 0
GROUP BY 
    a.brand, 
    a.city, 
    b.adcode,
    c.cookie, 
    c.token, 
    c.eid 
ORDER BY a.brand;"""
# start_date = '2024-11-17'
# end_date = '2024-11-22'
# sql = """SELECT DISTINCT a.品牌,a.城市,b.[行政区划代码],c.cookie,c._admin_tk,c.sesseid,SUM(CAST(上传订单数 AS INT)) 上传订单数
# FROM [dbo].[推送监控] a
# LEFT JOIN (SELECT DISTINCT 所属城市,行政区划代码 from python.dbo.品牌完单城市) b on a.[城市]=b.[所属城市]
# LEFT JOIN dbo.[小周账号信息配置表] c on a.品牌=c.brand
# where 日期 >= '{start_date}' and 日期 <= '{end_date}' and 推送标准='交通部' and 上传订单数>0
# GROUP BY a.品牌,a.城市,b.[行政区划代码],c.cookie,c._admin_tk,c.sesseid ORDER BY a.品牌;""".format(
#     start_date=start_date, end_date=end_date)
city_list = pd.read_sql(sql2, con=engine)
cookie_list = city_list.groupby('brand', as_index=False).first()[['brand', 'cookie', 'token', 'eid']]
# 使用 groupby 和 nunique 统计每个品牌对应的不同城市数量
city_len = city_list.groupby("brand")["city"].nunique()
# 获取昨天的日期
yesterday = datetime.now() - timedelta(days=2)
# start_date = datetime.strptime(start_date, '%Y-%m-%d')
# end_date = datetime.strptime(end_date, '%Y-%m-%d')
# 设置结束时间为 23:59:59
start_date = yesterday.replace(hour=00, minute=00, second=00)
end_date = yesterday.replace(hour=23, minute=59, second=59)
# 格式化为字符串
start_time = start_date.strftime('%Y-%m-%d %H:%M:%S')
end_time = end_date.strftime('%Y-%m-%d %H:%M:%S')
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.183',
    '_admin_sign': '76828b6260c0588b86dff532333faab9',
    '_admin_ts': str(round(time.time()))
}
sql = f"""delete from push_orders where date_time='{str(start_time)[:-9]}';"""
delete(sql)
# 先把所有品牌导出
for i in trange(len(city_list)):  # 循环城市列表，按城市导出
    while True:
        try:
            headers["cookie"] = city_list["cookie"][i]
            headers["_admin_tk"] = city_list["token"][i]
            headers["_admin_eid"], headers["_admin_session_eid"] = city_list["eid"][i], city_list["eid"][i]
            code = int(city_list["adcode"][i])
            input_info(code, headers, start_time, end_time)
            time.sleep(random.uniform(2, 3))
            break
        except Exception as f:
            traceback.print_exc()
            user_input = input(f"cookie已过期{emoji.emojize(':robot:')}，{emoji.emojize(':robot:')}y继续，n停止：")
            if user_input.lower() == 'y':
                city_list = pd.read_sql(sql2, con=engine)
                continue
            elif user_input.lower() == 'n':
                quit()
            else:
                print("输入无效，请输入 'y' 表示继续或 'n' 表示停止。")
print(f'{emoji.emojize(":ghost::ghost::ghost:")}已经全部导出~')
time.sleep(60 * 5)
# 查看哪些是可以下载的
result_list = [f'{brand}{city}' for brand, city in zip(city_list['brand'], city_list['city'])]
k = 0
while True:
    if not any("失败" not in item for item in result_list):  # 如果列表为空或者只有失败的城市的话就可以退出循环了
        # print(result_list)
        print(f'{emoji.emojize(":ghost::ghost::ghost:")}收工下班~{emoji.emojize(":ghost::ghost::ghost:")}')
        break
    headers["cookie"] = cookie_list["cookie"][k]
    headers["_admin_tk"] = cookie_list["token"][k]
    headers["_admin_eid"], headers["_admin_session_eid"] = cookie_list["eid"][k], cookie_list["eid"][k]
    brank = cookie_list["brand"][k]
    print(f'{emoji.emojize(":partying_face:")}{cookie_list["brand"][k]}开始{emoji.emojize(":partying_face:")}')
    result_list = detail(headers, brank, result_list, k)
    print(result_list)
    k = (k + 1) % 5
time.sleep(10)