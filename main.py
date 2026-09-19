from flask import Flask
import threading

app = Flask('')

@app.route('/')
def home():
    return "I'm alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

threading.Thread(target=run).start()

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import os
import html
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# البوت: https://t.me/RASEEDKOM_store_bot
# التوكن يُقرأ من Render > Environment باسم BOT_TOKEN (لا تكتبه في الكود)
TOKEN = os.environ["BOT_TOKEN"]
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID", "8491461365")  # الآيدي الخاص بك للإشعارات الفورية
bot = telebot.TeleBot(TOKEN)

# رابط الصورة الموحدة للمتجر (يجب أن يكون رابطاً مباشراً ينتهي بـ .jpg أو .png)
UNIFIED_IMAGE_URL = "https://i.postimg.cc/MpN8H2jq/IMG-3158"

# رابط الخاص المباشر الخاص بك أو الدعم
MY_PRIVATE_CHAT_LINK = "https://t.me/Raseedkom"

CHANNEL_LINK = "https://t.me/+riEDwvUvQdxmMzU0"

WELCOME_TEXT = "👋 مرحباً بك في متجر RASEEDKOM!\nاختر المنتج الذي تريده من القائمة أدناه:"

# لإضافة صورة خاصة بمنتج: زد داخل المنتج سطر  "image": "رابط مباشر أو file_id"
products = [
    {
        "id": "gemini_18m",
        "name": "Gemini 18 months",
        "price": "$1.80",
        "stock": 20,
        "icon": "⚡",
        "image": "https://i.postimg.cc/dtV9QBZv/IMG-3140.jpg",
        "description": "🤖 جيمني إي آي برو 18 شهراً [NW]\n⭐️ جيمني إي آي برو لمدة 18 شهراً\n✦ 🚫 تفعيل بدون بطاقة\n✦ ⏩ مساحة تخزين سحابي 5 تيرابايت على جوجل ون\n✦ 🚀 لا حاجة لشبكة افتراضية (VPN).\n\n✨ مميزات إضافية:\n- رصيد 1050 كريدي على Google Flow والصور مجاناً\n- عمل 3 فيديوهات مجاناً على Gemini كل يوم طيلة مدة الاشتراك (18 شهر)\n- طريقة التفعيل تكون على جيمايل خاص بك عن طريق رابط تفعيل فقط\n\nلقد اختبارته بنفسي لذلك لا يوجد استبدال\n🫶 ضمان لمدة 12 ساعة.",
    },
    {
        "id": "capcut_1m",
        "name": "Capcut pro 1M FW",
        "price": "$1.32",
        "stock": 23,
        "icon": "🍄",
        "image": "https://i.postimg.cc/DzpSgryL/IMG-3143.jpg",
        "description": "🎬 حسابات كاب كات (فريق) برو جاهزة مع 640 رصيد ذكاء اصطناعي\n\n⚡ تسليم فوري\n📧 حسابات جاهزة\n💎 وصول إلى CapCut Pro\n🚀 سريع وسهل",
    },
    {
        "id": "duolingo_12m",
        "name": "Duolingo Super Slot 12M",
        "price": "$7.00",
        "stock": 0,
        "icon": "🟢",
        "image": "https://i.postimg.cc/qM1j2YVZ/IMG-3365.jpg",
        "description": "🦉 سوبر دوولينجو 12 شهرًا (ترقية رسمية للحساب)\n- ضمان كامل\n- استخدام دوولينجو سوبر مع جميع الميزات المتقدمة\n- تعلم اللغات بدون إعلانات",
    },
    {
        "id": "duolingo_link_12m",
        "name": "Duolingo Super سنة (رابط) + ضمان شهر",
        "price": "$4.55",
        "stock": 21,
        "icon": "🦉",
        "image": "https://i.postimg.cc/qM1j2YVZ/IMG-3365.jpg",
        "description": "⭐ رابط الحصول على عرض Duolingo Super لمدة سنة مع ضمان شهر واحد\n\n📊 المبيعات: 103 حسابات\n\n🔗 رابط الحصول على عرض Duolingo Super لمدة سنة مع ضمان شهر واحد\n\n❇️ تجربة سلسة وفعّالة وغير محدودة لتعلّم اللغات الأجنبية.\n❇️ عند شراء العرض، ستحصل على العرض مباشرة على الحساب الأساسي المستخدم حاليًا.\n❇️ الطريقة: رابط للحصول على العرض.\n❇️ مدة الاشتراك: سنة واحدة.\n⚙️ الضمان: شهر واحد.\n⛓️‍💥 يُرجى استخدام الرابط مباشرة بعد الدفع.\n❇️ لا تحتاج إلى إضافة بطاقة دفع: فقط ادخل إلى الرابط الذي يرسله لك البوت واحصل على العرض",
    },
    {
        "id": "netflix_full",
        "name": "Netflix شهرين حساب كامل (5 بروفيلات)",
        "price": "$9.00",
        "stock": 100,
        "icon": "🍿",
        "image": "https://i.postimg.cc/DZYwrn6r/IMG-3153.jpg",
        "description": "📦 حسابات نتفليكس بريميوم - شهرين\n\n✅ حسابات نتفليكس بريميوم\n✅ تسجيل الدخول بالبريد الإلكتروني وكلمة المرور\n✅ ضمان لمدة شهر الأول\n🔵 أرخص سعر — 9$ يعني 4,5$ حساب كامل 😍\n✅ يدعم البث بجودة عالية\n✅ يمكن استخدام ما يصل إلى 5 ملفات شخصية و4 أجهزة\n✅ يعمل على الهاتف المحمول، الكمبيوتر المحمول، التابلت والتلفزيون الذكي\n✅ الدعم متاح 12/24 ساعة\n📊 المباعة: 216 حسابات",
    },
    {
        "id": "netflix_profile",
        "name": "Netflix شهرين بروفيل واحد",
        "price": "$2.70",
        "stock": 1000,
        "icon": "🍿",
        "image": "https://i.postimg.cc/DZYwrn6r/IMG-3153.jpg",
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
    },
    {
        "id": "snapchat_12m",
        "name": "Snapchat Plus+ 12M FW",
        "price": "$22.00",
        "stock": "♾️",
        "icon": "👻",
        "description": "👻 Snapchat Plus+ 12M FW available\n\n- الضمان: طيلة مدة اشتراك\n- المخزون: تفعيل يدوي حسابات\n- المباعة: 231 حسابات\n\n❞ الوصف:\nقم بتفعيل Snapchat+ وامنح حسابك تجربة Premium حقيقية مع ميزات حصرية: لمدة عام كامل \n\nلا حاجة لكلمة مرور، فقط معرف الحساب الخاص بك (ID)\nأندرويد + آيفون\n✅ حل للتخزين (حسب باقتك)\n🎨 ثيمات مذهلة\n👑 مظهر حساب جديد وفريد من نوعه\n⚡ تفعيل سريع وآمن\n\n👌طريقة تفعيل : ارسلي في خاص Username فقط و تفعيل سريع 💨",
    },
    {
        "id": "canva_edu_500",
        "name": "Canva Edu Pro — 500 مقعد",
        "price": "$10.00",
        "stock": 500,
        "icon": "🎨",
        "image": "https://i.postimg.cc/sxq1rsZR/IMG-3373.jpg",
        "description": "🎨 Canva Edu Pro — 500 مقعد\n\n🔥 حساب/لوحة Canva Education مخصصة للطلاب والمعلمين\nاستفد من مزايا Canva التعليمية وأدوات Pro لإنشاء تصاميم احترافية بسهولة.\n\n✨ ماذا تحصل عليه؟\n- 🎓 وصول إلى مزايا Canva التعليمية.\n- 💎 أدوات Canva Pro والعديد من الميزات الاحترافية.\n- 📚 قوالب تعليمية جاهزة.\n- 🎨 تصميم عروض تقديمية، منشورات، فيديوهات وملفات تعليمية.\n- 🤖 أدوات الذكاء الاصطناعي مثل Magic Write.\n\n📦 السعة: 500 مقعد\n💰 السعر: 10$ فقط\n⚠️ مهم: المنتج بدون ضمان.\n\n🚀 مناسب للطلاب، الأساتذة، المصممين وأصحاب المشاريع",
    },
    {
        "id": "canva_edu_5000",
        "name": "Canva Edu Pro — 5000 مقعد",
        "price": "$21.50",
        "stock": 5000,
        "icon": "🎨",
        "image": "https://i.postimg.cc/sxq1rsZR/IMG-3373.jpg",
        "description": "🎨 Canva Edu Pro — 5000 مقعد\n\n🔥 حساب/لوحة Canva Education\nاضافة 5000 شخص مع تحكم الكامل\n\n✨ ماذا تحصل عليه؟\n- 🎓 وصول إلى مزايا Canva التعليمية.\n- 💎 أدوات Canva Pro والعديد من الميزات الاحترافية.\n- 📚 قوالب تعليمية جاهزة.\n- 🎨 تصميم عروض تقديمية، منشورات، فيديوهات وملفات تعليمية.\n- 🤖 أدوات الذكاء الاصطناعي مثل Magic Write.\n\n📦 السعة: 5000 مقعد\n💰 السعر: 21.50$ فقط\n⚠️ مهم: المنتج مع ضمان\n\n🚀 مناسب للطلاب، الأساتذة، المصممين وأصحاب المشاريع",
    },
    {
        "id": "freefire_diamonds",
        "name": "Free Fire Diamonds 💎",
        "price": "$1.45 - $19.50",
        "stock": "♾️",
        "icon": "🔥",
        "description": "🔥 شحن Free Fire Diamonds 💎 بأسرع وأسهل طريقة! 🔥\n\nتحتاج تشحن جواهر حسابك؟ 💎\nمع خدمتنا تقدر تشحن Free Fire Diamonds عن طريق الـ ID فقط ✅\n\n🔒 بدون الحاجة إلى كلمة السر أو أي معلومات من حسابك\n⚡️ الشحن يتم بسرعة، وفي دقيقة واحدة فقط بعد إتمام الدفع وإرسال الـ ID.\n\n💎 أسعار الباقات بدون جواهر إضافية:\n\n110💎  ▶️  1.45$\n\n231💎  ▶️  2.20$\n\n583💎  ▶️  5.05$\n\n1188💎  ▶️  10.10$\n\n2420💎  ▶️  19.50$\n\n📩 طريقة الطلب:\n1️⃣ تتواصل معنا\n2️⃣ تختار الباقة المناسبة\n3️⃣ تقوم بالدفع\n4️⃣ ترسل لنا ID حسابك فقط\n5️⃣ يتم شحن الجواهر لحسابك ⚡️\n\n🛡️ ضمان متوفر ✅\n🚀 سرعة في التنفيذ\n🔐 لا نطلب أي معلومات حساسة من حسابك\n\n💎 اطلب شحنتك الآن واستمتع باللعبة! 🎮🔥",
    },
    {
        "type": "separator",
        "id": "sep_gift_cards",
        "text": "⬇️ بطقات الهداية ⬇️",
    },
    {
        "id": "apple_gift_tr",
        "name": "Apple Gift Card 🇹🇷 تركية",
        "price": "$1.00 - $5.70",
        "stock": "♾️",
        "icon": "🍎",
        "description": "🍎 Apple Gift Card 🇹🇷 — تركية\n\nمخصّصة لمتجر App Store التركي 📱\n💳 عند الدفع يصلك كود التفعيل مباشرة.\n\nApple Gift Card. 10TRK ▶️ 1.00$\n\nApple Gift Card. 50TRK ▶️ 1.35$\n\nApple Gift Card. 100TRK ▶️ 2.50$\n\nApple Gift Card. 150TRK ▶️ 3.60$\n\nApple Gift Card. 200TRK ▶️ 5.00$\n\nApple Gift Card. 250TRK ▶️ 5.70$\n\n\n🛡️ الضمان: ساعة واحدة من وقت الشراء.\n(لم يسبق أن واجهتنا أي مشكلة مع الأكواد.)",
    },
    {
        "id": "apple_gift_in",
        "name": "Apple Gift Card 🇮🇳 هندية",
        "price": "$1.40 - $28.10",
        "stock": "♾️",
        "icon": "🍎",
        "description": "🍎 Apple Gift Card 🇮🇳 — هندية\n\nبطاقات مخصّصة لمتجر App Store الهند 📱\n💳 عند الدفع يصلك كود التفعيل مباشرة.\n\n🎁 البطاقات والأسعار:\n\nApple Gift Card >100INR ▶️ 1.40$\n\nApple Gift Card >200INR ▶️ 2,45$\n\nApple Gift Card >250INR ▶️ 3,05$\n\nApple Gift Card >500INR ▶️ 6,15$\n\nApple Gift Card >1000INR ▶️ 12$\n\nApple Gift Card 1500INR▶️ 28,10$\n\n🛡️ الضمان: ساعة واحدة من وقت الشراء.\n(لم يسبق أن واجهتنا أي مشكلة مع الأكواد.)",
    },
    {
        "id": "apple_gift_fr",
        "name": "Apple Gift Card 🇫🇷 فرنسية",
        "price": "$2.45 - $116.22",
        "stock": "♾️",
        "icon": "🍎",
        "description": "🍎 Apple Gift Card 🇫🇷 — فرنسا\n\nبطاقات مخصّصة لمتجر App Store الفرنسي 📱\n💳 عند الدفع يصلك كود التفعيل مباشرة.\n\n🎁 البطاقات والأسعار:\n\nApple Gift Card >2EUR ▶️ 2,45$\n\nApple Gift Card >10EUR ▶️ 12$\n\nApple Gift Card >20EUR▶️ 23,65$\n\nApple Gift Card >50EUR ▶️ 59$\n\nApple Gift Card >75EUR ▶️ 89$\n\nApple Gift Card 100EUR▶️116,22$\n\n🛡️ الضمان: ساعة واحدة من وقت الشراء.\n(لم يسبق أن واجهتنا أي مشكلة مع الأكواد.)",
    },
]


