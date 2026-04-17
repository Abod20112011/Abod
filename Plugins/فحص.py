import platform, sys, os
from datetime import datetime
from telethon import events

# وقت بداية التشغيل
START_TIME = datetime.now()

def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "d"]
    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0: break
        time_list.append(int(result))
        seconds = int(remainder)
    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4: ping_time += time_list.pop() + ", "
    time_list.reverse()
    ping_time += ":".join(time_list)
    return ping_time

def setup(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.فحص$"))
    async def alive_check(event):
        start = datetime.now()
        await event.edit("⏳")
        end = datetime.now()
        ms = (end - start).microseconds / 1000
        uptime = get_readable_time((datetime.now() - START_TIME).total_seconds())
        me = await event.client.get_me()
        
        check_msg = (
            "┌───────────────────┐\n"
            f" ● NAME ⇨ {me.first_name}\n"
            f" ● STATUS ⇨ ONLINE\n"
            f" ● PING ⇨ {ms}ms\n"
            f" ● UP TIME ⇨ {uptime}\n"
            f" ● OS ⇨ {platform.system()}\n"
            "└───────────────────┘"
        )
        await event.edit(check_msg)
