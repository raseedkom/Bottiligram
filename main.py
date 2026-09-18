import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8611848632:AAHmwScCgQaCmDoQjDn1hAtL0w8OzpF9d5s"
ADMIN_CHAT_ID = "8491461365"  # الآيدي الخاص بك للإشعارات الفورية
bot = telebot.TeleBot(TOKEN)

# رابط الصورة الموحدة للمتجر
UNIFIED_IMAGE_URL = "https://i.postimg.cc/MpN8H2jq/IMG-3158"

# رابط الخاص المباشر الخاص بك أو الدعم
MY_PRIVATE_CHAT_LINK = "https://t.me/+213662608846"

products = [
    {
        "id": "gemini_18m",
        "name": "Gemini 18 months",
        "price": "$1.80",
        "stock": 20,
        "icon": "⚡",
        "description": "🤖 جيمني إي آي برو 18 شهراً [NW]\n⭐️ جيمني إي آي برو لمدة 18 شهراً\n✦ 🚫 تفعيل بدون بطاقة\n✦ ⏩ مساحة تخزين سحابي 5 تيرابايت على جوجل ون\n✦ 🚀 لا حاجة لشبكة افتراضية (VPN).\n\n✨ مميزات إضافية:\n- رصيد 1050 كريدي على Google Flow والصور مجاناً\n- عمل 3 فيديوهات مجاناً على Gemini كل يوم طيلة مدة الاشتراك (18 شهر)\n- طريقة التفعيل تكون على جيمايل خاص بك عن طريق رابط تفعيل فقط\n\nلقد اختبارته بنفسي لذلك لا يوجد استبدال\n🫶 ضمان لمدة 12 ساعة.",
    },
    {
        "id": "capcut_1m",
        "name": "Capcut pro 1M FW",
        "price": "$1.32",
        "stock": 23,
        "icon": "🍄",
        "description": "🎬 حسابات كاب كات (فريق) برو جاهزة مع 640 رصيد ذكاء اصطناعي\n\n⚡ تسليم فوري\n📧 حسابات جاهزة\n💎 وصول إلى CapCut Pro\n🚀 سريع وسهل",
    },
    {
        "id": "duolingo_12m",
        "name": "Duolingo Super Slot 12M",
        "price": "$7.00",
        "stock": 0,
        "icon": "🟢",
        "description": "🦉 سوبر دوولينجو 12 شهرًا (ترقية رسمية للحساب)\n- ضمان كامل\n- استخدام دوولينجو سوبر مع جميع الميزات المتقدمة\n- تعلم اللغات بدون إعلانات",
    },
    {
        "id": "netflix_full",
        "name": "Netflix شهرين حساب كامل (5 بروفيلات)",
        "price": "$9.00",
        "stock": 100,
        "icon": "🍿",
        "description": "📦 حسابات نتفليكس بريميوم - شهرين\n\n✅ حسابات نتفليكس بريميوم\n✅ تسجيل الدخول بالبريد الإلكتروني وكلمة المرور\n✅ ضمان لمدة شهر الأول\n🔵 أرخص سعر — 9$ يعني 4,5$ حساب كامل 😍\n✅ يدعم البث بجودة عالية\n✅ يمكن استخدام ما يصل إلى 5 ملفات شخصية و4 أجهزة\n✅ يعمل على الهاتف المحمول، الكمبيوتر المحمول، التابلت والتلفزيون الذكي\n✅ الدعم متاح 12/24 ساعة\n📊 المباعة: 216 حسابات",
    },
    {
        "id": "netflix_profile",
        "name": "Netflix شهرين بروفيل واحد",
        "price": "$2.70",
        "stock": 1000,
        "icon": "🍿",
        "description": "📦 حسابات نتفليكس بريميوم - شهرين\n\n✅ حسابات نتفليكس بريميوم\n❌ ممنوع تغيير الاسم و كلمة السر هاذا يتم طردك من الحساب مع عدم وجود ضمان\n✅ تسجيل الدخول بالبريد الإلكتروني وكلمة المرور\n🔵 أرخص سعر — 2.70$\n✅ يدعم البث بجودة عالية\n✅ يمكن استخدام بروفيل في حساب واحد\n✅ يعمل على الهاتف المحمول، الكمبيوتر المحمول، التابلت والتلفزيون الذكي\n✅ الدعم متاح عند الحاجة\n📊 المباعة: 216 حسابات",
    },
    {
        "id": "nordvpn_3m",
        "name": "NordVPN 3 Months",
        "price": "$3.55",
        "stock": 7,
        "icon": "🛡️",
        "description": "🛡️ NordVPN - 3 أشهر\n\n- وصول مميز إلى NordVPN لمدة 3 أشهر على ما يصل إلى 10 أجهزة في وقت واحد.\n\nخطوات التفعيل بالتفصيل:\n➡️ رابط التفعيل: https://my.nordaccount.com/activate\n- أدخل الرمز الخاص بك هنا\n➡️ أدخل عنوان بريدك الإلكتروني\n➡️ أدخل رمز التحقق المستلم على بريدك الإلكتروني\n➡️ في صفحة الدفع، قم بالتمرير إلى الأسفل وانقر فوق Skip (تخطي)\n\nتم! ما عليك سوى تسجيل الدخول باستخدام بريدك الإلكتروني على أي جهاز.\n\n📊 المباعة: 390 حسابات",
    },
    {
        "id": "n8n_starter_12m",
        "name": "N8N Starter 12m",
        "price": "$19.99",
        "stock": 6,
        "icon": "⚡",
        "description": "⚡ N8N Starter 12m\n\n- المدة: 12 شهراً\n- رمز قسيمة رسمي\n- 🚫 لا توجد ضمانات بعد تفعيل الرمز على حسابك\n\n⚠️ يرجى ملاحظة أنه يجب استبدال الرمز خلال 7 أيام من الشراء. قد تنصرم صلاحية الرمز التي لم يتم استخدامها خلال هذه الفترة وقد لم تعد مؤهلة للدعم أو الاستبدال.\n\n📊 المباعة: 4 حسابات",
    },
    {
        "id": "snapchat_3m",
        "name": "Snapchat Plus+ 3M FW",
        "price": "$3.50",
        "stock": "♾️",
        "icon": "👻",
        "description": "👻 Snapchat Plus+ 3M FW available\n\n- الضمان: 90 يوم\n- المخزون: تفعيل يدوي حسابات\n- المباعة: 354 حسابات\n\n❞ الوصف:\nقم بتفعيل Snapchat+ وامنح حسابك تجربة Premium حقيقية مع ميزات حصرية:\n\nلا حاجة لكلمة مرور، فقط اسم المستخدم الخاص بك (ID)\n✅ حل تخزين (حسب باقتك)\n🎨 ثيمات مذهلة\n👑 مظهر حساب جديد وفريد من نوعه\n⚡ تفعيل سريع وآمن\n\n👌طريقة تفعيل : ارسلي في خاص Username فقط و تفعيل سريع 💨",
    },
    {
        "id": "snapchat_6m",
        "name": "Snapchat Plus+ 6M FW",
        "price": "$6.50",
        "stock": "♾️",
        "icon": "👻",
        "description": "👻 Snapchat Plus+ 6M FW available\n\n- الضمان: 180 يوم\n- المخزون: تفعيل يدوي حسابات\n- المباعة: 354 حسابات\n\n❞ الوصف:\nقم بتفعيل Snapchat+ وامنح حسابك تجربة Premium حقيقية مع ميزات حصرية:\n\nلا حاجة لكلمة مرور، فقط معرف الحساب الخاص بك (ID)\nأندرويد + آيفون\n✅ حل للتخزين (حسب باقتك)\n🎨 ثيمات مذهلة\n👑 مظهر حساب جديد وفريد من نوعه\n⚡ تفعيل سريع وآمن\n\n👌طريقة تفعيل : ارسلي في خاص Username فقط و تفعيل سريع 💨",
    }
]

