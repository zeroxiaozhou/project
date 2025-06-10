import io
import random
import traceback
import zipfile
import os
import pandas as pd
import time
from datetime import datetime, timedelta
from sqlalchemy import create_engine
import requests
import pymssql
import emoji
def delete(sql, result):
    db = pymssql.connect(server='LAPTOP-HHMD1A48\XYCX', database='python', charset='utf8', user='sa', password='Xy202204')
    cursor = db.cursor()
    cursor.execute(sql, result)
    db.commit()
    db.close()


def to_day30ago_kpi():
    date = time.strftime("%Y-%m-%d", time.localtime(time.time() - 60 * 60 * 24))
    db = pymssql.connect(server='LAPTOP-HHMD1A48\XYCX', database='证件合规信息查询',
                         charset='utf8', user='sa', password='Xy202204')
    cursor = db.cursor()
    cursor.execute("""delete from [证件合规信息查询].[dbo].[近30天司机考核]""")
    db.commit()
    cursor.execute(
        f"""insert into [证件合规信息查询].[dbo].[近30天司机考核] select * from python.dbo.司机考核数据日数据 WHERE 数据日期>='{date}'""")
    # cursor.execute(
    #     f"""insert into [证件合规信息查询].[dbo].[近30天司机考核] select * from python.dbo.司机考核数据日数据 WHERE 数据日期 >='{date}'""")
    db.commit()
    db.close()
    print(f'近30天司机考核 执行完成{emoji.emojize(":popcorn::popcorn::popcorn:")}')


def to_day60ago_info():
    db = pymssql.connect(server='LAPTOP-HHMD1A48\XYCX', database='python', charset='utf8', user='sa',
                         password='Xy202204')
    cursor = db.cursor()
    cursor.execute("""DECLARE @day30ago DATE = DATEADD(day, -60, CONVERT(date, GETDATE()))
DECLARE @today DATE = convert(varchar(10),getdate(),23)
delete from [证件合规信息查询].[dbo].[全量信息]
insert into [证件合规信息查询].[dbo].[全量信息]
SELECT DISTINCT kpi.司机ID,
                ISNULL(driver.车牌号,'无000000'),
                kpi.城市,
                kpi.品牌,
                ISNULL(driver.身份证号,'100000000000000001'),
                driver.姓名,
                driver.车辆运输证号,
                @today AS 更新日期
FROM (SELECT DISTINCT 司机ID, LEFT(品牌, 4) AS 品牌, 城市 FROM python.dbo.司机考核数据日数据 where 数据日期 >= @day30ago) kpi
         LEFT JOIN (SELECT DISTINCT 司机ID, 城市, 品牌, 身份证号, 车牌号, 姓名, 车辆运输证号 FROM 证件合规信息查询.dbo.司机信息) driver
                   ON kpi.司机ID = driver.司机ID and kpi.城市 = driver.城市 and kpi.品牌 = driver.品牌""")
    db.commit()
    print(f'全量信息表更新完毕{emoji.emojize(":saluting_face::saluting_face::saluting_face:")}')
    cursor.execute("""-- 变量
DECLARE @day30ago DATE = DATEADD(day,-30,CONVERT(date, GETDATE()));
DECLARE @month_old INT = MONTH(DATEADD(MONTH,-1,GETDATE()))
-- 近30天双证完单 更新
delete from [证件合规信息查询].[dbo].[近30天双证完单]
insert into [证件合规信息查询].[dbo].[近30天双证完单]
select left(t1.品牌,4) 品牌,t1.城市,[人证],[车证],count(distinct t1.司机id) 去重完单司机数,count(*) 完单司机数,sum([完单量(总)])完单量
from (select * from [python].[dbo].[司机考核数据日数据] where convert(varchar(10), 末次完单时间, 23) >= @day30ago) t1
left join [证件合规信息查询].[dbo].[双证有效记录] t2
on t1.司机id=t2.司机id and left(t1.品牌,4) =left(t2.品牌,4)  and t1.城市=t2.城市
group by left(t1.品牌,4),t1.城市,[人证],[车证];
-- 近30天双证出车 更新
delete from [证件合规信息查询].[dbo].[近30天双证出车];
insert into [证件合规信息查询].[dbo].[近30天双证出车]
select left(kpi.品牌,4) as 品牌, kpi.城市, [人证], [车证], count(distinct kpi.司机id) 去重出车司机数
from [证件合规信息查询].[dbo].[近30天司机考核] kpi
left join [证件合规信息查询].[dbo].[双证有效记录] info
on kpi.司机id=info.司机ID and left(kpi.品牌,4) =left(info.品牌,4) and kpi.城市=info.城市
where convert(varchar(10), 末次出车时间, 23) >= @day30ago
group by left(kpi.品牌, 4), kpi.城市, 人证, 车证""")
    db.commit()
    db.close()
    print(f'近60天数据源更新完毕{emoji.emojize(":smiling_face_with_open_hands::smiling_face_with_open_hands:")}')