def find_product(product_id):
    return next((p for p in products if p["id"] == product_id), None)


def generate_store_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    for item in products:
        if item.get("type") == "separator":
            markup.add(InlineKeyboardButton(text=item["text"], callback_data="noop"))
            continue
        stock_display = item["stock"] if item["stock"] == "♾️" else f"📦 {item['stock']}"
        button_text = f"{item['icon']} {item['name']} | {item['price']} | {stock_display}"
        markup.add(InlineKeyboardButton(text=button_text, callback_data=f"buy_{item['id']}"))
    return markup


def send_main_menu(chat_id):
    try:
        bot.send_photo(chat_id, UNIFIED_IMAGE_URL, caption=WELCOME_TEXT, reply_markup=generate_store_keyboard())
    except Exception:
        bot.send_message(chat_id, WELCOME_TEXT, reply_markup=generate_store_keyboard())


@bot.message_handler(commands=["start"])
def send_welcome(message):
    send_main_menu(message.chat.id)


def notify_admin(user, product):
    try:
        username = f"@{user.username}" if user.username else user.first_name
        text = (
            f"🔔 <b>زبون اختار منتج من المتجر</b>\n\n"
            f"👤 الزبون: {html.escape(username)} (ID: <code>{user.id}</code>)\n"
            f"📦 المنتج: <b>{html.escape(product['name'])}</b>\n"
            f"💰 السعر: <b>{html.escape(product['price'])}</b>"
        )
        bot.send_message(ADMIN_CHAT_ID, text, parse_mode="HTML")
    except Exception as e:
        print(f"Error sending admin notification: {e}")


