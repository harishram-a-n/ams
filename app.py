#om
from flask import Flask, render_template, request, redirect, url_for,send_file,session,flash
from werkzeug.security import generate_password_hash,check_password_hash
import mysql.connector, datetime,os,zipfile
from datetime import timedelta
import pandas as pd
# pip install openpyxl


app = Flask(__name__)
app.secret_key = "nec_science_and_humanities_year-1"

@app.route('/', methods=["POST", "GET"])
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        data = (request.form["username"], request.form["password"])
        mydb = mysql.connector.connect(host="harishram2k6.mysql.pythonanywhere-services.com", user="harishram2k6", password="qazxsW#123", database='harishram2k6$attendance',
auth_plugin='mysql_native_password')
        cursor = mydb.cursor()
        command = "SELECT PASSWORD FROM login_data WHERE USERNAME=%s"
        cursor.execute(command, (data[0],))
        database_data = cursor.fetchall()
        mydb.close()
        if any(database_data):
            if not check_password_hash(database_data[0][0],data[1]):
                flash("Incorrect password")
                return render_template('index.html')
            elif check_password_hash(database_data[0][0],data[1]) and data[0]=='admin':
                session["admin_valid"] = True
                return redirect(url_for('admin'))
            else:
                session["valid"] = True
                return redirect(url_for('tutor', uid=data[0]))
        else:
            flash("User not found")
            return render_template('index.html')
    return render_template("index.html")

@app.route('/manage/students',methods=['POST','GET'])
def manage_student():
    if not("admin_valid" in session):
        return redirect(url_for('login'))
    mydb = mysql.connector.connect(host="harishram2k6.mysql.pythonanywhere-services.com", user="harishram2k6", password="qazxsW#123", database='harishram2k6$attendance',auth_plugin='mysql_native_password')
    cursor = mydb.cursor()
    cursor.execute('SELECT username FROM login_data')
    tutor_uids = list(map(lambda x:x[0],cursor.fetchall()))
    tutor_uids.remove("admin")
    mydb.close()
    if request.method=='POST':
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                flash("Select a file")
                return render_template('man_stu.html',tutors=tutor_uids)
            if 'xlsx' in file.filename:
                try:
                    file.save(os.path.join(os.getcwd(),file.filename))
                    df = pd.read_excel(file.filename)
                    heading = {'regno':None,'name':None,'tutor':None}
                    for i in tuple(df):
                        topic = i.strip().replace('.','').lower()
                        if topic in heading.keys():
                            heading[topic]=i
                        elif ('name' in topic) and ('student' in topic):
                            heading['name']=i
                    data = tuple(zip(df[heading['name']],df[heading['regno']],df[heading['tutor']]))
                    mydb = mysql.connector.connect(host="harishram2k6.mysql.pythonanywhere-services.com", user="harishram2k6", password="qazxsW#123", database='harishram2k6$attendance',auth_plugin='mysql_native_password')
                    cursor = mydb.cursor()
                    section = file.filename.split('.')[0].replace(" ",'_')
                    dept = file.filename.split()[0] if " " in file.filename else file.filename.split('.')[0]
                    tutor = None
                    for i in data:
                        if type(i[-1])!=float:
                            tutor = (i[-1].split('.'))[-1].strip().lower().replace(" ","")
                        name = i[0]
                        no = i[1]
                        cursor.execute("INSERT INTO tutor VALUES(%s,%s,%s,%s,%s)",(no,dept,name,tutor,section))
                        mydb.commit()
                except:
                    mydb.close()
                    os.remove(os.path.join(os.getcwd(), file.filename))
                    flash("Some error occured! check file format")
                    return render_template('man_stu.html',tutors=tutor_uids)
                finally:
                    mydb.close()
                    os.remove(os.path.join(os.getcwd(), file.filename))
                    flash("Completed")
                    return render_template('man_stu.html',tutors=tutor_uids)
            elif file.filename.lower()=='holidays.txt':
                file.save(os.path.join(os.getcwd(), "sample.txt"))
                try:
                    def is_valid_date(date_str, format='%Y-%m-%d'):
                        try:
                            datetime.datetime.strptime(date_str, format)
                            return True
                        except ValueError:
                            return False
                    with open("sample.txt","r") as f1:
                        dates = f1.readlines()
                        for i in dates:
                            if (not is_valid_date(i)):
                                os.remove("sample.txt")
                                flash("check date or date format!")
                                return render_template('man_stu.html',tutors=tutor_uids)
                        os.rename("sample.txt","holidays.txt")
                        flash("Completed !")
                        return render_template('man_stu.html',tutors=tutor_uids)
                except:
                    flash("Error occured!")
                    return render_template('man_stu.html',tutors=tutor_uids)
                finally:
                    try:
                        os.remove("sample.txt")
                    except:
                        pass
            else:
                flash("File not supported!")
                return render_template('man_stu.html',tutors=tutor_uids)
        elif 'regno' in request.form:
            got = request.form['regno'].strip()
            try:
                regno = int(got)
                mydb = mysql.connector.connect(host="harishram2k6.mysql.pythonanywhere-services.com", user="harishram2k6", password="qazxsW#123", database='harishram2k6$attendance',auth_plugin='mysql_native_password')
                cursor = mydb.cursor()
                cursor.execute("DELETE FROM tutor where regno=%s",(regno,))
                flash(f"{regno} removed successfully!")
                mydb.commit()
            except:
                flash("Verify Regno")
                return render_template("man_stu.html",tutors=tutor_uids)
            finally:
                mydb.close()
        elif request.method=="POST" and 'regnoFrom' in request.form:
            reg_start = request.form.get('regnoFrom')
            reg_end = request.form.get('regnoTo')
            tutor_id = request.form.get('changeOption')
            if any(reg_start) and any(reg_end) and any(tutor_id):
                try:
                    mydb = mysql.connector.connect(host="harishram2k6.mysql.pythonanywhere-services.com", user="harishram2k6", password="qazxsW#123", database='harishram2k6$attendance',auth_plugin='mysql_native_password')
                    cursor = mydb.cursor()
                    cursor.execute("UPDATE tutor SET tutor_uid=%s WHERE regno BETWEEN %s AND %s",(tutor_id,int(reg_start),int(reg_end)))
                    mydb.commit()
                    flash("Tutor upadated successfully!")
                except:
                    flash("Error occured!")
                    return render_template("man_stu.html",tutors=tutor_uids)
                finally:
                    mydb.close()
    return render_template("man_stu.html",tutors=tutor_uids)

