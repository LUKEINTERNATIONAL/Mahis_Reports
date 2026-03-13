import os

USE_LOCALHOST = True
START_DATE = '2025-12-01'
LOAD_FRESH_DATA = False # Set to True to always start from START_DATE and fetch fresh data. Not recommended for large datasets.
PREFIX_NAME = '/'  # Set to your desired prefix for https paths, e.g., '/myapp'


RELATIVE_DAYS = [ 'Today', 'Yesterday', 'Last 7 Days', 'Last 30 Days', 'This Week', 'Last Week', 'This Month', 'Last Month' ]

# REFERENTIAL COLUMNS - THESE SHOULD MATCH THE QUERY OUTPUT COLUMNS
DATA_FILE_NAME_ = "latest_data_opd.parquet"

FIRST_NAME_ = 'given_name'
LAST_NAME_ = 'family_name'
DATE_ = 'Date'
PERSON_ID_ = 'person_id'
ENCOUNTER_ID_ = 'encounter_id'
FACILITY_ = 'Facility'
AGE_GROUP_ = 'Age_Group'
AGE_ = 'Age'
GENDER_ = 'Gender'
NEW_REVISIT_ = 'new_revisit'
HOME_DISTRICT_ = 'Home_district'
TA_ = 'TA'
VILLAGE_ = 'Village'
FACILITY_CODE_ = 'Facility_CODE'
OBS_VALUE_CODED_ = 'obs_value_coded'
CONCEPT_NAME_ = 'concept_name'
VALUE_ = 'Value'
VALUE_NUMERIC_ = 'ValueN'
DRUG_NAME_ = 'DrugName'
VALUE_NAME_ = 'Value_name'
ORDER_NAME_ = 'Order_Name'
PROGRAM_ = 'Program'
ENCOUNTER_ = 'Encounter'

# HANDLE GLOBAL IMPORT OF DATA FROM PARQUET FILE AND MANAGE AS CACHE FILES
PARQUET_FILE_PATH = os.path.join(os.getcwd(), 'data', 'latest_data_opd.parquet')
CACHE_FILE_PATH = os.path.join(os.getcwd(), 'data', 'cache_opd.parquet')
TIMESTAMP_FILE_PATH = os.path.join(os.getcwd(), 'data', 'TimeStamp.csv')

# For local database connection
DB_CONFIG_LOCAL = {
    'host': 'localhost',
    'user': 'user',
    'password': 'password',
    'database': 'local_database',
    'port': 3306
}

# for production database connection
DB_CONFIG = {
    'host': 'hostname',
    'user': 'user',
    'password': 'password',
    'database': 'database',
    'port': 3306
}

# SSH configuration for production database connection
SSH_CONFIG = {
    'ssh_host': 'aws_host',
    'ssh_port': 22,
    'ssh_user': 'ubuntu',
    'ssh_password': 'password',  # OR use ssh_pkey if using key
    # 'ssh_pkey': 'key.pem',  #private key name stored in ssh directory
    'remote_bind_address': ('path_to_db_endpoint', 3306)
}

