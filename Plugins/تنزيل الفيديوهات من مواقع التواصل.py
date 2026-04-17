import asyncio
from telethon import events, functions
import database

# معرف البوت المستخدم للتحميل
DOWNLOAD_BOT = "@K0XBOT"

# ذاكرة مؤقتة لحفظ آيدي المحادثة وآيدي رسالة الانتظار
dl_data = {}

def setup(l313l):
    # 1. أمر التحميل الرئيسي
    @l313l.on(events.NewMessage(outgoing=True, pattern=r"^\.داون (.*)"))
    async def downloader(event):
        link = event.pattern_match.group(1).strip()
        
        if not link:
            return await event.edit("**⚠️ يرجى وضع رابط مع الأمر!**")
        
        # تحديث الإحصائيات
        try:
            database.update_stats("التحميل")
        except:
            pass
        
        # حفظ الرسالة لحذفها لاحقاً وحفظ آيدي المحادثة
        msg = await event.edit("⎉╎جـارِ التحميل انتظر قليلاً ▬▭")
        dl_data["chat"] = event.chat_id
        dl_data["msg_id"] = msg.id
        
        # إرسال الرابط للبوت
        try:
            await event.client.send_message(DOWNLOAD_BOT, "/start")
            await asyncio.sleep(2)
            await event.client.send_message(DOWNLOAD_BOT, link)
        except Exception as e:
            await event.edit(f"❌ خطأ: {str(e)}")

    # 2. موديول المراقبة والحذف التلقائي
    @l313l.on(events.NewMessage(incoming=True, from_users=DOWNLOAD_BOT))
    async def worker(event):
        if event.media:
            # جلب البيانات من الذاكرة
            target_chat = dl_data.get("chat", "me")
            old_msg_id = dl_data.get("msg_id")
            
            caption = "• uploader @BD_0I"
            
            try:
                # أ: حذف الرسالة القديمة "جارِ التحميل"
                if old_msg_id:
                    await event.client.delete_messages(target_chat, old_msg_id)
                
                # ب: إرسال الفيديو للمحادثة الأصلية
                await event.client.send_file(target_chat, event.media, caption=caption)
                
                # ج: تنظيف سجل البوت
                await event.client(functions.messages.DeleteHistoryRequest(
                    peer=DOWNLOAD_BOT,
                    max_id=0,
                    just_clear=False,
                    revoke=True
                ))
                
                # مسح الذاكرة بعد الاستخدام
                dl_data.clear()
                
            except Exception as e:
                await event.client.send_file("me", event.media, caption=f"❌ خطأ أثناء الحذف/الإرسال: {e}")

