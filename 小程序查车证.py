import requests
import json
import time
import base64
import random
import string
import pandas as pd
from tqdm import trange
from sqlalchemy import create_engine
class Wu_Han_Car:
    """
    爬取交互平台小程序的类
    """
    def __init__(self,i,city,df):
        self.che_pai = i
        self.city = city
        self.df = df
        self.today = str(time.strftime('%Y-%m-%d',time.localtime()))
        # 生成当前时间的时间戳
        self.now_time = int(time.time()) * 1000
        # 生成六个随机字母
        # string.digits:从0-9生成所有数字；string.ascii_letters：从a-z，A-Z中生成所有字母
        # random.sample(数组列表，个数)；从数据列表中随机抽取6个
        self.token = ''.join(random.sample(string.digits + string.ascii_letters, 6))
    def code(self):
        """
        获取验证码图片
        """
        url = f'https://licenseapi.ggjtfw.com/wyc/verifyCode?timestamp={self.now_time}&id={self.token}'
        header = {
            'User-Agent': 'User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 MicroMessenger/7.0.9.501 NetType/WIFI MiniProgramEnv/Windows WindowsWechat',
            'Accept':'image / webp, image / apng, image / *, * / *;q = 0.8',
            'Sec - Fetch - Site': 'cross - site',
            'Sec - Fetch - Mode': 'no - cors',
            'Sec - Fetch - Dest': 'image',
            'Referer': 'http://servicewechat.com/wx96c5729907475ac1/6/page-frame.html',
            'Accept - Encoding': 'gzip, deflate, br',
        }
        res = requests.get(url=url, headers=header).content
        img_path = r'D:\cat_data\venv\人证车证查合规\小程序验证码\save0.jpg'
        with open(img_path,'wb') as f:
            f.write(res)
        print('\n<----验证码图片保存完毕，开始解析验证码---->')
        return self.base64_api()
    def base64_api(self):
        """
        解析验证码图片
        :return:
        """
        with open(r'D:\cat_data\venv\人证车证查合规\小程序验证码\save0.jpg', 'rb') as f:
            base64_data = base64.b64encode(f.read())
            b64 = base64_data.decode()
        data = {"username": 'Xy123', "password": 'Xy123456', "typeid": 3, "image": b64}
        result = json.loads(requests.post("http://api.ttshitu.com/predict", json=data).text)
        if result['success']:
            yan_zheng_ma = result["data"]["result"]
        else:
            yan_zheng_ma = result["message"]
        print(f'<<<===解析完毕，验证码是===>>>{yan_zheng_ma}')
        return self.parse(yan_zheng_ma)
    def parse(self,yan_zheng_ma):
        """
        通过取得解析后的验证码去采集数据
        :param yan_zheng_ma:
        :return:
        """
        url = 'https://licenseapi.ggjtfw.com/wyc/queryDw'
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36 MicroMessenger/7.0.9.501 NetType/WIFI MiniProgramEnv/Windows WindowsWechat',
            'Referer': 'https://servicewechat.com/wx96c5729907475ac1/6/page-frame.html',
            'token': '6628a4348b7bb8ed58ea7a7193efc250af6a210faf8c7f53ababe385cfd1eed8',
            'cookies': 'coordinate=GD;car-pf=h5;lang=zh;mp_platform=26;openid=6628a4348b7bb8ed58ea7a7193efc250af6a210faf8c7f53ababe385cfd1eed8;app_version=;channel=;car-ps=mp-wx-miniapp'
        }
        data = {"code": yan_zheng_ma, "id": self.token, "vehno": self.che_pai}
        res = requests.post(url=url, headers=header, json=data).json()
        time.sleep(1)
        return self.write_parse(res)
    def write_parse(self,res):
        if res[0]['msg'] == '查询成功':
            print(f'{self.che_pai}成功返回==>>>{res}')
            # print(data['司机ID'])
            self.df = self.df.append(pd.DataFrame({'司机ID':all_data['司机ID'][data],'车牌号':res[0]['data'][0]['vehno'],'城市':res[0]['data'][0]['city'],
                                              '品牌':all_data['品牌'][data],'身份证号':all_data['身份证号'][data],'司机姓名':all_data['司机姓名'][data],'车辆运输证号':all_data['车辆运输证号'][data],
                                              '证件状态':'有效','更新日期':self.today,'是否取得网约车运输资质':'是'},index=[0]))
        elif res[0]['msg'] == '未取得网约车运输证':
            print('===>>>',self.che_pai, res[0]['msg'],'<<<===')
            self.df = self.df.append(pd.DataFrame({'司机ID': all_data['司机ID'][data], '车牌号': self.che_pai, '城市': self.city,
                                              '品牌':all_data['品牌'][data],'身份证号':all_data['身份证号'][data],'司机姓名':all_data['司机姓名'][data],'车辆运输证号':all_data['车辆运输证号'][data],
                                              '证件状态': '无效','更新日期':self.today, '是否取得网约车运输资质': res[0]["msg"]}, index=[0]))
        elif res[1]['msg'] == '验证码错误！':
            print(res[1]["msg"],'正在重新校验--0.0--')
            time.sleep(random.uniform(2,3))
            self.code()
        else:
            raise Exception(res[0]['msg'])
        return self.df

if __name__ == "__main__":
    day = '10-13'
    city = '长沙市'
    engine = create_engine('mssql+pymssql://sa:Xy202204@LAPTOP-HVPER022/yueyuechuxing?charset=utf8', echo=False)
    sql = "select * from [证件合规信息查询].[dbo].[每日需要查询数据] where 车牌号 is not  null  and 城市='%s'"%city
    all_data = pd.read_sql(sql, con=engine)
    # all_data = pd.read_excel(r'D:\双证合规\长沙市\缺失数据.xlsx')
    df = pd.DataFrame()
    for data in trange(len(all_data)):
        try:
            i = all_data['车牌号'][data]
            city = all_data['城市'][data]
            df = Wu_Han_Car(i,city,df).code()
            time.sleep(random.uniform(1,2))
        except Exception as e:
            print(f'跳过这个车牌号{i}',e)
            if str(e) == '暂时无法查询,请稍后再试!':
                writer_excel = pd.ExcelWriter(r'D:\双证合规\%s\%s车证%s.xlsx'%(city,city,day))
                df.to_excel(writer_excel, sheet_name='车证', index=False)
                break
    writer_excel = pd.ExcelWriter(r'D:\双证合规\%s\%s车证%s.xlsx'%(city,city,day))
    df.to_excel(writer_excel,sheet_name='车证', index=False)