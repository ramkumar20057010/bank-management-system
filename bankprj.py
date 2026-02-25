from flask import Flask,render_template,request,session,redirect
from datetime import datetime
from dateutil import relativedelta
from os import path

import pymysql
bank=Flask(__name__)
bank.config["aadhar_doc"]="static/uploads/aadhar_doc/"
bank.config["photo"]="static/uploads/photo/"
bank.config["pancard_doc"]="static/uploads/pancard_doc/"
bank.config["l_doc1"]="static/uploads/l_doc1/"
bank.config["l_doc2"]="static/uploads/l_doc2/"
bank.secret_key="EMO7028"

conn=pymysql.connect(host="localhost",user="root",password="12345678",db="bank_db")
cur=conn.cursor()
query=''' SELECT emi_id,due_date,fine FROM emi_schedule WHERE emi_status='Not Paid'; '''
cur.execute(query)
r=cur.fetchall()
curdate=datetime.today().date()
if r:
    for i in r:
        emi_id=i[0]
        duedate=i[1]
        fine=i[2]
        tenure=duedate+relativedelta.relativedelta(months=1)
        if curdate > tenure and fine!=500:
            cur=conn.cursor()
            query=''' UPDATE emi_schedule SET fine='500' WHERE emi_id=%s; '''
            cur.execute(query,(emi_id,))
            conn.commit()

@bank.route("/",methods=["GET","POST"])
def home():
    if session:
        if session["email"]=="admin123@gmail.com":
            return redirect("/adminHome")
    return render_template("home121.html")



@bank.route("/history",methods=["GET","POST"])
def history():
    r=""
    b=""
    if session:
        cur=conn.cursor()
        query=''' SELECT t.* FROM transactions t
         JOIN users u on t.tu_id=u.u_id WHERE u.u_id=%s; '''
        cur.execute(query,(session["uid"],))
        r=cur.fetchall()
        query=''' SELECT balance FROM users WHERE u_id=%s; '''
        cur.execute(query,(session["uid"],))
        b=cur.fetchone()
    return render_template("history32.html",rows=r,bal=b)


@bank.route("/loans",methods=["GET","POST"])
def loans():
    m=""
    em=""
    p=""
    ln=""
    if session:
        cur=conn.cursor()
        query=''' SELECT l.l_id,l.l_name FROM loans l
        JOIN users u on l.lu_id=u.u_id WHERE u.u_id=%s AND l.l_status="Active"; '''
        cur.execute(query,(session["uid"]))
        l=cur.fetchone()

        if l:
            m="Loan exist"
            ln=l[1]
            cur=conn.cursor()
            query=''' SELECT e.emi_id,e.emi_amount,e.fine,e.emi_status,e.due_date FROM emi_schedule e
            JOIN users u on e.uemi_id=u.u_id JOIN loans l ON e.lemi_id=l.l_id
            WHERE e.emi_status='Not Paid' AND u.u_id=%s ORDER BY e.due_date LIMIT 1; '''
            cur.execute(query,(session["uid"]))
            em=cur.fetchone()
            curdate=datetime.today().date()
            if em:
                if em[4]<=curdate:
                    p="show"
                else:
                    p="none"
            query=''' SELECT e.emi_status,e.lemi_id FROM emi_schedule e JOIN users u ON e.uemi_id=u.u_id 
            WHERE u.u_id=%s ORDER BY e.due_date DESC LIMIT 1; '''
            cur.execute(query,(session["uid"]))
            checkstatus=cur.fetchone()
            if checkstatus[0]=="Paid":
                cur=conn.cursor()
                query=''' UPDATE loans SET l_status='Completed' WHERE l_id=%s; '''
                cur.execute(query,(checkstatus[1],))
                conn.commit()

        else:
            m="Completed"


    if request.method=="POST":
        uid=request.form["uid"]
        loan_name=request.form["loan"]
        interest=request.form["interest"]
        timetenure=request.form["timetenure"]
        ldetails1=request.form["loanDetails"]
        ldetails2=request.form["loanYear"]
        ldoc1=request.files["loanimg"]
        ldoc2=request.files["loandoc"]
        lamount=request.form["loanAmount"]
        if ldoc1.filename!="" and ldoc2.filename!="":
            ldoc1_path=path.join(bank.config["l_doc1"],ldoc1.filename)
            ldoc2_path=path.join(bank.config["l_doc2"],ldoc2.filename)
            ldoc1.save(ldoc1_path)
            ldoc2.save(ldoc2_path)
        cur=conn.cursor()
        query=''' INSERT INTO loans(lu_id,l_name,interest,time_tenure,l_amount,
        l_details,l_doc_details,l_doc1,l_doc2) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s);'''
        cur.execute(query,(uid,loan_name,interest,timetenure,
                           lamount,ldetails1,ldetails2,ldoc1_path,ldoc2_path))
        conn.commit()
    if request.args.get("emi")=="emi":
        uid=request.args.get("uid")
        emi_id=request.args.get("emi_id")
        l1=request.args.get("l1")
        l2=request.args.get("l2")
        l3=request.args.get("l3")
        l4=request.args.get("l4")
        seckey=l1+l2+l3+l4
        if seckey==session["security_key"]:
            cur = conn.cursor()
            query = ''' SELECT balance FROM users WHERE u_id=%s; '''
            cur.execute(query, (uid,))
            b = cur.fetchone()
            balance=b[0]

            query=''' SELECT emi_amount,fine FROM emi_schedule WHERE emi_id=%s; '''
            cur.execute(query,(emi_id,))
            calc=cur.fetchone()
            total_amount=calc[0]+calc[1]
            if balance < total_amount:
                return "<script> alert('Inufficient Balance') </script>"
            if balance >= total_amount:
                bal=balance-total_amount
                curdate=datetime.today().date()
                query=''' UPDATE emi_schedule SET paid_date=%s,emi_status='Paid' WHERE emi_id=%s;  '''
                cur.execute(query,(curdate,emi_id))
                conn.commit()

                query=''' INSERT INTO transactions(tu_id,amount_role,amount,amount_status)
                VALUES(%s,'Loan',%s,'EMI Paid'); '''
                cur.execute(query,(uid,total_amount))
                conn.commit()

                query=''' UPDATE users SET balance=%s WHERE u_id=%s; '''
                cur.execute(query,(bal,uid))
                conn.commit()




        
    return render_template("loans65.html",msg=m,emi=em,pay=p,lname=ln)



