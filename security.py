import random
import string
import sqlite3
import hashlib


class Security:
    hash_object = hashlib.sha256()

    def get_dynamic_solt(self):
        res = ''
        for i in range(random.randint(5, 10)):
            res += random.choice(string.printable)
        id_delta = (ord(res[0]) * ord(res[1])) % ord(res[-1])
        return res, id_delta


    def generate_hash(self, password, account_id):
        if self.get_hash(password, account_id):
            print(account_id)
            print(self.get_hash(password, account_id))
            return False
        with open('static/solt.txt', 'r') as file:
            static_solt = file.read()
        temp = ''
        for i in range(len(password)):
            temp += static_solt[i]
            temp += password[i]
        solt_data = self.get_dynamic_solt()
        solt_con = sqlite3.connect('static/sqLite3/security_data.db')
        dynamic_id = account_id + solt_data[1]
        solt_con.cursor().execute('''INSERT INTO solt(account_id,solt) VALUES ( ?,? )''', (dynamic_id, solt_data[0]))
        solt_con.commit()
        solt_con.close()
        temp += solt_data[0]
        self.hash_object = hashlib.sha256()
        self.hash_object.update(temp.encode('utf-8'))
        return self.hash_object.hexdigest()


    def get_id_delta(self, solt):
        id_delta = (ord(solt[0]) * ord(solt[1])) % ord(solt[-1])
        return id_delta


    def find_dynamic_solt(self, account_id, data: dict):
        for solt, dnm_id in data.items():
            if dnm_id - self.get_id_delta(solt) == account_id:
                return solt
        return False


    def get_hash(self, password, account_id):
        solt_con = sqlite3.connect('static/sqLite3/security_data.db')
        temp = solt_con.cursor().execute('''SELECT * FROM solt''').fetchall()
        solt_con.close()
        data = {i[1]: i[0] for i in temp}
        solt_data = self.find_dynamic_solt(account_id, data)
        if not solt_data:
            return False
        with open('static/solt.txt', 'r') as file:
            static_solt = file.read()
        temp = ''
        for i in range(len(password)):
            temp += static_solt[i]
            temp += password[i]
        temp += solt_data
        print('will hashed:', temp)
        self.hash_object = hashlib.sha256()
        self.hash_object.update(temp.encode('utf-8'))
        return self.hash_object.hexdigest()


    def check_password_by_username(self, password, username):
        con = sqlite3.connect('static/sqLite3/data.db')
        cur = con.cursor()
        really_id = cur.execute('''SELECT id FROM accounts WHERE username=?''', (username,)).fetchone()
        if really_id is None:
            return False
        really_id = really_id[0]
        really_hash = cur.execute('''SELECT password_hash FROM accounts WHERE username=?''', (username,)).fetchone()[0]
        print(really_id)
        con.close()
        sistem_hash = self.get_hash(password, really_id)
        print(sistem_hash)
        print(really_hash)
        if not sistem_hash:
            return False
        return sistem_hash == really_hash


hash_object = hashlib.sha256()
hash_object.update('22'.encode('utf-8'))
print(hash_object.hexdigest())
hash_object = hashlib.sha256()
hash_object.update('22'.encode('utf-8'))
print(hash_object.hexdigest())
