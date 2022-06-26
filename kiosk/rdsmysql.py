"""
Function:
    connect_RDS: connect AWS RDS with mysql
    
    create_tables: create tables.
    
    get_tables_name: get table name from database
    
    get_table_info: get table info
    
    get_top_menu: get top menu
    
    insert_into_table: insert values into table
    
    select_table: select all values in table
"""
import sys
import pymysql
import tqdm
import datetime
import re
import requests

# 이미지 가져오기
from PIL import Image
import base64
from io import BytesIO

def connect_RDS(host, port, username, passwd, database):
    """
    connect AWS RDS with mysql

    Args:
        host: AWS RDS Endpoint
        port: mysql port(3306)
        username: username
        passwd: passworde of user
        database: database name

    Returns:
        conn
        cursor
    """
    conn = pymysql.connect(host=host, user=username, passwd=passwd, db=database, port=port, use_unicode=True, charset="utf8")
    try:
        conn = pymysql.connect(host=host, user=username, passwd=passwd, db=database, port=port, use_unicode=True, charset="utf8")
        cursor = conn.cursor()
    except:
        sys.exit(1)

    return conn, cursor

def create_tables(conn, cursor):
    """
    create tables.
    
    table's name: category, menu, orderinfo, orderdetail, shelter
    """
    query_create_table_category = """
    CREATE TABLE category
    (
        id INTEGER primary key AUTO_INCREMENT,
        name VARCHAR(20) NOT NULL
    );
    """
    query_create_table_menu = """
    CREATE TABLE menu
    (
        id INTEGER primary key AUTO_INCREMENT,
        name VARCHAR(20) NOT NULL,
        price INTEGER NOT NULL,
        image LONGBLOB NOT NULL,
        category_id INTEGER,
        FOREIGN KEY (category_id) REFERENCES category (id)
    )
    """
    query_create_table_orderinfo = """
    CREATE TABLE orderinfo
    (
        id INTEGER primary key AUTO_INCREMENT,
        weather VARCHAR(20) NOT NULL,
        process_time TIME NOT NULL,
        order_time DATETIME NOT NULL,
        senior VARCHAR(10) NOT NULL,
        gender VARCHAR(2) NOT NULL,
        shelter_id INTEGER NOT NULL,
        FOREIGN KEY (shelter_id) REFERENCES shelter (id)
    )
    """
    query_create_table_orderdetail = """
    CREATE TABLE orderdetail
    (
        id INTEGER primary key AUTO_INCREMENT,
        orderinfo_id INTEGER,
        menu_id INTEGER,
        amount INTEGER NOT NULL,
        FOREIGN KEY (orderinfo_id) REFERENCES orderinfo (id),
        FOREIGN KEY (menu_id) REFERENCES menu (id)
    )
    """
    query_create_table_shelter = """
    CREATE TABLE shelter
    (
        id INTEGER primary key AUTO_INCREMENT,
        name VARCHAR(20) NOT NULL,
        latitude DOUBLE NOT NULL,
        longitude DOUBLE NOT NULL
    )
    """
    
    cursor.execute("SHOW TABLES")
    tables = [table[0] for table in cursor.fetchall()]
    
    if "shelter" not in tables:
        cursor.execute(query_create_table_shelter)
    if "category" not in tables:
        cursor.execute(query_create_table_category)
    if "menu" not in tables:
        cursor.execute(query_create_table_menu)
    if "orderinfo" not in tables:
        cursor.execute(query_create_table_orderinfo)
    if "orderdetail" not in tables:
        cursor.execute(query_create_table_orderdetail)
    
    conn.commit()
    
def get_tables_name(cursor, db) -> tuple[str]:
    """
    get table name from database

    Args:
        cursor: mysql cursor
        db: database name

    Returns:
        tuple: name of tables
    """
    cursor.execute(f"USE {db}")
    cursor.execute("SHOW TABLES")
    tables = [table[0] for table in cursor.fetchall()]
    
    return tables

def get_table_info(cursor, db, table) -> tuple[str]:
    """
    get table info

    Args:
        cursor (_type_): mysql cursor
        db (_type_): _description_
        table (_type_): _description_

    Returns:
        tuple[str]: _description_
    """
    cursor.execute(f"USE {db}")
    cursor.execute(f"show columns from {table};")
    columns = cursor.fetchall()
    
    return columns

