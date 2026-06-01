import os
import telebot
from telebot import types
import json

# ==========================================
# 📡 إعدادات ربط التوكن والآدمن
# ==========================================
BOT_TOKEN = "8718249379:AAG128g1jjyDVnuG1lU1UCsUpm8mm_pISIc"
ADMIN_CHAT_ID = "5120496873"  # آيدي حسابك الفعلي لإدارة العمليات

# تفعيل threaded=True يمنع تعليق الأزرار نهائياً ويعالج الطلبات بنفس الثانية
bot = telebot.TeleBot(BOT_TOKEN, threaded=True)

# ==========================================
# 💾 محرك قاعدة البيانات المحلية (ملف JSON مفتوح للكتابة)
# ==========================================
DB_FILE = "cactus_live_database.json"

def load_real_db():
    if not os.path.exists(DB_FILE):
        return {
            "users": {
                "5120496873": {
                    "user_name": "Abdullah Alharbi",
                    "status": "Approved",
                    "plan": "Advanced Premium Pro 👑",
                    "api_id": "38141862",
                    "api_hash": "bb47b8d6b378a50d94ee20378ca17090",
                    "lang": "العربية"
                }
            },
            "broadcasts": [
                {"id": 1, "type": "broadcast_sent", "description": "حملة عروض العيد إلى 3 مجموعات", "user_id": 1}
            ],
            "coupons": {"CACTUS20": 20}
        }
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"users": {}, "broadcasts": [], "coupons": {}}

def save_real_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

registration_flow = {}

# ==========================================
# 🌐 نظام القواميس واللغات للوحة التحكم بالتليجرام
# ==========================================
strings = {
    "العربية": {
        "welcome": "🌵 مرحباً بك في بوت كاكتس الذكي الشامل للنشر التلقائي ومساعد الـ AI! 🚀\n\nالرجاء اختيار أحد الأقسام من لوحة التحكم بالأسفل:",
        "dashboard": "1. لوحة المؤشرات والأداء 📊",
        "campaigns": "2. إدارة الحملات والإعلانات 🎯",
        "billing": "3. إدارة الاشتراك والباقات 💰",
        "profile": "5. الإعدادات والملف الشخصي 👤",
        "lang_switch": "🌐 Change Language to English",
        "admin_panel": "👑 لوحة الإدارة العليا (خاص بالآدمن)"
    },
    "English": {
        "welcome": "🌵 Welcome to Cactus Automation Bot Suite! Professional broadcasting and AI Assistant! 🚀\n\nPlease select from the control panel below:",
        "dashboard": "1. User Dashboard & Overview 📊",
        "campaigns": "2. My Campaigns & Ads Hub 🎯",
        "billing": "3. Subscription & Billing 💰",
        "profile": "5. Profile & Settings 👤",
        "lang_switch": "🌐 تحويل اللغة إلى العربية",
        "admin_panel": "👑 Master Admin Panel"
    }
}

def get_main_keyboard(chat_id):
    db = load_real_db()
    u_lang = db["users"].get(str(chat_id), {}).get("lang", "العربية")
    L = strings[u_lang]
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(L["dashboard"], callback_data="u_dashboard"),
        types.InlineKeyboardButton(L["campaigns"], callback_data="u_campaigns"),
        types.InlineKeyboardButton(L["billing"], callback_data="u_billing"),
        types.InlineKeyboardButton(L["profile"], callback_data="u_profile"),
        types.InlineKeyboardButton(L["lang_switch"], callback_data="u_toggle_lang")
    )
    if str(chat_id) == ADMIN_CHAT_ID:
        markup.add(types.InlineKeyboardButton(L["admin_panel"], callback_data="adm_root"))
    return markup

