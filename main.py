import asyncio
import logging
import telebot
import os
import ssl
from datetime import datetime, timedelta
from aiohttp import web
from telebot import asyncio_helper
from servers import ServerClass
from uti import load_config, serv_to_table_str, alternative, milliseconds_to_day_from_now
from telebot.async_telebot import AsyncTeleBot
from hurry.filesize import size
from caching import (get_doadmin, set_doadmin_addAmount,
                     update_doadmin, set_doadmin_editServer,
                     set_doadmin_send_msg_to_all,
                     set_doadmin_addServer, clear_all_command,
                     set_doadmin_send_msg, get_doadmin_new,
                     update_doadmin_new, set_doadmin_edit_admin_stats)

from models import SqliteDB
from inlinebutton import (start_markup, conf_markup, yes_or_no_markup,
                          Download_link_markup, Admin_start_markup,
                          send_msg_too_all, myservice_reply,
                          back_to_home_admin, reset_or_add_admin,
                          send_msg_sure)
from text import text_start, text_start_2, test_my_servicee, service_call_text

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)  # Outputs debug messages to console.


# Error handler
class ExceptionHandler(telebot.ExceptionHandler):

    def handle(self, exception):
        logger.error(exception)


config = load_config()
price = load_config("price.yaml")
bot = AsyncTeleBot(config["TGToken"], exception_handler=ExceptionHandler())

db = SqliteDB()
s = ServerClass(db, "local", "hosr_add")

# webhook data
WEBHOOK_HOST = 'MammothYellowishArea.salehmast.repl.co'
WEBHOOK_PORT = 443  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr
# WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Path to the ssl certificate
# WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Path to the ssl private key
WEBHOOK_URL_BASE = "https://{}:{}".format(WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(config["TGToken"])

if db.get_telegram_ammunt(config["Admin_id"]) is None:
    db.add_row("users",
               (config["Admin_id"], False, None,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, True))


async def hello(request):
    # Remove webhook, it fails sometimes the set if there is a previous webhook
    logger.info('Starting up: removing old webhook')
    await bot.remove_webhook()
    # Set webhook
    logger.info('Starting up: setting webhook')
    await bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH, )
    # certificate=open(WEBHOOK_SSL_CERT, 'r'))

    return web.Response(text="Hello, world")

# Process webhook calls


async def handle(request):
    print("req ...")
    if request.match_info.get('token') == bot.token:
        print("req from tele")
        request_body_dict = await request.json()
        update = telebot.types.Update.de_json(request_body_dict)
        asyncio.ensure_future(bot.process_new_updates([update]))
        return web.Response()
    else:
        return web.Response(status=403)


# Remove webhook and closing session before exiting
async def shutdown(app):
    logger.info('Shutting down: removing webhook')
    await bot.remove_webhook()
    logger.info('Shutting down: closing session')
    await bot.close_session()


async def setup():
    app = web.Application()
    app.add_routes([web.get('/', hello)])

    app.router.add_post('/{token}/', handle)
    app.on_cleanup.append(shutdown)
    return app


class IsAdmin(telebot.asyncio_filters.SimpleCustomFilter):
    key = 'is_admin'

    @staticmethod
    async def check(message: telebot.types.Message):
        if message.chat.id == config["Admin_id"]:
            ammunt = db.get_telegram_ammunt(message.chat.id)
            if ammunt is None:
                db.add_row("users",
                           (message.chat.id, False, None,
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, True))
            return True
        result = db.get_is_admin(message.chat.id)
        return result


class IsAdminCall(telebot.asyncio_filters.SimpleCustomFilter):
    key = 'is_admin_call'

    @staticmethod
    async def check(call: telebot.types.CallbackQuery):
        if call.from_user.id == config["Admin_id"]:
            return True
        result = db.get_is_admin(call.from_user.id)
        return result


class CachingCommand(telebot.asyncio_filters.AdvancedCustomFilter):
    key = 'caching_command'

    @staticmethod
    async def check(message: telebot.types.Message, command: str):
        result = get_doadmin(message.from_user.id, command[0])
        return result != {}


