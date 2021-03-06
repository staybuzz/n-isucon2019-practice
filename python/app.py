from flask import Flask, request, abort, jsonify, make_response, send_file
import os
import pymysql.cursors
import json
import subprocess
import pathlib
import base64
import tempfile
from flask_login import LoginManager, UserMixin, login_required
from flask_login import login_user, logout_user, current_user

from utils.utility import get_salt, get_passwordhash
from utils.utility import get_today

from wsgi_lineprof.middleware import LineProfilerMiddleware
from wsgi_lineprof.filters import FilenameFilter, TotalTimeSorter

import pymysql
from DBUtils.PooledDB import PooledDB

static_folder = pathlib.Path(__file__).resolve().parent / 'public'
app = Flask(__name__, static_folder=str(static_folder), static_url_path='')
### lineprof
#app.config['PROFILE'] = True
#filters = [
#    FilenameFilter("app.py"),
#    lambda stats: filter(lambda stat: stat.total_time > 0.0001, stats),
#]
#lineprof_f = open("/tmp/lineprof.log", "w")
#app.wsgi_app = LineProfilerMiddleware(app.wsgi_app, stream=lineprof_f, filters=filters)


# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = 'for_flask_loginBMXFzvfMNqF1J9SXqeI8y/QCEj9bzTZBqCU'


class User(UserMixin):

    def __init__(self, user_id, username):
        self.id = user_id
        self.name = username

    def get_id(self):
        return self.id

    def get_username(self):
        return self.name

    @classmethod
    def get_user(cls, user_id):

        if user_id not in users:
            return None

        return users[user_id]


users = {}


@login_manager.user_loader
def load_user(user_id):
    return User.get_user(user_id)


dbparams = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE'),
    'cursorclass': pymysql.cursors.DictCursor
}
mySQLConnectionPool = PooledDB(creator=pymysql,
                               host=dbparams['host'],
                               user=dbparams['user'],
                               password=dbparams['password'],
                               database=dbparams['database'],
                               cursorclass=dbparams['cursorclass'])


@app.route('/')
def index():
    return send_file(str(static_folder) + '/index.html')


@app.route('/signin', methods=['POST'])
def signin():
    if request.json is None:
        abort(400)

    data = request.json
    username = data.get('username', '')
    password = data.get('password', '')

    if username == '' or password == '':
        abort(400)

    conn = mySQLConnectionPool.connection()

    with conn.cursor() as cursor:
        query = 'SELECT id, username, password_hash, salt FROM users WHERE username=%s'
        cursor.execute(query, (username, ))
        app.logger.debug(cursor._last_executed)
        result = cursor.fetchone()
        conn.close()

    if result is None:
        abort(401)

    salt = result.pop('salt', None)
    password_hash = result.pop('password_hash', None)

    if get_passwordhash(salt, password) != password_hash:
        abort(401)

    user = User(int(result['id']), username)
    login_user(user)
    users[result['id']] = user

    return jsonify(username=username), 200


@app.route('/signout', methods=['GET'])
@login_required
def signout():
    logout_user()
    return '', 204


# Todo: this GET method is for debugging
@app.route('/users', methods=['GET'])
def get_users_all():
    conn = mySQLConnectionPool.connection()
    with conn.cursor() as cursor:
        query = 'SELECT id, username FROM users ORDER BY id ASC ;'
        cursor.execute(query)
        app.logger.debug(cursor._last_executed)
        result = cursor.fetchall()

        if result is None:
            abort(404)

    conn.close()

    return jsonify(result)


@app.route('/users/<string:username>', methods=['GET'])
def get_users(username):
    conn = mySQLConnectionPool.connection()
    with conn.cursor() as cursor:
        query = 'SELECT id, username, created_at, updated_at '\
                'FROM users WHERE username = %s'
        cursor.execute(query, (username,))
        app.logger.debug(cursor._last_executed)
        result = cursor.fetchone()

        if result is None:
            abort(404)

    conn.close()

    return jsonify(result)