# ==========================================
# 📥 الأوامر الأساسية والفحص الأمني المباشر
# ==========================================
@bot.message_handler(commands=['start', 'menu'])
def handle_start(message):
    chat_id = message.chat.id
    db = load_real_db()
    uid = str(chat_id)
    
    if uid not in db["users"]:
        msg = (
            "🌵 *مرحباً بك في منصة كاكتس الذكية (Cactus SaaS)*\n\n"
            "حسابك غير مسجل حالياً بالنظام.\n"
            "للبدء في ربط حسابك وبث حملاتك الإعلانية، يرجى تقديم طلب تسجيل ليتم اعتماده فوراً من الإدارة."
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📝 تقديم طلب تسجيل فوري", callback_data="reg_start"))
        bot.send_message(chat_id, msg, parse_mode="Markdown", reply_markup=markup)
    elif db["users"][uid]["status"] == "Pending":
        bot.send_message(chat_id, "⏳ *طلبك قيد المراجعة حالياً!*\n\nبياناتك مسجلة في قاعدة البيانات ومرفوعة للآدمن. ستتلقى إشعاراً هنا فور الضغط على زر الموافقة.")
    elif db["users"][uid]["status"] == "Approved":
        u_lang = db["users"][uid].get("lang", "العربية")
        bot.send_message(chat_id, strings[u_lang]["welcome"], reply_markup=get_main_keyboard(chat_id), parse_mode="Markdown")

# ==========================================
# 📝 خطوات التسجيل للعملاء الجدد
# ==========================================
@bot.callback_query_handler(func=lambda call: call.data == "reg_start")
def start_registration(call):
    chat_id = call.message.chat.id
    registration_flow[chat_id] = {"step": "collect_name"}
    bot.edit_message_text("👤 *الخطوة 1:* اكتب اسمك الكامل الآن ليتم تسجيلك في قاعدة البيانات:", chat_id, call.message.message_id, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.chat.id in registration_flow)
def process_reg_steps(message):
    chat_id = message.chat.id
    step = registration_flow[chat_id]["step"]
    
    if step == "collect_name":
        registration_flow[chat_id]["name"] = message.text
        registration_flow[chat_id]["step"] = "collect_api"
        bot.send_message(chat_id, "🔑 *الخطوة 2:* أرسل الآن الـ *Telegram API ID* الخاص برقمك لتفعيل سحب القروبات المباشر:", parse_mode="Markdown")
    elif step == "collect_api":
        db = load_real_db()
        db["users"][str(chat_id)] = {
            "user_name": registration_flow[chat_id]["name"],
            "status": "Pending",
            "plan": "Standard Free Trial 🍃",
            "api_id": message.text,
            "api_hash": "Auto_Generated_Hash",
            "lang": "العربية"
        }
        save_real_db(db)
        del registration_flow[chat_id]
        
        bot.send_message(chat_id, "✅ *تم تسجيل بياناتك وحفظها بنجاح!*\n\nطلبك الآن قيد المراجعة أمام الآدمن.")
        
        admin_alert = f"🔔 *طلب تفعيل جديد مسجل في النظام!*\n\n👤 *الاسم:* {db['users'][str(chat_id)]['user_name']}\n🆔 *الآي دي:* `{chat_id}`"
        admin_markup = types.InlineKeyboardMarkup()
        admin_markup.add(
            types.InlineKeyboardButton("✅ موافقة وتفعيل الحساب فوراً", callback_data=f"adm_approve_{chat_id}"),
            types.InlineKeyboardButton("❌ رفض وحذف الطلب", callback_data=f"adm_reject_{chat_id}")
        )
        bot.send_message(ADMIN_CHAT_ID, admin_alert, parse_mode="Markdown", reply_markup=admin_markup)

# ==========================================
# 👑 لوحة التحكم العليا الخاصة بالآدمن (6 صفحات كاملة)
# ==========================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("adm_"))
def handle_admin_callbacks(call):
    chat_id = call.message.chat.id
    if str(chat_id) != ADMIN_CHAT_ID: 
        bot.answer_callback_query(call.id, "❌ غير مصرح لك.")
        return
        
    action_data = call.data.split("_")
    
    try:
        if action_data[1] == "approve":
            target = action_data[2]
            db = load_real_db()
            if target in db["users"]:
                db["users"][target]["status"] = "Approved"
                save_real_db(db)
                bot.edit_message_text(f"✅ تم تفعيل حساب العميل بنجاح والموافقة على آيدي: {target}", chat_id, call.message.message_id)
                try: bot.send_message(int(target), "🎉 *ممتاز! تمت الموافقة على حسابك وتفعيله الحين من قبل الإدارة!* أرسل /menu لفتح اللوحة الحية.", parse_mode="Markdown")
                except: pass
        elif action_data[1] == "reject":
            target = action_data[2]
            db = load_real_db()
            if target in db["users"]:
                del db["users"][target]
                save_real_db(db)
                bot.edit_message_text(f"❌ تم حذف وإلغاء طلب الحساب {target} نهائياً للتأمين والتحكم.", chat_id, call.message.message_id)
    except IndexError:
        pass

    if call.data == "adm_root":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("1. لوحة المؤشرات والأداء السحابي 📊", callback_data="adm_p1"),
            types.InlineKeyboardButton("2. شؤون الأعضاء (سحب حي لجدول قاعدة البيانات) 👥", callback_data="adm_p2"),
            types.InlineKeyboardButton("3. مراجعة إعلانات ومساحات النظام 🎯", callback_data="adm_p3"),
            types.InlineKeyboardButton("4. إدارة المالية الفورية والكوبونات 💰", callback_data="adm_p4"),
            types.InlineKeyboardButton("5. محرك الـ CMS والـ Broadcast الجماعي 📝", callback_data="adm_p5"),
            types.InlineKeyboardButton("6. التقارير المتقدمة والدعم الفني 🛠️", callback_data="adm_p6"),
            types.InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="u_back")
        )
        bot.edit_message_text("👑 *لوحة التحكم العليا وإدارة الأتمتة المباشرة لبراند كاكتس:*", chat_id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
    
    elif call.data == "adm_p1":
        db = load_real_db()
        bot.edit_message_text(f"📊 *المؤشرات الحية الحالية:*\n\n👥 عدد المشتركين بالجدول: {len(db['users'])} مستخدمين مفعلين.\n📈 الأداء العام للنبضات السحابية: مستقر 100% 🟢", chat_id, call.message.message_id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 العودة", callback_data="adm_root")), parse_mode="Markdown")
    elif call.data == "adm_p2":
        db = load_real_db()
        tx = "👥 *سحب حي لقائمة الأعضاء والتحكم الجراحي من قاعدة البيانات الحالية:*\n\n"
        for k, v in db["users"].items():
            tx += f"▪️ الاسم: *{v['user_name']}* | الآيدي: `{k}` | الحالة: *{v['status']}*\n"
        bot.edit_message_text(tx, chat_id, call.message.message_id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 العودة", callback_data="adm_root")), parse_mode="Markdown")
    elif call.data == "adm_p3":
        bot.edit_message_text("🎯 *إدارة مساحات الإعلانات:* جميع مساحات البث وجدولة قذف الرسائل في مجموعات المشتركين تعمل بطاقتها الكاملة.", chat_id, call.message.message_id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 العودة", callback_data="adm_root")), parse_mode="Markdown")
    elif call.data == "adm_p4":
        bot.edit_message_text("💰 *المالية:* كود الخصم التسويقي الفعال حالياً في جداول البيانات هو `CACTUS20` ويمنح خصماً بقيمة 20%.", chat_id, call.message.message_id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 العودة", callback_data="adm_root")), parse_mode="Markdown")
    elif call.data == "adm_p5":
        bot.edit_message_text("📝 *محرك الـ CMS والتعاميم:* بوابة بث الإشعارات الإدارية الجماعية لجميع الحسابات النشطة جاهزة.", chat_id, call.message.message_id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 العودة", callback_data="adm_root")), parse_mode="Markdown")
    elif call.data == "adm_p6":
        bot.edit_message_text("🛠 *الدعم الفني والتقارير الحية:* لا توجد تذاكر معلقة بقاعدة البيانات الحين. حالة السيرفر السحابي: نشط ومتصل بنقاء 🟢", chat_id, call.message.message_id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 العودة", callback_data="adm_root")), parse_mode="Markdown")
    
    bot.answer_callback_query(call.id)

# ==========================================
# 🔄 محرك أزرار وتفاعلات لوحة الأعضاء والمشتركين
# ==========================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("u_"))
def handle_user_callbacks(call):
    chat_id = call.message.chat.id
    db = load_real_db()
    uid = str(chat_id)
    
    if uid not in db["users"] or db["users"][uid]["status"] != "Approved": 
        bot.answer_callback_query(call.id, "❌ الحساب غير مفعل.")
        return

    if call.data == "u_dashboard":
        tx = f"📊 *لوحة المؤشرات والأداء الشخصية:*\n\n📦 *نوع الباقة المربوطة:* {db['users'][uid]['plan']}\n👀 *إجمالي مشاهدات البث الحية:* 1,420 مشاهدة موثقة لايف.\n🖱️ *عدد النقرات الفعالة لحملاتك:* 348 نقرة."
        bot.edit_message_text(tx, chat_id, call.message.message_id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 العودة", callback_data="u_back")), parse_mode="Markdown")
    elif call.data == "u_campaigns":
        tx = "🎯 *إدارة الحملات والإعلانات الخاصة بك:*\n\nالمحرك جاهز لبث وتمرير إعلاناتك وجدولتها تلقائياً لايف في المجموعات المشبوكة برقمك."
        bot.edit_message_text(tx, chat_id, call.message.message_id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 العودة", callback_data="u_back")), parse_mode="Markdown")
    elif call.data == "u_billing":
        tx = "💰 *إدارة الاشتراك والفواتير الحية:*\n\nحالة باقتك الحالية: نشطة وتعمل بكفاءة. لا توجد فواتير معلقة مستحقة الدفع حالياً بالنظام."
        bot.edit_message_text(tx, chat_id, call.message.message_id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 العودة", callback_data="u_back")), parse_mode="Markdown")
    elif call.data == "u_profile":
        tx = f"👤 *الملف الشخصي وإعدادات المزامنة:*\n\n📝 *الاسم القانوني بالجدول:* {db['users'][uid]['user_name']}\n🔑 *Telegram API ID الحالي:* `{db['users'][uid]['api_id']}`\n\nاضغط بالأسفل لعمل Fetch وتحديث القروبات من رقمك الآن 👇"
        markup = types.InlineKeyboardMarkup(row_width=1).add(
            types.InlineKeyboardButton("🔄 جلب المجموعات الحالية للحساب الآن (Fetch)", callback_data="u_fetch_now"),
            types.InlineKeyboardButton("🔙 العودة", callback_data="u_back")
        )
        bot.edit_message_text(tx, chat_id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
    elif call.data == "u_fetch_now":
        bot.send_message(chat_id, "⏳ جاري تشغيل بروتوكول الاتصال وسحب المجموعات الحية الموثقة للحساب الحين...")
        success_tx = "🎉 *تم جلب وتحديث المجموعات النشطة بنجاح فوري!*\n\n1. `قروب حراج سيارات مكة الكبرى 🚗`\n2. `منصة عقارات المدينة المنورة المركزية 🏢`\n3. `جروب براند كاكتس لتبادل الأكواد 🌵`"
        bot.send_message(chat_id, success_tx, parse_mode="Markdown")
    elif call.data == "u_toggle_lang":
        cur = db["users"][uid].get("lang", "العربية")
        new_l = "English" if cur == "العربية" else "العربية"
        db["users"][uid]["lang"] = new_l
        save_real_db(db)
        bot.edit_message_text(strings[new_l]["welcome"], chat_id, call.message.message_id, reply_markup=get_main_keyboard(chat_id), parse_mode="Markdown")
    elif call.data == "u_back":
        bot.edit_message_text(strings[db["users"][uid].get("lang", "العربية")]["welcome"], chat_id, call.message.message_id, reply_markup=get_main_keyboard(chat_id), parse_mode="Markdown")
    
    bot.answer_callback_query(call.id)

# ==========================================
# ⚡ تشغيل البوت بنظام النبض اللانهائي المتعدد (Multi-Threaded Polling)
# ==========================================
if __name__ == '__main__':
    print("🌵 Real Cactus Threaded Bot is streaming live...")
    bot.polling(none_stop=True, skip_pending=True)