class CachingCommandNew(telebot.asyncio_filters.AdvancedCustomFilter):
    key = 'caching_command_new'

    @staticmethod
    async def check(message: telebot.types.Message, command: str):
        result = get_doadmin_new(message.from_user.id, )
        print(result[b"command"] == bytes(command[0], "utf-8"))
        return result[b"command"] == bytes(command[0], "utf-8")


######################
# this is admin area #
######################

@bot.message_handler(is_admin=True, func=lambda message: message.text == "بازگشت به پنل ادمین")
@bot.message_handler(is_admin=True, commands=['start'])
async def start_admin(message):
    await bot.send_message(message.chat.id,
                           'You are admin of this bot!',
                           reply_markup=Admin_start_markup())


@bot.message_handler(is_admin=True,
                     func=lambda message: message.text == "شارژ حساب کاربر")
async def reply_markup_add_amount(message):
    clear_all_command(message.from_user.id)
    set_doadmin_addAmount(message.from_user.id, "", "")
    await bot.reply_to(message, text="کدام کاربر؟")


@bot.message_handler(is_admin=True,
                     func=lambda message: message.text == "پیام همگانی")
async def reply_markup_send_msg_to_all(message):
    clear_all_command(message.from_user.id)
    set_doadmin_send_msg_to_all(message.from_user.id, "")
    await bot.reply_to(message, text="پیامتو بنویس؟")


@bot.message_handler(is_admin=True,
                     func=lambda message: message.text == "افزودن سرور")
async def reply_markup_add_server(message):
    clear_all_command(message.from_user.id)
    set_doadmin_addServer(message.from_user.id, "", "", "", "", "")
    await bot.reply_to(message, text="ادرس سرور؟")


@bot.message_handler(is_admin=True,
                     func=lambda message: message.text == "مدیریت سرور")
async def reply_markup_edit_server(message):
    clear_all_command(message.from_user.id)
    set_doadmin_editServer(message.from_user.id, "", "", "", "", "")
    all_servers = db.get_serveers()

    await bot.reply_to(
        message,
        text=f"{serv_to_table_str(all_servers)}\n کدوم یکیو میخوای ویرایش کنی؟",
        parse_mode="HTML")


@bot.message_handler(is_admin=True,
                     func=lambda message: message.text == "آمار")
async def reply_markup_static(message):
    pass


@bot.message_handler(is_admin=True,
                     func=lambda message: message.text == "منوی اصلی")
async def callback_query_back_to_home(message):
    await bot.send_message(message.chat.id,
                           'You are admin of this bot!',
                           reply_markup=start_markup(True))


@bot.callback_query_handler(is_admin_call=True,
                            func=lambda call: call.data[:10] == "userchange")
async def reset_amount_for_user(call):
    await bot.answer_callback_query(call.id, "یکم صبر کن...")
    call_data = str(call.data).split("_")
    res = get_doadmin(call.from_user.id, "addAmount")
    await bot.delete_message(chat_id=call.from_user.id,
                             message_id=call.message.id)
    if res is {}:
        await bot.send_message(
            chat_id=call.from_user.id,
            text="مشکلی پیش اومده با زمان درخواست به اتمام رسیده:(((")
        return
    command = res[b"command"].decode("utf-8")
    do_to_userid = res[b"do_to_userid"].decode("utf-8")
    amount = res[b"amount"].decode("utf-8")

    if command == "addAmount" and do_to_userid != "" and amount != "":
        db_ammunt = db.get_telegram_ammunt(int(do_to_userid))
        print(db_ammunt)
        if db_ammunt is None:
            await bot.send_message(call.from_user.id,
                                   f"کاربر {do_to_userid}یاقت نشد :(")
            return
        if call_data[1] == "reset":
            db.update_user_data(int(do_to_userid), int(amount))
            await bot.send_message(
                call.from_user.id,
                f"حساب کاربر {do_to_userid} مبلغ{amount} ریست شد. مبلغ قبلی{db_ammunt}"
            )
        elif call_data[1] == "add":
            db.update_user_data(int(do_to_userid),
                                int(db_ammunt) + int(amount))
            await bot.send_message(
                call.from_user.id,
                f"حساب کاربر {do_to_userid} مبلغ{amount} اضافه شد، و به {int(db_ammunt)+int(amount)} رسید."
            )
        clear_all_command(call.from_user.id)