@app.route('/manage/attendance',methods=['POST','GET'])
def man_attendance():
    if not("admin_valid" in session):
        return redirect(url_for('login'))
    if request.method=="POST" and 'regNo' in request.form:
        try:
            mydb = mysql.connector.connect(host="harishram2k6.mysql.pythonanywhere-services.com", user="harishram2k6", password="qazxsW#123", database='harishram2k6$attendance',auth_plugin='mysql_native_password')
            data = (int(request.form.get('regNo')), request.form.get('date'))
            cursor = mydb.cursor()
            cursor.execute("DELETE FROM admin WHERE regno=%s AND date=%s",data)
            mydb.commit()
        except:
            pass
        finally:
            mydb.close()
            return render_template("edit_attendance.html")
    return render_template("edit_attendance.html")

@app.route('/manage/database', methods=['POST','GET'])
def man_database():
    if 'admin_valid' not in session:
        return redirect(url_for('login'))
    if request.method=="POST" and any(list(request.form)):
        try:
            mydb = mysql.connector.connect(host="harishram2k6.mysql.pythonanywhere-services.com", user="harishram2k6", password="qazxsW#123", database='harishram2k6$attendance',auth_plugin='mysql_native_password')
            cursor = mydb.cursor()
            if tuple(request.form)[0]=='student':
                cursor.execute("truncate tutor")
                mydb.commit()
            else:
                cursor.execute("truncate admin")
                mydb.commit()
            flash("Successfully deleted!")
        except:
            flash("Error occured!")
        finally:
            mydb.close()
            return render_template("drop_data.html")
    return render_template("drop_data.html")

@app.route('/manage/tutors', methods=['POST','GET'])
def submit_form():
    if not("admin_valid" in session):
        return redirect(url_for('login'))
    def db_data():
        mydb = mysql.connector.connect(host="harishram2k6.mysql.pythonanywhere-services.com", user="harishram2k6", password="qazxsW#123", database='harishram2k6$attendance',auth_plugin='mysql_native_password')
        cursor = mydb.cursor()
        cursor.execute("SELECT username,subject FROM login_data ORDER BY subject")
        data = cursor.fetchall()
        for i in range(len(data)):
            if data[i][0]=='admin':
                data.pop(i)
                break
        mydb.close()
        return data
    data = db_data()
    if request.method=="POST" and any(list(request.form)):
        try:
            mydb = mysql.connector.connect(host="harishram2k6.mysql.pythonanywhere-services.com", user="harishram2k6", password="qazxsW#123", database='harishram2k6$attendance',auth_plugin='mysql_native_password')
            cursor = mydb.cursor()
            cursor.execute("DELETE FROM login_data WHERE username=%s",tuple(request.form))
            mydb.commit()
        except:
            pass
        finally:
            mydb.close()
        data = db_data()
        return render_template("tutor_remove.html",tutors=data)
    return render_template("tutor_remove.html",tutors=data)