# 起始时间
# start_date = datetime.strptime('2023-12-31', '%Y-%m-%d')
# while start_date.month != 1 or start_date.day != 1:
# start_date -= timedelta(days=1)
start_date = datetime.now() - timedelta(days=1)
start_Time = start_date.strftime('%Y-%m-%d')
# 起始时间戳
startTime = int(start_date.timestamp() * 1000)
# 截止时间戳
end_time_obj = start_date.replace(hour=23, minute=59, second=59, microsecond=999999)
endTime = int(end_time_obj.timestamp() * 1000)
sql = "delete from python.[dbo].[司机考核数据日数据] where convert(varchar(10),末次完单时间,23)=%s"
delete(sql, start_Time)
time.sleep(2)
engine = create_engine('mssql+pymssql://sa:Xy202204@LAPTOP-HHMD1A48\XYCX/python?charset=utf8', echo=False)
dit = {
'蛋卷出行': {'file': 'Profile 5', 'user': 'danjuan', 'eid': '800761', 'sesseid': '800761'},
    '喜行约车': {'file': 'Profile 1', 'user': 'admin', 'eid': '800432', 'sesseid': '800432'},
    '神州专车': {'file': 'Profile 2', 'user': 'shenzhou', 'eid': '800447', 'sesseid': '800447'},

    '星徽出行': {'file': 'Profile 4', 'user': 'xinghui', 'eid': '800161', 'sesseid': '800161'},
    '江南出行': {'file': 'Profile 3', 'user': 'jiangnan', 'eid': '800188', 'sesseid': '800188'},
}