@bot.callback_query_handler(is_admin_call=True,
                            func=lambda call: call.data[:9] == "msgtouser")
async def msg_to_user(call):
    await bot.answer_callback_query(call.id, "یکم صبر کن...")
    call_data = str(call.data).split("_")
    if call_data[1] == "no":
        await bot.delete_message(chat_id=call.from_user.id,
                                 message_id=call.message.id)
        await bot.send_message(chat_id=call.from_user.id, text="ارسال پیام لغو شد")
        clear_all_command(call.from_user.id)

        return
    res = get_doadmin_new(call.from_user.id)
    print(res)
    await bot.delete_message(chat_id=call.from_user.id,
                             message_id=call.message.id)
    if res is {}:
        await bot.send_message(
            chat_id=call.from_user.id,
            text="مشکلی پیش اومده با زمان درخواست به اتمام رسیده:(((")
        return
    command = res[b"command"].decode("utf-8")
    user = res[b"user"].decode("utf-8")
    msg = res[b"msg"].decode("utf-8")
    print(command, user, msg)
    if command == "sendmsg" and user != "" and msg != "":
        try:
            await bot.send_message(user, msg)
            await bot.send_message(call.from_user.id,
                                   f"پیام {msg} یه کاربر {user} ارسال شد.")
        except:
            await bot.send_message(call.from_user.id, f"پیام ارسال نشد!!!")
        clear_all_command(call.from_user.id)


@bot.callback_query_handler(is_admin_call=True,
                            func=lambda call: call.data[:8] == "msgtoall")
async def msg_to_all(call):
    print("res")

    await bot.answer_callback_query(call.id, "یکم صبر کن...")
    call_data = str(call.data).split("_")
    if call_data[1] == "no":
        await bot.delete_message(chat_id=call.from_user.id,
                                 message_id=call.message.id)
        await bot.send_message(chat_id=call.from_user.id, text="ارسال پیام لغو شد")
        clear_all_command(call.from_user.id)
        return
    res = get_doadmin_new(call.from_user.id)
    await bot.delete_message(chat_id=call.from_user.id,
                             message_id=call.message.id)
    if res is {}:
        await bot.send_message(
            chat_id=call.from_user.id,
            text="مشکلی پیش اومده با زمان درخواست به اتمام رسیده:(((")
        return
    # command = res[b"command"].decode("utf-8")
    # user = res[b"user"].decode("utf-8")
    msg = res[b"msg"].decode("utf-8")
    if msg != "":
        try:
            item = db.get_users()
            task = []
            for i in item:
                task.append(asyncio.create_task(bot.send_message(i[0], msg)))
            await asyncio.gather(*task)
            await bot.send_message(call.from_user.id,
                                   f"پیام {msg} به کاربرها  ارسال شد.")
        except Exception as e:
            print(e)
            await bot.send_message(call.from_user.id, f"پیام ارسال نشد!!!")
        clear_all_command(call.from_user.id)


@bot.message_handler(is_admin=True,
                     func=lambda message: message.text == "موجودی کاربران")
async def callback_user_amount(message):
    num = db.get_count_of_raw("users")
    admin = db.get_count_of_raw_of_admin("users")
    await bot.reply_to(
        message, text=f"تعداد کاربران ربات {num}است و تعداد ادمین ها {admin}")


@bot.message_handler(is_admin=True,
                     func=lambda message: message.text == "ادمین ها")