@app.route('/users', methods=['POST'])
def post_users():
    if request.json is None:
        abort(400)

    data = request.json

    username = data.get('username', '')
    password = data.get('password', '')

    if username == '' or password == '':
        abort(400)  # missing arguments

    conn = mySQLConnectionPool.connection()
    try:
        with conn.cursor() as cursor:
            query = 'SELECT id FROM users WHERE username=%s'
            number_of_rows = cursor.execute(query, (username,))
            app.logger.debug(cursor._last_executed)

            if number_of_rows > 0:
                abort(409)  # existing user

        salt = get_salt()
        password_hash = get_passwordhash(salt, password)
        current_time = get_today()

        with conn.cursor() as cursor:
            query = 'INSERT INTO users (username, password_hash,' \
                    'salt, created_at, updated_at)' \
                    ' VALUES (%s, %s, %s, %s, %s);'
            cursor.execute(query, (username, password_hash,
                                   salt, current_time, current_time))
            app.logger.debug(cursor._last_executed)
            user_info = {
                'id': cursor.lastrowid,
                'username': username,
                'created_at': current_time,
                'updated_at': current_time
            }

        conn.commit()
    finally:
        conn.close()

    return jsonify(**user_info), 201


@app.route('/users/<string:username>', methods=['PATCH'])
@login_required
def patch_users(username):
    if request.json is None:
        abort(400)

    data = request.json

    new_username = data.get('username', '')
    password = data.get('password', '')

    if new_username == '' and password == '':
        abort(400)

    conn = mySQLConnectionPool.connection()
    try:
        with conn.cursor() as cursor:
            query = 'SELECT id, username, salt, password_hash FROM users WHERE username=%s'
            cursor.execute(query, (username))
            app.logger.debug(cursor._last_executed)
            result = cursor.fetchone()

            if result is None:
                abort(404)

        # Users must not change other username.
        user_id = current_user.get_id()
        if result['id'] != user_id:
            abort(403)

        if new_username == '':
            new_username = result['username']
        else:
            with conn.cursor() as cursor:
                query = 'SELECT id FROM users WHERE username=%s'
                cursor.execute(query, (new_username))
                app.logger.debug(cursor._last_executed)
                user = cursor.fetchone()

                # User can't change to existing username
                if user is not None:
                    abort(409)

        if password == '':
            salt = result['salt']
            password_hash = result['password_hash']
        else:
            salt = get_salt()
            password_hash = get_passwordhash(salt, password)

        with conn.cursor() as cursor:
            query = 'UPDATE users SET username=%s, password_hash=%s, '\
                    'salt=%s, updated_at=%s WHERE id=%s'
            cursor.execute(query,
                           (new_username, password_hash, salt,
                            get_today(), user_id))
            app.logger.debug(cursor._last_executed)

        conn.commit()

        with conn.cursor() as cursor:
            query = 'SELECT id, username, created_at, updated_at '\
                    'FROM users WHERE id=%s'
            cursor.execute(query, (user_id,))
            app.logger.debug(cursor._last_executed)
            result = cursor.fetchone()

        return jsonify(result)
    finally:
        conn.close()


@app.route('/users/<string:username>', methods=['DELETE'])
@login_required
def delete_users(username):
    conn = mySQLConnectionPool.connection()
    try:
        with conn.cursor() as cursor:
            query = 'SELECT id FROM users WHERE username=%s'
            cursor.execute(query, (username,))
            app.logger.debug(cursor._last_executed)
            result = cursor.fetchone()

        if result is None:
            abort(404)

        user_id = current_user.get_id()
        if result['id'] != user_id:
            abort(403)

        with conn.cursor() as cursor:
            query = 'DELETE FROM users WHERE id=%s'
            cursor.execute(query, (user_id,))
            app.logger.debug(cursor._last_executed)
            conn.commit()

        logout_user()
        return '', 204
    finally:
        conn.close()


@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    conn = mySQLConnectionPool.connection()

    try:
        with conn.cursor() as cursor:
            query = 'SELECT items.*, users.username FROM items INNER JOIN users ON items.user_id = users.id WHERE items.id=%s'
            cursor.execute(query, (item_id,))
            app.logger.debug(cursor._last_executed)
            result = cursor.fetchone()

            if result is None:
                abort(404)

            if result['likes'] is None:
                result['likes'] = ""

        result.pop('user_id')

        return jsonify(result)
    finally:
        conn.close()


