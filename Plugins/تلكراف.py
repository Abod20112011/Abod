import os
import requests
from datetime import datetime
from PIL import Image
from telethon import events
import database

# إعدادات الفئات والحقوق
plugin_category = "utils"

def resize_image(image):
    im = Image.open(image)
    im.save(image, "PNG")

# --- دالة الرفع الشاملة (تليجراف + جراف + كاتبوكس) ---
def upload_to_cloud(file_path):
    # 1. Telegra.ph
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        with open(file_path, 'rb') as f:
            response = requests.post(
                "https://telegra.ph/upload",
                files={'file': ('file', f, 'image/jpeg')},
                headers=headers,
                timeout=5
            )
        if response.status_code == 200 and isinstance(response.json(), list):
            return "https://telegra.ph" + response.json()[0]['src']
    except:
        pass

    # 2. Catbox.moe (المنقذ الدائم)
    try:
        with open(file_path, 'rb') as f:
            response = requests.post(
                "https://catbox.moe/user/api.php",
                data={"reqtype": "fileupload"},
                files={"fileToUpload": f},
                timeout=20
            )
        if response.status_code == 200:
            return response.text.strip()
    except:
        return None

def setup(l313l):
    @l313l.on(events.NewMessage(outgoing=True, pattern=r"^\.تلكراف (ميديا|نص)$"))
    async def telegraph_upload(event):
        # تحديث الإحصائيات في قاعدة البيانات
        database.update_stats("تلكراف")
        
        input_str = event.pattern_match.group(1)
        reply = await event.get_reply_message()
        
        if not reply:
            return await event.edit("` ⌔︙قـم بالـرد عـلى صـورة أولاً!`")

        if input_str == "ميديا":
            msg = await event.edit("` ⌔︙جـار الرفـع (محاولة عدة سيرفرات)...`")
            start = datetime.now()
            
            # تحميل الميديا مؤقتاً
            media = await event.client.download_media(reply)
            
            if not media:
                return await msg.edit("` ⌔︙فشل تحميل الميديا من سيرفرات التيليجرام!`")

            if media.endswith((".webp", ".png", ".jpg", ".jpeg")):
                # استخدام الدالة الذكية للرفع
                media_url = upload_to_cloud(media)
                
                if media_url:
                    end = datetime.now()
                    ms = (end - start).seconds
                    res_text = (
                        f"** ⌔︙تـم الـرفـع بـنجـاح ✅**\n"
                        f"** ⌔︙الـرابـط : ** [إضـغط هنـا]({media_url})\n"
                        f"** ⌔︙الرابط الخام : ** `{media_url}`\n"
                        f"** ⌔︙الوقـت : ** `{ms} ثانية`"
                    )
                    await msg.edit(res_text, link_preview=False)
                else:
                    await msg.edit("** ⌔︙فشل الرفع على جميع السيرفرات!**")
            else:
                await msg.edit("` ⌔︙عذراً، هذا النوع من الملفات غير مدعوم للرفع.`")
            
            # تنظيف الملفات المؤقتة
            if os.path.exists(media):
                os.remove(media)

        elif input_str == "نص":
            await event.edit("`⌔︙الرفع النصي متوقف حالياً في هذا الإصدار.`")
