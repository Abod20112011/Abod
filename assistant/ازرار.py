# -*- coding: utf-8 -*-
# assistant/bot_utils.py
# إرسال الأزرار الملونة عبر Bot API مع حماية المطور

import json
import logging
import requests
from telethon import events

# الوصول إلى دوال السورس الرئيسي
import sys
main_module = sys.modules.get('__main__')
if main_module:
    get_config = main_module.get_config
    OWNER_ID = main_module.OWNER_ID
else:
    def get_config(key): return None
    OWNER_ID = 6373993992

LOGGER = logging.getLogger(__name__)

# ------------------- دوال الإرسال الأساسية -------------------
def send_message_with_buttons(chat_id, text, buttons):
    """
    ترسل رسالة نصية مع أزرار ملونة.
    buttons: قائمة صفوف، كل صف قائمة من الأزرار.
    مثال للزر:
        {"text": "نص", "callback_data": "بيانات", "style": "primary"}
    الألوان: primary (أزرق), success (أخضر), danger (أحمر)
    """
    token = get_config("TOKEN")
    if not token:
        LOGGER.error("❌ التوكن غير موجود في القاعدة.")
        return None

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    keyboard = {"inline_keyboard": buttons}
    payload = {
        "chat_id": chat_id,
        "text": text,
        "reply_markup": json.dumps(keyboard),
        "parse_mode": "HTML"
    }
    try:
        resp = requests.post(url, json=payload, timeout=5)
        return resp.json()
    except Exception as e:
        LOGGER.error(f"❌ خطأ في إرسال الأزرار: {e}")
        return None

def send_photo_with_buttons(chat_id, photo_url, caption, buttons):
    """ترسل صورة (رابط) مع أزرار ملونة."""
    token = get_config("TOKEN")
    if not token:
        return None
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    keyboard = {"inline_keyboard": buttons}
    payload = {
        "chat_id": chat_id,
        "photo": photo_url,
        "caption": caption,
        "reply_markup": json.dumps(keyboard),
        "parse_mode": "HTML"
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        return resp.json()
    except Exception as e:
        LOGGER.error(f"❌ خطأ في إرسال الصورة مع الأزرار: {e}")
        return None

# ------------------- دالة مساعدة للاستدعاء من Plugins -------------------
async def send_colored_buttons_example(client, chat_id):
    """
    مثال: إرسال رسالة ترحيب مع ثلاثة أزرار ملونة.
    يمكنك استدعاء هذه الدالة من أي أمر في Plugins.
    """
    text = (
        "✨ <b>مرحباً بك في نظام الأزرار الملونة!</b>\n"
        "اختر أحد الأزرار أدناه:"
    )
    buttons = [
        [{"text": "🔵 زر أزرق (primary)", "callback_data": "btn_primary", "style": "primary"}],
        [{"text": "🟢 زر أخضر (success)", "callback_data": "btn_success", "style": "success"}],
        [{"text": "🔴 زر أحمر (danger)", "callback_data": "btn_danger", "style": "danger"}]
    ]
    send_message_with_buttons(chat_id, text, buttons)

# ------------------- معالج CallbackQuery المحمي (للمطور فقط) -------------------
def setup(client):
    @client.on(events.CallbackQuery())
    async def callback_handler(event):
        data = event.data.decode()
        user_id = event.query.user_id

        # 🔒 حماية: المطور فقط
        if user_id != OWNER_ID:
            await event.answer("🚫 هذا الزر مخصص للمطور فقط.", alert=True)
            return

        # معالجة الأزرار المختلفة
        if data == "btn_primary":
            await event.answer("✅ ضغطت الزر الأزرق (primary)!", alert=True)
            await event.edit("تم اختيار <b>الزر الأزرق</b>.", parse_mode="html", buttons=None)
        elif data == "btn_success":
            await event.answer("✅ ضغطت الزر الأخضر (success)!", alert=False)
            await event.edit("تم اختيار <b>الزر الأخضر</b>.", parse_mode="html", buttons=None)
        elif data == "btn_danger":
            await event.answer("⚠️ ضغطت الزر الأحمر (danger)!", alert=True)
            await event.edit("تم اختيار <b>الزر الأحمر</b>.", parse_mode="html", buttons=None)
        else:
            await event.answer("بيانات غير معروفة.", alert=True)

    LOGGER.info("✅ bot_utils: تم تحميل معالج CallbackQuery المحمي.")