@bank.route("/transactions",methods=["GET","POST"])
def transactions():
    ed=""
    ew=""
    if request.args.get("dep")=="dep":
        d1=request.args.get("d1")
        d2=request.args.get("d2")
        d3=request.args.get("d3")
        d4=request.args.get("d4")
        seckey=d1+d2+d3+d4
        if seckey==session["security_key"]:
            return redirect("/deposit")
        if seckey!=session["security_key"]:
            ed="Invalid Security key..."


    if request.args.get("with")=="with":
        w1=request.args.get("w1")
        w2=request.args.get("w2")
        w3=request.args.get("w3")
        w4=request.args.get("w4")
        seckey=w1+w2+w3+w4
        if seckey==session["security_key"]:
            return redirect("/withdraw")
        if seckey!=session["security_key"]:
            ew="Invalid Security key..."

    return render_template("transac32.html",err_dep=ed,err_wd=ew)


@bank.route("/deposit",methods=["GET","POST"])
def deposit():
    if request.args.get("deposit")=="deposited":
        uid=request.args.get("uid")
        dpamount=request.args.get("dpamount")
        cur=conn.cursor()
        query=''' INSERT INTO transactions(tu_id,amount_role,amount) VALUES(%s,'Deposit',%s); '''
        cur.execute(query,(uid,dpamount))
        conn.commit()
        return redirect("/transactions")

    return render_template("deposit34.html")




@bank.route("/withdraw",methods=["GET","POST"])
def withdraw():
    r=""
    if session:
        cur = conn.cursor()
        query = ''' SELECT balance FROM users; '''
        cur.execute(query)
        r=cur.fetchone()
    if request.args.get("withdraw")=="withdrawal":
        uid=request.args.get("uid")
        wamount=request.args.get("withamount")
        cur=conn.cursor()
        query=''' INSERT INTO transactions(tu_id,amount_role,amount,amount_status)
         VALUES(%s,'Withdraw',%s,'Withdrawn'); '''
        cur.execute(query,(uid,wamount))
        conn.commit()
        query=''' SELECT balance FROM users WHERE u_id=%s; '''
        cur.execute(query,(uid,))
        bal=cur.fetchone()
        balance=float(bal[0])-float(wamount)
        query=''' UPDATE users SET balance=%s WHERE u_id=%s; '''
        cur.execute(query,(balance,uid))
        conn.commit()
        return redirect("/transactions")

    return render_template("withdraw43.html",row=r)