# on production remove COLLATE utf8mb3_general_ci
QERY = """
SELECT 
    main.*,
    CASE 
        WHEN visit_days = 1 THEN 'New'
        ELSE 'Revisit'
    END AS new_revisit
FROM (
    SELECT 
        p.person_id,
        e.encounter_id,
        gender AS Gender, 
        FLOOR(DATEDIFF(CURRENT_DATE, birthdate) / 365) AS Age, 
        CASE 
            WHEN FLOOR(DATEDIFF(CURRENT_DATE, birthdate) / 365) < 5 THEN 'Under 5'
            ELSE 'Over 5'
        END AS Age_Group,
        DATE(e.encounter_datetime) AS Date, 
        pr.name AS Program, 
        l.name AS Facility,
        l.code AS Facility_CODE, 
        u.username AS User, 
        l.district AS District, 
        et.name AS Encounter,
        pa.state_province AS Home_district,
        pa.township_division AS TA,
        pa.city_village AS Village,
        v.visit_days,
        cn.name AS obs_value_coded,
        c.name AS concept_name,
        o.value_text as Value,
        o.value_numeric as ValueN,
        d.name as DrugName,
        cnn.name as Value_name
    FROM person AS p
    JOIN patient AS pa2 ON p.person_id = pa2.patient_id
    JOIN person_address AS pa ON p.person_id = pa.person_id
    JOIN encounter AS e ON p.person_id = e.patient_id
    JOIN encounter_type AS et ON e.encounter_type = et.encounter_type_id
    INNER JOIN program AS pr ON e.program_id = pr.program_id
    INNER JOIN users AS u ON e.provider_id = u.user_id
    INNER JOIN facilities AS l ON u.location_id = l.code COLLATE utf8mb3_general_ci
    -- Join with precomputed visit days
    JOIN (
        SELECT patient_id, COUNT(DISTINCT DATE(encounter_datetime)) AS visit_days
        FROM encounter
        GROUP BY patient_id
    ) AS v ON v.patient_id = p.person_id
    LEFT JOIN obs o ON o.encounter_id = e.encounter_id
    LEFT JOIN concept_name cn ON o.value_coded = cn.concept_id AND cn.locale = 'en' AND cn.concept_name_type = 'FULLY_SPECIFIED'
    LEFT JOIN concept_name c ON o.concept_id = c.concept_id
    LEFT JOIN concept co ON o.value_text = co.uuid
    LEFT JOIN concept_name cnn ON co.concept_id = cnn.concept_id
    LEFT JOIN drug as d on o.value_drug = d.drug_id
    WHERE p.voided = 0
    {date_filter}
) AS main

"""

actual_keys_in_data = ['person_id', 'encounter_id', 
                                       'Gender', 'Age', 'Age_Group', 
                                       'Date', 'Program', 'Facility', 
                                       'Facility_CODE', 'User', 'District', 
                                       'Encounter', 'Home_district', 'TA', 
                                       'Village', 'visit_days', 'obs_value_coded','concept_name', 'Value',"",
                                       'ValueN', 'DrugName', 'Value_name', 'new_revisit','count','count_set','sum','Order_Name']


# TEST CONNECTION
#!/usr/bin/env python3
"""
Database Connection Tester for Config
"""

import pymysql
import paramiko
from sshtunnel import SSHTunnelForwarder
import socket
import sys

def test_local_connection():
    """Test local database connection"""
    try:
        connection = pymysql.connect(
            host=DB_CONFIG_LOCAL['host'],
            user=DB_CONFIG_LOCAL['user'],
            password=DB_CONFIG_LOCAL['password'],
            database=DB_CONFIG_LOCAL['database'],
            port=DB_CONFIG_LOCAL['port'],
            connect_timeout=5
        )
        connection.close()
        return True, "Localhost connection successful"
    except pymysql.Error as e:
        return False, f"Localhost connection failed: {str(e)}"
    except Exception as e:
        return False, f"Localhost connection error: {str(e)}"

def test_direct_connection():
    """Test direct database connection"""
    try:
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            port=DB_CONFIG['port'],
            connect_timeout=5
        )
        connection.close()
        return True, "Direct database connection successful"
    except pymysql.Error as e:
        return False, f"Direct connection failed: {str(e)}"
    except Exception as e:
        return False, f"Direct connection error: {str(e)}"

