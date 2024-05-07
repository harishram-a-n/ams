#om
from flask import Flask, render_template, request, redirect, url_for,send_file,session,flash
from werkzeug.security import generate_password_hash,check_password_hash
import mysql.connector, datetime,os,zipfile,smtplib,random
from datetime import timedelta
import pandas as pd
# openpyxl imcluded


app = Flask(__name__)
app.secret_key = "nec_science_and_humanities_year-1"

def sendmail(to_address,otp):
    my_email = "harishram2706@gmail.com"
    password = "abrq pvfa jzvc bggb "
    with smtplib.SMTP("smtp.gmail.com",port=587) as connection:
        connection.starttls()
        connection.login(user=my_email, password=password)
        connection.sendmail(
        from_addr=my_email,
        to_addrs=to_address,
        msg=f"Subject: AMS\n\nYour OTP is: {otp}")

@app.route('/', methods=["POST", "GET"])
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        data = (request.form["username"], request.form["password"])
        mydb = mysql.connector.connect(host="necscienceandhumanities.mysql.pythonanywhere-services.com", user="necscienceandhum", password="qazxsW#123", database='necscienceandhum$default',auth_plugin='mysql_native_password')
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
                session[data[0]] = True
                return redirect(url_for('tutor', uid=data[0]))
        else:
            flash("User not found")
            return render_template('index.html')
    return render_template("index.html")

@app.route('/manage/students',methods=['POST','GET'])
def manage_student():
    if not("admin_valid" in session):
        return redirect(url_for('login'))
    mydb = mysql.connector.connect(host="necscienceandhumanities.mysql.pythonanywhere-services.com", user="necscienceandhum", password="qazxsW#123", database='necscienceandhum$default',auth_plugin='mysql_native_password')
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
                    file.save(os.path.join(os.path.dirname(__file__), file.filename))
                    df = pd.read_excel(os.path.join(os.path.dirname(__file__), file.filename))
                    heading = {'regno':None,'name':None,'tutor':None}
                    for i in tuple(df):
                        topic = i.strip().replace('.','').lower()
                        if topic in heading.keys():
                            heading[topic]=i
                        elif ('name' in topic) and ('student' in topic):
                            heading['name']=i
                    data = tuple(zip(df[heading['name']],df[heading['regno']],df[heading['tutor']]))
                    mydb = mysql.connector.connect(host="necscienceandhumanities.mysql.pythonanywhere-services.com", user="necscienceandhum", password="qazxsW#123", database='necscienceandhum$default',auth_plugin='mysql_native_password')
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
                    os.remove(os.path.join(os.path.dirname(__file__), file.filename))
                    flash("Some error occured! check file format")
                    return render_template('man_stu.html',tutors=tutor_uids)
                finally:
                    mydb.close()
                    os.remove(os.path.join(os.path.dirname(__file__), file.filename))
                    flash("Completed")
                    return render_template('man_stu.html',tutors=tutor_uids)
            elif file.filename.lower()=='holidays.txt':
                file.save(os.path.join(os.path.dirname(__file__), 'sample.txt'))
                try:
                    def is_valid_date(date_str, format='%Y-%m-%d'):
                        try:
                            datetime.datetime.strptime(date_str, format)
                            return True
                        except ValueError:
                            return False
                    with open(os.path.join(os.path.dirname(__file__), 'sample.txt'),"r") as f1:
                        dates = f1.readlines()
                        for i in dates:
                            if (not is_valid_date(i)):
                                os.remove(os.path.join(os.path.dirname(__file__), 'sample.txt'))
                                flash("check date or date format!")
                                return render_template('man_stu.html',tutors=tutor_uids)
                        os.rename(os.path.join(os.path.dirname(__file__), 'sample.txt'),os.path.join(os.path.dirname(__file__), 'holidays.txt'))
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
                mydb = mysql.connector.connect(host="necscienceandhumanities.mysql.pythonanywhere-services.com", user="necscienceandhum", password="qazxsW#123", database='necscienceandhum$default',auth_plugin='mysql_native_password')
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
                    mydb = mysql.connector.connect(host="necscienceandhumanities.mysql.pythonanywhere-services.com", user="necscienceandhum", password="qazxsW#123", database='necscienceandhum$default',auth_plugin='mysql_native_password')
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
    f_path = os.path.join(os.path.dirname(__file__), 'status.txt')
    with open(f_path,"r") as file:
        status = file.readline().strip()
    if request.method=='POST' and ('button_clicked' in request.form) and not(('flexSwitchCheckDefault' in request.form)):
        with open(f_path,"w") as file:
            pass
        return render_template("edit_attendance.html",state="")
    elif request.method=='POST' and ('flexSwitchCheckDefault' in request.form):
        with open(f_path,"w") as file:
            file.write("checked")
        return render_template("edit_attendance.html",state="checked")
    elif request.method=="POST" and 'regNo' in request.form:
        try:
            mydb = mysql.connector.connect(host="necscienceandhumanities.mysql.pythonanywhere-services.com", user="necscienceandhum", password="qazxsW#123", database='necscienceandhum$default',auth_plugin='mysql_native_password')
            data = (int(request.form.get('regNo')),request.form.get('date'))
            cursor = mydb.cursor()
            cursor.execute("DELETE FROM admin WHERE regno=%s AND date=%s",data)
            mydb.commit()
        except:
            pass
        finally:
            mydb.close()
            return render_template("edit_attendance.html",state=status)
    return render_template("edit_attendance.html",state=status)