async def callback_admin_changer(message):
    if message.chat.id == config["Admin_id"]:
        clear_all_command(message.from_user.id)
        set_doadmin_edit_admin_stats(message.from_user.id, "",)
        admin = db.get_list_of_admin("users")
        text = ""
        for i in admin:
            text += f" ادمین با ایدی {i[0]} تاریخ عضویت {i[3]} دارای {i[4]} تومان میباشد \n"
        text += "\nبرای تغییر وضعیت ادمین به کاربر عادی یا کار بر یه ادمین ای دی عددب رو بفرست"
        await bot.reply_to(message, text=text)
    else:
        await bot.reply_to(message, text="به این بخش دسترسی نداری:(")


@bot.message_handler(is_admin=True,
                     func=lambda message: message.text == "پیام به کاربر")
async def callback_user_send_msg_to_user(message):
    clear_all_command(message.from_user.id)
    set_doadmin_send_msg(message.from_user.id, "", "")
    await bot.reply_to(message, text="به کدام کاربر؟")


#####################
# this is user area #
#####################


@bot.message_handler(func=lambda message: message.text == "بازگشت")
@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
    ammunt = db.get_telegram_ammunt(message.chat.id)
    is_admin = db.get_is_admin(message.chat.id)
    if ammunt is None:
        db.add_row("users",
                   (message.chat.id, False, None,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, False))
        await bot.send_message(message.chat.id,
                               text_start.format(config["RobotName"]),
                               reply_markup=start_markup(bool(is_admin)))
        return
    await bot.send_message(message.chat.id,
                           text_start_2,
                           reply_markup=start_markup(bool(is_admin)))


@bot.message_handler(func=lambda message: message.text == "خرید کانفیگ")
async def replymarkup_BuyConf(message):
    await bot.send_message(chat_id=message.from_user.id,
                           text="انتخاب کن!",
                           reply_markup=conf_markup())


@bot.message_handler(
    func=lambda message: message.text == "🔶۴۰گیگ یک ماه (75,000هزار تومان)")
async def reply_markup_traffic_40(message):
    num = 40
    ammunt = db.get_telegram_ammunt(message.from_user.id)
    if ammunt is None:
        db.add_row("users",
                   (message.from_user.id, False, None,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, False))
    # print(price[int(call_data[1])])
    if price[num] <= ammunt:
        await bot.send_message(chat_id=message.from_user.id,
                               text="مطمئنی؟؟",
                               reply_markup=yes_or_no_markup(num))
    else:
        await bot.send_message(
            chat_id=message.from_user.id,
            text="لطفا حسابت رو شارژ کن",
        )
        return
    # print(call_data)


@bot.message_handler(
    func=lambda message: message.text == "🔷۵۰گیگ یک‌ ماه (90,000هزار تومان)")
async def reply_markup_traffic_50(message):
    num = 50
    ammunt = db.get_telegram_ammunt(message.from_user.id)
    if ammunt is None:
        db.add_row("users",
                   (message.from_user.id, False, None,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, False))
    # print(price[int(call_data[1])])
    if price[num] <= ammunt:
        await bot.send_message(chat_id=message.from_user.id,
                               text="مطمئنی؟؟",
                               reply_markup=yes_or_no_markup(num))
    else:
        await bot.send_message(
            chat_id=message.from_user.id,
            text="لطفا حسابت رو شارژ کن",
        )
        return
    # print(call_data)


@bot.message_handler(
    func=lambda message: message.text == "🔶۸۰گیگ یک ماه (145,000هزار تومان)")
async def reply_markup_traffic_80(message):
    num = 80

    ammunt = db.get_telegram_ammunt(message.from_user.id)
    if ammunt is None:
        db.add_row("users",
                   (message.from_user.id, False, None,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, False))
    # print(price[int(call_data[1])])
    if price[num] <= ammunt:
        await bot.send_message(chat_id=message.from_user.id,
                               text="مطمئنی؟؟",
                               reply_markup=yes_or_no_markup(num))
    else:
        await bot.send_message(
            chat_id=message.from_user.id,
            text="لطفا حسابت رو شارژ کن",
        )
        return
    # print(call_data)


