# -*- coding: utf-8 -*-
# Plugins/developer_menu.py - سورس عبود المطور
# أمر .المطور مع أزرار ملونة ونظام صلاحيات

import asyncio
import random
import time
import requests
from telethon import events, Button
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from telethon.errors import MessageNotModifiedError, FloodWaitError
import database  # يستدعي دوال get_config, set_config, session إلخ

# ------------------- الإعدادات -------------------
StartTime = time.time()
OWNER_ID = 6373993992
SUDO_USERS = []  # يمكنك إضافة آيديات المطورين الثانويين
PROGS = [OWNER_ID] + SUDO_USERS

TOKEN = database.get_config("TOKEN")
if not TOKEN:
    print("⚠️ تنبيه: التوكن غير موجود في قاعدة البيانات!")
BOT_URL = f"https://api.telegram.org/bot{TOKEN}"

PIC_URL = "https://files.catbox.moe/k4fxu0.jpg"  # صورة المطور
CHANNEL_USERNAME = "@lAYAI"
DEV_USERNAME = "@BD_0I"

# ------------------- دالة فحص الصلاحية -------------------
def is_authorized(user_id):
    return user_id in PROGS

# ------------------- معالج أمر .المطور -------------------
@events.register(events.NewMessage(outgoing=True, pattern=r"^\.المطور$"))
async def developer_info(event):
    """إرسال رسالة المطور مع أزرار ملونة عبر البوت المساعد"""
    if not TOKEN:
        await event.edit("❌ لم يتم العثور على توكن البوت! تأكد من تنصيبه.")
        return

    chat_id = event.chat_id

    # إعداد الكابشن
    caption = (
        "**⚡ سورس عبود المطور V11.0 ⚡**\n"
        "✛━━━━━━━━━━━━━✛\n"
        f"**• المطور الأساسي :** {DEV_USERNAME}\n"
        f"**• قناة السورس :** {CHANNEL_USERNAME}\n"
        "✛━━━━━━━━━━━━━✛\n"
        "**• النظام :** يعمل الآن بنجاح 🚀\n"
        "**• وقت التشغيل :** " + get_uptime()
    )

    # بناء الأزرار الملونة
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "🔵 المطور", "url": f"https://t.me/{DEV_USERNAME[1:]}", "style": "primary"},
                {"text": "🟢 القناة", "url": f"https://t.me/{CHANNEL_USERNAME[1:]}", "style": "success"}
            ],
            [
                {"text": "📊 إحصائيات", "callback_data": "dev_stats", "style": "primary"},
                {"text": "🔄 حالة السورس", "callback_data": "dev_status", "style": "success"}
            ],
            [
                {"text": "🔴 حظر السورس", "callback_data": "dev_block", "style": "danger"},
                {"text": "🟢 الغاء الحظر", "callback_data": "dev_unblock", "style": "success"}
            ],
            [
                {"text": "👑 أوامر المطور", "callback_data": "dev_help", "style": "primary"}
            ]
        ]
    }

    # إرسال الصورة مع الأزرار عبر Bot API
    payload = {
        "chat_id": chat_id,
        "photo": PIC_URL,
        "caption": caption,
        "reply_markup": keyboard,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(f"{BOT_URL}/sendPhoto", json=payload)
        if response.status_code == 200:
            await event.delete()  # حذف أمر .المطور
        else:
            await event.edit("❌ فشل إرسال الصورة عبر البوت. تحقق من صلاحيات البوت.")
    except Exception as e:
        await event.edit(f"⚠️ خطأ: {str(e)}")

def get_uptime():
    """حساب وقت التشغيل"""
    uptime_seconds = int(time.time() - StartTime)
    days = uptime_seconds // 86400
    hours = (uptime_seconds % 86400) // 3600
    minutes = (uptime_seconds % 3600) // 60
    return f"{days} يوم, {hours} ساعة, {minutes} دقيقة"

# ------------------- معالج الضغط على الأزرار (CallbackQuery) -------------------
@events.register(events.CallbackQuery)
async def callback_handler(event):
    """معالجة ضغطات الأزرار مع فحص الصلاحية"""
    data = event.data.decode("utf-8")
    user_id = event.query.user_id

    # التحقق من الصلاحية (المطور فقط)
    if not is_authorized(user_id):
        await event.answer("⛔ هذا الزر خاص بالمطور فقط!", alert=True)
        return

    # ---------- ردود الأزرار ----------
    if data == "dev_stats":
        # جلب إحصائيات من قاعدة البيانات
        try:
            from database import session, Stats
            plugins_count = session.query(Stats).count()
            stats_text = f"📊 عدد الموديولات المحملة: {plugins_count}\n⏱ وقت التشغيل: {get_uptime()}"
        except:
            stats_text = "⚠️ تعذر جلب الإحصائيات."
        await event.answer(stats_text, alert=True)

    elif data == "dev_status":
        status = "✅ السورس يعمل بكامل طاقته." if database.get_config("is_blocked") != "yes" else "🔴 السورس في وضع الحظر."
        await event.answer(status, alert=True)

    elif data == "dev_block":
        database.set_config("is_blocked", "yes")
        await event.answer("🔴 تم تفعيل وضع الحظر العام.", alert=True)

    elif data == "dev_unblock":
        database.set_config("is_blocked", "no")
        await event.answer("🟢 تم إلغاء وضع الحظر.", alert=True)

    elif data == "dev_help":
        help_text = (
            "**⚙️ أوامر المطور:**\n"
            "`.تنصيب` - تحديث الجلسة والتوكن\n"
            "`.اعادة تشغيل` - إعادة تشغيل السورس\n"
            "`.تحديث المكاتب` - تحديث المكتبات\n"
            "`.لوك` - إرسال سجل الأخطاء\n"
        )
        await event.answer(help_text, alert=True)

# ------------------- نظام منع الأوامر للمحظورين (اختياري) -------------------
@events.register(events.NewMessage(outgoing=True))
async def block_check(event):
    if database.get_config("is_blocked") == "yes":
        if event.text and event.text.startswith("."):
            if event.sender_id not in PROGS:
                await event.edit("⚠️ عذراً، الحساب محظور من استخدام الأوامر حالياً.")
                await asyncio.sleep(3)
                await event.delete()
                raise events.StopPropagation

# ------------------- ربط الأحداث -------------------
def setup(client):
    client.add_event_handler(developer_info)
    client.add_event_handler(callback_handler)
    client.add_event_handler(block_check)