def get_top_menu(cursor, **kwargs):
    """
    get top menu

    Args:
        cursor: cursor
        gender: gender. ['M', 'F']
        senior: senior. ['senior', 'normal']
        weather: weather. ['sunny', 'cloud', 'rain']
        days: days that count. for example, days=30 is "counting from 30 days in advance"
        dates: dates that count. [start, end]. for example, dates=['2022/06/01', '2022/06/25'] is "counting from 2022/06/01 to 2022/06/25"
        top_cnt: top count. default is 3
    """
    options = list()

    if "gender" in kwargs:
        if kwargs['gender'] in ["M", "F"]:
            options.append(f"i.gender='{kwargs['gender']}'")
    if "senior" in kwargs:
        if kwargs['senior'] in ["senior", "normal"]:
            options.append(f"i.senior='{kwargs['senior']}'")
    if "weather" in kwargs:
        if kwargs["weather"] in ["sunny", "cloud", "rain"]:
            options.append(f"i.weather='{kwargs['weather']}'")
    if "days" in kwargs:
        options.append(f"DATEDIFF(i.order_time, DATE_ADD(NOW(), INTERVAL -{kwargs['days']} DAY)) >= {kwargs['days']}")
    elif "dates" in kwargs:
        dates = kwargs["dates"]
        if all(re.match("[0-9]{4}\/[0-1][0-9]\/[0-3][0-9]", day) for day in dates):
            options.append(f"DATEDIFF(i.order_time, '{dates[0]}') >= 0")
            options.append(f"DATEDIFF(i.order_time, '{dates[1]}') <= 0")
        
    # print(options)
    if len(options) > 0:
        options = "WHERE " + " AND ".join(options)
    else:
        options = ""
    # print(options)
        
        
    top_cnt = kwargs["top_cnt"] if "top_cnt" in kwargs else 3
    
        
    query = f"""
    SELECT menu_id, menu_name, COUNT(amount) AS mount_count
	FROM (SELECT d.id,
					 d.orderinfo_id,
					 d.menu_id,
					 d.totalprice,
					 d.amount,
					 d.price,
					 d.menu_name,
					 i.gender,
					 i.senior,
					 i.weather,
					 i.order_time
				FROM (SELECT d.id,
								 d.orderinfo_id,
								 d.menu_id,
								 d.amount,
								 m.name AS menu_name,
								 m.price,
								 d.amount * m.price AS totalprice
							FROM orderdetail AS d
							LEFT OUTER JOIN menu AS m
							ON d.menu_id = m.id
						) AS d
				LEFT OUTER JOIN orderinfo AS i
				ON i.id = d.orderinfo_id
				{options}
			) AS ordertotal
	GROUP BY menu_id
	ORDER BY mount_count DESC LIMIT {top_cnt}
    """
    
    cursor.execute(query)
    return cursor.fetchall()
    
def insert_into_table(conn, cursor, db, table, list_args):
    """
    insert values into table

    Args:
        conn: connection
        cursor: cursor
        db: database name
        table: table name
        list_args: values list. for example, [{'hour':4, 'transport':'bus'}, {'hour':2.5, 'transport':'train'}]
    """
    cursor.execute(f"USE {db}")
    cursor.execute(f"show columns from {table};")
    columns = [c[0] for c in cursor.fetchall()]
    columns.remove("id")
    
    try:
        if table in get_tables_name(cursor, db):
            for args in tqdm.tqdm(list_args):
                # time.sleep(0.2)
                query = f"INSERT INTO {table} (" + ",".join(columns) + ") VALUES ("
            
                values = list()
                
                for column in columns:
                    if type(args[column]) == str and args[column] != "NOW()":
                        values.append(f"'{args[column]}'")
                    else:
                        values.append(str(args[column]))
                query += ",".join(values) + ")"
            
                cursor.execute(query)
    except:
        print(query)
                
    conn.commit()

