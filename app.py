from flask import Flask, render_template, request, url_for,redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

def initialise_table(): 
    conn = sqlite3.connect('splitwise.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS GroupDetails(Id INT,GroupName TEXT,PRIMARY KEY(Id));')
    conn.commit()
    conn.close()

initialise_table()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # get group name from form data
        group_name = request.form['groupname']
        conn = sqlite3.connect('splitwise.db')
        c = conn.cursor()
        c.execute('INSERT INTO GroupDetails(GroupName) VALUES (?)', (group_name,))
        query = 'CREATE TABLE "{table_name}" (daate varchar(50), description1 TEXT, cost REAL)'.format(table_name=group_name)
        c.execute(query)
        conn.commit()
        conn.close()
        return redirect(url_for('addmember'))
    else:
        # render input form
        conn = sqlite3.connect('splitwise.db', check_same_thread=False)
        c = conn.cursor()
        c.execute('SELECT GroupName FROM GroupDetails')
        name = c.fetchall()
        conn.close()
        return render_template('base.html', name=name)
@app.route('/groupsumbit')
def groupsumbit():
    member_name = request.args.get('name')
    return render_template('group.html', member_name=member_name)


@app.route('/addexpense')
def addexpense():
    table = request.args.get('member_name')
    print(table)
    conn = sqlite3.connect('splitwise.db')
    c = conn.cursor()
    c.execute('SELECT * FROM "{table_name}"'.format(table_name=table))
    members = [description[0] for description in c.description]
    conn.commit()
    conn.close()
    return render_template('expense.html', table=table,members=members[3:])

@app.route('/addmember', methods=['GET', 'POST'])
def addmember():
    if request.method == 'POST':
        member_name = request.form['memname']

        conn = sqlite3.connect('splitwise.db')
        c = conn.cursor()
        c.execute('SELECT GroupName from GroupDetails order by Id DESC limit 1')
        grp = c.fetchall()[0][0]
        print(grp)
        query = 'ALTER TABLE "{table_name}" ADD COLUMN "{column_name}" REAL'.format(
            table_name=grp,
            column_name=member_name
        )
        c.execute(query)
        c.execute('SELECT * FROM "{table_name}"'.format(table_name=grp))
        members = [description[0] for description in c.description]
        print(members)
        conn.commit()
        conn.close()

        return render_template('member.html',members=members[3:])
    else:
        return render_template('member.html',members=[])

@app.route('/insertexpense', methods=['POST'])
def insertexpense():
    data=request.json
    table=data['1']
    desc=data['2']
    cost=float(data['3'])
    arr=data['4']
    brr=data['5']
    now=datetime.now()
    datestring=now.strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect('splitwise.db')
    c = conn.cursor()
    c.execute('INSERT INTO "{table_name}"(daate,description1,cost) values("{val1}","{val2}","{val3}")'.format(table_name=table,val1=datestring,val2=desc,val3=cost))
    i=0
    for val in brr:
        value=float(val)
        c.execute('UPDATE "{table_name}" SET "{column}"="{value}" WHERE daate="{datestring}"'.format(table_name=table,column=arr[i],value=value,datestring=datestring))
        i=i+1
    conn.commit()
    conn.close()
    return "inserted"
@app.route('/balance', methods=['GET'])
def balance():
    table = request.args.get('table_name')
    arr=[]
    brr=[]
    conn = sqlite3.connect('splitwise.db')
    c = conn.cursor()
    c.execute('SELECT * FROM "{table_name}"'.format(table_name=table))
    members = [description[0] for description in c.description]
    i=0
    for member in members:
        if(i>2):
            arr.append(member)
            c.execute('SELECT SUM("{col}") FROM "{table_name}"'.format(table_name=table,col=member))
            brr.append(float(c.fetchall()[0][0]))
            print(member)

        i=i+1
    print(arr,brr)    
    conn.commit()
    conn.close()
    return render_template('balance.html',table=table, arr=arr,brr=brr)

@app.route('/transaction', methods=['GET'])
def transaction():
    table = request.args.get('table_name')
    conn = sqlite3.connect('splitwise.db')
    c = conn.cursor()
    c.execute('SELECT * FROM "{table_name}"'.format(table_name=table))
    data=c.fetchall()
    c.execute('SELECT * FROM "{table_name}"'.format(table_name=table))
    members = [description[0] for description in c.description]
    conn.commit()
    conn.close()
    return render_template('transaction.html',members=members,data=data,table=table)
@app.route('/settleup', methods=['GET'])
def settleup():
    key = request.args.get('table_key')
    table = request.args.get('table')
    conn = sqlite3.connect('splitwise.db')
    c = conn.cursor()
    c.execute('SELECT * FROM "{table_name}" WHERE daate="{val}"'.format(table_name=table,val=key))
    data=c.fetchall()
    c.execute('SELECT * FROM "{table_name}"'.format(table_name=table))
    members = [description[0] for description in c.description]
    print(data)
    conn.commit()
    conn.close()
    return render_template('settleup.html',members=members,data=data,table=table,key=key)

@app.route('/finalsettel', methods=['POST'])
def finalsettel():
    data=request.json
    key=data['1']
    col=data['2']
    king=data['3']
    tab=data['4']
    conn = sqlite3.connect('splitwise.db')
    c = conn.cursor()
    c.execute('UPDATE "{table_name}" SET "{col2}"=ROUND("{col2}"+"{col1}",4) WHERE daate="{key}"'.format(table_name=tab,col2=king,col1=col,key=key))
    c.execute('UPDATE "{table_name}" SET "{col1}"=0 WHERE daate="{key}"'.format(table_name=tab,col1=col,key=key))
    conn.commit()
    conn.close()
    return "done"


if __name__ == '__main__':
    app.run(debug=True)
