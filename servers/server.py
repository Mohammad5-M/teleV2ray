import requests
import logging
from datetime import datetime
from servers import gen_user_config_vless_ws, gen_data_for_req
import uuid
from models import *
from uti import time_in_defult_days_milliseconds


class ServerClass:
    CHECK_POINT = True

    def __init__(self, db: SqliteDB, serv_and_port, host_add, username="admin", password="admin") -> None:
        self.db = db

        if self.db.get_serveers() == None:
            self.db.add_row("servers", (None, "test", "port",
                                        "user", "pass", 0, True, "host_add"))
            self.server_id = 1
            self.CHECK_POINT = False

        ns = self.db.get_server_from_in_use(True)
        self.server_id = ns[0]
        self.serv = ns[1]
        self.serv_and_port = f"{ns[1]}:{ns[2]}"
        self.username = ns[3]
        self.password = ns[4]
        self.user_count = ns[5]
        self.host_add = ns[7]

        if self.user_count >= 70:
            try:
                self.db.update_servers_in_use(self.server_id, False)
                self.db.update_servers_in_use(self.server_id+1, True)
                self.update_cashed_server()
            except:
                logging.warning("Next server not find")
        logging.info("{} {}".format(self.serv_and_port, self.host_add))

    def update_cashed_server(self):
        ns = self.db.get_server_from_in_use(True)
        self.server_id = ns[0]
        self.serv = ns[1]
        self.serv_and_port = f"{ns[1]}:{ns[2]}"
        self.username = ns[3]
        self.password = ns[4]
        self.user_count = ns[5]
        self.host_add = ns[7]

        if self.user_count >= 70:
            try:
                self.db.update_servers_in_use(self.server_id, False)
                self.db.update_servers_in_use(self.server_id+1, True)
                self.update_cashed_server()
            except:
                logging.warning("Next server not find")
        logging.info("{} {}".format(self.serv_and_port, self.host_add))

    def gen_url(self, telegram_id, traffic_limit):
        if self.user_count >= 70:
            print("1")
            if self.next_server() == None:
                print("2")
                return None, None
        random_client_id = str(uuid.uuid4())
        email = f"{random_client_id}@channel"
        port = self.db.generate_random_port(self.serv)
        print(port)
        creation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_config = gen_user_config_vless_ws(name=telegram_id, email=email, uuid=random_client_id,
                                               server_address=self.serv, port=port, traffic_limit=traffic_limit)
        print(user_config)
        r = self.login()
        resp = requests.post(url=f"http://{self.serv_and_port}/xui/inbound/add",
                             data=user_config, cookies=r.cookies)
        json_res = resp.json()
        print(type(json_res))  # TODO //
        self.user_count = self.db.server_user_count_updator(self.serv)
        print("3")
        self.db.add_row('inbounds', (json_res['obj']['id'], random_client_id, str(
            json_res), self.serv, port, traffic_limit, creation_date, telegram_id))
        print("4")
        return resp.ok, json_res

    def next_server(self):
        try:
            self.db.update_servers_in_use(self.server_id, False)
            self.db.update_servers_in_use(self.server_id+1, True)
            self.update_cashed_server()
        except:
            logging.warning("Next server not find")
            return
        logging.info("{} {}".format(self.serv_and_port, self.host_add))

    def gen_url_same_port(self, telegram_id, traffic_limit, port):
        if self.user_count >= 70:
            d = self.next_server()
            if d == None:
                return None, None
        random_client_id = str(uuid.uuid4())
        # f2828282-1cb1-46ab-b5b5-18ba510dd1ef@407599569.com
        email = f"{random_client_id}@{telegram_id}"
        # port = self.db.generate_random_port(self.serv)
        print(port)
        creation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        user_config = gen_data_for_req(
            port, random_client_id, None, email, None, traffic_limit, time_in_defult_days_milliseconds())
        print(user_config)

        headers = {"Content-Type": "application/json"}
        resp = requests.post(url=f"http://{self.serv_and_port}/addClients",
                             headers=headers, json=user_config, )
        print(resp)
        if resp:
            json_res = resp.json()
            self.user_count = self.db.server_user_count_updator(self.serv)
            print("3")
            self.db.add_row('inbounds', (json_res["id_in_pan"], random_client_id,
                                         resp.text, self.serv, port, traffic_limit, creation_date, telegram_id))
            print("4")
            return resp.ok, json_res
        return None, None

    def login(self):
        self.lasttime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        payload = {'username': self.username, 'password': self.password}
        url = f"http://{self.serv_and_port}/login"  # TODO: Make it with https
        resp = requests.post(url, data=payload)
        return resp

    def get_user_data_cdn(self, serv, panport, email):
        url = f"http://{serv}:{panport}/user/{email}"
        r = requests.get(url)
        return r.json()

    def get_admin_data_cdn(self, serv, panport, conf_port, uuid):
        url = f"http://{serv}:{panport}/admin/{conf_port}/{uuid}"
        r = requests.get(url)
        return r.json()

    def get_user_data(self, id_of_panel):
        r = self.login()
        url = f"http://{self.serv_and_port}/xui/API/inbounds/get/{id_of_panel}"
        r = requests.get(url, cookies=r.cookies)
        return r.json()


if __name__ == "__main__":
    db = SqliteDB()
    server = ServerClass(db,)
    # server.gen_url_same_port(123456, 70, 443)

    # user_config = {"port": 443, "id": "247184e4-b357-4d3b-bddd-af1df4b52a25", "alterId": 0,
    #                "email": "247282e4-b357-4d3b-bddd-af1df4b52a25@emddail", "limitIp": 0, "totalGB": 42949672960, "expiryTime": ""}

    # headers = {"Content-Type": "application/json"}
    # resp = requests.post(url=f"http://192.168.1.35:8000/addClients",
    #
    # headers=headers, json=user_config, )
    print(server.update_cashed_server())
# creation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# user_config = gen_user_config_vless_ws(name="telegram_id", email="email11@hhh", uuid="6e52bc35-66ed-42bd-be7f-47bd83f99aca@channel",
#                                        server_address="localhost", port=80, traffic_limit=70000)
# print(get_user_data("localhot:54321", "1"))
# one = login()
# print(one)
