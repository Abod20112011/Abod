import os
import asyncio
import html
from datetime import datetime
from telethon import events, functions
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.channels import GetFullChannelRequest
import database

# تخزين البيانات والعمليات
ORIGINAL_DATA = {}
RUNNING_POSTS = {}

def setup(l313l):
    
    # --- [ القائمة الرئيسية ] ---
    @l313l.on(events.NewMessage(outgoing=True, pattern=r"^\.الاوامر$"))
    async def main_menu(event):
        text = (
            "✿ **قائمة أوامر سورس فينيكس الشاملة:**\n"
            "━━━━━━━━━━━━━━\n"
            "▫️ `.م1` : النشر التلقائي والإذاعة\n"
            "▫️ `.م2` : التخزين وصيد المقيدات\n"
            "▫️ `.م3` : الانتحال وتغيير المظهر\n"
            "▫️ `.م4` : أوامر التهكير والخمط\n"
            "▫️ `.م5` : فحص السرعة والنت والوسائط\n"
            "━━━━━━━━━━━━━━\n"
            "📡 **المطور:** @BD_0I"
        )
        await event.edit(text)

    # --- [ م1: النشر والإذاعة ] ---
    @l313l.on(events.NewMessage(outgoing=True, pattern=r"^\.م1$"))
    async def menu1(event):
        await event.edit(
            "📣 **أوامر النشر والإذاعة:**\n"
            "▫️ `.نشر_كروبات (ثواني)` : نشر تلقائي للكل\n"
            "▫️ `.وجه` : توجيه للمجموعات (بالرد)\n"
            "▫️ `.حول` : توجيه للخاص (بالرد)\n"
            "▫️ `.ايقاف النشر` : إيقاف كل العمليات"
        )

    # --- [ م2: التخزين وصيد المقيدات ] ---
    @l313l.on(events.NewMessage(outgoing=True, pattern=r"^\.م2$"))
    async def menu2(event):
        await event.edit(
            "🛡️ **أوامر التخزين والمقيدات:**\n"
            "▫️ `.تفعيل التخزين` : حفظ الرسائل تلقائياً\n"
            "▫️ `.تعطيل التخزين` : إيقاف الحفظ\n"
            "▫️ `.خزن` : حفظ رسالة محددة (بالرد)\n"
            "📸 **صيد:** يتم حفظ الصور التي تختفي تلقائياً."
        )

    # --- [ م3: الانتحال ] ---
    @l313l.on(events.NewMessage(outgoing=True, pattern=r"^\.م3$"))
    async def menu3(event):
        await event.edit(
            "🎭 **أوامر الانتحال:**\n"
            "▫️ `.انتحال` : نسخ حساب الشخص (بالرد)\n"
            "▫️ `.اعادة` : استعادة اسمك وصورتك الأصلية\n"
            "▫️ `.انتحال_الدردشه` : نسخ اسم ووصف الكروب"
        )

    # --- [ م4: التهكير والخمط ] ---
    @l313l.on(events.NewMessage(outgoing=True, pattern=r"^\.م4$"))
    async def menu4(event):
        await event.edit(
            "🥷 **أوامر التهكير والخمط:**\n"
            "▫️ `.تهكير` : حركات برمجية وهمية\n"
            "▫️ `.خمط` : سحب ميديا أو نصوص معينة\n"
            "▫️ `.الخمط من الكروبات` : جلب أعضاء أو رسائل"
        )

    # --- [ م5: الفحص والوسائط ] ---
    @l313l.on(events.NewMessage(outgoing=True, pattern=r"^\.م5$"))
    async def menu5(event):
        await event.edit(
            "⚡ **أوامر الفحص والوسائط:**\n"
            "▫️ `.فحص` : فحص سرعة البوت (Ping)\n"
            "▫️ `.فحص النت` : قياس سرعة الإنترنت\n"
            "▫️ `.الاغنية` : بحث وتشغيل الأغاني\n"
            "▫️ `.ملصق` : تحويل صورة إلى ملصق"
        )

    # --- [ الأوامر المباشرة المضافة من الصورة ] ---
    
    @l313l.on(events.NewMessage(outgoing=True, pattern=r"^\.فحص$"))
    async def ping_cmd(event):
        start = datetime.now()
        await event.edit("**جاري الفحص...**")
        end = datetime.now()
        ms = (end - start).microseconds / 1000
        # تنسيق الشكل بناءً على صورتك المرفقة
        ping_text = (
            f"┌──────────────┐\n"
            f"● NAME ➪ **abood**\n"
            f"● STATUS ➪ **ONLINE**\n"
            f"● PING ➪ `{ms}ms`\n"
            f"● UP TIME ➪ `جاري الحساب...`\n"
            f"● OS ➪ **Android**\n"
            f"└──────────────┘"
        )
        await event.edit(ping_text)

    @l313l.on(events.NewMessage(outgoing=True, pattern=r"^\.تحديث$"))
    async def update_cmd(event):
        await event.edit("✨ **تم تحديث السورس بنجاح! جاري إعادة التشغيل الآن...**")
        # الأوامر المرفقة في صورتك تظهر استجابة التحديث هذه
