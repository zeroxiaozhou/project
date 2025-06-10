import traceback
import requests
import pandas as pd
import browser_cookie3
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import random
from sqlalchemy import create_engine, text
import pymysql
import emoji

db = pymysql.connect(
    host='HgDataBase',
    port=4408,
    user='root',
    password='M25xx%ycl',
    database='sophon',
    charset='utf8mb4'
)
engine = create_engine('mysql+pymysql://root:M25xx%ycl@HgDataBase:4408/sophon?utf8mb4', echo=False)

def delete(sql):
    cursor = db.cursor()
    cursor.execute(sql)
    db.commit()


def get_cookie():
    while True:
        ck_df = pd.DataFrame()
        for i in dit:
            cookie_path = browser_cookie3.chrome(
                cookie_file=rf'C:\Users\XYCX\AppData\Local\Google\Chrome\User Data\{dit[i]["file"]}\Network\Cookies',
                domain_name='admin.yueyuechuxing.cn')
            string, admin_tk = '', 'error'
            for cookie_file in cookie_path:
                if cookie_file.name == 'stk':
                    string = string + cookie_file.name + '=' + cookie_file.value + ';'
                    admin_tk = cookie_file.value
                else:
                    string = string + cookie_file.name + '=' + cookie_file.value + ';'
            ck_df = ck_df._append(
                pd.DataFrame({'account': '小周', 'brand': i, 'eid': dit[i]["eid"], 'session_eid': dit[i]["eid"],
                              'token': admin_tk, 'cookie': string}, index=pd.Index([len(ck_df)])))
            time.sleep(random.uniform(0.8, 1))
        if 'error' in ck_df['token'].values:
            print(f'cookie错误，正在重新写入{emoji.emojize(":warning::warning::warning:")}')
            time.sleep(random.uniform(2, 3))
        else:
            ck_df.to_sql('accounts', con=engine, if_exists='append', index=False)  # append 累加replace重新创表
            print(f'已写入数据库{emoji.emojize(":partying_face::partying_face::partying_face:")}')
            break


def wanshan():
    cursor = db.cursor()
    # cursor.execute("""delete from daily_credential_monitoring WHERE date_time = CURDATE() - INTERVAL 1 DAY;""")
    # db.commit()
    cursor.execute("""
INSERT INTO daily_credential_monitoring
SELECT DISTINCT 
    a.driverId AS driver_id,
    COALESCE(a.vehicleNo, '无000000') AS plate_no, 
    d.city, 
    c.brand, 
    COALESCE(b.id_card, '100000000000000005'), 
    COALESCE(a.driverName, '无数据') AS driver_name, 
    COALESCE(b.licence_no, '10000001'), 
    CURDATE() - INTERVAL 1 DAY AS date_time  -- MySQL 日期函数替换
FROM 
    driver_car_push a 
LEFT JOIN 
    drivers b ON a.driverId = b.driver_id 
LEFT JOIN 
    accounts c ON a.tenantId = c.eid 
LEFT JOIN 
    edsac.push_city_info d ON a.adcode = d.adcode;
""")
    # cursor.execute("""
    # insert into daily_credential_monitoring
    # SELECT DISTINCT
    #     a.driverId, AS driver_id
    #     COALESCE(a.vehicleNo, '无000000') AS plate_no,
    #     d.城市名 AS city,
    #     c.brand AS brand,
    #     COALESCE(b.身份证号, '100000000000000005') AS id_card,
    #     COALESCE(a.driverName, '无数据') AS driver_name,
    #     COALESCE(b.车辆运输证号, '10000001') AS licence_no,
    #     CONVERT(varchar(10), GETDATE() - 1, 23) AS date_time
    # FROM
    #     driver_car_push a
    # LEFT JOIN
    #    driver b ON a.driverId = b.司机ID
    # LEFT JOIN
    #     accounts c ON a.tenantId = c.sesseid
    # LEFT JOIN
    #     [配置表].[dbo].[城市行政id] d ON a.adcode = d.行政区划代码
    # """)
    # db.commit()
    # cursor.execute("""delete from 证件合规信息查询.dbo.[每日推送司机累计] where convert(varchar(10),更新日期,23)=CONVERT(varchar(10), GETDATE()-1, 23)""")
    # db.commit()
    # cursor.execute("""insert into 证件合规信息查询.dbo.每日推送司机累计 select * from 证件合规信息查询.dbo.每日需要查询数据""")
    # cursor.execute("""insert into 每日推送司机累计 select * from daily_credential_monitoring""")
    db.commit()
    db.close()
    print(f'完善信息处理完成{emoji.emojize(":smiling_face_with_hearts::smiling_face_with_hearts:")}')