@app.route('/add/tutor', methods=['POST','GET'])
def tutor_add():
    if not("admin_valid" in session):
        return redirect(url_for('login'))
    if request.method=='POST':
        mydb = mysql.connector.connect(host="harishram2k6.mysql.pythonanywhere-services.com", user="harishram2k6", password="qazxsW#123", database='harishram2k6$attendance',auth_plugin='mysql_native_password')
        cursor = mydb.cursor()
        cursor.execute("SELECT username FROM login_data")
        u_name = cursor.fetchall()
        u_name = tuple(map(lambda x:x[0],u_name))
        mydb.close()
        data = (request.form["username"].strip().lower(), request.form["password"],request.form["subject"])
        if data[0] in u_name:
            flash("user exist!")
            return render_template("add_tutor.html")
        elif data[0].strip()=='' or data[1].strip()=='' or data[2].strip()=='':
            flash("data incomplete!")
            return render_template("add_tutor.html")
        else:
            mydb = mysql.connector.connect(host="harishram2k6.mysql.pythonanywhere-services.com", user="harishram2k6", password="qazxsW#123", database='harishram2k6$attendance',auth_plugin='mysql_native_password')
            cursor = mydb.cursor()
            data = list(data)
            data[1]=generate_password_hash(data[1],method='pbkdf2:sha256',salt_length=8)
            cursor.execute("INSERT INTO login_data (username,password,subject) VALUES(%s,%s,%s)",data)
            mydb.commit()
            mydb.close()
            flash(f"Successfully added {data[0]}!")
            return render_template("add_tutor.html")
    return render_template("add_tutor.html")

@app.route('/admin', methods=["POST", "GET"])
def admin():
    if not("admin_valid" in session):
        return redirect(url_for('login'))
    for i in os.listdir("/home/harishram2k6/mysite"):
        if '.csv' in i or '.zip' in i:
            os.remove("/home/harishram2k6/mysite/"+i)
    if request.method=="POST" and ('submit' in request.form):
        data = (request.form["startDate"], request.form["endDate"])
        if not(any(data[0])) or not(any(data[0])):
            return render_template('admin.html',js_code="Date not selected")
        mydb = mysql.connector.connect(host="harishram2k6.mysql.pythonanywhere-services.com", user="harishram2k6", password="qazxsW#123", database='harishram2k6$attendance',
        auth_plugin='mysql_native_password')
        cursor = mydb.cursor()
        command = "select regno,name,reason,date from admin where date between %s and %s order by sec"
        cursor.execute(command, data)
        data = cursor.fetchall()
        mydb.close()
        return render_template('admin.html', data=data)
    elif request.method=="POST" and ('download' in request.form):
        data = (request.form["startDate"],request.form["endDate"])
        if not(any(data[0])) or not(any(data[0])):
            flash("Date not selected")
            return render_template('admin.html')
        mydb = mysql.connector.connect(host="harishram2k6.mysql.pythonanywhere-services.com",user="harishram2k6",password="qazxsW#123",database = 'harishram2k6$attendance',auth_plugin='mysql_native_password')
        cursor = mydb.cursor()
        command = "select regno,name,reason,date,sec from admin where date between %s and %s order by sec"
        cursor.execute(command,data)
        data = cursor.fetchall()
        mydb.close()
        try:
            regno, name, reason, date, student_sec = zip(*[(i[0], i[1], i[2], i[3].strftime("%Y-%m-%d"),i[4]) for i in data])
        except:
            flash("No data available within the given date range")
            return render_template('admin.html')
        df_data = {"REGNO":regno,"SECTION":student_sec,"NAME":name,"REASON":reason,"DATE":date}
        df = pd.DataFrame(df_data)
        path = os.path.join(os.path.dirname(__file__), 'data.csv')
        df.to_csv(path, index=False)
        with open(path,"r") as file:
            line = file.readlines()
            data = list(map(lambda x:x.strip().split(","),line))
            data.pop(0)
            name = data[0][1]
            files_name = []
            dep_file = open(os.path.join(os.path.dirname(__file__),name+".csv"),"w")
            files_name.append(os.path.join(os.path.dirname(__file__),name+".csv"))
            for i in data:
                if (i[1]==name):
                    line = (",".join(i)+"\n")
                    dep_file.write(line)
                else:
                    dep_file.close()
                    name = i[1]
                    dep_file = open(os.path.join(os.path.dirname(__file__),name+".csv"),"w")
                    files_name.append(os.path.join(os.path.dirname(__file__),name+".csv"))
                    line = (",".join(i)+"\n")
                    dep_file.write(line)
            dep_file.close()
            f_name = os.path.join(os.path.dirname(__file__),'department.zip')
            with zipfile.ZipFile(f_name, 'w') as zipf:
                for file in files_name:
                    zipf.write(file)
        os.remove(path)
        return send_file(f_name, as_attachment=True)
    elif request.method=="POST" and ('monthly-report-download' in request.form):
        mydb = mysql.connector.connect(host="harishram2k6.mysql.pythonanywhere-services.com", user="harishram2k6", password="qazxsW#123", database='harishram2k6$attendance',auth_plugin='mysql_native_password')
        cursor = mydb.cursor()
        hol_path = os.path.join(os.path.dirname(__file__), 'holidays.txt')
        with open(hol_path,"r") as file:
            holidays = tuple(map(lambda x:x.strip(),file.readlines()))
        def get_dates_current_month():
            today = datetime.date.today()
            first_day_of_month = today.replace(day=1)
            current_date = first_day_of_month
            dates_list = []
            while current_date <= today:
                if current_date.weekday()==6 or (current_date in holidays):
                    current_date += timedelta(days=1)
                dates_list.append(current_date)
                current_date += timedelta(days=1)
            return list(map(str,dates_list))
        column_name = ','.join(["NAME","REGNO"] + get_dates_current_month()+["PERCENTAGE"])
        c_name = get_dates_current_month()
        line = ""
        cursor.execute("SELECT NAME,REGNO FROM tutor")
        name_regno = cursor.fetchall()
        total_working_hours = len(c_name)*8
        f_path = os.path.join(os.path.dirname(__file__), 'month_data.txt')
        with open(f_path,"w") as file:
            file.write(column_name+"\n")
            for i in name_regno:
                name = i[0]
                regno = i[1]
                line+=(i[0]+','+str(i[1]))
                date = datetime.date.today()
                cursor.execute("SELECT date from admin where regno=%s and date between %s and %s",(regno,str(date.replace(day=1)),str(date)))
                leave_date = cursor.fetchall()
                leave_date = [str(item[0]) for item in leave_date]
                for i in range(len(c_name)):
                    if (c_name[i] in leave_date):
                        line+=",A"
                    else:
                        line+=", "
                line+=(','+str(100-(float("{:.2f}".format(((len(leave_date)*8)/total_working_hours)*100)))))
                file.write(line+'\n')
                line=''
        mydb.close()
        os.rename(f_path,f_path.replace("txt","csv"))
        if os.path.exists(f_path.replace('txt','csv')):
            return send_file(f_path.replace('txt','csv'), as_attachment=True)
        else:
            return "Error: month_data.txt not found", 404
    else:
        return render_template("admin.html")