@app.route('/manage/database', methods=['POST','GET'])
def man_database():
    if 'admin_valid' not in session:
        return redirect(url_for('login'))
    if request.method=="POST" and any(list(request.form)):
        try:
            mydb = mysql.connector.connect(host="necscienceandhumanities.mysql.pythonanywhere-services.com", user="necscienceandhum", password="qazxsW#123", database='necscienceandhum$default',auth_plugin='mysql_native_password')
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

@app.route("/reset_password/confirm",methods=["POST","GET"])
def confirm_reset():
    if not("otp" in session):
        return redirect(url_for("login"))
    if (request.method=='POST' and "OTP" in request.form):
        if (int(request.form.get("OTP").strip())!=session.get("otp")):
            flash("OTP Invalid!")
        elif (len(request.form.get("password"))<8):
            flash("Password must be a minimum of eight characters!")
        else:
            mydb = mysql.connector.connect(host="necscienceandhumanities.mysql.pythonanywhere-services.com", user="necscienceandhum", password="qazxsW#123", database='necscienceandhum$default',auth_plugin='mysql_native_password')
            cursor = mydb.cursor()
            cursor.execute("UPDATE login_data SET password=%s WHERE username=%s",(generate_password_hash(request.form.get("password"),method='pbkdf2:sha256',salt_length=8),session.get("u_name").replace("resetpasswd","")))
            mydb.commit()
            mydb.close()
            session.clear()
            flash("Password updated successfully!")
            return redirect(url_for("login"))
    return render_template("confirm.html")

