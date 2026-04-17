# تهكير.py
import asyncio
import random
from telethon import events

def setup(cli):
    
    @cli.on(events.NewMessage(outgoing=True, pattern=r'\.تهكير$'))
    async def hack_cmd(event):
        """تهكير بالرد على الرسالة"""
        reply = await event.get_reply_message()
        
        if not reply:
            await event.edit("᯽︙ يرجى الرد على الشخص الذي تريد تهكيرـه!")
            return
        
        await event.edit("يتـم الاختـراق ..")
        animation_chars = [
            "᯽︙ تـم الربـط بسـيرفرات الـتهكير الخـاصة",
            "تـم تحـديد الضحـية",
            "**تهكيـر**... 0%\n▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ ",
            "**تهكيـر**... 4%\n█▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ ",
            "**تهكيـر**... 8%\n██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ ",
            "**تهكيـر**... 20%\n█████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ ",
            "**تهكيـر**... 36%\n█████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ ",
            "**تهكيـر**... 52%\n█████████████▒▒▒▒▒▒▒▒▒▒▒▒ ",
            "**تهكيـر**... 84%\n█████████████████████▒▒▒▒ ",
            "**تهكيـر**... 100%\n████████████████████████ ",
            "᯽︙ ** تـم اخـتراق الضـحية**..\n\n⚠️ تم سحب جميع بياناتك السرية!",
        ]
        
        for i in range(11):
            await asyncio.sleep(3)
            await event.edit(animation_chars[i])

    @cli.on(events.NewMessage(outgoing=True, pattern=r'\.تهكير2$'))
    async def hack2_cmd(event):
        """تهكير متطور مع محاكاة هاكر"""
        if event.fwd_from:
            return

        # المرحلة الأولى: محاكاة الاختراق
        await event.edit("**جارِ الاختراق الضحية..**")
        
        phase1_chars = [
            "**جار تحديد الضحية...**",
            "**تم تحديد الضحية بنجاح ✓**",
            "`يتم الاختراق... 0%\n▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `",
            "`يتم الاختراق... 4%\n█▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `",
            "`يتم الاختراق... 8%\n██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `",    
            "`يتم الاختراق... 20%\n█████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `",
            "`يتم الاختراق... 36%\n█████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `",
            "`يتم الاختراق... 52%\n█████████████▒▒▒▒▒▒▒▒▒▒▒▒ `",
            "`يتم الاختراق... 84%\n█████████████████████▒▒▒▒ `",
            "`يتم الاختراق... 100%\n████████████████████████ `",
            "` تم رفع معلومات الشخص...\n\nسيتم ربط المعلومات بسيرفرات التهكير الخاصه..`"
        ]

        for char in phase1_chars:
            await asyncio.sleep(3)
            await event.edit(char)

        await asyncio.sleep(2)

        # المرحلة الثانية: محاكاة Terminal فقط لحد ls
        await event.edit("**يتم الاتصال لسحب التوكن الخاص به عبر موقع.telegram.org**")
        await asyncio.sleep(1)
        
        # هذه فقط المرحلة الأولى من Terminal
        terminal_stage1 = [
            "`root@anon:~#` ",
            "`root@anon:~# ls`",
            "`root@anon:~# ls\n\n  usr  ghost  codes  \n\nroot@aono:~#`",
            "`root@anon:~# ls\n\n  usr  ghost  codes  \n\nroot@aono:~# # So Let's Hack it ...`",
            "`root@anon:~# ls\n\n  usr  ghost  codes  \n\nroot@aono:~# # So Let's Hack it ...\nroot@anon:~# `",
            "`root@anon:~# ls\n\n  usr  ghost  codes  \n\nroot@aono:~# # So Let's Hack it ...\nroot@anon:~# touch setup.py`",
            "`root@anon:~# ls\n\n  usr  ghost  codes  \n\nroot@aono:~# # So Let's Hack it ...\nroot@anon:~# touch setup.py\n\nsetup.py deployed ...`",
            "`root@anon:~# ls\n\n  usr  ghost  codes  \n\nroot@aono:~# # So Let's Hack it ...\nroot@anon:~# touch setup.py\n\nsetup.py deployed ...\nيتم الان الرفع عبر CMD تلقائياً ...`",
        ]

        for char in terminal_stage1:
            await asyncio.sleep(1)
            await event.edit(char)
        
        await asyncio.sleep(2)

        # الأن نرسل رسالة جديدة للمرحلة الثانية
        msg2 = await event.respond("**↻ يستمر الاختراق...**")
        
        # المرحلة الثانية في رسالة جديدة
        terminal_stage2 = [
            "`root@anon:~# ls\n\n  usr  ghost  codes  \n\nroot@aono:~# # So Let's Hack it ...\nroot@anon:~# touch setup.py\n\nsetup.py deployed ...\nيتم الان الرفع عبر CMD تلقائياً ...\n\nroot@anon:~# trap whoami`",
            "`root@anon:~# ls\n\n  usr  ghost  codes  \n\nroot@aono:~# # So Let's Hack it ...\nroot@anon:~# touch setup.py\n\nsetup.py deployed ...\nيتم الان الرفع عبر CMD تلقائياً ...\n\nroot@anon:~# trap whoami\n\nwhoami=user`",
            "`root@anon:~# ls\n\n  usr  ghost  codes  \n\nroot@aono:~# # So Let's Hack it ...\nroot@anon:~# touch setup.py\n\nsetup.py deployed ...\nيتم الان الرفع عبر CMD تلقائياً ...\n\nroot@anon:~# trap whoami\n\nwhoami=user\nboost_trap on force ...`",
            "`root@anon:~# ls\n\n  usr  ghost  codes  \n\nroot@aono:~# # So Let's Hack it ...\nroot@anon:~# touch setup.py\n\nsetup.py deployed ...\nيتم الان الرفع عبر CMD تلقائياً ...\n\nroot@anon:~# trap whoami\n\nwhoami=user\nboost_trap on force ...\nvictim detected in ghost ...`",
            "`root@anon:~# ls\n\n  usr  ghost  codes  \n\nroot@aono:~# # So Let's Hack it ...\nroot@anon:~# touch setup.py\n\nsetup.py deployed ...\nيتم الان الرفع عبر CMD تلقائياً ...\n\nroot@anon:~# trap whoami\n\nwhoami=user\nboost_trap on force ...\nvictim detected in ghost ...\n\nتم اكتمال العملية ✓!`",
            "`root@anon:~# ls\n\n  usr  ghost  codes  \n\nroot@aono:~# # So Let's Hack it ...\nroot@anon:~# touch setup.py\n\nsetup.py deployed ...\nيتم الان الرفع عبر CMD تلقائياً ...\n\nroot@anon:~# trap whoami\n\nwhoami=user\nboost_trap on force ...\nvictim detected  in ghost ...\n\nتم اكتمال العملية ✓!\nيتم الان استخراج توكن الضحية!\nToken=`[معلومات مشفرة]`",
        ]

        for char in terminal_stage2:
            await asyncio.sleep(1)
            await msg2.edit(char)
        
        await asyncio.sleep(2)

        # المرحلة الثالثة: عملية سحب البيانات في رسالة ثالثة
        msg3 = await event.respond("**📁 يتم استخراج البيانات...**")
        
        progress_messages = [
            ("`يتم سحب الصور والمعلومات...\n 0%completed.\nTERMINAL:\nDownloading Bruteforce-Telegram-0.1.tar.gz (1.3) kB`", 2),
            ("`يتم سحب الصور والمعلومات...\n 4% completed\n TERMINAL:\nDownloading Bruteforce-Telegram-0.1.tar.gz (9.3 kB)\nCollecting Data Package`", 1),
            ("`يتم سحب الصور والمعلومات...\n 6% completed\n TERMINAL:\nDownloading Bruteforce-Telegram-0.1.tar.gz (9.3 kB)\nCollecting Data Packageseeing target account chat\n lding chat tg-bot bruteforce finished`", 2),
            ("`يتم سحب الصور والمعلومات....\n 8%completed\n TERMINAL:\nDownloading Bruteforce-Telegram-0.1.tar.gz (9.3 kB)\nCollecting Data Packageseeing target account chat\n lding chat tg-bot bruteforce finished\n creating pdf of chat`", 1),
            ("`يتم سحب الصور والمعلومات...\n 15%completed\n Terminal:chat history from telegram exporting to private database.\n terminal 874379gvrfghhuu5tlotruhi5rbh installing`", 2),
            ("`يتم سحب الصور والمعلومات...\n 24%completed\n TERMINAL:\nDownloading Bruteforce-Telegram-0.1.tar.gz (9.3 kB)\nCollecting Data Packageseeing target account chat\n lding chat tg-bot bruteforce finished\nerminal:chat history from telegram exporting to private database.\n terminal 874379gvrfghhuu5tlotruhi5rbh installed\n creting data into pdf`", 2),
            ("`يتم سحب الصور والمعلومات...\n 32%completed\n looking for use history \n downloading-telegram -id prtggtgf . gfr (12.99 mb)\n collecting data starting imprute attack to user account\n chat history from telegram exporting to private database.\n terminal 874379gvrfghhuu5tlotruhi5rbh installed\n creted data into pdf\nDownload sucessful Bruteforce-Telegram-0.1.tar.gz (1.3)`", 1),
            ("`يتم سحب الصور والمعلومات...\n 38%completed\n\nDownloading Bruteforce-Telegram-0.1.tar.gz (9.3 kB)\nCollecting Data Package\n  Downloading Telegram-Data-Sniffer-7.1.1-py2.py3-none-any.whl (82 kB): finished with status 'done'\nCreated wheel for telegram: filename=Telegram-Data-Sniffer-0.0.1-py3-none-any.whl size=1306 sha256=cb224caad7fe01a6649188c62303cd4697c1869fa12d280570bb6ac6a88e6b7e`", 2),
            ("`100%\n█████████████████████████ `\n\n\n  TERMINAL:\nيتم تنزيل Bruteforce-Telegram-0.1.tar.gz (9.3 kB)\nCollecting Data Package\n  يتم تنزيل Telegram-Data-Sniffer-7.1.1-py2.py3-none-any.whl (82 kB)\nBuilding wheel for Tg-Bruteforcing (setup.py): finished with status 'done'\nCreated wheel for telegram: filename=Telegram-Data-Sniffer-0.0.1-py3-none-any.whl size=1306 sha256=cb224caad7fe01a6649188c62303cd4697c1869fa12d280570bb6ac6a88e6b7e\n  Stored in directory: `", 5),
            ("`✅ تم سحب جميع معلومات الحساب بنجاح!\n\n⚠️ تم استخراج:\n- جميع الصور\n- المحادثات\n- جهات الاتصال\n- التوكنات\n- المعلومات الشخصية`", 5),
        ]

        for msg, delay in progress_messages:
            await msg3.edit(msg)
            await asyncio.sleep(delay)

        # المرحلة الأخيرة: رابط عشوائي
        h = random.randint(1, 5)
        links = {
            1: "دحماس",
            2: "حسنان",
            3: "حبيطي",
            4: "فاينل القوي",
            5: "سلبوح العراقي"
        }
        
        final_msg = f"`📂 تم رفع جميع البيانات في مجلد PDF\n\n😂 لا تقلق انا فقط من أرئ معلوماتك 😎😎\n\nاذا لم تصدق ادخل الى هذا الرابط وانظر بنفسك:`\n\n🔗 {links[h]}"
        await msg3.edit(final_msg)

    @cli.on(events.NewMessage(outgoing=True, pattern=r'\.مساعده$'))
    async def help_cmd(event):
        """عرض أوامر التهكير"""
        help_text = """
        **🎮 أوامر التهكير للتسلية:**
        
        `.تهكير` - مع الرد على رسالة للشخص
        `.تهكير2` - تهكير متطور مع محاكاة هاكر كاملة
        
        **⚠️ ملاحظة:** هذه الأوامر للتسلية فقط ولا تقوم باختراق حقيقي!
        """
        await event.edit(help_text)