from flask import Flask, render_template
from libs.print_error_info import *
from flask_cors import CORS
import pandas as pd
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from threading import Thread

app = Flask(__name__)
CORS(app)
config_df = pd.read_excel('./config/爬虫配置.xls')
cols = "id	表名	表注释   爬取周期	爬取时间	conn	时间列	最大延迟	备注"
config_df.columns = ['id', 'table_name', 'table_comments', 'period', 'cron_time', 'conn', 'time_col', 'max_delay', 'note']
config_df['last_update'] = None
config_df['correct'] = 1


@app.route('/')
def root_():
    return render_template('index.html')


@app.route('/get_config_json')
def get_config_json_():
    json_data = config_df.to_json(orient='records')
    # print_json_info(json_data)
    return {'success': json.loads(json_data)}


def gen_session(conn_str):
    try:
        engine = create_engine(conn_str, pool_size=0, max_overflow=-1)
        Session = sessionmaker(bind=engine)
        session = Session()
        return session
    except:
        show_error_log('连接失败', conn_str)
        return '连接失败'


def init_conn_dic():
    conn_dic = {}
    for conn_str in config_df['conn']:
        if not conn_dic.get(conn_str):
            obj = gen_session(conn_str)
            conn_dic[conn_str] = obj
    return conn_dic


def judge_correct(time_str, max_delay_str):
    timestamp = make_time(time_str)
    max_delay = eval(max_delay_str)
    # show_log('timestamp',timestamp)
    # show_log('max_delay',max_delay)
    return 1 if int(time.time()) - timestamp < max_delay else 0


def monitor_loop():
    global config_df, g_conn_dic
    while True:
        g_conn_dic = init_conn_dic()
        for _, item in config_df.iterrows():
            session = g_conn_dic.get(item['conn'])
            sql_str = f"select {item['time_col']} from {item['table_name']} order by {item['time_col']} desc limit 1"
            show_log('sql_str', sql_str)

            try:
                res = session.execute(text(sql_str))
                last_update = res.fetchall()[0][0]
                correct = judge_correct(last_update, item['max_delay'])
                config_df.loc[config_df['id'] == item['id'], 'correct'] = correct
            except:
                print_error_info()
                last_update = None
            config_df.loc[config_df['id'] == item['id'], 'last_update'] = last_update
        for k, v in g_conn_dic.items():
            v.close()
        g_conn_dic = {}
        time.sleep(60)


if __name__ == '__main__':
    t = Thread(target=monitor_loop)
    t.start()

    app.run(host='0.0.0.0', port=9527)