@app.route('/items', methods=['GET'])
def get_items():
    ITEM_LIMIT = 10
    offset = int(request.args.get('page', 0)) * ITEM_LIMIT
    sort = request.args.get('sort', '')

    conn = mySQLConnectionPool.connection()
    try:
        with conn.cursor() as cursor:
            if sort == 'like':
                query = 'SELECT items.id, items.title, items.created_at, users.username ' \
                        'FROM items left join users on items.user_id = users.id ORDER BY items.likes_count DESC ' \
                        'LIMIT %s OFFSET %s ;'
                cursor.execute(query, (ITEM_LIMIT, offset,))
                app.logger.debug(cursor._last_executed)
            else:
                query = 'SELECT items.id, items.title, items.created_at, users.username ' \
                        'FROM items left join users on items.user_id = users.id ORDER BY items.created_at DESC '\
                        'LIMIT %s OFFSET %s ;'
                cursor.execute(query, (ITEM_LIMIT, offset,))
                app.logger.debug(cursor._last_executed)

            result = cursor.fetchall()

            query = 'SELECT count(id) FROM items'
            cursor.execute(query,)
            app.logger.debug(cursor._last_executed)
            result_for_count = cursor.fetchone()
            num_total_items = result_for_count['count(id)']

        response = {
            'count': num_total_items,
            'items': result
        }

        return jsonify(response)
    finally:
        conn.close()


@ app.route('/users/<string:username>/icon', methods=['POST'])
@ login_required
def post_icon(username):
    if username != current_user.get_username():
        abort(403)

    if 'iconimage' not in request.files:
        abort(400)

    icon_dir = os.path.join(str(static_folder), 'users', username)
    if os.path.exists(os.path.join(icon_dir, 'icon')):
        abort(409)

    file = request.files['iconimage']
    if not os.path.exists(icon_dir):
        os.makedirs(icon_dir)
    with open(os.path.join(icon_dir, 'icon'), 'wb') as tempf:
        file.save(tempf)
    return "", 201


@ app.route('/users/<string:username>/icon', methods=['GET'])
def get_icon(username):
    conn = mySQLConnectionPool.connection()
    try:
        with conn.cursor() as cursor:
            query = 'SELECT id FROM users WHERE username=%s'
            cursor.execute(query, (username,))
            app.logger.debug(cursor._last_executed)
            result = cursor.fetchone()

        if result is None:
            return '', 404

        icon_path = os.path.join(str(static_folder), 'users', username, 'icon')
        if not os.path.exists(icon_path):
            return send_file(str(static_folder) + '/img/default_user_icon.png',
                             mimetype='image/png')
        return send_file(icon_path, mimetype='image/png')

    finally:
        conn.close()


@ app.route('/items', methods=['POST'])
@ login_required
def post_item():
    if request.json is None:
        abort(400)

    data = request.json
    title = data.get('title', '')
    body = data.get('body', '')

    if title == '' or body == '':
        abort(400)  # missing arguments

    conn = mySQLConnectionPool.connection()

    try:
        with conn.cursor() as cursor:
            today = get_today()
            user_id = str(current_user.get_id())

            query = 'INSERT INTO items '\
                '(user_id, title, body, created_at, updated_at) '\
                    'VALUES (%s, %s, %s, %s, %s);'
            cursor.execute(query, (user_id, title, body, today, today))
            app.logger.debug(cursor._last_executed)
            item_id = str(cursor.lastrowid)

        conn.commit()

        with conn.cursor() as cursor:
            query = 'SELECT * FROM items WHERE id=%s'
            cursor.execute(query, (item_id))
            app.logger.debug(cursor._last_executed)
            result = cursor.fetchone()

        if result['likes'] is None:
            result['likes'] = ''

        result['username'] = current_user.get_username()
        result.pop('user_id')

        response = jsonify(result)
        response.status_code = 201
        return response
    finally:
        conn.close()


@ app.route('/items/<int:item_id>', methods=['PATCH'])
@ login_required
def patch_item(item_id):
    if request.json is None:
        abort(400)

    data = request.json
    conn = mySQLConnectionPool.connection()

    try:
        with conn.cursor() as cursor:
            query = 'SELECT * FROM items WHERE id=%s'
            cursor.execute(query, (item_id))
            app.logger.debug(cursor._last_executed)
            result = cursor.fetchone()

            if result is None:
                abort(404)

        user_id = current_user.get_id()
        if result['user_id'] != user_id:
            abort(403)

        title = data.get('title', '')
        body = data.get('body', '')

        if title == '' and body == '':
            abort(400)  # missing arguments

        if title == '':
            title = result['title']

        if body == '':
            body = result['body']

        with conn.cursor() as cursor:
            query = 'UPDATE items SET title=%s, body=%s, updated_at=%s '\
                'WHERE id=%s'

            now = get_today()
            cursor.execute(query, (title, body, now, item_id))
            app.logger.debug(cursor._last_executed)

        conn.commit()

        with conn.cursor() as cursor:
            query = 'SELECT * FROM items WHERE id=%s'
            cursor.execute(query, (item_id))
            app.logger.debug(cursor._last_executed)
            result = cursor.fetchone()

        if result['likes'] is None:
            result['likes'] = ''

        result['username'] = current_user.get_username()
        result.pop('user_id')

        return jsonify(result)
    finally:
        conn.close()