@bot.message_handler(
    func=lambda message: message.text == "🔷۱۰۰گیگ یک ماه (170,000هزار تومان)")
async def reply_markup_traffic_100(message):
    num = 100
    ammunt = db.get_telegram_ammunt(message.from_user.id)
    if ammunt is None:
        db.add_row("users",
                   (message.from_user.id, False, None,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, False))
    # print(price[int(call_data[1])])
    if price[num] <= ammunt:
        await bot.send_message(chat_id=message.from_user.id,
                               text="مطمئنی؟؟",
                               reply_markup=yes_or_no_markup(num))
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text="لطفا حسابت رو شارژ کن")
        return
    # print(call_data)


@bot.callback_query_handler(func=lambda call: call.data[0:5] == "tryes")
async def callback_query_tryes(call):
    call_data = str(call.data).split("_")
    print(call_data)
    ammunt = db.get_telegram_ammunt(call.from_user.id)
    if ammunt is None:
        db.add_row("users",
                   (call.from_user.id, False, None,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, False))
    # print(price[int(call_data[1])])
    if price[int(call_data[1])] <= ammunt:
        pass
    else:
        await bot.answer_callback_query(call.id, "لطفا حسابت رو شارژ کن")
        return
    # kharid
    await bot.answer_callback_query(call.id, "یکم صبر کن...")
    if call_data[1] == "40":
        traffic_limit = 42949672960
    elif call_data[1] == "50":
        traffic_limit = 53687091200
    elif call_data[1] == "80":
        traffic_limit = 85899345920
    elif call_data[1] == "100":
        traffic_limit = 107374182400

    if call_data[2] == "hamrah":
        port = 2083
    elif call_data[2] == "iran":
        port = 443

    if s.CHECK_POINT is False:
        return
    code, resp = s.gen_url_same_port(call.from_user.id,
                                     traffic_limit=traffic_limit,
                                     port=port)
    if code == None and resp == None:
        await bot.delete_message(chat_id=call.from_user.id,
                                 message_id=call.message.id)
        await bot.send_message(call.from_user.id,
                               "یوزر ساخته نشد دوباره تلاش کنید",
                               parse_mode="markdown")
        return
    db.update_user_data(call.from_user.id,
                        int(ammunt) - int(price[int(call_data[1])]))
    if code:
        print(resp)
        if config['CDN_ADD'] != None:
            msg = f"```{db.link_gen_cdn(resp,s.host_add,resp['alterId'],cdn_add=config['CDN_ADD'])}```\n"
        else:
            msg = f"همراه اول```{db.link_gen_cdn(resp,s.host_add,resp['alterId'])}```\n"

        await bot.delete_message(chat_id=call.from_user.id,
                                 message_id=call.message.id)
        await bot.send_message(call.from_user.id, msg, parse_mode="markdown")
        # msg = f"ایرانسل رایتل ثابت```{db.link_gen_new(resp,s.host_add)}```\n"
        # await bot.send_message(call.from_user.id, msg, parse_mode="markdown")
    if code is None:
        await bot.send_message(call.from_user.id,
                               "به نظر مشکلی وجود دارد با ادمین تماس بگیر",
                               parse_mode="markdown")


@bot.callback_query_handler(func=lambda call: call.data[0:4] == "trno")
async def callback_query_trno(call):
    await bot.edit_message_text(chat_id=call.from_user.id,
                                message_id=call.message.id,
                                text=text_start,
                                reply_markup=start_markup(False))


@bot.message_handler(func=lambda message: message.text == "کیف پول")
async def callback_query_MyWallet(message):
    print("hi")

    ammunt = db.get_telegram_ammunt(message.from_user.id)
    print(ammunt)

    if ammunt is None:
        db.add_row("users",
                   (message.from_user.id, False, None,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, False))
    if not ammunt:
        await bot.send_message(chat_id=message.from_user.id,
                               text="موجودی شما 0 تومان است")
        return
    await bot.send_message(
        chat_id=message.from_user.id,
        text=f"موجودی شما {ammunt} تومان است",
    )