@bank.route("/profile",methods=["GET","POST"])
def profile():
    r=""
    if session:
        cur=conn.cursor()
        query=''' SELECT * FROM users WHERE u_id=%s; '''
        cur.execute(query,(session["uid"],))
        r=cur.fetchone()
    return render_template("profile12.html",row=r)



@bank.route("/login",methods=["GET","POST"])
def login():
    e=""
    if request.args.get("log")=="logged":
        email=request.args.get("email")
        pwd=request.args.get("pwd")
        cur=conn.cursor()
        query=''' SELECT u_id,u_name,email,security_key,balance FROM users 
         WHERE email=%s AND  pass=%s;'''
        cur.execute(query,(email,pwd))
        row=cur.fetchone()
        if row=="":
            e="Invalid Credentials..."
        if row:
            session["uid"]=row[0]
            session["u_name"]=row[1]
            session["email"]=row[2]
            session["security_key"]=row[3]
            session["balance"]=row[4]
            return redirect("/")


    return render_template("login23.html",err=e)



@bank.route("/register",methods=["GET","POST"])
def register():
    r=""
    l=""
    e=""
    if request.method=="POST":
        uname=request.form["uname"]
        email=request.form["mail"]
        aadharno=request.form["aadharno"]
        mobno=request.form["mobno"]
        dob=request.form["dob"]
        occupation=request.form["occupation"]
        address=request.form["address"]
        aadhar_doc=request.files["aadhardoc"]
        profile=request.files["profile"]
        pancard=request.files["pancard"]
        pwd=request.form["pwd"]
        cur = conn.cursor()
        query = """ SELECT email FROM users WHERE email=%s; """
        cur.execute(query,(email,))
        checkEmail=cur.fetchone()
        if checkEmail:
            e="Email already exists...."
        query=""" SELECT aadhar_no FROM users WHERE aadhar_no=%s;"""
        cur.execute(query,(aadharno,))
        checkAadharno=cur.fetchone()
        if checkAadharno:
            e="Aadhar number already exists...."
        if e=="":
            if aadhar_doc.filename!="" and profile.filename!="" and pancard.filename!="":
                aadhar_filepath=path.join(bank.config["aadhar_doc"],aadhar_doc.filename)
                profile_filepath=path.join(bank.config["photo"],profile.filename)
                pancard_filepath=path.join(bank.config["pancard_doc"],pancard.filename)
                aadhar_doc.save(aadhar_filepath)
                profile.save(profile_filepath)
                pancard.save(pancard_filepath)
                cur=conn.cursor()
                query=''' INSERT INTO users(u_name,email,aadhar_no,mobile_no,dob,occupation,u_address,aadhar_doc,profile_pic,pancard_doc,pass)
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s); '''
                cur.execute(query,
        (uname,email,aadharno,mobno,dob,occupation,address,aadhar_filepath,profile_filepath,pancard_filepath,pwd))
                conn.commit()
                r="security"
                l=cur.lastrowid

    if request.args.get("rs")=="regs":
        uid=request.args.get("lastid")
        r1=request.args.get("r1")
        r2=request.args.get("r2")
        r3=request.args.get("r3")
        r4=request.args.get("r4")
        security=r1+r2+r3+r4
        cur=conn.cursor()
        query=''' UPDATE users SET security_key=%s WHERE u_id=%s; '''
        cur.execute(query,(security,uid))
        conn.commit()
        return redirect("/login")

    return render_template("register13.html",regkey=r,last=l,err=e)



@bank.route("/logout",methods=["GET","POST"])
def logout():
    session.clear()
    return redirect("/")

