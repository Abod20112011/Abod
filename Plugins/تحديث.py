import os
import sys
import asyncio
import subprocess
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError
from telethon import events

# --- الإعدادات ---
GITHUB_REPO_URL = "https://github.com/Abod20112011/Abod.git"
UPSTREAM_REPO_BRANCH = "main"  # تأكد أنه main في مستودعك

def restart_bot():
    """إعادة تشغيل البوت بالكامل"""
    os.execl(sys.executable, sys.executable, *sys.argv)

async def gen_chlog(repo, diff):
    """توليد سجل التغييرات (الملفات المحدثة)"""
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
        
        changelog_str = f"**✧︙ تـحديثـات جـديـدة مـتـوفـرة لـسـورس عـبـود:**\n\n{changelog}"
        changelog_str += f"\n\n**⌔ لـتـحديث الـبوت الآن ارسل:** `.تحديث الان`"
        
        await event.edit(changelog_str)

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.تحديث الان$"))
    async def perform_update(event):
        await event.edit("ᯓ **𝗦𝗢𝗨𝗥𝗖𝗘 𝗔𝗕𝗢𝗗** 🝢 **تـحـديـث الـبـوت**\n%𝟸𝟶 ▬▬▭▭▭▭▭▭▭▭")
        await asyncio.sleep(1)
        
        try:
            repo = Repo()
            ups_rem = repo.remote("upstream")
            ups_rem.fetch(UPSTREAM_REPO_BRANCH)
            
            await event.edit("ᯓ **𝗦𝗢𝗨𝗥𝗖𝗘 𝗔𝗕𝗢𝗗** 🝢 **تـحـديـث الـبـوت**\n%𝟻𝟶 ▬▬▬▬▬▭▭▭▭▭")
            
            # السحب الإجباري للتحديثات
            repo.git.reset("--hard", f"upstream/{UPSTREAM_REPO_BRANCH}")
            
            await event.edit("ᯓ **𝗦𝗢𝗨𝗥𝗖𝗘 𝗔𝗕𝗢𝗗** 🝢 **تـحـديـث الـبـوت**\n%𝟾𝟶 ▬▬▬▬▬▬▬▬▭▭")
            
            # تحديث المكاتب إذا وجد ملف requirements
            if os.path.exists("requirements.txt"):
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            
            await event.edit("ᯓ **𝗦𝗢𝗨𝗥𝗖𝗘 𝗔𝗕𝗢𝗗** 🝢 **تـحـديـث الـبـوت**\n%𝟷𝟶𝟶 ▬▬▬▬▬▬▬▬▬▬💯")
            await asyncio.sleep(1)
            
            await event.edit("**✨ تـم تـحديث سـورس عـبـود بـنـجاح! جـاري إعـادة الـتشغـيل...**")
            await asyncio.sleep(2)
            restart_bot()
            
        except Exception as e:
            await event.edit(f"❌ **حدث خطأ أثناء التحديث:**\n`{str(e)}`")

    print(f"✅ تم تحميل موديول التحديث المتطور بنجاح.")