@bot.message_handler(
    func=lambda message: message.text == "دریافت نرم افزار یا اپلیکیشن")
async def callback_query_GetAPP(message):
    await bot.send_message(chat_id=message.from_user.id,
                           text="برای دانلود انتخاب کن",
                           reply_markup=Download_link_markup())


@bot.message_handler(func=lambda message: message.text == "استعلام سرویس من")
async def callback_query_MyService(message):
    call_list = db.get_services(message.from_user.id)
    if call_list is None:
        await bot.send_message(message.from_user.id, "اول سرویس خریداری کنید")
        return
    text = ""
    num = 1
    list_of_id = []
    for i in call_list:
        list_of_id.append(i[1])
        text += test_my_servicee.format(str(num), str(i[7]), str(i[6]),
                                        size(int(i[5])), str(i[4]), str(i[3]))
        num += 1

    await bot.send_message(chat_id=message.from_user.id,
                           text=text,
                           reply_markup=myservice_reply(list_of_id,
                                                        message.from_user.id,), parse_mode="HTML")


@ bot.message_handler(func=lambda message: message.text == "آیدی من")
async def callback_query_my_id(message):
    text_ = f"ایدی شما ```{message.from_user.id}```"
    await bot.send_message(message.from_user.id, text_, parse_mode="markdown")


@ bot.callback_query_handler(func=lambda call: call.data[0:3] == "GMS")
async def callback_query_GMS(call):
    call_data = str(call.data).split("_")
    # if s.CHECK_POINT is False:
    #     return
    checck = s.get_user_data_cdn(
        f"{call_data[1]}@{call.from_user.id}abc.com".replace("-", ""))

    if checck is None:
        await bot.answer_callback_query(call.id, "اطلاعات یافت نشد")
        await bot.send_message(call.from_user.id, "اطلاعات یافت نشد")
        return
    mandeh = checck[7] - (checck[4] + checck[5])
    masrafi = (checck[4] + checck[5])
    tarikh = checck[6]
    timedelta()
    vasiat = checck[2]
    koll = checck[7]

    if vasiat == 0:
        vasiat = "غیر فعال"
    elif vasiat == 1:
        vasiat = "فعال"

    if tarikh == 0:
        tarikh = "نامحدود"
        text = service_call_text.format(str(vasiat), size(int(masrafi), alternative),
                                        size(int(mandeh), alternative), size(int(koll), alternative), str(tarikh))
    else:
        text = service_call_text.format(str(vasiat), size(int(masrafi), alternative),
                                        size(int(mandeh), alternative), size(int(koll), alternative), str(milliseconds_to_day_from_now(tarikh))+" روز")
    await bot.answer_callback_query(call.id, "ok")
    await bot.send_message(call.from_user.id, text)


@ bot.message_handler(is_admin=True,
                      caching_command=["addAmount"],
                      func=lambda message: True)
async def addAmount_admin(message):
    # print("is here")
    res = get_doadmin(message.from_user.id, "addAmount")
    command = res[b"command"].decode("utf-8")
    do_to_userid = res[b"do_to_userid"].decode("utf-8")
    amount = res[b"amount"].decode("utf-8")
    if res is {}:
        await bot.reply_to(message, "دستور شناسایی نشد :|")
        return
    if do_to_userid == "":
        try:
            int(message.text)
            update_doadmin(message.from_user.id, command, "do_to_userid",
                           message.text)
            await bot.reply_to(message, "حالا به چه مقدار؟")

        except:
            await bot.reply_to(message, text="متوجه نشدم ،کدام کاربر؟")
            return
    elif amount == "":
        try:
            print(message.text)
            int(message.text)
            update_doadmin(message.from_user.id, command,
                           "amount", message.text)
            await bot.reply_to(message,
                               "مقدار قبلی را ریست کنم یا اضافه",
                               reply_markup=reset_or_add_admin())
        except Exception as e:
            print(e)
            await bot.reply_to(message, text="متوجه نشدم چه مقدار؟")
            return


