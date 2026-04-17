import os
import sys
import asyncio
import subprocess
from telethon import events

# إعدادات المستودع (GitHub)
GITHUB_REPO_URL = "https://github.com/Abod20112011/Abod.git"

def restart_host():
    """إعادة تشغيل السورس لتطبيق التحديثات"""
    python = sys.executable
    os.execl(python, python, *sys.argv)

def setup(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.تحديث$"))
    async def github_update(event):
        await event.edit("🔍 **جاري فحص التحديثات من مستودع GitHub...**")
        
        try:
            # التأكد من وجود git في الجهاز
            if not os.path.exists(".git"):
                await event.edit("📦 **أول تحديث لك.. جاري تهيئة التحديث عبر GitHub...**")
                # إذا لم يكن الملف مهيأ كـ git، نقوم بعمل init و remote add
                subprocess.check_output(["git", "init"])
                subprocess.check_output(["git", "remote", "add", "origin", GITHUB_REPO_URL])
            
            await event.edit("📥 **جاري سحب الملفات الجديدة من GitHub...**")
            
            # جلب التحديثات (Fetch)
            subprocess.check_output(["git", "fetch", "--all"])
            # تصفير التغييرات المحلية لتجنب التضارب واستبدالها بالجديد (Reset)
            subprocess.check_output(["git", "reset", "--hard", "origin/main"])
            
            await event.edit("✨ **تم تحديث السورس بنجاح من GitHub!**\nجاري إعادة التشغيل لتطبيق التغييرات...")
            await asyncio.sleep(2)
            restart_host()

        except subprocess.CalledProcessError as e:
            await event.edit(f"❌ **فشل التحديث!** تأكد من تثبيت git في تيرمكس:\n`pkg install git`\nالخطأ: `{str(e)}`")
        except Exception as e:
            await event.edit(f"❌ **حدث خطأ غير متوقع:**\n`{str(e)}`")

    print(f"✅ تم تحميل موديول التحديث عبر GitHub بنجاح.")