@bank.route("/adminHome",methods=["GET","POST"])
def admin():
    u=""
    f=""
    t=""
    tr=""
    if session:
        cur=conn.cursor()
        query=''' SELECT COUNT(u_id) FROM users; '''
        cur.execute(query)
        u=cur.fetchone()
        query=''' SELECT SUM(amount) FROM transactions 
        WHERE amount_status='Deposited' AND t_date=(CURRENT_DATE()); '''
        cur.execute(query)
        f=cur.fetchone()
        query=""" SELECT SUM(amount) FROM transactions WHERE amount_status='Deposited'; """
        cur.execute(query)
        t=cur.fetchone()

        query=''' SELECT t.t_id,u.profile_pic,u.u_name,t.amount_role,t.amount,t.transactioned_at FROM transactions t
        JOIN users u ON t.tu_id=u.u_id WHERE t.amount_status='Deposited' OR 
        t.amount_status='Withdrawn' OR t.amount_status='Loan Paid' ORDER BY t.t_id DESC LIMIT 10; '''
        cur.execute(query)
        tr=cur.fetchall()

    return render_template("admin_home43.html",users=u[0],total=t[0],today=f[0],transactions=tr)


@bank.route("/users",methods=["GET","POST"])
def users():
    r=""
    if session:
        cur=conn.cursor()
        query=''' SELECT u_id,profile_pic,u_name,mobile_no,email,balance FROM users; '''
        cur.execute(query)
        r=cur.fetchall()

    return render_template("users21.html",rows=r)

@bank.route("/borrowers",methods=["GET","POST"])
def borrowers():
    r=""
    if session:
        cur=conn.cursor()
        query=''' SELECT u.u_id,u.profile_pic,u.u_name,u.mobile_no,u.email,l.l_name,l.l_id
         FROM loans l JOIN users u on l.lu_id=u.u_id  WHERE l.l_status='Active'; '''
        cur.execute(query)
        r=cur.fetchall()
    return render_template("borrowers32.html",rows=r)


@bank.route("/depositrequest",methods=["GET","POST"])
def depositrequest():
    r=""
    if session:
        cur=conn.cursor()
        query=''' SELECT t.t_id,u.u_name,u.email,u.mobile_no,t.amount
            FROM transactions t JOIN users u ON t.tu_id=u.u_id 
            WHERE t.amount_status is NULL; '''
        cur.execute(query)
        r=cur.fetchall()
    if request.args.get("depositrequest")=="deposit":
        tid=request.args.get("tid")
        cur = conn.cursor()
        query=''' SELECT t.amount,u.balance,u.u_id FROM transactions t 
            JOIN users u on t.tu_id=u.u_id WHERE t.t_id=%s; '''
        cur.execute(query,(tid,))
        tp=cur.fetchone()
        amount=tp[0]
        balance=tp[1]
        uid=tp[2]
        query=''' UPDATE transactions SET amount_status='Deposited' WHERE t_id=%s; '''
        cur.execute(query,(tid,))
        conn.commit()
        balance=float(balance)+float(amount)
        query=''' UPDATE users SET balance=%s WHERE u_id=%s; '''
        cur.execute(query,(balance,uid))
        conn.commit()
    return render_template("depositrequest45.html",rows=r)




@bank.route("/loanrequest",methods=["GET","POST"])
def loanrequest():
    r=""
    if session:
        cur=conn.cursor()
        query=''' SELECT l.l_id,u.profile_pic,u.u_name,u.mobile_no,
        u.email,u.u_id,l.l_name,l.l_amount FROM 
        loans l JOIN users u on lu_id=u.u_id WHERE l.l_status='Not Active';
         '''
        cur.execute(query)
        r=cur.fetchall()

    return render_template("loanrequest76.html",rows=r)



@bank.route("/viewusers",methods=["GET","POST"])
def viewusers():
    r=""
    if session:
        if request.args.get("use")=="users":
            uid=request.args.get("uid")
            cur=conn.cursor()
            query=''' SELECT * FROM users WHERE u_id=%s; '''
            cur.execute(query,(uid,))
            r=cur.fetchone()


    return render_template("viewusers34.html",row=r)



@bank.route("/viewborrowers",methods=["GET","POST"])
def viewborrowers():
    r=""
    if request.args.get("borrow")=="borrowers":
        lid=request.args.get("lid")
        cur=conn.cursor()
        query=''' SELECT u.u_name,u.dob,u.email,u.mobile_no,u.u_address,u.aadhar_no,
         u.u_id,u.aadhar_doc,u.pancard_doc,l.l_name,l.l_amount,l.l_doc1,l.l_doc2,u.profile_pic FROM loans l
         JOIN users u on l.lu_id=u.u_id WHERE l.l_id=%s;'''
        cur.execute(query,(lid,))
        r=cur.fetchone()


    return render_template("viewborrowers35.html",row=r)