def test_ssh_connection():
    """Test SSH tunnel and database connection"""
    try:
        # First test SSH connection
        ssh_config = SSH_CONFIG.copy()
        
        # Prepare SSH connection arguments
        ssh_args = {
            'ssh_address_or_host': (ssh_config['ssh_host'], ssh_config['ssh_port']),
            'ssh_username': ssh_config['ssh_user'],
            'remote_bind_address': ssh_config['remote_bind_address']
        }
        
        # Add either password or private key
        if 'ssh_password' in ssh_config and ssh_config['ssh_password']:
            ssh_args['ssh_password'] = ssh_config['ssh_password']
        elif 'ssh_pkey' in ssh_config and ssh_config['ssh_pkey']:
            # Look for key file in ssh directory relative to script location
            key_path = os.path.join(os.path.dirname(__file__), 'ssh', ssh_config['ssh_pkey'])
            if os.path.exists(key_path):
                ssh_args['ssh_pkey'] = key_path
            else:
                ssh_args['ssh_pkey'] = ssh_config['ssh_pkey']
        else:
            return False, "SSH configuration missing authentication method"
        
        # Create tunnel
        with SSHTunnelForwarder(**ssh_args) as tunnel:
            tunnel.start()
            
            # Test database connection through tunnel
            connection = pymysql.connect(
                host='127.0.0.1',
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                database=DB_CONFIG['database'],
                port=tunnel.local_bind_port,
                connect_timeout=5
            )
            connection.close()
            tunnel.stop()
            
            return True, "SSH tunnel and database connection successful"
            
    except paramiko.ssh_exception.AuthenticationException:
        return False, "SSH authentication failed - check username, password or key"
    except paramiko.ssh_exception.SSHException as e:
        return False, f"SSH connection failed: {str(e)}"
    except socket.error as e:
        return False, f"Network error: {str(e)}"
    except pymysql.Error as e:
        return False, f"Database connection through SSH failed: {str(e)}"
    except Exception as e:
        return False, f"SSH tunnel error: {str(e)}"

def test_query_execution(connection_params):
    """Test if a simple query can be executed"""
    try:
        connection = pymysql.connect(**connection_params)
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        connection.close()
        return True, "Query execution successful"
    except Exception as e:
        return False, f"Query execution failed: {str(e)}"

def main():
    print("=" * 60)
    print("DATABASE CONFIGURATION TESTER")
    print("=" * 60)
    
    print(f"\nConfiguration Settings:")
    print(f"USE_LOCALHOST: {USE_LOCALHOST}")
    print(f"START_DATE: {START_DATE}")
    print(f"PREFIX_NAME: {PREFIX_NAME}")
    print("-" * 60)
    
    if USE_LOCALHOST:
        print("\nTesting Localhost Configuration...")
        success, message = test_local_connection()
        
        if success:
            print(f"{message}")
            # Test query execution
            conn_params = {
                'host': DB_CONFIG_LOCAL['host'],
                'user': DB_CONFIG_LOCAL['user'],
                'password': DB_CONFIG_LOCAL['password'],
                'database': DB_CONFIG_LOCAL['database'],
                'port': DB_CONFIG_LOCAL['port']
            }
            query_success, query_message = test_query_execution(conn_params)
            if query_success:
                print(f"{query_message}")
                print("\n🎉 Configurations for Localhost are safe to use!")
            else:
                print(f"{query_message}")
                print("\nConnection works but query execution failed - check database permissions")
        else:
            print(f"{message}")
            print("\nDatabase connection failed, check credentials")
            
    else:
        print("\nTesting Production Configuration...")
        
        # Test direct connection first
        direct_success, direct_message = test_direct_connection()
        
        if direct_success:
            print(f"{direct_message}")
            # Test query execution
            conn_params = {
                'host': DB_CONFIG['host'],
                'user': DB_CONFIG['user'],
                'password': DB_CONFIG['password'],
                'database': DB_CONFIG['database'],
                'port': DB_CONFIG['port']
            }
            query_success, query_message = test_query_execution(conn_params)
            if query_success:
                print(f"{query_message}")
                print("\nConfigurations for Production are safe to use!")
            else:
                print(f"{query_message}")
                print("\nDirect connection works but query execution failed - check database permissions")
        
        else:
            print(f"{direct_message}")
            print("\nAttempting SSH Tunnel Connection...")
            
            # Test SSH connection
            ssh_success, ssh_message = test_ssh_connection()
            
            if ssh_success:
                print(f"{ssh_message}")
                print("\n🎉 Configurations for Production with SSH are safe to use!")
            else:
                print(f"{ssh_message}")
                print("\n Database connection failed, check credentials")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    # Check if required modules are installed
    required_modules = ['pymysql', 'paramiko', 'sshtunnel']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print("Missing required modules. Please install:")
        print(f"pip install {' '.join(missing_modules)}")
        sys.exit(1)
    
    main()