# 申请导出司机考核
# for account in dit:
#     ck = pd.read_sql("select * from 证件合规信息查询.dbo.小周账号信息配置表 where Account='%s'"% dit[account]['user'], con=engine)
#     url = 'https://admin.yueyuechuxing.cn/bos/admin/v1/common/export/server/standardExport'
#     header = {
#         'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
#         '_admin_resource_key': 'driverAssessment-Data',
#         '_admin_eid': dit[account]['eid'],
#         '_window_id': '1747098371791',
#         '_admin_session_eid': dit[account]['sesseid'],
#         '_admin_sign': '76828b6260c0588b86dff532333faab9',
#         '_admin_ts': str(round(time.time())),
#     }
#     while True:
#         header['cookie'] = ck['cookie'][0]
#         header['_admin_tk'] = ck['_admin_tk'][0]
#         try:
#             data = {
#                 'agreementFlag': 1,
#                 'agreementId': '10',
#                 'agreementVersion': '1679563874669',
#                 'desens': 0,
#                 'desensitizeFieldInfos': '[{"fieldName":"mobile","fieldTitle":"司机手机号","selected":1},{"fieldName":"driver_name","fieldTitle":"司机姓名","selected":1},{"fieldName":"plate_no","fieldTitle":"车牌号","selected":1}]',
#                 'exportParams': {
#                     # value:[开始时间戳-结束时间戳] matchValue：（起始时间，截止时间）
#                     'ds': {'value': [startTime, endTime], 'matchValue': "%s~%s" % (start_Time, start_Time)},
#                     'employee_type': {'matchValue': "全部", 'value': []},
#                     # 'finish_order_sum': {'value': [1, None], 'matchValue': "大于1"},
#                     'state': {'matchValue': "正常", 'value': ["3"]},
#                     'is_plat_dispatcher': {'matchValue': '全部', 'value': [0, 1]},
#                     'dispatcher_realtime': {'matchValue': '', 'value': ['0', '1']},
#                     'dispatcher_booking': {'matchValue': '', 'value': ['0', '1']},
#                     'resign_state': {'matchValue': '全部', 'value': [0, 1, 2]},
#                     'tenant_id': {'matchValue': account, 'value': [dit[account]['sesseid']]}},
#                 'desensExportFlag': False,
#                 'pageFlag': "assetsDriverAssessBIExport"
#             }
#             res = requests.post(url, headers=header, json=data, timeout=90)
#             print(f'{account} {res.json()}')
#             if res.json()['code'] == 1:
#                 time.sleep(random.uniform(2, 3))
#                 break
#             elif res.json()['code'] == 7600:
#                 user_input = input(f"cookie已过期{emoji.emojize(':robot:')}，{emoji.emojize(':robot:')}y继续，n停止：")
#                 if user_input.lower() == 'y':
#                     ck = pd.read_sql(
#                         "select * from 证件合规信息查询.dbo.小周账号信息配置表 where Account='%s'" % dit[account]['user'],
#                         con=engine)
#                     continue
#                 elif user_input.lower() == 'n':
#                     quit()
#                 else:
#                     print("输入无效，请输入 'y' 表示继续或 'n' 表示停止。")
#             else:
#                 print(f'导出失败，重来{emoji.emojize(":carp_streamer::carp_streamer::carp_streamer:")}')
#                 time.sleep(random.uniform(2, 3))
#         except requests.exceptions.ConnectionError:
#             print(f'连接超时{emoji.emojize(":dizzy::dizzy::dizzy::dizzy:")}')
#             traceback.print_exc()
#             time.sleep(random.uniform(1, 2))
#         except Exception as e:
#             print(f'程序异常( ´◔︎ ‸◔︎`)正在重新爬取(꒪⌓꒪){emoji.emojize(":hear_no_evil_monkey::hear_no_evil_monkey:")}')
#             traceback.print_exc()
#             time.sleep(random.uniform(3, 6))
# print(f'=====全部品牌申请导出司机考核数据完成{emoji.emojize(":partying_face::partying_face::partying_face:")}=====')
# time.sleep(60)


def parse():
    """
    返回的是司机考核的导出列表
    """
    while True:
        try:
            data_res = {"pageNum": 1, "pageSize": 10, "pageFlag": "assetsDriverAssessBIExport", "configName": ""}
            result = requests.post(audit_url, headers=header, json=data_res)
            lst = result.json()['data']['list']
            if lst:
                return lst
            else:
                time.sleep(random.uniform(3, 6))
        except requests.exceptions.ConnectionError:
            print(f'连接超时{emoji.emojize(":dizzy::dizzy::dizzy::dizzy:")}')
            time.sleep(random.uniform(1, 2))
        except Exception:
            traceback.print_exc()
            time.sleep(random.uniform(3, 6))


def detail(file):
    """
    如果司机考核数据太大，下载的就是压缩包，此函数是下载压缩包然后解压并返回解压好的文件的所在路径
    """
    file_name = fr'D:\经营数据源\{list[num]["condition"][0][3::]}.zip'
    print(file_name)
    with open(file_name, 'wb') as file_zip:
        for chunk in file.iter_content(chunk_size=1024):
            file_zip.write(chunk)
    f = zipfile.ZipFile(file_name, 'r')  # 压缩文件位置
    for p in f.namelist():
        f.extract(p, r"D:/司机考核数据/")  # 解压位置
    f.close()
    files = os.listdir(r"D:/司机考核数据/")
    return files