@app.route('/manage/<uid>', methods=["POST", "GET"])
def tutor(uid):
    if not("valid" in session):
        return redirect(url_for('login'))
    mydb = mysql.connector.connect(host="harishram2k6.mysql.pythonanywhere-services.com", user="harishram2k6", password="qazxsW#123", database='harishram2k6$attendance',
    auth_plugin='mysql_native_password')
    cursor = mydb.cursor()
    cursor.execute("SELECT DISTINCT SEC FROM tutor WHERE TUTOR_UID=%s",(uid,))
    tutor_sec = (cursor.fetchone())[0]
    cursor.execute("SELECT NAME,REGNO,DEPARTMENT,SEC FROM tutor WHERE SEC=%s", (tutor_sec,))
    data = cursor.fetchall()
    mydb.close()
    if request.method == "POST":
        mydb = mysql.connector.connect(host="harishram2k6.mysql.pythonanywhere-services.com", user="harishram2k6", password="qazxsW#123", database='harishram2k6$attendance',
        auth_plugin='mysql_native_password')
        cursor = mydb.cursor()
        selected_checkboxes = request.form.getlist('checkbox')
        # selected_checkboxes --> ['0','1']
        reason = [request.form[i] for i in selected_checkboxes]
        # reason --> ['reason 1','reason 2']
        current_date = datetime.datetime.now()
        current_date = current_date.strftime('%Y-%m-%d')
        for i, j in zip(selected_checkboxes, reason):
            val = (data[0][3], data[0][2], data[int(i)][1], j, current_date, data[int(i)][0])
            cursor.execute("INSERT INTO admin (sec,department,regno,reason,date,name) VALUES(%s,%s,%s,%s,%s,%s)", val)
            mydb.commit()
        mydb.close()
        flash("Submitted Successfully!")
    return render_template("tutor.html", data=data, length=len(data))

if __name__ == "__main__":
    app.run(debug=False)
