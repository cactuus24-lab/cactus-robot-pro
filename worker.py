import sqlite3
import asyncio
from telethon import TelegramClient
from datetime import datetime
import time

# بيانات الآدمن والمطور المشغلة للسيرفر وجلسات العملاء
ADMIN_API_ID = 32109331
ADMIN_API_HASH = "695c0a4d56b9663c3827451797a19eb4"

async def run_broadcaster():
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    
    c.execute("SELECT id, username, message, schedule_time, interval_hours, last_sent, status FROM schedule WHERE status IN ('نشط', 'فوري')")
    tasks = c.fetchall()
    
    for task in tasks:
        task_id, username, message, schedule_time_str, interval_hours, last_sent_str, status = task
        
        c.execute("SELECT api_id, api_hash, phone, expire_date, excluded_groups FROM users WHERE username=? AND status='مفعّل'", (username,))
        user_info = c.fetchone()
        
        if not user_info: continue
            
        api_id, api_hash, phone, expire_date_str, excluded_groups_str = user_info
        
        # مراجعة صلاحية انتهاء الاشتراك للعميل قبل البث
        if datetime.now() > datetime.strptime(expire_date_str, '%Y-%m-%d'):
            c.execute("UPDATE users SET status='منتهي الصلاحية' WHERE username=?", (username,))
            c.execute("UPDATE schedule SET status='موقوف' WHERE username=?", (username,))
            conn.commit()
            continue
            
        excluded_list = [g.strip() for g in excluded_groups_str.split(',') if g.strip()]
        should_send = False
        
        if status == 'فوري':
            should_send = True
        elif status == 'نشط':
            start_time = datetime.strptime(schedule_time_str, '%Y-%m-%d %H:%M:%S')
            last_sent = datetime.strptime(last_sent_str, '%Y-%m-%d %H:%M:%S')
            hours_since_last_send = (datetime.now() - last_sent).total_seconds() / 3600
            if datetime.now() >= start_time and hours_since_last_send >= interval_hours:
                should_send = True
                
        if should_send:
            # نستخدم بيانات ربط التليجرام الخاصة بالعميل لإتمام البث باسمه وثقة حسابة الرسمي
            client = TelegramClient(f"session_{username}", int(api_id), api_hash)
            await client.connect()
            
            if await client.is_user_authorized():
                async for dialog in client.iter_dialogs():
                    if dialog.is_group:
                        if dialog.name in excluded_list: continue # تخطي المجموعات المستبعدة
                            
                        try:
                            await client.send_message(dialog.id, message)
                            c.execute("INSERT INTO reports (username, group_name, status, date) VALUES (?, ?, 'ناجح', ?)", 
                                      (username, dialog.name, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                        except Exception:
                            c.execute("INSERT INTO reports (username, group_name, status, date) VALUES (?, ?, 'فشل', ?)", 
                                      (username, dialog.name, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                        conn.commit()
                        await asyncio.sleep(2) # تأخير ذكي لحماية كاملة ضد الحظر والسخونة للحساب
                
                if status == 'فوري':
                    c.execute("UPDATE schedule SET status='تم الإرسال الفوري' WHERE id=?", (task_id))
                else:
                    c.execute("UPDATE schedule SET last_sent=? WHERE id=?", (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), task_id))
                conn.commit()
            await client.disconnect()

if __name__ == "__main__":
    asyncio.run(run_broadcaster())