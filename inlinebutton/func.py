from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def start_markup(is_admin: bool):
    markup = ReplyKeyboardMarkup()
    markup.row_width = 2
    markup.add(KeyboardButton("خرید کانفیگ", ))
    markup.add(KeyboardButton("کیف پول", ),
               KeyboardButton("استعلام سرویس من", ))
    markup.add(KeyboardButton("کد تخفیف", ),
               KeyboardButton("آیدی من", ))
    markup.add(KeyboardButton(
        "دریافت نرم افزار یا اپلیکیشن", ))

    markup.add(KeyboardButton("ارتباط با ما", ),
               KeyboardButton("راهنما", ))
    if is_admin:
        markup.add(KeyboardButton(
            "بازگشت به پنل ادمین", ))
    return markup


def conf_markup():
    markup = ReplyKeyboardMarkup()
    markup.row_width = 2
    markup.add(KeyboardButton(
        "🔶۴۰گیگ یک ماه (75,000هزار تومان)", ))
    markup.add(KeyboardButton(
        "🔷۵۰گیگ یک‌ ماه (90,000هزار تومان)", ))
    markup.add(KeyboardButton(
        "🔶۸۰گیگ یک ماه (145,000هزار تومان)", ))
    markup.add(KeyboardButton(
        "🔷۱۰۰گیگ یک ماه (170,000هزار تومان)", ))
    markup.add(KeyboardButton(
        "بازگشت", ))
    return markup


def yes_or_no_markup(in_num):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton(
        "بله", callback_data=f"tryes_{in_num}"))
    markup.add(InlineKeyboardButton(
        "خیر", callback_data="trno_00"))

    return markup


def reset_or_add_admin():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton(
        "ریست کن", callback_data=f"userchange_reset"))
    markup.add(InlineKeyboardButton(
        "اضافه کن", callback_data="userchange_add"))

    return markup


def send_msg_sure():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton(
        "بله پیام ارسال شود", callback_data=f"msgtouser_yes"))
    markup.add(InlineKeyboardButton(
        "خیر", callback_data="msgtouser_no"))

    return markup


def send_msg_too_all():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton(
        "بله پیام ارسال شود", callback_data=f"msgtoall_yes"))
    markup.add(InlineKeyboardButton(
        "خیر", callback_data="msgtoall_no"))

    return markup


def Download_link_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton(
        "Fair for ios", url="https://apps.apple.com/us/app/fair-vpn/id1533873488?platform=iphone"))
    markup.add(InlineKeyboardButton(
        "V2rayNG for Android", url="https://github.com/2dust/v2rayNG/releases"))
    markup.add(InlineKeyboardButton(
        "V2rayN for Windows", url="https://github.com/2dust/v2rayN/releases"))
    markup.add(InlineKeyboardButton(
        "Fair for Mac OS", url="https://apps.apple.com/us/app/fair-vpn/id1533873488?platform=mac"))

    return markup


def Admin_start_markup():
    markup = ReplyKeyboardMarkup()
    markup.add(KeyboardButton(
        "مدیریت سرور"), KeyboardButton("افزودن سرور",))
    markup.add(KeyboardButton(
        "آمار",), KeyboardButton("پیام همگانی", ))
    markup.add(KeyboardButton(
        "موجودی کاربران", ), KeyboardButton("ادمین ها", ))
    markup.add(KeyboardButton(
        "شارژ حساب کاربر", ), KeyboardButton("کد تخفیف", ))
    markup.add(KeyboardButton(
        "منوی اصلی", ), KeyboardButton("پیام به کاربر",))

    return markup


def myservice_reply(list_of_id, user_id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    for i in list_of_id:
        markup.add(InlineKeyboardButton(
            f"استعلام شماره {i}", callback_data=f"GMS_{i}"))

    return markup


def back_to_home_admin():
    markup = ReplyKeyboardMarkup()
    markup.row_width = 2
    markup.add(KeyboardButton(
        "بازگشت", ))

    return markup