@bank.route("/viewloans",methods=["GET","POST"])
def viewloans():
    r=""
    if request.args.get("loanrequest")=="loanrequested":
        lid=request.args.get("lid")
        cur=conn.cursor()
        query=''' SELECT u.u_name,u.dob,u.email,u.mobile_no,u.u_address,
        u.aadhar_no,u.u_id,l.l_name,l.l_amount,u.aadhar_doc,u.pancard_doc,l.l_doc2,
        l.l_id,u.profile_pic  FROM loans l JOIN users u on l.lu_id=u.u_id WHERE l.l_id=%s; '''
        cur.execute(query,(lid,))
        r=cur.fetchone()
    if request.args.get("laccept")=="laccepted":
        lid=request.args.get("lid")
        l_amount=request.args.get("lamount")
        cur=conn.cursor()
        query=''' UPDATE loans SET l_amount=%s ,l_status='Active' WHERE l_id=%s; '''
        cur.execute(query,(l_amount,lid))
        conn.commit()

        query=''' SELECT l.l_id,u.u_id,l.l_amount,l.interest,l.time_tenure,u.balance FROM loans l
         JOIN users u on l.lu_id=u.u_id WHERE l_id=%s; '''
        cur.execute(query,(lid,))
        l=cur.fetchone()
        lid=l[0]
        uid=l[1]
        p=l[2]
        i=l[3]
        n=l[4]
        r=i/(12*100)
        emi=round(p*r*(1+r)**n/(1+r)**n-1)
        curdate=datetime.today().date()
        for i in range(n):
            cur=conn.cursor()
            duedate=curdate+relativedelta.relativedelta(months=i)
            query=''' INSERT INTO emi_schedule(lemi_id,uemi_id,emi_amount,due_date)
             VALUES(%s,%s,%s,%s);'''
            cur.execute(query,(lid,uid,emi,duedate))
            conn.commit()
        balance=l[5]+p
        cur=conn.cursor()
        query=''' UPDATE users SET balance=%s WHERE u_id=%s; '''
        cur.execute(query,(balance,uid))
        conn.commit()

        query = ''' INSERT INTO transactions(tu_id,amount_role,amount,amount_status)
         VALUES(%s,'Loan',%s,'Loan Received'); '''
        cur.execute(query,(uid,p))
        conn.commit()

        return redirect("/loanrequest")


    if request.args.get("reject")=="rejected":
        lid=request.args.get("lid")
        cur=conn.cursor()
        query=''' DELETE FROM loans WHERE l_id=%s; '''
        cur.execute(query,(lid,))
        conn.commit()
        return redirect("/loanrequest")
    return render_template("viewloan464.html",row=r)

@bank.route("/viewtransactions")
def viewtransactions():
    tr=""
    if session:
        cur=conn.cursor()
        query = ''' SELECT t.t_id,u.profile_pic,u.u_name,t.amount_role,t.amount,t.transactioned_at FROM transactions t
                JOIN users u ON t.tu_id=u.u_id WHERE t.amount_status='Deposited' OR 
                t.amount_status='Withdrawn' OR t.amount_status='Loan Received' OR t.amount_status='EMI Paid' ORDER BY t.t_id DESC; '''
        cur.execute(query)
        tr = cur.fetchall()
    return render_template("viewtransactions21.html",transactions=tr)





@bank.route("/personalloan",methods=["GET","POST"])
def personalloan():
    return render_template("personal_loan32.html")

@bank.route("/homeloan",methods=["GET","POST"])
def homeloan():
    return render_template("home_loan21.html")

@bank.route("/carloan",methods=["GET","POST"])
def carloan():
    return render_template("car_loan12.html")

@bank.route("/educationloan",methods=["GET","POST"])
def educationloan():
    return render_template("education_loan34.html")

@bank.route("/goldloan",methods=["GET","POST"])
def goldloan():
    return render_template("gold_loan23.html")

@bank.route("/landloan",methods=["GET","POST"])
def landloan():
    return render_template("land_loan76.html")



if __name__=="__main__":
    bank.run(debug=True)