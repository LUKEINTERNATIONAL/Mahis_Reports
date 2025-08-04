import mysql.connector
from sshtunnel import SSHTunnelForwarder, create_logger
import pandas as pd
from config import DB_CONFIG_AWS_TEST, SSH_CONFIG_TEST
import logging
import os
import socket
import pymysql
logger = create_logger(loglevel=logging.DEBUG)

# def fetch_data(query):
#     conn = mysql.connector.connect(**DB_CONFIG)
#     df = pd.read_sql(query, conn)
#     conn.close()
#     return df

def fetch_data(query):
    with SSHTunnelForwarder(
        (SSH_CONFIG_TEST['ssh_host'], 22),
        ssh_username=SSH_CONFIG_TEST['ssh_user'],
        ssh_private_key='ssh/dhd-dev-aetc-pub-key.pem',
        remote_bind_address=SSH_CONFIG_TEST['remote_bind_address']
    ) as tunnel:
        print(f"Tunnel is open on local port: {tunnel.local_bind_port}")
        sock = socket.socket()
        sock.settimeout(10)
        sock.connect((DB_CONFIG_AWS_TEST['host'], tunnel.local_bind_port))
        print("Socket connection succeeded!")
        sock.close()
        conn = pymysql.connect(
            host=DB_CONFIG_AWS_TEST['host'],
            port=tunnel.local_bind_port,
            user=DB_CONFIG_AWS_TEST['user'],
            password=DB_CONFIG_AWS_TEST['password'],
            database=DB_CONFIG_AWS_TEST['database'],
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

def load_stored_data(filename=f'{path}/data/latest_data_opd.csv'):
    return pd.read_csv(filename)


