import asyncio
from telethon import events, functions
import database

# معرف البوت المستخدم للتحميل
DOWNLOAD_BOT = "@K0XBOT"

# ذاكرة مؤقتة لحفظ مكان طلب التحميل (لإرجاع الفيديو لنفس المحادثة)
# تم تعريفها خارج الـ setup لضمان استقرارها
last_download_chats = {}

def setup(l313l):
    # 1. أمر التحميل الرئيسي
    @l313l.on(events.NewMessage(outgoing=True, pattern=r"^\.داون (.*)"))
    async def downloader(event):
        link = event.pattern_match.group(1).strip()
        
        if not link:
            return await event.edit("**⚠️ يرجى وضع رابط مع الأمر!**")
        
        # حفظ آيدي المحادثة الحالية لإرسال الفيديو لها لاحقاً
        last_download_chats["current"] = event.chat_id
        
        # تحديث الإحصائيات
        try:
            database.update_stats("التحميل")
        except:
            pass
        
        await event.edit("⎉╎جـارِ التحميل انتظر قليلاً ▬▭")
        
        # إرسال الرابط للبوت (ستارت ثم الرابط)
        try:
            await event.client.send_message(DOWNLOAD_BOT, "/start")
            await asyncio.sleep(2)
            await event.client.send_message(DOWNLOAD_BOT, link)
        except Exception as e:
            await event.edit(f"❌ خطأ في الاتصال بالبوت: {str(e)}")

    # 2. موديول المراقبة (يحول الفيديو للمحادثة الأصلية)
    @l313l.on(events.NewMessage(incoming=True, from_users=DOWNLOAD_BOT))
    async def worker(event):
        # التأكد أن الرسالة تحتوي على ميديا (فيديو أو صور)
        if event.media:
            # جلب آيدي المحادثة التي تم طلب التحميل منها
            # إذا لم يجدها، سيرسلها للرسائل المحفوظة كخيار احتياطي
            target_chat = last_download_chats.get("current", "me")
            
            caption = "• uploader @BD_0I"
            
            try:
                # إرسال الملف للمحادثة الأصلية
                await event.client.send_file(target_chat, event.media, caption=caption)
                
                # تنظيف المحادثة مع بوت التحميل ليبقى الحساب نظيفاً
                await event.client(functions.messages.DeleteHistoryRequest(
                    peer=DOWNLOAD_BOT,
                    max_id=0,
                    just_clear=False,
                    revoke=True  # حذف من الطرفين إذا أمكن
                ))
            except Exception as e:
                # في حال فشل الإرسال للمحادثة، يرسلها للمحفوظة كـ Backup
                await event.client.send_file("me", event.media, caption=f"{caption}\n⚠️ فشل الإرسال للمجموعة: {e}")

    # 3. أمر إضافي لتنظيف الذاكرة (لوك)
    @l313l.on(events.NewMessage(outgoing=True, pattern=r"^\.لوك_داون$"))
    async def clear_dl_cache(event):
        last_download_chats.clear()
        await event.edit("✅ تم تنظيف ذاكرة التحميل بنجاح.")