# ---------- عرض المنتج ----------
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def handle_product_view(call):
    product_id = call.data.replace("buy_", "")
    selected_product = find_product(product_id)
    if not selected_product:
        bot.answer_callback_query(call.id)
        return

    # إشعار فوري لك عند اختيار الزبون للمنتج
    notify_admin(call.from_user, selected_product)

    markup = InlineKeyboardMarkup()

    # زر "اطلب الآن" يوجه الزبون للخاص المباشر
    markup.add(InlineKeyboardButton(text="اطلب الآن 🛒", url=MY_PRIVATE_CHAT_LINK))
    markup.add(InlineKeyboardButton(text="اشترك في القناة استفد من الخصم -%", url=CHANNEL_LINK))

    stock_val = selected_product["stock"]
    if stock_val == "♾️" or (isinstance(stock_val, int) and stock_val > 0):
        caption_bottom = "🛒 لإتمام الطلب والشراء، اضغط على زر 'اطلب الآن 🛒' لتتوجه مباشرة للخاص."
    else:
        caption_bottom = "❌ هذا المنتج نفد من المخزون حالياً.\n🛒 للاستفسار أو الطلب المسبق، اضغط على 'اطلب الآن'."
        markup.add(InlineKeyboardButton(text="🔔 أعلمني عند التوفر", callback_data=f"notify_{selected_product['id']}"))

    markup.add(InlineKeyboardButton(text="رجوع ⬅️", callback_data="back_to_main"))

    display_stock = "♾️" if stock_val == "♾️" else str(stock_val)
    caption = (
        f"✅ اخترت: *{selected_product['name']}*\n"
        f"💰 السعر: *{selected_product['price']}*\n"
        f"📦 المتوفر: *{display_stock}*\n\n"
        f"❞ الوصف:\n{selected_product['description']}\n\n"
        f"{caption_bottom}"
    )

    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass

    # صورة المنتج الخاصة (إن وُجدت) ثم الصورة الموحدة، ثم نص فقط كحل أخير
    chat_id = call.message.chat.id
    sent = False
    for photo in (selected_product.get("image"), UNIFIED_IMAGE_URL):
        if not photo:
            continue
        for parse_mode in ("Markdown", None):
            try:
                bot.send_photo(
                    chat_id,
                    photo,
                    caption=caption if parse_mode else caption.replace("*", ""),
                    parse_mode=parse_mode,
                    reply_markup=markup,
                )
                sent = True
                break
            except Exception:
                continue
        if sent:
            break
    if not sent:
        bot.send_message(chat_id, caption.replace("*", ""), reply_markup=markup)

    bot.answer_callback_query(call.id)


@bot.message_handler(content_types=["photo"])
def get_photo_file_id(message):
    # أرسل صورة للبوت من حسابك فقط، فيرد عليك بـ file_id لتضعه في "image" للمنتج
    if str(message.chat.id) != str(ADMIN_CHAT_ID):
        return
    file_id = message.photo[-1].file_id
    bot.reply_to(message, f"file_id:\n<code>{file_id}</code>", parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: call.data == "noop")
def handle_noop(call):
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == "back_to_main")
def handle_back(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    send_main_menu(call.message.chat.id)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("notify_"))
def handle_notify(call):
    bot.answer_callback_query(
        call.id,
        text="✅ تم تسجيل اهتمامك! سنحاول توفير المنتج في أقرب وقت.",
        show_alert=True,
    )


print("Bot is running...")
bot.infinity_polling()