def parse():
    while True:
        try:
            data = {
                'adcode': str(da['adcode'][j]),
                'pageNum': 1,
                'pageSize': 100,
                'testGroup': "0"
            }
            res = requests.post(url, json=data, headers=header, timeout=30)
            total = res.json()['data']['totalNum']
            result = res.json()['data']['totalPage']
            print(f"{da['brand'][j]}, {da['city'][j]}, {str(da['adcode'][j])} 条数：{total} 页数：{result}")
            res.close()
            break
        except Exception:
            traceback.print_exc()
            time.sleep(random.uniform(1, 2))
            ck = pd.read_sql("select * from accounts where account='小周'and brand='%s'" % dit[account]['user'], con=engine)
            header['cookie'] = ck['cookie'][0]
            header['_admin_tk'] = ck['token'][0]
    return int(result)


def detail(city_adcode, g):
    while True:
        try:
            new_data = {'adcode': str(city_adcode),
                        'pageNum': g,
                        'pageSize': '100',
                        'testGroup': "0",
                        }
            new_res = requests.session().post(url, json=new_data, headers=header)
            new_result = new_res.json()['data']
            if new_result is not None:
                new_df = pd.DataFrame(new_result['items'])
                time.sleep(random.uniform(0.8, 0.1))
                break  # 当前页请求成功后，跳出循环
            else:
                print(new_res.json(), '失败的页数', new_data)
                time.sleep(20)
        except Exception as c:
            # traceback.print_exc()
            print('报错原因', c)
            time.sleep(random.uniform(1, 1.5))
    return new_df, city_adcode


sql = f"""DELETE FROM driver_car_push"""
sql2 = '''delete from accounts'''
delete(sql)
delete(sql2)
url = 'https://admin.yueyuechuxing.cn/admin/v1/sv/driver/findSummaryList'
# url = 'https://admin.yueyuechuxing.cn/bos/admin/v1/sv/driver/findSummaryList'
dit = {
    '蛋卷出行': {'file': 'Profile 5', 'user': '蛋卷出行', 'eid': '800761'},
    '喜行约车': {'file': 'Profile 1', 'user': '喜行约车', 'eid': '800432'},
    '神州专车': {'file': 'Profile 2', 'user': '神州专车', 'eid': '800447'},
    '星徽出行': {'file': 'Profile 4', 'user': '星徽出行', 'eid': '800161'},
    '江南出行': {'file': 'Profile 3', 'user': '江南出行', 'eid': '800188'},
}
get_cookie()

start_time = time.time()
for account in dit:
    ck = pd.read_sql("select * from accounts where account='小周'and brand='%s'" % dit[account]['user'], con=engine)
    cookie = ck['cookie'][0]
    _admin_tk = ck['token'][0]
    sql = "select * from edsac.push_city_info where left(brand,4)='%s'" % account
    da = pd.read_sql(sql, con=engine)
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.54',
        'cookie': cookie,
        '_admin_eid': dit[account]['eid'],
        '_admin_mask': '0',
        '_admin_resource_key': 'personCarPush',
        '_admin_session_eid': dit[account]['eid'],
        '_admin_sign': '76828b6260c0588b86dff532333faab9',
        '_admin_tk': _admin_tk,
        '_admin_ts': str(round(time.time())),
    }
    final_df = pd.DataFrame()  # 用于保存最终结果
    # 创建线程池
    pool = ThreadPoolExecutor(20)
    future_list = []
    for j in range(len(da['adcode'])):
        result = parse() + 1
        time.sleep(random.uniform(0.3, 0.4))
        for g in tqdm(range(1, result), desc=f'{da["city"][j]}'):  # 将进度条与行政区划代码关联起来
            future = pool.submit(detail, da['adcode'][j], g)
            future_list.append(future)
            time.sleep(random.uniform(0.7, 0.8))
            # 每提交20个任务，等待前面提交的任务完成, 当任务不满足20个线程的时候，那么最大线程数就等于最大任务数
            # 如果任务数等于线程池大小，就等待一个任务完成并将其结果保存到 final_df 中
            if g % 20 == 0 or g == result - 1:
                for completed_future in as_completed(future_list):
                    new_df, city_adcode = completed_future.result()
                    final_df = final_df._append(new_df, ignore_index=True)
                future_list.clear()
    final_df = final_df[['tenantId', 'adcode', 'driverId', 'driverName', 'vehicleNo']]
    while True:
        try:
            final_df.to_sql('driver_car_push', con=engine, if_exists='append', index=False)
            break
        except Exception as e:
            print(f'写入数据库失败{e}')
            time.sleep(random.uniform(2, 3))
    print(f'=============={account}完成{emoji.emojize(":party_popper::party_popper::party_popper:")}=================')
wanshan()
end_time = time.time()
total_time = end_time - start_time
print(f'程序运行总时间为：{total_time // 60} 分钟{emoji.emojize(":exploding_head::exploding_head::exploding_head:")}')
print("爬取司机完善字段好了！！！！！！！！！！！！！！！")
print("可以开始城市查询了！！！！！！！！！！")


print("开始取消推送解绑车辆")
import 车辆完善_mysql
import 取消推送_mysql
print("解绑车取消推送完成")