def generate_store_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    for item in products:
        stock_display = item['stock'] if item['stock'] == "♾️" else f"📦 {item['stock']}"
        button_text = f"{item['icon']} {item['name']} | {item['price']} | {stock_display}"
        markup.add(InlineKeyboardButton(text=button_text, callback_data=f"buy_{item['id']}"))
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = "👋 مرحباً بك في متجر RASEEDKOM!\nاختر المنتج الذي تريده من القائمة أدناه:"
    try:
        bot.send_photo(message.chat.id, UNIFIED_IMAGE_URL, caption=welcome_text, reply_markup=generate_store_keyboard())
    except:
        bot.send_message(message.chat.id, welcome_text, reply_markup=generate_store_keyboard())

@bot.callback_query_handler(func=lambda call: call.data.startswith('buy_'))
def handle_purchase(call):
    product_id = call.data.replace('buy_', '')
    selected_product = next((p for p in products if p['id'] == product_id), None)
    
    if selected_product:
        markup = InlineKeyboardMarkup()
        
        # زر "اطلب الآن" يوجه الزبون للخاص المباشر
        order_button = InlineKeyboardButton(text="اطلب الآن 🛒", url=MY_PRIVATE_CHAT_LINK)
        markup.add(order_button)
        
        channel_button = InlineKeyboardButton(text="اشترك في القناة استفد من الخصم -%", url="https://t.me/+riEDwvUvQdxmMzU0")
        markup.add(channel_button)

        stock_val = selected_product['stock']
        if stock_val == "♾️" or (isinstance(stock_val, int) and stock_val > 0):
            caption_bottom = "🛒 لإتمام الطلب والشراء، اضغط على زر 'اطلب الآن 🛒' لتتوجه مباشرة للخاص."
        else:
            caption_bottom = "❌ هذا المنتج نفد من المخزون حالياً.\n🛒 للاستفسار أو الطلب المسبق، اضغط على 'اطلب الآن'."
            notify_button = InlineKeyboardButton(text="🔔 أعلمني عند التوفر", callback_data=f"notify_{selected_product['id']}")
            markup.add(notify_button)

        display_stock = "♾️" if stock_val == "♾️" else str(stock_val)
        caption = (
            f"✅ اخترت: *{selected_product['name']}*\n"
            f"💰 السعر: *{selected_product['price']}*\n"
            f"📦 المتوفر: *{display_stock}*\n\n"
            f"❞ الوصف:\n{selected_product['description']}\n\n"
            f"{caption_bottom}"
        )
        
        back_button = InlineKeyboardButton(text="رجوع ⬅️", callback_data="back_to_main")
        markup.add(back_button)
        
        # إرسال إشعار فوري لك في الخاص (ADMIN_CHAT_ID)
        try:
            user = call.from_user
            username = f"@{user.username}" if user.username else user.first_name
            admin_notification = (
                f"🚨 *طلب شراء جديد من المتجر!*\n\n"
                f"👤 الزبون: {username} (ID:{user.id}`)\n"
                f"📦 المنتج: *{selected_product['name']}*\n"
                f"💰 السعر: *{selected_product['price']}*\n\n"
                f"💬 ضغط الزبون على زر 'اطلب الآن' وتوجه للخاص."
            )
            bot.send_message(ADMIN_CHAT_ID, admin_notification, parse_mode="Markdown")
        except Exception as e:
            print(f"Error sending admin notification: {e}")

        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
            
        try:
            bot.send_photo(
                call.message.chat.id, 
                UNIFIED_IMAGE_URL, 
                caption=caption, 
                parse_mode="Markdown",
                reply_markup=markup
            )
        except Exception as e:
            bot.send_message(call.message.chat.id, caption, parse_mode="Markdown", reply_markup=markup)
            
        bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == 'back_to_main')
def handle_back(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    welcome_text = "👋 مرحباً بك في متجر RASEEDKOM!\nاختر المنتج الذي تريده من القائمة أدناه:"
    try:
        bot.send_photo(call.message.chat.id, UNIFIED_IMAGE_URL, caption=welcome_text, reply_markup=generate_store_keyboard())
    except:
        bot.send_message(call.message.chat.id, welcome_text, reply_markup=generate_store_keyboard())
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('notify_'))
def handle_notify(call):
    bot.answer_callback_query(call.id, text="✅ تم تسجيل اهتمامك! سنحاول توفير المنتج في أقرب وقت.", show_alert=True)

print("Bot is running...")
bot.infinity_polling()