@ bot.message_handler(is_admin=True,
                      caching_command_new=["addserver"],
                      func=lambda message: True)
async def addserver_admin(message):
    print("is here")
    res = get_doadmin_new(message.from_user.id, )
    # command = res[b"command"].decode("utf-8")
    host = res[b"host"].decode("utf-8")
    port = res[b"port"].decode("utf-8")
    user = res[b"user"].decode("utf-8")
    password = res[b"password"].decode("utf-8")
    host_add = res[b"host_add"].decode("utf-8")

    if res is {}:
        await bot.reply_to(message, "دستور شناسایی نشد :|")
        return
    if host == "":
        update_doadmin_new(message.from_user.id, "host", message.text)
        await bot.reply_to(message, "شماره پورت پنل؟")
    elif port == "":
        try:
            int(message.text)
            update_doadmin_new(message.from_user.id, "port", message.text)
            await bot.reply_to(message, "نام کاربری؟")
        except Exception as e:
            print(e)
            await bot.reply_to(message, text="تام کاربری را متوجه نشدم ")
            return
    elif user == "":
        update_doadmin_new(message.from_user.id, "user", message.text)
        await bot.reply_to(message, "پسورد را وارد کنید")
    elif password == "":
        update_doadmin_new(message.from_user.id, "password", message.text)
        await bot.reply_to(message, "ادرس هوست نیم را وارد کنید")
    elif host_add == "":
        global s
        if s.CHECK_POINT is False:
            s = ServerClass(
                db,
                f"{host}:{port}",
                message.text,
                user,
                password,
            )
        if db.get_serveer_exist(host) is None:
            if db.get_server_from_in_use(True) is None:
                db.add_row("servers",
                           (None, host, port, user, password, 0, True, message.text))
            else:
                db.add_row("servers",
                           (None, host, port, user, password, 0, False, message.text))
            s.update_cashed_server()
            await bot.reply_to(
                message,
                f"سرور با مشخصات {host}|{port}|{user}|{password}|{message.text}  اضافه شد"
            )
            clear_all_command(message.from_user.id)
            return
        await bot.reply_to(
            message,
            f'|{host}|{port}|{user}|{password}|{message.text}قبلا موجود بود')
        clear_all_command(message.from_user.id)


@ bot.message_handler(is_admin=True,
                      caching_command_new=["editserver"],
                      func=lambda message: True)
async def editserver_admin(message):
    print("is here edit sever")
    res = get_doadmin_new(message.from_user.id, )
    print(res)

    ID = res[b"id"].decode("utf-8")
    # command = res[b"command"].decode("utf-8")
    host = res[b"host"].decode("utf-8")
    port = res[b"port"].decode("utf-8")
    user = res[b"user"].decode("utf-8")
    password = res[b"password"].decode("utf-8")
    host_add = res[b"host_add"].decode("utf-8")

    if res is {}:
        await bot.reply_to(message, "دستور شناسایی نشد :|")
        return
    if ID == "":
        update_doadmin_new(message.from_user.id, "id", message.text)
        await bot.reply_to(message, "ادرس سرور؟")
    elif host == "":
        update_doadmin_new(message.from_user.id, "host", message.text)
        await bot.reply_to(message, "شماره پورت پنل؟")
    elif port == "":
        try:
            int(message.text)
            update_doadmin_new(message.from_user.id, "port", message.text)
            await bot.reply_to(message, "نام کاربری؟")
        except Exception as e:
            print(e)
            await bot.reply_to(message, text="تام کاربری را متوجه نشدم ")
            return
    elif user == "":
        update_doadmin_new(message.from_user.id, "user", message.text)
        await bot.reply_to(message, "پسورد را وارد کنید")
    elif password == "":
        update_doadmin_new(message.from_user.id, "password", message.text)
        await bot.reply_to(message, "ادرس هوست نیم را وارد کنید")
    elif host_add == "":
        print("one")
        global s
        if s.CHECK_POINT is False:
            s = ServerClass(db, f"{host}:{port}", message.text, user, password)
        # if db.get_serveer_exist(host):
        #     return
        one = db.get_server_from_id(ID)
        if one[6] == True:
            s = ServerClass(db, f"{host}:{port}", message.text, user, password)
        db.update_server(ID, host, port, user, password, message.text)
        s.update_cashed_server()
        await bot.reply_to(
            message,
            f"سرور با مشخصات {ID}|{host}|{port}|{user}|{password}|{message.text}  ویرایش شد"
        )
        clear_all_command(message.from_user.id)


