import os
from sqlalchemy import create_engine, Column, String, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# إعداد قاعدة البيانات (تستخدم SQLite افتراضياً في تيرمكس)
DB_URL = os.getenv("DATABASE_URL", "sqlite:///phoenix.db")
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# --- تعريف الجداول ---

class Config(Base):
    __tablename__ = "config"
    variable = Column(String(255), primary_key=True)
    value = Column(String(255), nullable=False)

class MutedUsers(Base):
    __tablename__ = "muted_users"
    user_id = Column(BigInteger, primary_key=True)
    full_name = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True)

# إنشاء الجداول فور تشغيل الملف
Base.metadata.create_all(engine)

# --- دوال الإعدادات (Config) ---

def get_config(variable_name):
    """جلب إعداد معين من قاعدة البيانات"""
    res = session.query(Config).filter(Config.variable == variable_name).first()
    return res.value if res else None

def set_config(variable_name, value):
    """حفظ أو تحديث إعداد"""
    res = session.query(Config).filter(Config.variable == variable_name).first()
    if res:
        res.value = str(value)
    else:
        res = Config(variable=variable_name, value=str(value))
        session.add(res)
    session.commit()

def del_config(variable_name):
    """حذف إعداد معين"""
    res = session.query(Config).filter(Config.variable == variable_name).first()
    if res:
        session.delete(res)
        session.commit()

# --- دوال الكتم (Mute System) ---

def is_muted(user_id):
    """التحقق إذا كان المستخدم مكتوماً"""
    res = session.query(MutedUsers).filter(MutedUsers.user_id == user_id).first()
    return True if res else False

def add_muted(user_id, full_name=None, username=None):
    """إضافة مستخدم لقائمة الكتم"""
    if not is_muted(user_id):
        new_mute = MutedUsers(user_id=user_id, full_name=full_name, username=username)
        session.add(new_mute)
        session.commit()

def remove_muted(user_id):
    """إلغاء كتم مستخدم"""
    res = session.query(MutedUsers).filter(MutedUsers.user_id == user_id).first()
    if res:
        session.delete(res)
        session.commit()

def get_all_muted():
    """جلب كل المكتومين بتنسيق قابل للتفكيك (Unpacking)"""
    muted = session.query(MutedUsers).all()
    return [(user.user_id, user.full_name, user.username) for user in muted]

def clear_all_muted():
    """مسح قائمة المكتومين بالكامل"""
    session.query(MutedUsers).delete()
    session.commit()

# --- أسطر إضافية لدعم موديول التخزين المحسن ---

def is_storage_on():
    """التحقق من حالة تشغيل نظام التخزين"""
    return get_config("STORAGE_MASTER") == "on"

def get_storage_chat():
    """جلب آيدي مجموعة التخزين"""
    chat_id = get_config("STORAGE_CHAT_ID")
    return int(chat_id) if chat_id else None
