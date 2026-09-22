from flask import Flask
import threading

app = Flask('')

@app.route('/')
def home():
    return "I'm alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

threading.Thread(target=run).start()

import os
import json
import html
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

try:
    from telebot.types import BotCommand, BotCommandScopeChat
except ImportError:  # مكتبة قديمة: زر القائمة لن يعمل لكن البوت يشتغل
    BotCommand = BotCommandScopeChat = None

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

SUPPORTED_LANGS = ("ar", "en", "fr")

# ---------- نصوص الواجهة بالثلاث لغات ----------
CHOOSE_LANG_TEXT = "🌐 اختر لغتك\nChoose your language\nChoisissez votre langue"

TEXTS = {
    "ar": {
        "welcome": "👋 مرحباً بك في متجر RASEEDKOM!\nاختر المنتج الذي تريده من القائمة أدناه:",
        "order_now": "اطلب الآن 🛒",
        "join_channel": "اشترك في القناة استفد من الخصم -%",
        "back": "رجوع ⬅️",
        "notify_me": "🔔 أعلمني عند التوفر",
        "notify_ok": "✅ تم تسجيل اهتمامك! سنحاول توفير المنتج في أقرب وقت.",
        "change_lang": "🌐 اللغة / Language / Langue",
        "chosen": "✅ اخترت:",
        "price": "💰 السعر:",
        "available": "📦 المتوفر:",
        "description": "❞ الوصف:",
        "cmd_language": "🌐 تغيير اللغة",
        "cmd_support": "💬 الدعم",
        "support_msg": "💬 للدعم والطلبات، تواصل معي مباشرة في الخاص 👇",
        "support_btn": "💬 تواصل مع الدعم",
        "buy_hint": "🛒 لإتمام الطلب والشراء، اضغط على زر 'اطلب الآن 🛒' لتتوجه مباشرة للخاص.",
        "out_of_stock": "❌ هذا المنتج نفد من المخزون حالياً.\n🛒 للاستفسار أو الطلب المسبق، اضغط على 'اطلب الآن'.",
    },
    "en": {
        "welcome": "👋 Welcome to the RASEEDKOM store!\nChoose the product you want from the list below:",
        "order_now": "Order now 🛒",
        "join_channel": "Join the channel for discounts -%",
        "back": "Back ⬅️",
        "notify_me": "🔔 Notify me when available",
        "notify_ok": "✅ Your interest has been noted! We will try to restock as soon as possible.",
        "change_lang": "🌐 اللغة / Language / Langue",
        "chosen": "✅ You chose:",
        "price": "💰 Price:",
        "available": "📦 Available:",
        "description": "❞ Description:",
        "cmd_language": "🌐 Change language",
        "cmd_support": "💬 Support",
        "support_msg": "💬 For support and orders, contact me directly in private 👇",
        "support_btn": "💬 Contact support",
        "buy_hint": "🛒 To complete your order, tap 'Order now 🛒' to go directly to the private chat.",
        "out_of_stock": "❌ This product is currently out of stock.\n🛒 For questions or pre-orders, tap 'Order now'.",
    },
    "fr": {
        "welcome": "👋 Bienvenue dans la boutique RASEEDKOM !\nChoisissez le produit souhaité dans la liste ci-dessous :",
        "order_now": "Commander maintenant 🛒",
        "join_channel": "Rejoignez le canal pour des réductions -%",
        "back": "Retour ⬅️",
        "notify_me": "🔔 M'avertir dès la disponibilité",
        "notify_ok": "✅ Votre intérêt est enregistré ! Nous ferons de notre mieux pour remettre le produit en stock rapidement.",
        "change_lang": "🌐 اللغة / Language / Langue",
        "chosen": "✅ Vous avez choisi :",
        "price": "💰 Prix :",
        "available": "📦 Disponible :",
        "description": "❞ Description :",
        "cmd_language": "🌐 Changer de langue",
        "cmd_support": "💬 Assistance",
        "support_msg": "💬 Pour l'assistance et les commandes, contactez-moi directement en privé 👇",
        "support_btn": "💬 Contacter l'assistance",
        "buy_hint": "🛒 Pour finaliser votre commande, appuyez sur « Commander maintenant 🛒 » pour aller directement en privé.",
        "out_of_stock": "❌ Ce produit est actuellement en rupture de stock.\n🛒 Pour toute question ou précommande, appuyez sur « Commander maintenant ».",
    },
}

