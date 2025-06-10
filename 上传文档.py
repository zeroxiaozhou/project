import hashlib
import random
import os
import requests
import pandas as pd
import time
from tqdm import trange
from sqlalchemy import create_engine
def calculate_md5(data: bytes) -> str:
    md5_hash = hashlib.md5()
    md5_hash.update(data)
    return md5_hash.hexdigest()

def parse(driverID):
    while True:
        json_data = {
            'driverId': driverID,
        }

        response = requests.post(
            'https://admin.yueyuechuxing.cn/admin/v1/assets/driver/contract/pageList',
            headers=header,
            json=json_data,
        )
        result = response.json()["data"]["items"]
        try:
            if result:
                dit = result[0]
                return dit
            else:
                return None
        except Exception as e:
            print('报错原因', e)
            time.sleep(random.uniform(1, 1.5))

def detail(file_path):
    while True:
        with open(file_path, 'rb') as file:
            pdf_data = file.read()
            length = len(pdf_data)
            md5_hash = calculate_md5(pdf_data)
        file = {'file': (file_path, pdf_data, 'application/pdf')}
        data = {
            'md5': md5_hash,
            'contentType': 'application/pdf',
            'group': 'public',
            'module': 'image',
            'fileLength': length,
            'mode': 'PUBLIC_READ_WITH_CDN'
        }
        response = requests.post(
            'https://admin.yueyuechuxing.cn/admin/v1/common/upload/pdf',
            headers=header,
            data=data,
            files=file
        )
        try:
            if response.json()["code"] == 1:
                pdf_url = response.json()["data"]["url"]
                return pdf_url
            else:
                print(response.json())
                time.sleep(random.uniform(1.5, 2))
        except Exception as e:
            print('detail报错原因', e)
            time.sleep(random.uniform(1, 1.5))

def upload(file_path, driverID):
    while True:
        pdf_url = detail(file_path)
        dit = parse(driverID)
        if dit is None:
            return None
        json_data = {
            'id': dit["id"],
            'driverId': dit["driverId"],
            'company': dit["company"],
            'effectiveDate': dit["effectiveDate"],
            'expiryDate': dit["expiryDate"],
            'type': 2,
            'contractImg': pdf_url,
            'signDate': dit["expiryDate"],
        }

        response = requests.post(
            'https://admin.yueyuechuxing.cn/admin/v1/assets/driver/contract/save',
            headers=header,
            json=json_data,
        )
        try:
            if response.json()["code"] == 1:
                # print(json_data)
                return response.json()
            else:
                print(f"\033[33m错误返回：\033[0m{response.json()}")
                time.sleep(random.uniform(1.5, 2))
        except Exception as e:
            print('报错原因', e)
            time.sleep(random.uniform(1, 1.5))



if __name__ == '__main__':
    engine = create_engine('mssql+pymssql://sa:Xy202204@LAPTOP-HHMD1A48\XYCX/证件合规信息查询?charset=utf8', echo=False)
    df = pd.DataFrame()
    url = 'https://admin.yueyuechuxing.cn/admin/v1/manage/virtualCarTeam/driverList'
    ck = pd.read_sql("select * from 证件合规信息查询.dbo.小周账号信息配置表 where Account='admin'", con=engine)
    cookie = ck['cookie'][0]
    _admin_tk = ck['_admin_tk'][0]
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.54',
        'cookie': cookie,
        '_admin_eid': ck['eid'][0],
        '_admin_mask': '0',
        '_admin_resource_key': 'personCarPush',
        '_admin_session_eid': ck['sesseid'][0],
        '_admin_sign': '76828b6260c0588b86dff532333faab9',
        '_admin_tk': _admin_tk,
        '_admin_ts': str(round(time.time())),
    }
    file_list = os.listdir(r'D:\喜行约车司机协议PDF分类\24年喜行约车协议PDF06-04\PDF总数')
    driver_list = []
    for i in trange(len(file_list)):
        driverID = file_list[i].split(".")[0]
        file_path = rf"D:\喜行约车司机协议PDF分类\24年喜行约车协议PDF06-04\PDF总数\{driverID}.pdf"
        res = upload(file_path, driverID)
        if res is None:
            driver_list.append(driverID)
            continue
        time.sleep(random.uniform(1, 1.5))
    print(f"这些司机没有合同信息：{driver_list}")