@ app.route('/items/<int:item_id>', methods=['DELETE'])
@ login_required
def delete_item(item_id):
    conn = mySQLConnectionPool.connection()
    try:
        with conn.cursor() as cursor:
            query = 'SELECT user_id FROM items WHERE id=%s'
            cursor.execute(query, (item_id,))
            app.logger.debug(cursor._last_executed)
            result = cursor.fetchone()

            if result is None:
                abort(404)

            user_id = current_user.get_id()
            if result['user_id'] != user_id:
                abort(403)

            query = 'DELETE FROM items WHERE id=%s'
            cursor.execute(query, (item_id,))
            app.logger.debug(cursor._last_executed)
            conn.commit()

            return '', 204
    finally:
        conn.close()


@ app.route('/items/<int:item_id>/likes', methods=['GET'])
def get_likes(item_id):
    conn = mySQLConnectionPool.connection()
    try:
        with conn.cursor() as cursor:
            query = 'SELECT likes, likes_count FROM items WHERE id=%s'
            cursor.execute(query, (item_id,))
            app.logger.debug(cursor._last_executed)
            result = cursor.fetchone()

            if result is None:
                abort(404)

            likes = result['likes']

            if likes is None:
                res = {"likes": "", "like_count": 0}
            else:
                likes_count = result['likes_count']
                res = {"likes": likes, "like_count": likes_count}

            return jsonify(res)
    finally:
        conn.close()


@ app.route('/items/<int:item_id>/likes', methods=['POST'])
@ login_required
def post_likes(item_id):
    conn = mySQLConnectionPool.connection()

    try:
        with conn.cursor() as cursor:
            query = 'SELECT likes, likes_count FROM items WHERE id=%s'
            cursor.execute(query, (item_id,))
            app.logger.debug(cursor._last_executed)
            result = cursor.fetchone()

            if result is None:
                abort(404)

            username = current_user.get_username()
            likes = result['likes'] or ''
            likes_count = result['likes_count'] or 0
            if len(likes) == 0:
                likes_str = username
                likes_count += 1
            else:
                current_likes_list = likes.split(',')

                if username not in current_likes_list:
                    current_likes_list.append(username)
                    likes_str = ','.join(list(current_likes_list))
                    likes_count += 1
                else:
                    likes_str = likes

            query = 'UPDATE items SET likes=%s, likes_count=%s WHERE id=%s'
            cursor.execute(query, (likes_str, likes_count, item_id,))
            app.logger.debug(cursor._last_executed)
            conn.commit()
    finally:
        conn.close()

    return '', 204


@ app.route('/items/<int:item_id>/likes', methods=['DELETE'])
@ login_required
def delete_likes(item_id):
    conn = mySQLConnectionPool.connection()

    try:
        with conn.cursor() as cursor:
            query = 'SELECT likes, likes_count FROM items WHERE id=%s'
            cursor.execute(query, (item_id,))
            app.logger.debug(cursor._last_executed)
            result = cursor.fetchone()

            if result is None:
                abort(404)

            likes = result['likes'] or ''
            likes_count = result['likes_count'] or 0
            if len(likes) == 0:
                abort(404)
            else:
                username = current_user.get_username()
                current_likes_list = likes.split(',')

                if username not in current_likes_list:
                    abort(404)
                else:
                    current_likes_list.remove(username)
                    likes_count -= 1
                    if len(current_likes_list) == 0:
                        likes_str = None
                    else:
                        likes_str = ','.join(list(current_likes_list))

            query = 'UPDATE items SET likes=%s, likes_count=%s WHERE id=%s'
            cursor.execute(query, (likes_str, likes_count, item_id,))
            app.logger.debug(cursor._last_executed)
            conn.commit()
    finally:
        conn.close()

    return '', 204


@ app.route('/items/<int:item_id>/comments', methods=['GET'])
def get_comments(item_id):
    conn = mySQLConnectionPool.connection()

    try:
        with conn.cursor() as cursor:
            query = 'SELECT * FROM comments WHERE id=%s'
            cursor.execute(query, (item_id,))
            app.logger.debug(cursor._last_executed)
            result = cursor.fetchone()

            query = 'SELECT id FROM items WHERE id=%s'
            cursor.execute(query, (item_id,))
            app.logger.debug(cursor._last_executed)
            result_item = cursor.fetchone()

            if result_item is None:
                abort(404)

            data = {'item_id': item_id}
            if result is None:
                data['comments'] = list()
                return jsonify(data)

            item_comments_except_null = list()
            for key, value in result.items():
                if key == 'id' or value is None:
                    continue

                item_comments_except_null.append(json.loads(value))

            data['comments'] = item_comments_except_null
            return jsonify(data)
    finally:
        conn.close()


