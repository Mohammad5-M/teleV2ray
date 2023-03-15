import redis
import json
from datetime import timedelta
from uti import load_config


config = load_config()

r = redis.Redis(host=config["Redis_host"], port=config["Redis_port"], username=config["Redis_user"],
                password=config["Redis_pass"], socket_timeout=None, db=0)

# [addAmount, user_id, amount, reset]


def set_doadmin_addAmount(admin_id, do_to_userid="", amount=""):
    ex = timedelta(minutes=10)
    r.hset(f"addAmount{admin_id}", mapping={"command": "addAmount",
                                            "do_to_userid": do_to_userid, "amount": amount, })
    r.expire(admin_id, ex)


def set_doadmin_send_msg(admin_id, user="", msg=""):
    ex = timedelta(minutes=10)
    r.hset(admin_id, mapping={"command": "sendmsg",
                              "user": user, "msg": msg})
    r.expire(admin_id, ex)


def set_doadmin_send_msg_to_all(admin_id, msg=""):
    ex = timedelta(minutes=10)
    r.hset(admin_id, mapping={"command": "sendmsgtoall",
                              "msg": msg})
    r.expire(admin_id, ex)


def set_doadmin_addServer(admin_id, host="", port="", user="", password="", host_add=""):
    ex = timedelta(minutes=10)
    r.hset(admin_id, mapping={"command": "addserver",
                              "host": host, "port": port, "user": user, "password": password, "host_add": host_add})
    r.expire(admin_id, ex)


def set_doadmin_edit_admin_stats(admin_id, chat_id_of_user=""):
    ex = timedelta(minutes=10)
    r.hset(admin_id, mapping={"command": "editadmin",
                              "chat_id_of_user": chat_id_of_user})
    r.expire(admin_id, ex)


def set_doadmin_editServer(admin_id, id="", host="", port="", user="", password="", host_add=""):
    ex = timedelta(minutes=10)
    r.hset(admin_id, mapping={"command": "editserver", "id": id,
                              "host": host, "port": port, "user": user, "password": password, "host_add": host_add})
    r.expire(admin_id, ex)


def update_doadmin(admin_id, command, which_field, val: str):
    ex = timedelta(minutes=10)
    r.hset(f"{command}{admin_id}", which_field, val)
    r.expire(admin_id, ex)


def update_doadmin_new(admin_id, which_field, val: str):
    ex = timedelta(minutes=10)
    r.hset(admin_id, which_field, val)
    r.expire(admin_id, ex)


def get_doadmin(admin_id, command):
    res = r.hgetall(f"{command}{admin_id}")
    if res is None:
        return None
    return res


def get_doadmin_new(admin_id, ):
    res = r.hgetall(admin_id)
    if res is None:
        return None
    return res


def set_do_admin(admin_id, URI="",):
    ex = timedelta(minutes=10)
    r.hset(admin_id, mapping={"command": "admingetdata", "URI": URI, })
    r.expire(admin_id, ex)


def clear_all_command(admin_id):
    r.delete(f"addserver{admin_id}", f"addAmount{admin_id}", admin_id)


def set_do_user(user_id, URI="",):
    ex = timedelta(minutes=10)
    r.hset(user_id, mapping={"command": "usergetdata", "URI": URI, })
    r.expire(user_id, ex)


if __name__ == "__main__":
    # set_doadmin_addAmount(407599569, 123456789, 100000)
    # set_doadmin_addServer(407599569, "local", 585, "admin", "admin")
    # update_doadmin_addAmount(407599569, b"amount", "155000")
    # clear_all_command(407599569)
    res = get_doadmin_new(407599569)
    # command = res[b"command"].decode("utf-8")

    print(res)
