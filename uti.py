import json
import re
import base64
import yaml
from datetime import datetime, timedelta


def load_config(path='config.yaml'):
    with open(path, 'r') as stream:
        config = yaml.safe_load(stream)
    return config


def serv_to_table_str(all_list: list):
    text = "<code>|ID|     server    |port|user|pass|UC|U|</code>\n"
    char = " "
    for i in all_list:
        text += "<code>|{}|{}|{}|{}~|{}~|{}|{}|</code>\n".format(str(i[0])[:2].center(2, char), str(i[1])[:15].center(15, char), str(i[2])[:4].center(4, char), str(i[3])[:3].center(3, char),
                                                                 str(i[4])[:3].center(3, char), str(i[5]).center(2, char), str(bool(i[6]))[0])
    print(text)
    return text


# print(serv_to_table_str([(1, '192,168,1,35', 8000, 'admin',
#       'admin', 1, 1), (2, '192.168.1.22', '5000', 'admin', '', 0, 0)]))
def decoder_into_utf8(base64_string: str):
    """basicly is returning decoded string but you have to now we use standard decode wich is RFC 4648"""
    base64_bytes = base64_string.encode("utf-8")
    sample_string_bytes = base64.standard_b64decode(base64_bytes)
    sample_string = sample_string_bytes.decode("utf-8")
    return sample_string


def encode_utf8(sample_string: dict) -> str:
    sample_string = json.dumps(sample_string)
    sample_string_bytes = sample_string.encode("utf-8")
    base64_bytes = base64.standard_b64encode(sample_string_bytes)
    base64_string = base64_bytes.decode("utf-8")
    return base64_string


def conf_ch_cdn(add: str,  host: str,
                id: str, net: str, path: str, port: str,
                ps: str,  sni: str, tls: str,
                type: str = "", v: str = "2", aid: str = "0", alpn: str = "http/1.1", scy: str = "auto"):

    r = {"add": add, "aid": aid, "alpn": alpn, "host": host, "id": id, "net": net,
         "path": path, "port": port, "ps": ps, "scy": scy, "sni": sni, "tls": tls, "type": type, "v": v}
    return f"vmess://{encode_utf8(r)}"


def conf_ch(add: str,
            id: str, net: str, path: str, port: str,
            ps: str,  tls: str, type: str,
            host: str = "", sni: str = "",
            v: str = "2", aid: str = "0", alpn: str = "", scy: str = "auto"):

    r = {"add": add, "aid": aid, "alpn": alpn, "host": host, "id": id, "net": net,
         "path": path, "port": port, "ps": ps, "scy": scy, "sni": sni, "tls": tls, "type": type, "v": v}
    return f"vmess://{encode_utf8(r)}"


alternative = [
    (1024 ** 5, ' پتابایت'),
    (1024 ** 4, ' ترابایت'),
    (1024 ** 3, ' گیگابایت'),
    (1024 ** 2, ' مگابایت'),
    (1024 ** 1, ' کیلوبایت'),
    (1024 ** 0, (' بایت', ' بایت')),
]


def time_in_defult_days_milliseconds(days=30):
    presentDate = datetime.now()
    ddd = timedelta(days=days) + presentDate
    ddd = ddd.timestamp()*1000.0
    return ddd.__int__()


def milliseconds_to_day_from_now(millisec):
    presentDate = datetime.now()
    return (datetime.fromtimestamp(millisec/1000.0) - presentDate).days


def milliseconds_now(millisec):
    presentDate = datetime.now()
    # if millisec/1000.0 - presentDate <= 0:
    #     return "پایان رسیده"
    return (datetime.fromtimestamp(millisec/1000.0) - presentDate).__str__().split(".")[0].replace("days", "روز") + "ساعت"


if __name__ == "__main__":
    # ppp = time_in_defult_days_milliseconds()
    ppp = milliseconds_now(1681241291461)

    print(ppp)
