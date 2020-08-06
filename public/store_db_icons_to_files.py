import pymysql.cursors
import base64
import os
import pathlib

dbparams = {
    'host': 'localhost',
    'user': 'isucon',
    'password': 'nocusi',
    'database': 'app',
    'cursorclass': pymysql.cursors.DictCursor
}
conn = pymysql.connect(**dbparams)
static_folder = pathlib.Path(__file__).resolve().parent

# get icon set user
try:
    with conn.cursor() as cursor:
        query = 'SELECT users.username, icon.icon FROM icon INNER JOIN users ON icon.user_id = users.id'
        # query = 'SELECT users.username, icon.user_id FROM icon INNER JOIN users ON icon.user_id = users.id'
        cursor.execute(query)
        result = cursor.fetchall()
    # print(result)

    for r in result:
        icon_dir = os.path.join(str(static_folder), 'users', r['username'])
        if not os.path.exists(icon_dir):
            os.makedirs(icon_dir)
        with open(os.path.join(icon_dir, 'icon'), 'wb') as f:
            f.write(base64.b64decode(r['icon']))

finally:
    conn.close()
