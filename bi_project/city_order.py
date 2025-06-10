from flask import Flask, render_template, g, request, jsonify, make_response
import pymysql
import json
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import requests
import logging
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
import secrets
import os
from dotenv import load_dotenv
from sqlalchemy import exc
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    JWTManager, create_access_token, get_jwt_identity, 
    jwt_required, set_access_cookies, unset_jwt_cookies,
    get_jwt, verify_jwt_in_request, current_user
)
# from flask_cors import CORS
app = Flask(__name__, static_folder='static')
# CORS(app)


# 请求处理之前调用的方
@app.before_request
def before_request():
    # 使用g对象保存请求之前处理的变量
    # print('请求处理之前调用。。。。。连接数据。。。')
    g.conn = pymysql.connect(host='47.93.173.200',
                             user='root',
                             password='Xy=202212',
                             database='bak_yueyuechuxing',
                             charset='utf8')
    # 创建g的数据操作游标属性cursor ，并设置查询时返回数据类型
    g.cursor = g.conn.cursor(pymysql.cursors.DictCursor)


# 请求关闭之前调用
@app.teardown_request
def teardown_request(exception):
    # print('请求关闭之前调用。。。。。。关闭数据库。')
    # 获取对象的属性, getattr,如果存在g的属性conn则返回属性，如果没有返回第三个参数
    conn = getattr(g, 'conn', None)
    cursor = getattr(g, 'cursor', None)
    if conn is not None and cursor is not None:
        # 关闭游标和数据库连接
        cursor.close()
        conn.close()

# 这是宝可梦网站的，展示单量用的
@app.route('/<city>')
def show_city(city):
    city_dit = {"wuhan": "武汉市", "fuzhou": "福州市", "hefei": "合肥市", "luoyang": "洛阳市"}
    g.cursor.execute(
        "SELECT brand, city, pay_order_sum, match_driver_sum, DATE_FORMAT(date_time, '%%Y-%%m-%%d') AS date_time FROM bak_yueyuechuxing.daily_push_order WHERE city=%s ORDER BY date_time ASC", (city_dit[city],))
    result = g.cursor.fetchall()
    if city == 'hefei' or city == 'luoyang':
        print(result)
        return jsonify(result)
    else:
        result = g.cursor.fetchall()
        current_date = datetime.now()
        formatted_date = current_date.strftime("%Y-%m-%d")
        if len(result) == 8:
            print('返回前端的数据', result)
        else:
            print('没有当天的数据', result)
            dit = {'brand': result[0]['brand'], 'city': result[0]['city'], 'pay_order_sum': '暂无更新', 'date_time': formatted_date}
            result.insert(0, dit)
        # 柱形图参数
        xAxis_data = [result[7]['date_time'], result[6]['date_time'], result[5]['date_time'], result[4]['date_time'], result[3]['date_time'],
                    result[2]['date_time'], result[1]['date_time']]
        series_data = [result[7]['pay_order_sum'], result[6]['pay_order_sum'], result[5]['pay_order_sum'], result[4]['pay_order_sum'],
                    result[3]['pay_order_sum'], result[2]['pay_order_sum'], result[1]['pay_order_sum']]
        # 折线图参数
        return render_template("index.html", result_data=result, xAxis_data=xAxis_data, series_data=series_data)


# powerbi获取令牌用的接口（添加JWT保护）
@app.route('/api/embed_token', methods=['POST'])
@jwt_required()  # 添加JWT认证保护
def get_embed_token():
    table_data = request.get_json()
    tablename = table_data.get('tablename')
    # 配置信息
    PBI_CLIENT_ID = "fc9562ac-ea68-4da9-872b-d5500b2c54a7"  # 客户端ID
    PBI_CLIENT_SECRET = "2qtpu-xGeQQ2~hy6R9qrUq~85~~oN4-t4r"  # 客户端密钥
    PBI_TENANT_ID = "a57dcbde-032f-4047-a9bc-872800adb61a"  # 租户ID
    PBI_GROUP_ID = "01c5b293-3cfc-47cb-837a-07081108889d"  # 工作区ID
    PBI_NAME = tablename  # 报表名称
    print(PBI_NAME)
    try:
        # 1. 获取Azure AD令牌
        auth_url = f"https://login.chinacloudapi.cn/{PBI_TENANT_ID}/oauth2/token"
        auth_data = {
            "grant_type": "client_credentials",
            "resource": "https://analysis.chinacloudapi.cn/powerbi/api",
            "client_id": PBI_CLIENT_ID,
            "client_secret": PBI_CLIENT_SECRET
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        auth_response = requests.post(auth_url, headers=headers, data=auth_data)
        auth_response.raise_for_status()  # 检查请求是否成功
        access_token = auth_response.json().get("access_token")
        if not access_token:
            return jsonify({"error": "获取access_token失败,请联系工程师Mr.周"}), 500
        # 2. 获取工作区中的报表列表
        headers = {"Authorization": f"Bearer {access_token}"}
        url = f"https://api.powerbi.cn/v1.0/myorg/groups/{PBI_GROUP_ID}/reports"
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        reports = res.json().get('value', [])
        if not reports:
            return jsonify({"error": "这个工作区没有报表,请换个工作区ID,实在不行就联系工程师Mr.周"}), 404
        # 找到需要的报表ID，然后用这个报表ID获取该报表的嵌入令牌
        report = next((r for r in reports if r['name'] == PBI_NAME), None)
        if not report:
            return jsonify({"error": f"你要的这个报表不存在,请换个报表ID,实在不行就联系工程师Mr.周"}), 404
        # 3. 获取报表的嵌入令牌
        new_url = f"https://api.powerbi.cn/v1.0/myorg/groups/{PBI_GROUP_ID}/reports/{report['id']}/GenerateToken"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        data = {"accessLevel": "View", "allowSaveAs": "true"}
        response = requests.post(new_url, headers=headers, json=data)
        response.raise_for_status()
        embed_token = response.json()
        print("embed_token")
        # 返回必要的信息给前端
        return jsonify({
            "embed_token": embed_token,
            "embed_url": report['embedUrl'],
            "report_id": report['id']
        })
    except requests.exceptions.RequestException as e:
        logging.error(f"Power BI接口请求失败: {str(e)}")
        return jsonify({"error": "获取Power BI资源失败,请联系工程师Mr.周"}), 500
    except Exception as e:
        logging.error(f"处理嵌入令牌时发生未知错误: {str(e)}")
        return jsonify({"error": "处理报表嵌入令牌时发生未知错误,请联系工程师Mr.周"}), 500


# 配置部分（关键修改：时效设置为1分钟）
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Xy=202212@47.93.173.200/bak_yueyuechuxing'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secrets.token_hex(32)
# 登录时效配置（测试阶段设置为1分钟，生产环境改回所需时间）
# app.config['LOGIN_EXPIRES_HOURS'] = 1  # 保留小时单位配置（1分钟=1/60小时）
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=1440)
# JWT其他配置（保持不变）
app.config['JWT_SECRET_KEY'] = app.config['SECRET_KEY']
app.config['JWT_TOKEN_LOCATION'] =  ['headers', 'cookies']  # 同时检查请求头和Cookie
app.config['JWT_COOKIE_SECURE'] = False  # 开发环境设为False，生产环境设为True
app.config['JWT_COOKIE_CSRF_PROTECT'] = True  # 启用CSRF保护
app.config["JWT_SECRET_KEY"] = os.environ.get('JWT_SECRET_KEY')  # 从环境变量中读取JWT密钥

