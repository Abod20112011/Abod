import asyncio
import os
import pytz
import urllib.request
from datetime import datetime
from telethon import events, functions, types

# إعداد توقيت العراق
def get_iraq_time():
    return datetime.now(pytz.timezone('Asia/Baghdad')).strftime('%I:%M %p')

# رابط الصورة الموحد
STORAGE_PHOTO = "https://files.catbox.moe/k4fxu0.jpg"

# ذاكرة مؤقتة لمنع تكرار كليشة معلومات المستخدم في الخاص
PM_SESSIONS = set()

def setup(l313l):
    # --- 1. أمر التفعيل ---
    @l313l.on(events.NewMessage(outgoing=True, pattern=r"^\.تفعيل التخزين$"))
    async def enable(event):
        import database
        if not event.is_group:
            return await event.edit("⚠️ **يجب تفعيل التخزين داخل المجموعة المراد التخزين فيها.**")
        
        chat_id = event.chat_id
        database.set_config("STORAGE_CHAT_ID", str(chat_id))
        database.set_config("STORAGE_MASTER", "on")
        
        await event.edit("⏳ **جاري التفعيل وضبط الإعدادات...**")
        
        # حل مشكلة الصورة: تحميلها ثم رفعها لتجنب خطأ No such file
        local_path = "temp_storage_photo.jpg"
        try:
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            urllib.request.install_opener(opener)
            urllib.request.urlretrieve(STORAGE_PHOTO, local_path)
            
            await event.client(functions.channels.EditPhotoRequest(
                channel=chat_id,
                photo=await event.client.upload_file(local_path)
            ))
            if os.path.exists(local_path):
                os.remove(local_path)
        except Exception as e:
            print(f"Photo Error: {e}")
            
        await event.edit("✅ **تم تفعيل نظام التخزين بنجاح!**\nسيتم إرسال التاكات، وبداية محادثات الخاص، والتعديلات هنا.")

    @l313l.on(events.NewMessage(outgoing=True, pattern=r"^\.تعطيل التخزين$"))
    async def disable(event):
        import database
        database.set_config("STORAGE_MASTER", "off")
        PM_SESSIONS.clear()
        await event.edit("❌ **تم تعطيل نظام التخزين بالكامل.**")

    # --- 2. محرك صيد الرسائل والتاكات ---
    @l313l.on(events.NewMessage(incoming=True))
    async def handler(event):
        import database
        is_on = database.get_config("STORAGE_MASTER")
        storage_id = database.get_config("STORAGE_CHAT_ID")
        
        if is_on != "on" or not storage_id or event.out:
            return

        try:
            storage_id = int(storage_id)
            if event.chat_id == storage_id:
                return

            sender = await event.get_sender()
            name = getattr(sender, 'first_name', 'مستخدم مخفي')
            
            # أ. تخزين الخاص (الكليشة مرة واحدة فقط لكل مستخدم)
            if event.is_private:
                if event.sender_id not in PM_SESSIONS:
                    info_text = (
                        f"👤 **محادثة جديدة في الخاص**\n"
                        f"⌔┊المرسل : **{name}**\n"
                        f"⌔┊الايدي : `{event.sender_id}`\n"
                        f"⏰┊الوقت : {get_iraq_time()}"
                    )
                    await event.client.send_message(storage_id, info_text)
                    PM_SESSIONS.add(event.sender_id)
                
                # توجيه الرسالة فوراً
                await event.client.forward_messages(storage_id, event.message)

            # ب. تخزين التاكات (المنشن)
            elif event.mentioned:
                chat = await event.get_chat()
                chat_title = getattr(chat, 'title', 'مجموعة غير معروفة')
                msg_link = f"https://t.me/c/{str(event.chat_id).replace('-100', '')}/{event.id}"
                
                tag_text = (
                    f"📌 **#تاك_جديد**\n"
                    f"⌔┊المجموعة : **{chat_title}**\n"
                    f"⌔┊المرسل : **{name}**\n"
                    f"⌔┊الرسالة : {event.text or 'وسائط'}\n"
                    f"🔗┊الرابط : [اضغط هنا]({msg_link})\n"
                    f"⏰┊الوقت : {get_iraq_time()}"
                )
                await event.client.send_message(storage_id, tag_text, link_preview=False)
        except: pass

    # --- 3. كاشف تعديل الرسائل ---
    @l313l.on(events.MessageEdited(incoming=True))
    async def edit_logger(event):
        import database
        is_on = database.get_config("STORAGE_MASTER")
        storage_id = database.get_config("STORAGE_CHAT_ID")
        
        if is_on != "on" or not storage_id or event.out:
            return
            
        try:
            storage_id = int(storage_id)
            if event.chat_id == storage_id:
                return

            sender = await event.get_sender()
            name = getattr(sender, 'first_name', 'مستخدم مخفي')
            
            old_message = getattr(event, 'old_message', None)
            old_text = old_message.text if old_message and old_message.text else "غير محفوظة"
            new_text = event.text if event.text else "وسائط"

            if old_text == new_text and old_text != "غير محفوظة":
                return

            edit_text = (
                f"⚠️ **تعديل رسالة!**\n"
                f"⌔┊المرسل : **{name}**\n"
                f"⌔┊قبل : `{old_text}`\n"
                f"⌔┊بعد : `{new_text}`\n"
                f"⏰┊الوقت : {get_iraq_time()}"
            )
            await event.client.send_message(storage_id, edit_text)
        except: pass