@ app.route('/items/<int:item_id>/comments', methods=['POST'])
@ login_required
def post_comment(item_id):
    if request.json is None:
        abort(400)

    data = request.json
    comment = data.get('comment', '')

    if comment == '':
        abort(400)

    conn = mySQLConnectionPool.connection()
    try:
        with conn.cursor() as cursor:
            query = 'SELECT id FROM items WHERE id=%s'
            cursor.execute(query, (item_id,))
            app.logger.debug(cursor._last_executed)
            result = cursor.fetchone()

            if result is None:  # if item_id is't exist in items table
                abort(404)

            query = 'SELECT * FROM comments WHERE id=%s'
            cursor.execute(query, (item_id,))
            app.logger.debug(cursor._last_executed)
            result = cursor.fetchone()

            username = current_user.get_username()
            comment_data = {'comment': comment, 'username': username}
            if result is None:  # first comment
                comment_data['comment_id'] = 1
                query = 'INSERT INTO comments (id, comment_001) '\
                    'VALUES (%s, %s)'
                cursor.execute(query, (item_id, json.dumps(comment_data)))
                app.logger.debug(cursor._last_executed)
            else:
                for key, value in sorted(result.items()):
                    if value is None:
                        comment_data['comment_id'] = int(key[-3:])
                        query = 'UPDATE comments SET ' + key + \
                            '=%s WHERE id=%s'
                        cursor.execute(query,
                                       (json.dumps(comment_data), item_id))
                        app.logger.debug(cursor._last_executed)
                        break
                    if key == 'id':
                        continue

            conn.commit()

            comment_data['item_id'] = item_id
            return jsonify(comment_data), 201
    finally:
        conn.close()


@ app.route('/items/<int:item_id>/comments/<int:comment_id>',
            methods=['DELETE'])
@ login_required
def delete_coment(item_id, comment_id):
    conn = mySQLConnectionPool.connection()
    try:
        with conn.cursor() as cursor:
            query = 'SELECT * FROM comments WHERE id=%s'
            cursor.execute(query, (item_id,))
            app.logger.debug(cursor._last_executed)
            result = cursor.fetchone()

            if result is None:
                abort(404)

            status_code = 404

            for key, value in result.items():
                if key == 'id' or value is None:
                    continue
                else:
                    comment = json.loads(value)
                    username = current_user.get_username()
                    if comment['comment_id'] != comment_id:
                        continue
                    else:
                        if comment['username'] != username:
                            abort(403)
                        else:
                            query = 'UPDATE comments SET ' + key + \
                                '=NULL WHERE id=%s'
                            cursor.execute(query, item_id)
                            app.logger.debug(cursor._last_executed)
                            conn.commit()
                            status_code = 204
                            break

            return '', status_code
    finally:
        conn.close()


def get_username_by_id(user_id):
    conn = mySQLConnectionPool.connection()

    try:
        with conn.cursor() as cursor:
            query = 'SELECT username FROM users WHERE id = %s'
            cursor.execute(query, (user_id,))
            app.logger.debug(cursor._last_executed)
            result = cursor.fetchone()

        return result['username']
    finally:
        conn.close()


@ app.route('/initialize', methods=['GET'])
def get_initialize():
    subprocess.call(['../common/db/init.sh'])
    get_likes_count()
    return '', 200


@ app.route('/get_likes_count', methods=['GET'])
def get_likes_count():
    conn = mySQLConnectionPool.connection()
    try:
        with conn.cursor() as cursor:
            query = 'SELECT id, likes FROM items'
            cursor.execute(query, )
            app.logger.debug(cursor._last_executed)
            result = cursor.fetchall()

            for item in result:

                likes = item['likes']

                if likes is None:
                    query = 'UPDATE items SET likes_count=0 where id=%s'
                    cursor.execute(query, (item['id'],))
                else:
                    likes_count = len(likes.split(','))
                    query = 'UPDATE items SET likes_count=%s where id=%s'
                    cursor.execute(query, (likes_count, item['id'],))

            conn.commit()
            return "Done", 200
    finally:
        conn.close()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