@app.route("/reset_password",methods=['POST','GET'])
def reset_password():
    if request.method=='POST' and "u_name" in request.form:
        try:
            mydb = mysql.connector.connect(host="necscienceandhumanities.mysql.pythonanywhere-services.com", user="necscienceandhum", password="qazxsW#123", database='necscienceandhum$default',auth_plugin='mysql_native_password')
            cursor = mydb.cursor()
            cursor.execute("SELECT mail FROM login_data WHERE username=%s",(request.form.get("u_name"),))
            data = cursor.fetchone()
            if not(data) or request.form.get("u_name")=='admin':
                flash("User not found!")
            else:
                session["u_name"]=request.form.get("u_name")+"resetpasswd"
                session["otp"]=random.randint(1000,9999)
                sendmail(data[0],session.get("otp"))
                mail = data[0].split('@')
                mail[0]=(len(mail[0])//2)*"*"+mail[0][len(mail[0])//2:]
                mail = '@'.join(mail)
                flash(f"OTP sent to {mail}!")
                mydb.close()
                return redirect(url_for("confirm_reset"))
        except:
            flash("Error occured!")
        finally:
            mydb.close()
    return render_template("send_otp.html")


@app.route('/manage/tutors', methods=['POST','GET'])
def submit_form():
    if not("admin_valid" in session):
        return redirect(url_for('login'))
    def db_data():
        mydb = mysql.connector.connect(host="necscienceandhumanities.mysql.pythonanywhere-services.com", user="necscienceandhum", password="qazxsW#123", database='necscienceandhum$default',auth_plugin='mysql_native_password')
        cursor = mydb.cursor()
        cursor.execute("SELECT username,subject FROM login_data where username!='admin' ORDER BY subject")
        data = cursor.fetchall()
        mydb.close()
        return data
    data = db_data()
    if request.method=="POST" and any(list(request.form)):
        try:
            mydb = mysql.connector.connect(host="necscienceandhumanities.mysql.pythonanywhere-services.com", user="necscienceandhum", password="qazxsW#123", database='necscienceandhum$default',auth_plugin='mysql_native_password')
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
    if request.method=="POST":
        print(tuple(request.form))
    if request.method=='POST' and "username" in request.form:
        mydb = mysql.connector.connect(host="necscienceandhumanities.mysql.pythonanywhere-services.com", user="necscienceandhum", password="qazxsW#123", database='necscienceandhum$default',auth_plugin='mysql_native_password')
        cursor = mydb.cursor()
        cursor.execute("SELECT username FROM login_data")
        u_name = cursor.fetchall()
        u_name = tuple(map(lambda x:x[0],u_name))
        mydb.close()
        data = (request.form["username"].strip().lower(), request.form["password"],request.form["subject"],request.form["email"].strip().lower())
        if data[0] in u_name:
            flash("user exist!")
            return render_template("add_tutor.html")
        elif len(data[1])<8:
            flash("Password should be a minimum of eight characters")
        elif len(data[3].split("@"))<2 or len(data[3].split("@"))>2 or ('@' not in data[3]):
            flash("Gmail invalid!")
            return render_template("add_tutor.html")
        elif data[0].strip()=='' or data[1].strip()=='' or data[2].strip()=='':
            flash("Form incomplete!")
            return render_template("add_tutor.html")
        else:
            session["data"]=data
            session["onetimepasswd"]=random.randint(1000,9999)
            sendmail(data[3],session.get("onetimepasswd"))
            flash("A OTP has been sent to your mail verify it!")
            return render_template("verify_otp.html")
    elif request.method=="POST" and "OTP" in request.form:
        if not(request.form.get("OTP").isdigit()):
            flash("OTP Invalid!")
        elif int(request.form.get("OTP"))!=session.get("onetimepasswd"):
            flash("OTP Invalid!")
        else:
            mydb = mysql.connector.connect(host="necscienceandhumanities.mysql.pythonanywhere-services.com", user="necscienceandhum", password="qazxsW#123", database='necscienceandhum$default',auth_plugin='mysql_native_password')
            cursor = mydb.cursor()
            data = list(session.get("data"))
            data[1]=generate_password_hash(data[1],method='pbkdf2:sha256',salt_length=8)
            cursor.execute("INSERT INTO login_data (username,password,subject,mail) VALUES(%s,%s,%s,%s)",tuple(data))
            mydb.commit()
            mydb.close()
            session.clear()
            flash(f"Successfully added {session.get('data')[0]}!")
            return render_template("add_tutor.html")
    return render_template("add_tutor.html")

@app.route('/admin', methods=["POST", "GET"])
def admin():
    if not("admin_valid" in session):
        return redirect(url_for('login'))
    for i in os.listdir(os.path.dirname(__file__)):
        if '.csv' in i or '.zip' in i or ".xlsx" in i:
            os.remove(os.path.join(os.path.dirname(__file__), i))
    if request.method=="POST" and ('submit' in request.form):
        data = (request.form["startDate"], request.form["endDate"])
        if not(any(data[0])) or not(any(data[0])):
            return render_template('admin.html',js_code="Date not selected")
        mydb = mysql.connector.connect(host="necscienceandhumanities.mysql.pythonanywhere-services.com", user="necscienceandhum", password="qazxsW#123", database='necscienceandhum$default',auth_plugin='mysql_native_password')
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
        mydb = mysql.connector.connect(host="necscienceandhumanities.mysql.pythonanywhere-services.com", user="necscienceandhum", password="qazxsW#123", database='necscienceandhum$default',auth_plugin='mysql_native_password')
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
        mydb = mysql.connector.connect(host="necscienceandhumanities.mysql.pythonanywhere-services.com", user="necscienceandhum", password="qazxsW#123", database='necscienceandhum$default',auth_plugin='mysql_native_password')
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
    if not(uid in session):
        return redirect(url_for('login'))
    with open(os.path.join(os.path.dirname(__file__), 'status.txt'),'r') as status_file:
        status = status_file.readline()
    if status:
        return render_template("closed.html",data="Attendance Closed By Admin")
    with open(os.path.join(os.path.dirname(__file__), 'holidays.txt'),'r') as file:
        h_days = tuple(map(lambda x:x.strip(),file.readlines()))
    if (str(datetime.date.today()) in h_days) or (datetime.date.today().weekday()==6):
        return render_template("closed.html",data="Site Temporarily Suspended For Holiday")
    mydb = mysql.connector.connect(host="necscienceandhumanities.mysql.pythonanywhere-services.com", user="necscienceandhum", password="qazxsW#123", database='necscienceandhum$default',auth_plugin='mysql_native_password')
    cursor = mydb.cursor()
    cursor.execute("SELECT DISTINCT SEC FROM tutor WHERE TUTOR_UID=%s",(uid,))
    tutor_sec = (cursor.fetchone())[0]
    cursor.execute("SELECT NAME,REGNO,DEPARTMENT,SEC FROM tutor WHERE SEC=%s", (tutor_sec,))
    data = cursor.fetchall()
    mydb.close()
    current_date = datetime.datetime.now()
    current_date = current_date.strftime('%Y-%m-%d')
    if request.method == "POST":
        mydb = mysql.connector.connect(host="necscienceandhumanities.mysql.pythonanywhere-services.com", user="necscienceandhum", password="qazxsW#123", database='necscienceandhum$default',auth_plugin='mysql_native_password')
        cursor = mydb.cursor()
        selected_checkboxes = request.form.getlist('checkbox')
        # selected_checkboxes --> ['0','1']
        reason = [request.form[i] for i in selected_checkboxes]
        # reason --> ['reason 1','reason 2']
        for i, j in zip(selected_checkboxes, reason):
            val = (data[0][3], data[0][2], data[int(i)][1], j, current_date, data[int(i)][0])
            cursor.execute("INSERT INTO admin (sec,department,regno,reason,date,name) VALUES(%s,%s,%s,%s,%s,%s)", val)
            mydb.commit()
        mydb.close()
        flash("Submitted Successfully!")
    return render_template("tutor.html", data=data, length=len(data),t_day=current_date)

if __name__ == "__main__":
    app.run(debug=True)