# لإضافة صورة خاصة بمنتج: زد داخل المنتج سطر  "image": "رابط مباشر أو file_id"
products = [
    {
        "id": "gemini_18m",
        "name": "Gemini 18 months",
        "price": "$1.80",
        "stock": 20,
        "icon": "⚡",
        "image": "https://i.postimg.cc/52zRxRM3/IMG-3570.jpg",
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
        "image": "https://i.postimg.cc/QdBHVc6V/IMG-3571.jpg",
        "description": "🦉 سوبر دوولينجو 12 شهرًا (ترقية رسمية للحساب)\n- ضمان كامل\n- استخدام دوولينجو سوبر مع جميع الميزات المتقدمة\n- تعلم اللغات بدون إعلانات",
    },
    {
        "id": "duolingo_link_12m",
        "name": "Duolingo Super سنة (رابط) + ضمان شهر",
        "price": "$4.55",
        "stock": 21,
        "icon": "🦉",
        "image": "https://i.postimg.cc/QdBHVc6V/IMG-3571.jpg",
        "description": "⭐ رابط الحصول على عرض Duolingo Super لمدة سنة مع ضمان شهر واحد\n\n📊 المبيعات: 103 حسابات\n\n🔗 رابط الحصول على عرض Duolingo Super لمدة سنة مع ضمان شهر واحد\n\n❇️ تجربة سلسة وفعّالة وغير محدودة لتعلّم اللغات الأجنبية.\n❇️ عند شراء العرض، ستحصل على العرض مباشرة على الحساب الأساسي المستخدم حاليًا.\n❇️ الطريقة: رابط للحصول على العرض.\n❇️ مدة الاشتراك: سنة واحدة.\n⚙️ الضمان: شهر واحد.\n⛓️‍💥 يُرجى استخدام الرابط مباشرة بعد الدفع.\n❇️ لا تحتاج إلى إضافة بطاقة دفع: فقط ادخل إلى الرابط الذي يرسله لك البوت واحصل على العرض",
    },
    {
        "id": "netflix_full",
        "name": "Netflix شهرين حساب كامل (5 بروفيلات)",
        "price": "$9.00",
        "stock": 100,
        "icon": "🍿",
        "image": "https://i.postimg.cc/zDM5d4D3/IMG-3568.jpg",
        "description": "📦 حسابات نتفليكس بريميوم - شهرين\n\n✅ حسابات نتفليكس بريميوم\n✅ تسجيل الدخول بالبريد الإلكتروني وكلمة المرور\n✅ ضمان لمدة شهر الأول\n🔵 أرخص سعر — 9$ يعني 4,5$ حساب كامل 😍\n✅ يدعم البث بجودة عالية\n✅ يمكن استخدام ما يصل إلى 5 ملفات شخصية و4 أجهزة\n✅ يعمل على الهاتف المحمول، الكمبيوتر المحمول، التابلت والتلفزيون الذكي\n✅ الدعم متاح 12/24 ساعة\n📊 المباعة: 216 حسابات",
    },
    {
        "id": "netflix_profile",
        "name": "Netflix شهرين بروفيل واحد",
        "price": "$2.70",
        "stock": 1000,
        "icon": "🍿",
        "image": "https://i.postimg.cc/zDM5d4D3/IMG-3568.jpg",
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


# ---------- ترجمات المنتجات (الإنجليزية والفرنسية) ----------
# إذا لم توجد ترجمة لمنتج أو لحقل معيّن، يُعرض النص العربي الأصلي
TRANSLATIONS = {
    "sep_gift_cards": {
        "en": {
            "text": "⬇️ Gift Cards ⬇️"
        },
        "fr": {
            "text": "⬇️ Cartes cadeaux ⬇️"
        }
    },
    "gemini_18m": {
        "en": {
            "description": "🤖 Gemini AI Pro 18 months [NW]\n⭐️ Gemini AI Pro for 18 months\n✦ 🚫 Activation without a card\n✦ ⏩ 5 TB of Google One cloud storage\n✦ 🚀 No VPN needed.\n\n✨ Extra features:\n- 1050 free credits on Google Flow and images\n- 3 free videos on Gemini every day for the whole subscription (18 months)\n- Activation is done on your own Gmail through an activation link only\n\nI tested it myself, so there is no replacement\n🫶 12-hour warranty."
        },
        "fr": {
            "description": "🤖 Gemini AI Pro 18 mois [NW]\n⭐️ Gemini AI Pro pour 18 mois\n✦ 🚫 Activation sans carte bancaire\n✦ ⏩ 5 To de stockage cloud Google One\n✦ 🚀 Aucun VPN nécessaire.\n\n✨ Avantages supplémentaires :\n- 1050 crédits gratuits sur Google Flow et images\n- 3 vidéos gratuites sur Gemini chaque jour pendant toute la durée de l'abonnement (18 mois)\n- L'activation se fait sur votre propre Gmail via un lien d'activation uniquement\n\nJe l'ai testé moi-même, donc il n'y a pas de remplacement\n🫶 Garantie de 12 heures."
        }
    },
    "capcut_1m": {
        "en": {
            "description": "🎬 Ready CapCut Pro (team) accounts with 640 AI credits\n\n⚡ Instant delivery\n📧 Ready accounts\n💎 Access to CapCut Pro\n🚀 Fast and easy"
        },
        "fr": {
            "description": "🎬 Comptes CapCut Pro (équipe) prêts avec 640 crédits d'IA\n\n⚡ Livraison instantanée\n📧 Comptes prêts\n💎 Accès à CapCut Pro\n🚀 Rapide et facile"
        }
    },
    "duolingo_12m": {
        "en": {
            "description": "🦉 Super Duolingo 12 months (official account upgrade)\n- Full warranty\n- Use Duolingo Super with all advanced features\n- Learn languages without ads"
        },
        "fr": {
            "description": "🦉 Super Duolingo 12 mois (mise à niveau officielle du compte)\n- Garantie complète\n- Utilisez Duolingo Super avec toutes les fonctionnalités avancées\n- Apprenez les langues sans publicité"
        }
    },
    "duolingo_link_12m": {
        "en": {
            "name": "Duolingo Super 1 year (link) + 1 month warranty",
            "description": "⭐ Link to get a Duolingo Super offer for one year with a 1-month warranty\n\n📊 Sales: 103 accounts\n\n🔗 Link to get a Duolingo Super offer for one year with a 1-month warranty\n\n❇️ A smooth, effective and unlimited experience for learning foreign languages.\n❇️ When you buy the offer, it is applied directly to the main account you currently use.\n❇️ Method: a link to claim the offer.\n❇️ Subscription duration: one year.\n⚙️ Warranty: one month.\n⛓️‍💥 Please use the link right after payment.\n❇️ No payment card needed: just open the link the bot sends you and get the offer"
        },
        "fr": {
            "name": "Duolingo Super 1 an (lien) + garantie 1 mois",
            "description": "⭐ Lien pour obtenir l'offre Duolingo Super pendant un an avec une garantie d'un mois\n\n📊 Ventes : 103 comptes\n\n🔗 Lien pour obtenir l'offre Duolingo Super pendant un an avec une garantie d'un mois\n\n❇️ Une expérience fluide, efficace et illimitée pour apprendre les langues étrangères.\n❇️ Lors de l'achat, l'offre est appliquée directement sur le compte principal que vous utilisez actuellement.\n❇️ Méthode : un lien pour obtenir l'offre.\n❇️ Durée de l'abonnement : un an.\n⚙️ Garantie : un mois.\n⛓️‍💥 Veuillez utiliser le lien juste après le paiement.\n❇️ Aucune carte bancaire nécessaire : ouvrez simplement le lien envoyé par le bot et obtenez l'offre"
        }
    },
    "netflix_full": {
        "en": {
            "name": "Netflix 2 months full account (5 profiles)",
            "description": "📦 Netflix Premium accounts - 2 months\n\n✅ Netflix Premium accounts\n✅ Login with email and password\n✅ 1-month warranty\n🔵 Cheapest price — 9$ means 4.5$ for a full account 😍\n✅ High-quality streaming\n✅ Up to 5 profiles and 4 devices\n✅ Works on mobile, laptop, tablet and smart TV\n✅ Support available 12/24 hours\n📊 Sold: 216 accounts"
        },
        "fr": {
            "name": "Netflix 2 mois compte complet (5 profils)",
            "description": "📦 Comptes Netflix Premium - 2 mois\n\n✅ Comptes Netflix Premium\n✅ Connexion par e-mail et mot de passe\n✅ Garantie d'un mois\n🔵 Prix le plus bas — 9$ soit 4,5$ le compte complet 😍\n✅ Streaming haute qualité\n✅ Jusqu'à 5 profils et 4 appareils\n✅ Fonctionne sur mobile, ordinateur portable, tablette et Smart TV\n✅ Support disponible 12/24 heures\n📊 Vendus : 216 comptes"
        }
    },
    "netflix_profile": {
        "en": {
            "name": "Netflix 2 months single profile",
            "description": "📦 Netflix Premium accounts - 2 months\n\n✅ Netflix Premium accounts\n❌ Do not change the name or the password, otherwise you will be removed from the account with no warranty\n✅ Login with email and password\n🔵 Cheapest price — 2.70$\n✅ High-quality streaming\n✅ One profile on one account\n✅ Works on mobile, laptop, tablet and smart TV\n✅ Support available when needed\n📊 Sold: 216 accounts"
        },
        "fr": {
            "name": "Netflix 2 mois un seul profil",
            "description": "📦 Comptes Netflix Premium - 2 mois\n\n✅ Comptes Netflix Premium\n❌ Interdiction de changer le nom ou le mot de passe, sinon vous serez exclu du compte sans garantie\n✅ Connexion par e-mail et mot de passe\n🔵 Prix le plus bas — 2,70$\n✅ Streaming haute qualité\n✅ Un profil sur un compte\n✅ Fonctionne sur mobile, ordinateur portable, tablette et Smart TV\n✅ Support disponible en cas de besoin\n📊 Vendus : 216 comptes"
        }
    },
    "nordvpn_3m": {
        "en": {
            "description": "🛡️ NordVPN - 3 months\n\n- Premium access to NordVPN for 3 months on up to 10 devices at the same time.\n\nActivation steps in detail:\n➡️ Activation link: https://my.nordaccount.com/activate\n- Enter your code here\n➡️ Enter your email address\n➡️ Enter the verification code received in your email\n➡️ On the payment page, scroll down and click Skip\n\nDone! Just log in with your email on any device.\n\n📊 Sold: 390 accounts"
        },
        "fr": {
            "description": "🛡️ NordVPN - 3 mois\n\n- Accès premium à NordVPN pendant 3 mois sur jusqu'à 10 appareils simultanément.\n\nÉtapes d'activation détaillées :\n➡️ Lien d'activation : https://my.nordaccount.com/activate\n- Saisissez votre code ici\n➡️ Saisissez votre adresse e-mail\n➡️ Saisissez le code de vérification reçu par e-mail\n➡️ Sur la page de paiement, faites défiler vers le bas et cliquez sur Skip (Passer)\n\nC'est fait ! Connectez-vous simplement avec votre e-mail sur n'importe quel appareil.\n\n📊 Vendus : 390 comptes"
        }
    },
    "n8n_starter_12m": {
        "en": {
            "description": "⚡ N8N Starter 12m\n\n- Duration: 12 months\n- Official voucher code\n- 🚫 No warranty after the code is activated on your account\n\n⚠️ Please note that the code must be redeemed within 7 days of purchase. Codes not used within this period may expire and are no longer eligible for support or replacement.\n\n📊 Sold: 4 accounts"
        },
        "fr": {
            "description": "⚡ N8N Starter 12m\n\n- Durée : 12 mois\n- Code coupon officiel\n- 🚫 Aucune garantie après l'activation du code sur votre compte\n\n⚠️ Veuillez noter que le code doit être utilisé dans les 7 jours suivant l'achat. Les codes non utilisés durant cette période peuvent expirer et ne sont plus éligibles au support ni au remplacement.\n\n📊 Vendus : 4 comptes"
        }
    },
    "snapchat_3m": {
        "en": {
            "description": "👻 Snapchat Plus+ 3M FW available\n\n- Warranty: 90 days\n- Stock: manual activation accounts\n- Sold: 354 accounts\n\n❞ Description:\nActivate Snapchat+ and give your account a real Premium experience with exclusive features:\n\nNo password needed, only your username (ID)\n✅ Storage solution (depending on your plan)\n🎨 Amazing themes\n👑 A new and unique account look\n⚡ Fast and safe activation\n\n👌Activation method: send me only your Username in private and get fast activation 💨"
        },
        "fr": {
            "description": "👻 Snapchat Plus+ 3M FW disponible\n\n- Garantie : 90 jours\n- Stock : comptes à activation manuelle\n- Vendus : 354 comptes\n\n❞ Description :\nActivez Snapchat+ et offrez à votre compte une vraie expérience Premium avec des fonctionnalités exclusives :\n\nAucun mot de passe nécessaire, uniquement votre nom d'utilisateur (ID)\n✅ Solution de stockage (selon votre forfait)\n🎨 Thèmes magnifiques\n👑 Un look de compte nouveau et unique\n⚡ Activation rapide et sécurisée\n\n👌Méthode d'activation : envoyez-moi uniquement votre Username en privé pour une activation rapide 💨"
        }
    },
    "snapchat_6m": {
        "en": {
            "description": "👻 Snapchat Plus+ 6M FW available\n\n- Warranty: 180 days\n- Stock: manual activation accounts\n- Sold: 354 accounts\n\n❞ Description:\nActivate Snapchat+ and give your account a real Premium experience with exclusive features:\n\nNo password needed, only your account ID\nAndroid + iPhone\n✅ Storage solution (depending on your plan)\n🎨 Amazing themes\n👑 A new and unique account look\n⚡ Fast and safe activation\n\n👌Activation method: send me only your Username in private and get fast activation 💨"
        },
        "fr": {
            "description": "👻 Snapchat Plus+ 6M FW disponible\n\n- Garantie : 180 jours\n- Stock : comptes à activation manuelle\n- Vendus : 354 comptes\n\n❞ Description :\nActivez Snapchat+ et offrez à votre compte une vraie expérience Premium avec des fonctionnalités exclusives :\n\nAucun mot de passe nécessaire, uniquement l'ID de votre compte\nAndroid + iPhone\n✅ Solution de stockage (selon votre forfait)\n🎨 Thèmes magnifiques\n👑 Un look de compte nouveau et unique\n⚡ Activation rapide et sécurisée\n\n👌Méthode d'activation : envoyez-moi uniquement votre Username en privé pour une activation rapide 💨"
        }
    },
    "snapchat_12m": {
        "en": {
            "description": "👻 Snapchat Plus+ 12M FW available\n\n- Warranty: for the whole subscription period\n- Stock: manual activation accounts\n- Sold: 231 accounts\n\n❞ Description:\nActivate Snapchat+ and give your account a real Premium experience with exclusive features: for a full year\n\nNo password needed, only your account ID\nAndroid + iPhone\n✅ Storage solution (depending on your plan)\n🎨 Amazing themes\n👑 A new and unique account look\n⚡ Fast and safe activation\n\n👌Activation method: send me only your Username in private and get fast activation 💨"
        },
        "fr": {
            "description": "👻 Snapchat Plus+ 12M FW disponible\n\n- Garantie : pendant toute la durée de l'abonnement\n- Stock : comptes à activation manuelle\n- Vendus : 231 comptes\n\n❞ Description :\nActivez Snapchat+ et offrez à votre compte une vraie expérience Premium avec des fonctionnalités exclusives : pour une année complète\n\nAucun mot de passe nécessaire, uniquement l'ID de votre compte\nAndroid + iPhone\n✅ Solution de stockage (selon votre forfait)\n🎨 Thèmes magnifiques\n👑 Un look de compte nouveau et unique\n⚡ Activation rapide et sécurisée\n\n👌Méthode d'activation : envoyez-moi uniquement votre Username en privé pour une activation rapide 💨"
        }
    },
    "canva_edu_500": {
        "en": {
            "name": "Canva Edu Pro — 500 seats",
            "description": "🎨 Canva Edu Pro — 500 seats\n\n🔥 Canva Education account/dashboard for students and teachers\nEnjoy Canva's education benefits and Pro tools to create professional designs easily.\n\n✨ What do you get?\n- 🎓 Access to Canva education benefits.\n- 💎 Canva Pro tools and many professional features.\n- 📚 Ready-made education templates.\n- 🎨 Design presentations, posts, videos and educational files.\n- 🤖 AI tools such as Magic Write.\n\n📦 Capacity: 500 seats\n💰 Price: only 10$\n⚠️ Important: no warranty on this product.\n\n🚀 Suitable for students, teachers, designers and business owners"
        },
        "fr": {
            "name": "Canva Edu Pro — 500 places",
            "description": "🎨 Canva Edu Pro — 500 places\n\n🔥 Compte/tableau de bord Canva Éducation pour les étudiants et les enseignants\nProfitez des avantages éducatifs de Canva et des outils Pro pour créer facilement des designs professionnels.\n\n✨ Ce que vous obtenez :\n- 🎓 Accès aux avantages éducatifs de Canva.\n- 💎 Les outils Canva Pro et de nombreuses fonctionnalités professionnelles.\n- 📚 Modèles éducatifs prêts à l'emploi.\n- 🎨 Création de présentations, publications, vidéos et documents éducatifs.\n- 🤖 Outils d'IA comme Magic Write.\n\n📦 Capacité : 500 places\n💰 Prix : seulement 10$\n⚠️ Important : produit sans garantie.\n\n🚀 Idéal pour les étudiants, enseignants, designers et porteurs de projets"
        }
    },
    "canva_edu_5000": {
        "en": {
            "name": "Canva Edu Pro — 5000 seats",
            "description": "🎨 Canva Edu Pro — 5000 seats\n\n🔥 Canva Education account/dashboard\nAdd 5000 people with full control\n\n✨ What do you get?\n- 🎓 Access to Canva education benefits.\n- 💎 Canva Pro tools and many professional features.\n- 📚 Ready-made education templates.\n- 🎨 Design presentations, posts, videos and educational files.\n- 🤖 AI tools such as Magic Write.\n\n📦 Capacity: 5000 seats\n💰 Price: only 21.50$\n⚠️ Important: this product comes with a warranty\n\n🚀 Suitable for students, teachers, designers and business owners"
        },
        "fr": {
            "name": "Canva Edu Pro — 5000 places",
            "description": "🎨 Canva Edu Pro — 5000 places\n\n🔥 Compte/tableau de bord Canva Éducation\nAjoutez 5000 personnes avec un contrôle total\n\n✨ Ce que vous obtenez :\n- 🎓 Accès aux avantages éducatifs de Canva.\n- 💎 Les outils Canva Pro et de nombreuses fonctionnalités professionnelles.\n- 📚 Modèles éducatifs prêts à l'emploi.\n- 🎨 Création de présentations, publications, vidéos et documents éducatifs.\n- 🤖 Outils d'IA comme Magic Write.\n\n📦 Capacité : 5000 places\n💰 Prix : seulement 21,50$\n⚠️ Important : produit avec garantie\n\n🚀 Idéal pour les étudiants, enseignants, designers et porteurs de projets"
        }
    },
    "freefire_diamonds": {
        "en": {
            "description": "🔥 Free Fire Diamonds 💎 top-up in the fastest and easiest way! 🔥\n\nNeed to top up your account's diamonds? 💎\nWith our service you can top up Free Fire Diamonds with the ID only ✅\n\n🔒 No password or any account information needed\n⚡️ The top-up is fast, in just one minute after payment is completed and the ID is sent.\n\n💎 Package prices without bonus diamonds:\n\n110💎 ▶️ 1.45$\n\n231💎 ▶️ 2.20$\n\n583💎 ▶️ 5.05$\n\n1188💎 ▶️ 10.10$\n\n2420💎 ▶️ 19.50$\n\n📩 How to order:\n1️⃣ Contact us\n2️⃣ Choose the package that suits you\n3️⃣ Make the payment\n4️⃣ Send us only your account ID\n5️⃣ The diamonds are added to your account ⚡️\n\n🛡️ Warranty available ✅\n🚀 Fast execution\n🔐 We don't ask for any sensitive account information\n\n💎 Order your top-up now and enjoy the game! 🎮🔥"
        },
        "fr": {
            "description": "🔥 Recharge Free Fire Diamonds 💎 de la manière la plus rapide et la plus simple ! 🔥\n\nBesoin de recharger les diamants de votre compte ? 💎\nRechargez Free Fire Diamonds avec l'ID uniquement ✅\n\n🔒 Aucun mot de passe ni information de compte requis\n⚡️ Recharge en une minute après le paiement et l'envoi de l'ID.\n\n💎 Prix des packs sans diamants bonus :\n\n110💎 ▶️ 1.45$\n\n231💎 ▶️ 2.20$\n\n583💎 ▶️ 5.05$\n\n1188💎 ▶️ 10.10$\n\n2420💎 ▶️ 19.50$\n\n📩 Comment commander :\n1️⃣ Contactez-nous\n2️⃣ Choisissez le pack qui vous convient\n3️⃣ Effectuez le paiement\n4️⃣ Envoyez-nous uniquement l'ID de votre compte\n5️⃣ Les diamants sont ajoutés à votre compte ⚡️\n\n🛡️ Garantie disponible ✅\n🚀 Exécution rapide\n🔐 Aucune information sensible demandée\n\n💎 Commandez votre recharge maintenant et profitez du jeu ! 🎮🔥"
        }
    },
    "apple_gift_tr": {
        "en": {
            "name": "Apple Gift Card 🇹🇷 Turkish",
            "description": "🍎 Apple Gift Card 🇹🇷 — Turkey\n\nFor the Turkish App Store 📱\n💳 After payment you receive the activation code immediately.\n\nApple Gift Card. 10TRK ▶️ 1.00$\n\nApple Gift Card. 50TRK ▶️ 1.35$\n\nApple Gift Card. 100TRK ▶️ 2.50$\n\nApple Gift Card. 150TRK ▶️ 3.60$\n\nApple Gift Card. 200TRK ▶️ 5.00$\n\nApple Gift Card. 250TRK ▶️ 5.70$\n\n\n🛡️ Warranty: one hour from the time of purchase.\n(We have never had any problem with the codes.)"
        },
        "fr": {
            "name": "Apple Gift Card 🇹🇷 Turque",
            "description": "🍎 Apple Gift Card 🇹🇷 — Turquie\n\nDestinée à l'App Store turc 📱\n💳 Après le paiement, vous recevez immédiatement le code d'activation.\n\nApple Gift Card. 10TRK ▶️ 1.00$\n\nApple Gift Card. 50TRK ▶️ 1.35$\n\nApple Gift Card. 100TRK ▶️ 2.50$\n\nApple Gift Card. 150TRK ▶️ 3.60$\n\nApple Gift Card. 200TRK ▶️ 5.00$\n\nApple Gift Card. 250TRK ▶️ 5.70$\n\n\n🛡️ Garantie : une heure à partir de l'achat.\n(Nous n'avons jamais eu de problème avec les codes.)"
        }
    },
    "apple_gift_in": {
        "en": {
            "name": "Apple Gift Card 🇮🇳 Indian",
            "description": "🍎 Apple Gift Card 🇮🇳 — India\n\nCards for the Indian App Store 📱\n💳 After payment you receive the activation code immediately.\n\n🎁 Cards and prices:\n\nApple Gift Card >100INR ▶️ 1.40$\n\nApple Gift Card >200INR ▶️ 2,45$\n\nApple Gift Card >250INR ▶️ 3,05$\n\nApple Gift Card >500INR ▶️ 6,15$\n\nApple Gift Card >1000INR ▶️ 12$\n\nApple Gift Card 1500INR ▶️ 28,10$\n\n🛡️ Warranty: one hour from the time of purchase.\n(We have never had any problem with the codes.)"
        },
        "fr": {
            "name": "Apple Gift Card 🇮🇳 Indienne",
            "description": "🍎 Apple Gift Card 🇮🇳 — Inde\n\nCartes destinées à l'App Store indien 📱\n💳 Après le paiement, vous recevez immédiatement le code d'activation.\n\n🎁 Cartes et prix :\n\nApple Gift Card >100INR ▶️ 1.40$\n\nApple Gift Card >200INR ▶️ 2,45$\n\nApple Gift Card >250INR ▶️ 3,05$\n\nApple Gift Card >500INR ▶️ 6,15$\n\nApple Gift Card >1000INR ▶️ 12$\n\nApple Gift Card 1500INR ▶️ 28,10$\n\n🛡️ Garantie : une heure à partir de l'achat.\n(Nous n'avons jamais eu de problème avec les codes.)"
        }
    },
    "apple_gift_fr": {
        "en": {
            "name": "Apple Gift Card 🇫🇷 French",
            "description": "🍎 Apple Gift Card 🇫🇷 — France\n\nCards for the French App Store 📱\n💳 After payment you receive the activation code immediately.\n\n🎁 Cards and prices:\n\nApple Gift Card >2EUR ▶️ 2,45$\n\nApple Gift Card >10EUR ▶️ 12$\n\nApple Gift Card >20EUR ▶️ 23,65$\n\nApple Gift Card >50EUR ▶️ 59$\n\nApple Gift Card >75EUR ▶️ 89$\n\nApple Gift Card 100EUR ▶️ 116,22$\n\n🛡️ Warranty: one hour from the time of purchase.\n(We have never had any problem with the codes.)"
        },
        "fr": {
            "name": "Apple Gift Card 🇫🇷 Française",
            "description": "🍎 Apple Gift Card 🇫🇷 — France\n\nCartes destinées à l'App Store français 📱\n💳 Après le paiement, vous recevez immédiatement le code d'activation.\n\n🎁 Cartes et prix :\n\nApple Gift Card >2EUR ▶️ 2,45$\n\nApple Gift Card >10EUR ▶️ 12$\n\nApple Gift Card >20EUR ▶️ 23,65$\n\nApple Gift Card >50EUR ▶️ 59$\n\nApple Gift Card >75EUR ▶️ 89$\n\nApple Gift Card 100EUR ▶️ 116,22$\n\n🛡️ Garantie : une heure à partir de l'achat.\n(Nous n'avons jamais eu de problème avec les codes.)"
        }
    }
}


# ---------- حفظ لغة كل زبون ----------
LANG_FILE = "user_lang.json"
try:
    with open(LANG_FILE, encoding="utf-8") as f:
        user_lang = json.load(f)
except Exception:
    user_lang = {}


def save_langs():
    try:
        with open(LANG_FILE, "w", encoding="utf-8") as f:
            json.dump(user_lang, f)
    except Exception as e:
        print(f"Could not save languages: {e}")


def get_lang(user_id):
    lang = user_lang.get(str(user_id), "ar")
    return lang if lang in SUPPORTED_LANGS else "ar"


def t(lang, key):
    return TEXTS.get(lang, TEXTS["ar"])[key]


def tr(item, field, lang):
    if lang != "ar":
        value = TRANSLATIONS.get(item["id"], {}).get(lang, {}).get(field)
        if value:
            return value
    return item[field]


def set_user_commands(chat_id, lang):
    # زر Menu: "تغيير اللغة" و"الدعم" بلغة الزبون
    if BotCommand is None:
        return
    try:
        bot.set_my_commands(
            [
                BotCommand("language", t(lang, "cmd_language")),
                BotCommand("support", t(lang, "cmd_support")),
            ],
            scope=BotCommandScopeChat(chat_id),
        )
    except Exception as e:
        print(f"Could not set commands: {e}")


def set_default_commands():
    # القائمة الافتراضية (قبل ما يختار الزبون لغته)
    if BotCommand is None:
        return
    try:
        bot.set_my_commands(
            [
                BotCommand("language", "🌐 اللغة / Language / Langue"),
                BotCommand("support", "💬 الدعم / Support"),
            ]
        )
    except Exception as e:
        print(f"Could not set default commands: {e}")


def find_product(product_id):
    return next((p for p in products if p["id"] == product_id), None)


def generate_store_keyboard(lang):
    markup = InlineKeyboardMarkup(row_width=2)
    for item in products:
        if item.get("type") == "separator":
            markup.add(InlineKeyboardButton(text=tr(item, "text", lang), callback_data="noop"))
            continue
        stock_display = item["stock"] if item["stock"] == "♾️" else f"📦 {item['stock']}"
        button_text = f"{item['icon']} {tr(item, 'name', lang)} | {item['price']} | {stock_display}"
        markup.add(InlineKeyboardButton(text=button_text, callback_data=f"buy_{item['id']}"))
    markup.add(InlineKeyboardButton(text=t(lang, "change_lang"), callback_data="change_lang"))
    return markup


def send_language_menu(chat_id):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
        InlineKeyboardButton(text="🇩🇿 العربية", callback_data="lang_ar"),
        InlineKeyboardButton(text="🇫🇷 Français", callback_data="lang_fr"),
    )
    try:
        bot.send_photo(chat_id, UNIFIED_IMAGE_URL, caption=CHOOSE_LANG_TEXT, reply_markup=markup)
    except Exception:
        bot.send_message(chat_id, CHOOSE_LANG_TEXT, reply_markup=markup)


def send_main_menu(chat_id, lang):
    caption = t(lang, "welcome")
    try:
        bot.send_photo(chat_id, UNIFIED_IMAGE_URL, caption=caption, reply_markup=generate_store_keyboard(lang))
    except Exception:
        bot.send_message(chat_id, caption, reply_markup=generate_store_keyboard(lang))


@bot.message_handler(commands=["start"])
def send_welcome(message):
    uid = str(message.from_user.id)
    if uid in user_lang:
        set_user_commands(message.chat.id, get_lang(uid))
        send_main_menu(message.chat.id, get_lang(uid))
    else:
        send_language_menu(message.chat.id)


@bot.message_handler(commands=["language", "lang"])
def choose_language(message):
    send_language_menu(message.chat.id)


@bot.message_handler(commands=["support"])
def support_command(message):
    lang = get_lang(message.from_user.id)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text=t(lang, "support_btn"), url=MY_PRIVATE_CHAT_LINK))
    bot.send_message(message.chat.id, t(lang, "support_msg"), reply_markup=markup)


