import mysql.connector
from sshtunnel import SSHTunnelForwarder, create_logger
import pandas as pd
from config import DB_CONFIG_AWS_TEST, SSH_CONFIG_TEST, DB_CONFIG_AWS_PROD, SSH_CONFIG_AWS
import logging
import datetime
import os
import socket
import pymysql
logger = create_logger(loglevel=logging.DEBUG)

# LOCAL
# def fetch_data(query):
#     conn = mysql.connector.connect(**DB_CONFIG)
#     df = pd.read_sql(query, conn)
#     conn.close()
#     return df

# REMOTE
ssh_route = SSH_CONFIG_AWS
db_route = DB_CONFIG_AWS_PROD

def fetch_data(query):
    with SSHTunnelForwarder(
        (ssh_route['ssh_host'], 22),
        ssh_username=ssh_route['ssh_user'],
        ssh_private_key='ssh/dhd-prod-devops-mahis-kp.pem',
        remote_bind_address=ssh_route['remote_bind_address']
    ) as tunnel:
        print(f"Tunnel is open on local port: {tunnel.local_bind_port}")
        sock = socket.socket()
        sock.settimeout(10)
        sock.connect((db_route['host'], tunnel.local_bind_port))
        print("Socket connection succeeded!")
        sock.close()
        conn = pymysql.connect(
            host=db_route['host'],
            port=tunnel.local_bind_port,
            user=db_route['user'],
            password=db_route['password'],
            database=db_route['database'],
            connect_timeout=30,
            ssl={'ssl': {'fake_flag_to_enable_ssl': True}}  # or proper config
        )
        print("✅ Connected to database")
        df = pd.read_sql(query, conn)
        print("✅ Data fetched successfully")
        print(df)
        conn.close()
        return df

path = os.getcwd()
def store_data(df, filename=f'{path}/data/latest_data_opd.csv'):
    os.makedirs(os.path.dirname(f'{path}/{filename}'), exist_ok=True)
    df.to_csv(filename, index=False)
    
    #create a timestamp in csv
    saving_time = pd.DataFrame(data={'saving_time':[str(datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S"))]})
    saving_time.to_csv(f'{path}/data/TimeStamp.csv')

def load_stored_data(filename=f'{path}/data/latest_data_opd.csv'):
    return pd.read_csv(filename)