def select_table(cursor, db, table):
    """
    select all values in table

    Args:
        cursor: cursor
        db: database name
        table: table name

    Returns:
        tuple of table's value
    """
    cursor.execute(f"USE {db}")
    cursor.execute(f"SELECT * FROM {table}")
    result = cursor.fetchall()
    
    return result

def select_table_where(cursor, db, table, **kwargs):
    """
    select all values in table

    Args:
        cursor: cursor
        db: database name
        table: table name

    Returns:
        tuple of table's value
    """
    cursor.execute(f"USE {db}")
    
    # opt = list()sew3
    # for key in kwargs:

    cursor.execute(f"SELECT * FROM {table}")
    
    result = cursor.fetchall()
    
    return result

def insert_into_orderinfo(conn, cursor, **kwargs):
    """_summary_

    Args:
        conn (_type_): _description_
        cursor (_type_): _description_
    """
    column = dict()
    column["gender"] = kwargs["gender"]
    column["senior"] = kwargs["senior"]
    column["shelter_id"] = kwargs["shelter_id"]
    
    tmp = select_table(cursor, "KIOSK", "shelter")
    try:
        for row in tmp:
            if row[0] == column["shelter_id"]:
                lat = row[2]
                lon = row[3]
    except:
        print("해당하는 휴게소 id가 없습니다.")

    json_weather = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid=e3a6f5bd6a9fbebf266d7139f119084b").json()
    weather_id = str(json_weather['weather'][0]['id'])
    if weather_id in ("800", "801", "802"):
        weather = "sunny"
    elif weather_id in ("210", "211", "212", "221",
                        "701", "711", "721", "731", "741", "751", "761", "762", "771", "781"):
        weather = "cloud"
    else:
        weather = "rain"
    column["weather"] = weather
    
    UTC = datetime.timezone(datetime.timedelta(hours=0))
    column["process_time"] = datetime.datetime.fromtimestamp(kwargs["process_time"][1].timestamp() - kwargs["process_time"][0].timestamp(), tz=UTC).strftime("%H:%M:%S")
    column["order_time"] = "NOW()"
    
    insert_into_table(conn, cursor, "KIOSK", "orderinfo", [column])
    
    cursor.execute("SELECT MAX(ID) FROM orderinfo")
    
    return cursor.fetchall()[0][0]


# def insert_into_orderinfo(conn, cursor, **kwargs):
    # for column in columns



if __name__ == "__main__":
    host_master = "noname-rds-instance.cryncpn8iv7d.ap-southeast-1.rds.amazonaws.com"
    host_slave = "noname-rds-instance-replica.cryncpn8iv7d.ap-southeast-1.rds.amazonaws.com"
    port = 3306
    username = "root"
    database = "KIOSK"
    passwd = "awsbigdata"
    
    conn_m, cursor_m = connect_RDS(host_master, port, username, passwd, database)
    conn_s, cursor_s = connect_RDS(host_slave, port, username, passwd, database)

    import datetime
    # print(insert_into_order(conn_m, cursor_m, gender="M", senior="senior", shelter_id=7, process_time=[datetime.datetime.fromtimestamp(datetime.datetime.now().timestamp()-100), datetime.datetime.now()]))
    start = datetime.datetime.fromtimestamp(datetime.datetime.now().timestamp()-100)
    end = datetime.datetime.now()
    
    # orderinfo_id = insert_into_orderinfo(conn_m, cursor_m, gender="M", senior="senior", shelter_id=7, process_time=[start, end])
    # insert_into_table(conn_m, cursor_m, "KIOSK", "orderdetail", [{"menu_id":5, "amount":3, "orderinfo_id":orderinfo_id}])
    # print(insert_into_order(conn_m, cursor_m, gender="M", senior="senior", shelter_id=7, process_time=[start, end]))
    
    print('===========')
    print(get_top_menu(cursor_s, gender="M", senior="normal", weather="cloud", dates=["2022/06/01", "2022/06/30"], top_cnt=5))
    
    # 이미지 가져오기
    # images = select_table(cursor_s, database, "menu")
    # for image in select_table(cursor_s, database, "menu")[:2]:
    #     img = Image.open(BytesIO(base64.b64decode(image[4])))
    #     img.show()
    