def notify_admin(user, product, lang):
    try:
        username = f"@{user.username}" if user.username else user.first_name
        text = (
            f"🔔 <b>زبون اختار منتج من المتجر</b>\n\n"
            f"👤 الزبون: {html.escape(username)} (ID: <code>{user.id}</code>)\n"
            f"📦 المنتج: <b>{html.escape(product['name'])}</b>\n"
            f"💰 السعر: <b>{html.escape(product['price'])}</b>\n"
            f"🌐 اللغة: {lang}"
        )
        bot.send_message(ADMIN_CHAT_ID, text, parse_mode="HTML")
    except Exception as e:
        print(f"Error sending admin notification: {e}")


# ---------- اختيار اللغة ----------
@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def handle_set_lang(call):
    lang = call.data.replace("lang_", "")
    if lang not in SUPPORTED_LANGS:
        bot.answer_callback_query(call.id)
        return
    user_lang[str(call.from_user.id)] = lang
    save_langs()
    set_user_commands(call.message.chat.id, lang)
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    send_main_menu(call.message.chat.id, lang)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == "change_lang")
def handle_change_lang(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    send_language_menu(call.message.chat.id)
    bot.answer_callback_query(call.id)


# ---------- عرض المنتج ----------
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def handle_product_view(call):
    product_id = call.data.replace("buy_", "")
    selected_product = find_product(product_id)
    if not selected_product:
        bot.answer_callback_query(call.id)
        return

    lang = get_lang(call.from_user.id)

    # إشعار فوري لك عند اختيار الزبون للمنتج
    notify_admin(call.from_user, selected_product, lang)

    markup = InlineKeyboardMarkup()

    # زر "اطلب الآن" يوجه الزبون للخاص المباشر
    markup.add(InlineKeyboardButton(text=t(lang, "order_now"), url=MY_PRIVATE_CHAT_LINK))
    markup.add(InlineKeyboardButton(text=t(lang, "join_channel"), url=CHANNEL_LINK))

    stock_val = selected_product["stock"]
    if stock_val == "♾️" or (isinstance(stock_val, int) and stock_val > 0):
        caption_bottom = t(lang, "buy_hint")
    else:
        caption_bottom = t(lang, "out_of_stock")
        markup.add(InlineKeyboardButton(text=t(lang, "notify_me"), callback_data=f"notify_{selected_product['id']}"))

    markup.add(InlineKeyboardButton(text=t(lang, "back"), callback_data="back_to_main"))

    display_stock = "♾️" if stock_val == "♾️" else str(stock_val)
    caption = (
        f"{t(lang, 'chosen')} *{tr(selected_product, 'name', lang)}*\n"
        f"{t(lang, 'price')} *{selected_product['price']}*\n"
        f"{t(lang, 'available')} *{display_stock}*\n\n"
        f"{t(lang, 'description')}\n{tr(selected_product, 'description', lang)}\n\n"
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
    send_main_menu(call.message.chat.id, get_lang(call.from_user.id))
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("notify_"))
def handle_notify(call):
    bot.answer_callback_query(
        call.id,
        text=t(get_lang(call.from_user.id), "notify_ok"),
        show_alert=True,
    )


set_default_commands()

print("Bot is running...")
bot.infinity_polling()
