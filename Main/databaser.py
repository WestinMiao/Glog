import pymysql
import datetime
import json
import pprint
import time
from .methods import ftime
from flask import request
from flask import make_response
from flask import redirect
from werkzeug.security import generate_password_hash, check_password_hash

class Database(object):
    def connect(self, address, username, password, block):
        self.db = pymysql.connect("localhost", "root", "George219@", "mydb")
        self.cursor = self.db.cursor()


    #Content
    def get_block_amount(self):
        try:
            self.cursor.execute("select count(*) from block2;")
            a = self.cursor.fetchone()
            return a[0]
        except Exception as e:
            self.db.rollback()
            print(f"<------get_block_amount error------>\n{e}\n")


    def get_content	(self, amount, time_format = True):
        try:
            self.cursor.execute("select * from block2 order by id desc limit %s;", amount)
            results = self.cursor.fetchall()
            content = dict()
            if time_format == True:
                for i in range(amount):
                    content[i] = {
                        "id": results[i][0],
                        "title": results[i][1],
                        "content": results[i][2],
                        "post_time": ftime(datetime.datetime.now() - results[i][3]),
                        "edit_time": ftime(datetime.datetime.now() - results[i][4]),
                    }
            elif time_format == False:
                for i in range(amount):
                    content[i] = {
                        "id": results[i][0],
                        "title": results[i][1],
                        "content": results[i][2],
                        "post_time": results[i][3].strftime("%Y-%m-%d"),
                        "edit_time": results[i][4].strftime("%Y-%m-%d"),
                    }
            return content
        except Exception as e:
            print(f'''<------get_content error------>\n{e}\n''')


    #User
    def get_new_user_id(self):
        try:
            self.cursor.execute("select user_id from user order by user_id desc limit 1;")
            results = self.cursor.fetchall()
            if results == ():
                return 1
            return results[0][0] + 1
        except Exception as e:
            self.db.rollback()
            print(f"<------get_new_user_id Error------>\n{e}\n")


    def register(self, username, password):
        try:
            self.cursor.execute(
                '''select user_id from user where username = %s limit 1;''', username)
            result = self.cursor.fetchall()
            if result == ():
                password_hash = generate_password_hash(password)
                self.cursor.execute(
                    '''insert into user values(%s, %s, %s, %s, %s)''',
                    (self.get_new_user_id(), username, password_hash, datetime.datetime.now(), datetime.datetime.now()))
                self.db.commit()
                return "000"#register success
            else:
                return "001"#register failure, username exist
        except Exception as e:
            self.db.rollback()
            print(f"<------register error------>\n{e}\n")
            return "002"  #register failure, server error
            
    
    def login(self, username, password):
        try:
            self.cursor.execute(
                '''select user_id , password from user where username = %s limit 1;''', username)
            a = self.cursor.fetchall()
            if a == ():
                return("001")#user does not exist
            else:
                if check_password_hash(a[0][1], password): 
                    self.cursor.execute('''UPDATE user SET last_login_time = %s where user_id = %s;''', (datetime.datetime.now(), a[0][0]))
                    self.db.commit()
                    return ("000")#login success
                else:
                    return ("002")#login failure, username/password is uncorrect
        except Exception as e:
            print(f"<------login error------>\n{e}\n")
            return "003"  #login failure, server error
            
    
    #Editor
    def get_new_block_id(self):
        try:
            self.cursor.execute(
                    f"select * from block2 order by id desc limit 1;"
                    )
            results = self.cursor.fetchall()
            return results[0][0] + 1
        except Exception as e:
            self.db.rollback()
            print(f'''<------get_new_id error------>\n{e}\n''')


    def select(self, block_id):
        try:
            self.cursor.execute("select * from block2 where id = %s;", block_id)
            results = self.cursor.fetchall()
            if results == ():
                return "001"#connot find the block
            content = {
                "id": results[0][0],
                "title": results[0][1],
                "content": results[0][2],
                "post_time": ftime(datetime.datetime.now() - results[0][3]),
                "edit_time": ftime(datetime.datetime.now() - results[0][4]),
            }
            return content
        except Exception as e:
            self.db.rollback()
            print(f"<------select error------>\n{e}\n")
            return "002"#failure, server error
                

    def create(self, title, content):
        try:
            number = self.get_new_block_id()
            self.cursor.execute(
                "insert into block2 values(%s, %s, %s, %s, %s);",
                (number, title, content, datetime.datetime.now(), datetime.datetime.now())
            )
            self.db.commit()
            return str(number)
        except Exception as e:
            self.db.rollback()
            print(f"<------create error------>\n{e}\n")
            return "000"


    def edit(self, block):
        try:
            self.cursor.execute('''UPDATE block2 SET title = %s,content = %s,edit_time= % s where id= % s; ''', 
                                (block['title'], block['content'], block['edit_time'], block['id']) )
            self.db.commit()
            return "000"#Success
        except Exception as e:
            self.db.rollback()
            print(f"<------edit error------>\n{e}\n")
            return "001"  #Edit failure, server error
    
    
    def delete(self, block_id):
        try:
            self.cursor.execute('''DELETE FROM block2 where id = %s;''',block_id)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print(f"<------delete error------>\n{e}\n")

    def disconnect(self):
        self.cursor.close()



db = Database()
db.connect("localhost", "root", "George219@", "mydb")
print(db.delete(3))