@ bot.message_handler(is_admin=True,
                      caching_command_new=["sendmsg"],
                      func=lambda message: True)
async def addmsg_admin(message):
    res = get_doadmin_new(message.from_user.id)
    # command = res[b"command"].decode("utf-8")
    user = res[b"user"].decode("utf-8")
    msg = res[b"msg"].decode("utf-8")

    if res is {}:
        await bot.reply_to(message, "دستور شناسایی نشد :|")
        return
    if user == "":
        update_doadmin_new(message.from_user.id, "user", message.text)
        await bot.reply_to(message, "پیامت رو ینویس")
    elif msg == "":
        update_doadmin_new(message.from_user.id, "msg", message.text)
        await bot.reply_to(message,
                           f"پیام {user} یه کاربر {message.text} ارسال شود؟",
                           reply_markup=send_msg_sure())


@ bot.message_handler(is_admin=True,
                      caching_command_new=["editadmin"],
                      func=lambda message: True)
async def editadmin(message):
    res = get_doadmin_new(message.from_user.id)
    chat_id_of_user = res[b"chat_id_of_user"].decode("utf-8")
    if int(message.text) == config["Admin_id"]:
        await bot.reply_to(message, " ای دی خودته :|")
        return
    if res is {}:
        await bot.reply_to(message, "دستور شناسایی نشد :|")
        return
    if chat_id_of_user == "":
        # update_doadmin_new(message.from_user.id,
        #                    "chat_id_of_user", message.text)
        id_admin_or_not = db.get_is_admin(int(message.text))
        if id_admin_or_not == True:
            db.admin_updator(int(message.text), False)
            await bot.reply_to(message, "کاربر ادمین به یوزر عادی تغییر وضعیت داد")
        elif id_admin_or_not == False:
            db.admin_updator(int(message.text), True)
            await bot.reply_to(message, "کاربر به ادمین تغییر وضعیت داد")


@ bot.message_handler(is_admin=True,
                      caching_command_new=["sendmsgtoall"],
                      func=lambda message: True)
async def msg_admin_all(message):
    res = get_doadmin_new(message.from_user.id)
    # command = res[b"command"].decode("utf-8")
    msg = res[b"msg"].decode("utf-8")

    if res is {}:
        await bot.reply_to(message, "دستور شناسایی نشد :|")
        return
    if msg == "":
        update_doadmin_new(message.from_user.id, "msg", message.text)
        await bot.reply_to(message,
                           f"پیام   {message.text} به تمام کاربرهاارسال شود؟",
                           reply_markup=send_msg_too_all())


if __name__ == "__main__":
    print("Robot is working...")
    bot.add_custom_filter(IsAdmin())
    bot.add_custom_filter(IsAdminCall())
    bot.add_custom_filter(CachingCommand())
    bot.add_custom_filter(CachingCommandNew())
    if config["Sand_box"]:
        asyncio_helper.proxy = 'http://127.0.0.1:2080'

        loop = asyncio.new_event_loop()
        loop.create_task(bot.polling(non_stop=True),)
        loop.run_forever()
    else:
        # Build ssl context
        # context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        # context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)
        # # Start aiohttp server
        web.run_app(
            setup(),
            host=WEBHOOK_LISTEN,
            port=WEBHOOK_PORT,
            # ssl_context=context,
        )
