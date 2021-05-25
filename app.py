from flask import Flask, render_template, request, flash, url_for, redirect, session, jsonify, make_response
import pyodbc
import datetime
from waitress import serve
import mysql.connector
from datetime import timezone
app = Flask(__name__)



config = {
    'user': 'root',
    'host': '34.123.210.240',
    'database': 'Test_DB'
}

# now we establish our connection
conn = mysql.connector.connect(**config)


# conn = pyodbc.connect('Driver={SQL Server};'
#                      'Server=DESKTOP-VQFCIJ2;'
#                      'Database=Test_DB;'
#                      'Trusted_Connection=yes;')


@app.route('/v1/insert', methods=['POST'])
def posting():
    some_json = request.get_json(force=True)
    value = some_json['value']
    value_2 = some_json['value_2']
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    device_key = some_json['key']
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    cursor.execute(
        "Insert into A_" + str(device_key) + " values ('" + str(value) + "','" + str(value_2) + "','" + str(date) + "')")
    conn.commit()
    return jsonify({"you sent": some_json}), 201
    conn.close()


@app.route('/v1/get', methods=['POST'])
def getting():
    some_json = request.get_json(force=True)
    key = (some_json['key'])
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    length_of_key = len(key)
    value_list = []
    value_2_list = []
    time_list = []
    for i in range(0, length_of_key):
        cursor.execute("SELECT value,value_2,time FROM A_" + str(key[i]) + " order by time desc LIMIT 1;")
        for row in cursor:
            value_list.append(int(row[0]))
            value_2_list.append(int(row[1]))
            time_list.append(str(row[2]))

    print(value_list)
    print(value_2_list)
    print(time_list)

    return jsonify({"value": [value_list],
                    "value_2": [value_2_list],
                    "time": [time_list]})
    conn.close()

@app.route('/v1/getall', methods=['POST'])
def gettingall():
    some_json = request.get_json(force=True)
    key = (some_json['key'])
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    length_of_key = len(key)
    value_list = []
    value_2_list = []
    time_list = []
    for i in range(0, length_of_key):
        cursor.execute("SELECT value,value_2,time FROM A_" + str(key[i]) + " order by time asc ;")
        for row in cursor:
            value_list.append(int(row[0]))
            value_2_list.append(int(row[1]))
            time_list.append(str(row[2]))

    return jsonify({"value": [value_list],
                    "value_2": [value_2_list],
                    "time": [time_list]})




    conn.close()


@app.route('/')
def homepage():
    session["username"] = None
    return redirect(url_for("login"))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        try:
            user_email = request.form["email"]
            user_password = request.form["password"]
            user_con_password = request.form["con_password"]

            cursor = conn.cursor()
            cursor.execute(
                "SELECT u_email,u_password from users where u_email ='" + user_email + "';")
            list_cursor = list(cursor)
            if len(list_cursor) == 0:

                if user_password == user_con_password:

                    cursor = conn.cursor()
                    cursor.execute("Insert into users (u_email , u_password) values ('" + user_email + "','" + user_password + "')")
                    conn.commit()

                    return redirect(url_for("login"))

                else:
                    flash("Passwords do not match")
                    return render_template("signup.html")
            else:
                flash("User Already Exists")
                return render_template("signup.html")
        except Exception as e:
            flash(e)
            return render_template("signup.html")
    else:
        return render_template("signup.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        user_email = request.form["email"]
        user_password = request.form["password"]

        cursor = conn.cursor()
        cursor.execute(
            "SELECT u_email,u_password from users where u_email ='" + user_email + "' and u_password ='" + user_password + "';")
        list_cursor = list(cursor)
        if len(list_cursor) > 0:
            flash("WELCOME USER")
            session["username"] = user_email
            return redirect(url_for("dashboard"))
        else:
            flash("Wrong password")
            return render_template("login.html")
    else:
        if session["username"] is None:
            return render_template("login.html")
        else:
            return redirect(url_for("dashboard"))


@app.route('/dashboard/')
def dashboard():
    if session["username"] is not None:
        username = session["username"]
        cursor = conn.cursor()
        cursor.execute("select u_id from users where u_email ='" + session["username"] + "';")
        list_cursor = list(cursor.fetchone())
        u_id = int(list_cursor[0])
        temp_device_key = []

        cursor.execute(
            "SELECT device_key FROM conn_devices where u_id = " + str(u_id) + " LIMIT 10")
        for row in cursor:
            temp_device_key.append(row[0])
        return render_template("dashboard.html", username=username, sensors_number=len(temp_device_key),
                               device_key=temp_device_key, device_date=str(datetime.datetime.now()),
                               len=len(temp_device_key))
    else:
        return redirect(url_for("login"))


@app.route('/add_device', methods=['POST'])
def add_device():
    if request.method == "POST":
        if "username" in session:
            cursor = conn.cursor()
            cursor.execute("select u_id from users where u_email ='" + session["username"] + "';")
            list_cursor = list(cursor.fetchone())
            u_id = int(list_cursor[0])
            device_key = request.form["device_key"]
            device_type = request.form["device_type"]

            cursor.execute("select device_key, device_type from "
                           "devices where device_key ='" + device_key + "' and device_type ='" + device_type + "';")

            list_cursor = list(cursor)
            if len(list_cursor) > 0:
                cursor.execute("Insert into conn_devices values (" + device_key + "," + str(u_id) + ");")
                conn.commit()
                cursor.execute("Create table A_" + str(device_key) + "(value int,value_2 int, time datetime);")
                conn.commit()
                return redirect(url_for("dashboard"))
            else:
                return "<h1> DEVICE IS NOT PRESENT IN DATABASE </h1>"


        else:
            return "<h1> Please Login First </h1>"

    else:
        return render_template("dashboard.html")


@app.route('/v1/sensor_page/<device_key>/')
def sensor_page(device_key):
    if session["username"] is not None:
        username = session["username"]
        cursor = conn.cursor()
        cursor.execute("select u_id from users where u_email ='" + session["username"] + "';")
        list_cursor = list(cursor.fetchone())
        u_id = int(list_cursor[0])
        temp_device_key = []
        temp_device_key.append(int(device_key))

        return render_template("sensor_page.html", username=username, sensors_number=1,
                               device_key=temp_device_key, device_date=str(datetime.datetime.now()),
                               len=1)
    else:
        return redirect(url_for("login"))


@app.route('/logout', methods=['GET'])
def logout():
    session["username"] = None
    return redirect(url_for("login"))


if __name__ == '__main__':
    app.config['SESSION_TYPE'] = 'memcached'
    app.config['SECRET_KEY'] = 'super secret key'
    app.run(debug=True, threaded=True, host='0.0.0.0')
    # serve(app, host='0.0.0.0', port=8080, threads=1) #WAITRESS!
    #app.run(host='0.0.0.0', port=5000)