data_list = ['司机ID', '司机姓名', '司机手机号', '司机类型', '激活时间', '状态', '品牌',
             '注册时间', '首次出车时间', '末次出车时间', '首次完单时间', '末次完单时间', '城市', '运力公司', '出车时长', '服务时长',
             '有效出车时长', '高峰期出车时长', '高峰期有效出车时长', '出勤达标天数', '应答量(总)',
             '完单量(总)', '完成支付订单量', '出车天数', '完单天数', '考核完单率', '订单应付金额',
             '订单总金额', '投诉订单量', '行程费退款金额', '远程调度费退款金额', '附加费退款金额', '行程费',
             '远程调度费', '附加费', '司机抽佣行程费', '奖励金额-首单奖', '奖励金额-冲单奖',
             '总奖励金额', '早高峰应答量', '早高峰完单量',
             '晚高峰应答量', '晚高峰完单量', '服务分', '车队', '车牌号', '奖励金额-平台出资']

# 查看是否通过审批
for account in dit:
    ck = pd.read_sql("select * from 证件合规信息查询.dbo.小周账号信息配置表 where Account='%s'" % dit[account]['user'],
                     con=engine)
    cookie = ck['cookie'][0]
    _admin_tk = ck['_admin_tk'][0]
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        'cookie': cookie,
        '_admin_eid': dit[account]['eid'],
        '_admin_session_eid': dit[account]['sesseid'],
        '_admin_sign': '76828b6260c0588b86dff532333faab9',
        '_admin_tk': _admin_tk,
        '_admin_ts': str(round(time.time())),
    }
    audit_url = 'https://admin.yueyuechuxing.cn/bos/admin/v2/ai/common/export/server/getExportRecords'
    # 定义num和name，num是保证for循环中的break退出后重新循环能接着上一个循环的位置，name是判断该账号成功写入几个品牌的司机考核数据
    num = 0
    name = ['']
    while True:
        try:
            list = parse()
            if account[0:4] in name[0]:
                print(f'\033[1;36m===={account}写入完成{emoji.emojize(":smiling_face_with_sunglasses:")}=======\033[0m')
                break
            for let in range(len(list)):
                if (str(start_Time) in list[num]['condition'][2] and account[0:4] in list[num]['condition'][0] and
                        '司机考核' in list[num]['configName']):
                    print(f'{list[num]["configName"]}{emoji.emojize(":repeat_button:")}{list[num]["condition"]}')
                    auditState = list[num]["auditState"]
                    downloadStatus = list[num]["downloadStatus"]
                    if auditState == 0:
                        print(f'待审核{emoji.emojize(":enraged_face::enraged_face::enraged_face::enraged_face:")}')
                        time.sleep(random.uniform(180, 200))
                        break
                    elif auditState == 1:
                        if downloadStatus == -1:
                            print(f'已审核，数据处理中{emoji.emojize(":face_with_steam_from_nose::face_with_steam_from_nose:")}')
                            time.sleep(random.uniform(180, 200))
                            break
                        elif downloadStatus in [0, 1]:
                            print(f'可以下载啦，正在下载❛‿˂̵✧{emoji.emojize(":envelope_with_arrow::envelope_with_arrow:")}')
                            dow_url = 'https://admin.yueyuechuxing.cn' + list[num]['artifact']
                            while True:
                                try:
                                    file = requests.get(dow_url, headers=header, timeout=None)
                                    if '.zip' in dow_url:
                                        filelist = detail(file)
                                        print(filelist)
                                        for new_file in filelist:
                                            datn = pd.read_excel(fr'D:\司机考核数据\{new_file}')
                                            datn.insert(7, '品牌', account)
                                            print(f'{new_file}解压且读取完成{emoji.emojize(":incoming_envelope:")}')
                                            datn = datn[data_list]  # 筛选出需要的列
                                            datn['数据日期'] = start_Time
                                            datn['司机ID'] = datn['司机ID'].apply(lambda x: str(x).replace('.0', ''))
                                            datn.to_sql('司机考核数据日数据', con=engine, if_exists='append', index=False)
                                            os.remove(fr'D:\司机考核数据\{new_file}')
                                            print(f'\033[31m写入数据库完成(✿◡‿◡){emoji.emojize(":partying_face:")}\033[0m')

                                    else:
                                        datn = pd.read_excel(io.BytesIO(file.content))
                                        datn.insert(7, '品牌', account)
                                        print(f'文件读取完成(u‿ฺu✿ฺ){emoji.emojize(":incoming_envelope:")}')
                                        datn = datn[data_list]  # 筛选出需要的列
                                        datn['数据日期'] = start_Time
                                        datn['司机ID'] = datn['司机ID'].apply(lambda x: str(x).replace('.0', ''))
                                        datn.to_sql('司机考核数据日数据', con=engine, if_exists='append', index=False)
                                        print(f'\033[31m写入数据库完成(✿◡‿◡){emoji.emojize(":partying_face:")}\033[0m')
                                    name[0] = list[num]["condition"][0]
                                    time.sleep(random.uniform(2, 3))
                                    break
                                except requests.exceptions.ConnectionError:
                                    print(f'连接超时{emoji.emojize(":dizzy::dizzy::dizzy::dizzy:")}')
                                    traceback.print_exc()
                                    time.sleep(random.uniform(1, 2))
                                except Exception as e:
                                    print(f'写入异常正在重新写入{emoji.emojize(":loudly_crying_face:")}======>>>{e}')
                                    # traceback.print_exc()
                                    time.sleep(random.uniform(3, 6))
                            if account[0:4] in name[0]:
                                break
                else:
                    print('不是司机考核，下一个')
                    # print(str(start_date), list[num]['condition'][3],'=====\n', account[0:4], list[num]['tenantName'], '======\n', list[num]['configName'])
                    num += 1
                    time.sleep(random.uniform(1, 1))
                    break
        except requests.exceptions.ConnectionError:
            print(f'连接超时{emoji.emojize(":dizzy::dizzy::dizzy::dizzy:")}')
            time.sleep(random.uniform(1, 2))
        except Exception:
            # traceback.print_exc()
            time.sleep(random.uniform(3, 6))
            user_input = input(f"cookie已过期{emoji.emojize(':robot:')}，{emoji.emojize(':robot:')}y继续，n停止：")
            if user_input.lower() == 'y':
                ck = pd.read_sql(
                    "select * from 证件合规信息查询.dbo.小周账号信息配置表 where Account='%s'" % dit[account]['user'],
                    con=engine)
                # ck = pd.read_sql("select * from accounts where account='%s'" % dit[account]['user'], con=engine)
                header['cookie'] = ck['cookie'][0]
                header['_admin_tk'] = ck['_admin_tk'][0]
            elif user_input.lower() == 'n':
                quit()
            else:
                print("输入无效，请输入 'y' 表示继续或 'n' 表示停止。")
# 更新近30天司机考核
to_day30ago_kpi()
sql2 = "delete from [python].[dbo].[司机考核数据日数据] where [完单量(总)]=%s"
delete(sql2, '0.0')
print(f'{emoji.emojize(":cowboy_hat_face:")}已删除完单量为0的{emoji.emojize(":cowboy_hat_face::cowboy_hat_face:")}')
# 更新近30天全量/出车/完单
to_day60ago_info()
print(f'{emoji.emojize(":hundred_points::hundred_points:")}执行完毕{emoji.emojize(":hundred_points::hundred_points:")}')
