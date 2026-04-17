import os
import sys
import asyncio
import subprocess
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError
from telethon import events

# --- الإعدادات الخاصة بعبود ---
GITHUB_REPO_URL = "https://github.com/Abod20112011/Abod.git"
UPSTREAM_REPO_BRANCH = "main" 

def restart_bot():
    """إعادة تشغيل البوت لتطبيق التحديثات"""
    # في الهوست، إعادة تشغيل ملف main.py يضمن تنفيذ setup.sh مجدداً
    os.execl(sys.executable, sys.executable, *sys.argv)

async def gen_chlog(repo, diff):
    """توليد سجل الملفات التي تم تغييرها في GitHub"""
    d_form = "%d/%m/%y"
    return "".join(
        f" • {c.message} [{c.author}]\n ({c.committed_datetime.strftime(d_form)})\n"
        for c in repo.iter_commits(diff)
    )

def setup(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.تحديث$"))
    async def check_update(event):
        await event.edit("**✧︙ جـاري البـحـث عـن تـحديثـات لـسـورس عـبـود...**")
        
        try:
            repo = Repo()
        except (InvalidGitRepositoryError, NoSuchPathError):
            repo = Repo.init()
            origin = repo.create_remote("upstream", GITHUB_REPO_URL)
            origin.fetch()
            repo.create_head(UPSTREAM_REPO_BRANCH, origin.refs[UPSTREAM_REPO_BRANCH])
            repo.heads[UPSTREAM_REPO_BRANCH].set_tracking_branch(origin.refs[UPSTREAM_REPO_BRANCH])
            repo.heads[UPSTREAM_REPO_BRANCH].checkout(True)
        
        try:
            ups_rem = repo.remote("upstream")
        except BaseException:
            ups_rem = repo.create_remote("upstream", GITHUB_REPO_URL)
        
        ups_rem.fetch(UPSTREAM_REPO_BRANCH)
        changelog = await gen_chlog(repo, f"HEAD..upstream/{UPSTREAM_REPO_BRANCH}")
        
        if not changelog:
            return await event.edit("**✧︙ لا توجد تحديثات جديدة حالياً، السورس محدث!**")
        
        # عرض سجل التغييرات والملفات المحدثة كما طلبت
        changelog_str = f"**✧︙ تـحديثـات جـديـدة مـتـوفـرة لـسـورس عـبـود:**\n\n{changelog}"
        changelog_str += f"\n\n**⌔ لـتـحديث الـبوت الآن ارسل:** `.تحديث الان`"
        
        await event.edit(changelog_str)

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.تحديث الان$"))
    async def perform_update(event):
        # شريط التحميل بالنسب المئوية كما طلبت
        zzz = await event.edit("ᯓ **𝗦𝗢𝗨𝗥𝗖𝗘 𝗔𝗕𝗢𝗗** 🝢 **تـحـديـث الـبـوت**\n**•─────────────────•**\n%𝟸𝟶 ▬▬▭▭▭▭▭▭▭▭")
        await asyncio.sleep(1)
        
        try:
            repo = Repo()
            ups_rem = repo.remote("upstream")
            ups_rem.fetch(UPSTREAM_REPO_BRANCH)
            
            await zzz.edit("ᯓ **𝗦𝗢𝗨𝗥𝗖𝗘 𝗔𝗕𝗢𝗗** 🝢 **تـحـديـث الـبـوت**\n**•─────────────────•**\n%𝟻𝟶 ▬▬▬▬▬▭▭▭▭▭")
            
            # تحديث الملفات إجبارياً لمطابقة GitHub
            repo.git.reset("--hard", f"upstream/{UPSTREAM_REPO_BRANCH}")
            
            await zzz.edit("ᯓ **𝗦𝗢𝗨𝗥𝗖𝗘 𝗔𝗕𝗢𝗗** 🝢 **تـحـديـث الـبـوت**\n**•─────────────────•**\n%𝟾𝟶 ▬▬▬▬▬▬▬▬▭▭")
            
            # تحديث المكاتب إذا وجد ملف requirements.txt
            if os.path.exists("requirements.txt"):
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            
            await zzz.edit("ᯓ **𝗦𝗢𝗨𝗥𝗖𝗘 𝗔𝗕𝗢𝗗** 🝢 **تـحـديـث الـبـوت**\n**•─────────────────•**\n%𝟷𝟶𝟶 ▬▬▬▬▬▬▬▬▬▬💯")
            await asyncio.sleep(1)
            
            await event.edit("**✨ تـم تـحديث سـورس عـبـود بـنـجاح! جـاري إعـادة الـتشغـيل...**")
            await asyncio.sleep(2)
            restart_bot()
            
        except Exception as e:
            await event.edit(f"❌ **حدث خطأ أثناء التحديث:**\n`{str(e)}`")

    print(f"✅ تم تحميل موديول التحديث المتطور بنجاح.")
