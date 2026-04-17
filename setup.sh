#!/bin/bash

# ألوان للتنسيق
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🌀 جاري بدء تنصيب سورس عبود...${NC}"

# 1. تحديث النظام وتنصيب المتطلبات الأساسية
echo -e "${GREEN}📦 تحديث البكجات وتنصيب المتطلبات (Python, Git)...${NC}"
if [ -d "/data/data/com.termux/files/usr/bin" ]; then
    # إذا كان الجهاز تيرمكس
    pkg update -y && pkg upgrade -y
    pkg install python git -y
else
    # إذا كان الجهاز سيرفر Linux/Host
    sudo apt update && sudo apt upgrade -y
    sudo apt install python3 python3-pip git -y
fi

# 2. سحب السورس من GitHub
echo -e "${GREEN}📥 جاري سحب ملفات السورس من GitHub...${NC}"
if [ -d "Abod" ]; then
    cd Abod
    git pull
else
    git clone https://github.com/Abod20112011/Abod.git
    cd Abod
fi

# 3. تنصيب المكاتب البرمجية
echo -e "${GREEN}📚 جاري تنصيب المكاتب (Requirements)...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    # تنصيب المكاتب الأساسية إذا لم يوجد ملف requirements
    pip install telethon sqlalchemy pytz psycopg2-binary
fi

# 4. تشغيل السورس
echo -e "${BLUE}🚀 تم التنصيب بنجاح! جاري تشغيل السورس الآن...${NC}"
python3 main.py
