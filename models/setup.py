import sqlite3
import random
import json
from utils import *


class SqliteDB:
    def __init__(self, db_path="database.db"):
        self.db_path = db_path
        self.connect()
        self.conn.row_factory = sqlite3.Row
        self.cursor.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not self.cursor.fetchone():
            self.cursor.execute(
                f"CREATE TABLE users (telegram_id,is_blocked, uuid, creation_date,ammunt_of_monny,is_admin)")
        self.cursor.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='inbounds'")
        if not self.cursor.fetchone():
            self.cursor.execute(
                f"CREATE TABLE inbounds (id_in_panel, uuid, all_json, server, port, max_limit, creation_date,telegram_id)")

        self.cursor.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='servers'")
        if not self.cursor.fetchone():
            self.cursor.execute(
                f"CREATE TABLE servers (ID INTEGER PRIMARY KEY,server,port_pan,username,password,user_count,in_use,host_add)")

    def get_uuid_from_telegram_id(self, telegram_id):
        """Returns a list of dictionaries containing the link and server for the given telegram_id, or None if not found"""
        query = f"SELECT uuid FROM inbounds WHERE telegram_id = ?"
        self.cursor.execute(query, (telegram_id,))
        row = self.cursor.fetchone()
        if row:
            return row[0]
        else:
            return None

    def link_gen(self, json_fild: dict):
        uuid = json.loads(json_fild["obj"]["settings"])[
            "clients"][0]["id"]
        port = json_fild["obj"]["port"]
        protocol = json_fild["obj"]["protocol"]
        network = json.loads(json_fild["obj"]["streamSettings"])[
            "network"]
        security = json.loads(json_fild["obj"]["streamSettings"])[
            "security"]
        serverName = json.loads(json_fild["obj"]["streamSettings"])[
            "tlsSettings"]["serverName"]
        path = json.loads(json_fild["obj"]["streamSettings"])[
            "wsSettings"]["path"]
        Host = json.loads(json_fild["obj"]["streamSettings"])[
            "wsSettings"]["header"]["Host"]

        one = f"{protocol}://{uuid}@{serverName}:{port}?type={network}&security={security}&path={path}&host={Host}&sni={Host}&alpn=http/1.1#{uuid}"
        print(one)
        return one

    def link_gen_cdn(self, json_fild: dict, serverName, alterID, cdn_add="104.17.32.105"):
        # print(json_fild)
        uuid = json_fild["id"]
        port = json_fild["port"]
        protocol = json_fild["protocol"]
        try:
            network = json.loads(json_fild["streamSettings"])["network"]
        except:
            network = ""
        try:
            security = json.loads(json_fild["streamSettings"])["security"]
        except:
            security = ""
        try:
            path = json.loads(json_fild["streamSettings"])[
                "wsSettings"]["path"]
        except:
            path = ""
        try:
            Host = json.loads(json_fild["streamSettings"])[
                "wsSettings"]["header"]["Host"]
        except:
            Host = serverName
        serverName = cdn_add
        print(uuid, port, protocol, network, security, Host, path, serverName)
        if protocol == "vless" or protocol == "trojan":
            one = f"{protocol}://{uuid}@{serverName}:{port}?type={network}&security={security}&path={path}&host={Host}&sni={Host}&aid={alterID}#Config CDN {Host}"
            return one
        elif protocol == "vmess":
            one = conf_ch_cdn(serverName, Host, uuid, network,
                              path, port, f"Config CDN {Host}", Host, security, aid=alterID)
            return one

    def link_gen_new(self, json_fild: dict, serverName):
        # print(json_fild)
        uuid = json_fild["id"]
        port = json_fild["port"]
        protocol = json_fild["protocol"]
        try:
            network = json.loads(json_fild["streamSettings"])["network"]
        except:
            network = ""
        try:
            security = json.loads(json_fild["streamSettings"])["security"]
        except:
            security = ""
        try:
            if serverName is None:
                serverName = json.loads(json_fild["streamSettings"])[
                    "tlsSettings"]["serverName"]
        except:
            pass
            # serverName = ""
        try:
            path = json.loads(json_fild["streamSettings"])[
                "wsSettings"]["path"]
        except:
            path = ""
        try:
            Host = json.loads(json_fild["streamSettings"])[
                "wsSettings"]["header"]["Host"]
        except:
            Host = ""

        print(uuid, port, protocol, network, security, Host, path, serverName)
        if protocol == "vless" or protocol == "trojan":
            one = f"{protocol}://{uuid}@{serverName}:{port}?type={network}&security={security}&path={path}&host={Host}&sni={Host}#Config {Host}"
            return one
        elif protocol == "vmess":
            if network == "grpc":
                typee = "gun"
            one = conf_ch(serverName,  uuid, network,
                          path, port, f"Config {Host}", security, type=typee)
            return one

    def generate_random_port(self, server):
        """Generates a random port that is not in the table for the given server"""
        port = random.randint(10000, 50000)
        query = f"SELECT ? WHERE NOT EXISTS (SELECT 1 FROM inbounds WHERE server = ? AND port = ?)"
        self.cursor.execute(query, (port, server, port))
        row = self.cursor.fetchone()
        if row:
            return row[0]
        return None

    def get_telegram_ammunt(self, telegram_id):
        """Returns a list of dictionaries containing the link and server for the given telegram_id, or None if not found"""
        query = f"SELECT ammunt_of_monny FROM users WHERE telegram_id = ?"
        self.cursor.execute(query, (telegram_id,))
        row = self.cursor.fetchone()
        if row:
            return row[0]
        else:
            return None

    def get_clients(self, server, totalGB):
        # Select the columns you want to retrieve
        self.cursor.execute(
            "SELECT uuid FROM users WHERE server=?", (server,))

        # Fetch all rows as a list of tuples
        rows = self.cursor.fetchall()

        # Create an empty list to store the JSON objects
        json_list = []

        # Iterate through the rows
        for row in rows:
            json_list.append(
                {'email': row[0], 'id': row[1], 'flow': 'xtls-rprx-direct', 'totalGB': totalGB})

        return json_list

    def get_is_admin(self, telegram_id):
        """Returns a list of dictionaries containing the link and server for the given telegram_id, or None if not found"""
        query = f"SELECT is_admin FROM users WHERE telegram_id = ?"
        self.cursor.execute(query, (telegram_id,))
        row = self.cursor.fetchone()
        if row:
            return row[0]
        else:
            return None

    def get_services(self, telegram_id):
        """Returns a list of dictionaries containing the link and server for the given telegram_id, or None if not found"""
        query = f"SELECT * FROM inbounds WHERE telegram_id = ?"
        self.cursor.execute(query, (telegram_id,))
        row = self.cursor.fetchall()
        if row:
            return row
        else:
            return None

    def admin_updator(self, telegram_id, admin_t_o_f: bool):
        # update the settings for the given id
        self.conn.execute(
            "UPDATE users SET is_admin = ? WHERE telegram_id = ?", (admin_t_o_f, telegram_id))
        # commit the changes and close the connection
        self.conn.commit()

    def update_user_data(self, telegram_id, ammunt_of_monny):
        # update the settings for the given id
        self.conn.execute(
            "UPDATE users SET ammunt_of_monny = ? WHERE telegram_id = ?", (ammunt_of_monny, telegram_id))
        # commit the changes and close the connection
        self.conn.commit()

    def get_serveer_exist(self, host):
        """Returns a list of dictionaries containing the link and server for the given telegram_id, or None if not found"""
        query = f"SELECT * FROM servers WHERE server = ?"
        self.cursor.execute(query, (host,))
        row = self.cursor.fetchone()
        if row:
            return row
        else:
            return None

    def get_serveers(self):
        """Returns a list of dictionaries containing the link and server for the given telegram_id, or None if not found"""
        query = f"SELECT * FROM servers"
        self.cursor.execute(query,)
        row = self.cursor.fetchall()
        if row:
            return row
        else:
            return None

    def get_server_from_id(self, Id):
        """Returns a list of dictionaries containing the link and server for the given telegram_id, or None if not found"""
        query = f"SELECT * FROM servers WHERE ID = ?"
        self.cursor.execute(query, (Id,))
        row = self.cursor.fetchone()
        if row:
            return row
        else:
            return None

    def get_server_from_in_use(self, in_use: bool):
        """Returns a list of dictionaries containing the link and server for the given telegram_id, or None if not found"""
        query = f"SELECT * FROM servers WHERE in_use = ?"
        self.cursor.execute(query, (in_use,))
        row = self.cursor.fetchall()
        if row:
            return row[-1]
        else:
            return None

    def server_user_count_updator(self, host):
        # update the settings for the given id
        val = self.get_serveer_exist(host)[5]
        self.conn.execute(
            "UPDATE servers SET user_count = ? WHERE server = ?", (val+1, host))
        # commit the changes and close the connection
        self.conn.commit()
        return val+1

    def update_servers_in_use(self, ID, T_o_F):
        # update the settings for the given id
        self.conn.execute(
            "UPDATE servers SET in_use = ? WHERE ID = ?", (T_o_F, ID))
        # commit the changes and close the connection
        self.conn.commit()

    def add_row(self, table_name, values):
        placeholders = ", ".join("?" * len(values))
        query = f"INSERT INTO {table_name} VALUES ({placeholders})"
        self.cursor.execute(query, values)
        self.conn.commit()

    def update_server(self,  ID, server, port, username, password, host_add, in_use=None):
        # update the settings for the given id
        self.conn.execute(
            "UPDATE servers SET server = ?,port_pan = ?,username = ?,password = ?,host_add=? WHERE id = ?", (server, port, username, password, host_add, ID))
        # commit the changes and close the connection
        self.conn.commit()

    def port_updator(self, server, port):
        # update the settings for the given id
        self.conn.execute(
            "UPDATE servers SET port_pan = ? WHERE server = ?", (port, server))
        # commit the changes and close the connection
        self.conn.commit()

    def get_count_of_raw(self, table):
        query = f"SELECT COUNT(*) FROM {table} "
        self.cursor.execute(query,)
        return self.cursor.fetchone()[0]

    def get_count_of_raw_of_admin(self, table):
        query = f"SELECT COUNT(*) FROM {table}  WHERE is_admin = 1"
        self.cursor.execute(query,)
        return self.cursor.fetchone()[0]

    def get_list_of_admin(self, table):
        query = f"SELECT * FROM {table}  WHERE is_admin = 1"
        self.cursor.execute(query,)
        return self.cursor.fetchall()

    def get_users(self):
        """Returns a list of dictionaries containing the link and server for the given telegram_id, or None if not found"""
        query = f"SELECT telegram_id FROM users "
        self.cursor.execute(query, )
        row = self.cursor.fetchall()
        if row:
            return row
        else:
            return None

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def close_db(self):
        self.conn.close()


if __name__ == "__main__":
    db = SqliteDB()
    # ddd = db.admin_updator(407599569, True)
    # ddd = db.admin_updator(407599569, True)
    ddd = db.get_list_of_admin("users")

    # ddd = db.get_clients("localhost", 70000)
    print(ddd)