db = SQLAlchemy(app)  # 定义db实例
jwt = JWTManager(app)
logging.basicConfig(level=logging.INFO)  # 配置日志记录

# 数据库模型（保持不变）
class Account(db.Model):
    """
    账号表
    """
    __tablename__ = 'Account'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    pwd = db.Column(db.Text, nullable=False)  # 使用TEXT类型存储哈希
    tablename = db.Column(db.String(100))
    filter = db.Column(db.String(100))

    def verify_password(self, password):
        """验证密码是否正确"""
        return check_password_hash(self.pwd, password)

# JWT异常处理（保持不变）
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'success': False,
        'message': '登录已过期，请重新登录'
    }), 401

# load_dotenv()
def decode_key(base64_key):
    # 解码Base64密钥
    key_bytes = base64.b64decode(base64_key)
    # 截断为32字节（256位）
    return key_bytes[:32]
# 获取环境变量中的密钥
ENCRYPTION_KEY = os.getenv('VITE_ENCRYPTION_KEY')
# 解码并处理密钥
DECRYPTION_KEY = decode_key(ENCRYPTION_KEY)
# AES解密函数
def decrypt_password(encrypted_password):
    try:
        # 前端返回格式: "Base64(IV):Base64(密文)"
        parts = encrypted_password.split(':')
        if len(parts) != 2:
            raise ValueError("Invalid encrypted format. Expected 'IV:ciphertext'")
        # 解码IV和密文
        iv = base64.b64decode(parts[0])
        ciphertext = base64.b64decode(parts[1])
        # 创建AES解密器 - 使用CBC模式
        cipher = AES.new(DECRYPTION_KEY, AES.MODE_CBC, iv=iv)
        # 解密并去除填充
        decrypted_bytes = unpad(cipher.decrypt(ciphertext), AES.block_size)
        return decrypted_bytes.decode('utf-8')
    except ValueError as ve:
        print(f"格式错误: {str(ve)}")
        return None
    except Exception as e:
        print(f"解密失败: {str(e)}")
        return None
    

# 登录接口（保持不变，自动使用JWT配置的过期时间）
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    encrypted_password = data.get('password')
    # 解密密码
    password = decrypt_password(encrypted_password)
    if password is None:
        return jsonify({
            "success": False,
            "message": "安全验证失败,请联系工程师Mr.周"
        }), 400
    
    try:
        user = Account.query.filter_by(username=username).first()
        if not user:
            # 账号不存在
            return jsonify({
                "success": False,
                "message": "都没有这个账号,你发神经啊"
            }), 400
            
        if not user.verify_password(password):
            return jsonify({
                "success": False,
                "message": "密码都能输错了,回家吧孩子,回家好吗"
            }), 400
            
        tablename_dict = json.loads(user.tablename)
        filter_dict = json.loads(user.filter)
        access_token = create_access_token(identity=str(user.id))
        
        response = jsonify({
            "success": True,
            "message": "登录成功",
            "user": {
                "id": user.id,
                "username": user.username,
                "tablename": tablename_dict,
                "filter": filter_dict
            },
            "access_token": access_token
        })
        
        # 添加登录日志
        print(f"用户登录成功: {username}")
        return response, 200
        
    except Exception as e:
        print(f"登录异常: {str(e)}")
        return jsonify({
            "success": False,
            "message": "服务器内部错误,请联系工程师Mr.周"
        }), 500






if __name__ == '__main__':
    app.run(host='127.0.0.1', port=1319)
    # app.run(debug=True)
