# -*- coding: utf-8 -*-
# ============================================================
# main.py  — ملف التحديث الوحيد
# يقرأ الكود القديم من bot_base.py (هو نفسه main.py القديم بعد إعادة تسميته)
# ويطبّق عليه التعديلات: طلبات يدوية A/B + محفظة + جرس التوفر + سجل الطلبات.
# ============================================================
import os, sys

# ===== إعدادات يمكنك تعديلها =====
GIFT_MAX_QTY = 3      # أقصى كمية في بطاقات الهداية
GEMINI_MAX_QTY = 5    # أقصى كمية في Gemini (حسب المتوفر في المخزون)
REF_NEED_USERS = 20   # عدد المحالين النشطين المطلوب
REF_NEED_USD = 10     # مجموع مشتريات المحالين المطلوب ($)
REF_REWARD_USD = 1    # مكافأة الإحالة ($)
DAILY_GIFT_COINS = 10  # هدية Raseedkom Coins اليومية
SW_PRIZE_COINS = 25    # جائزة تحدي التوقيت
SW_TOLERANCE = 0.30    # الفارق المسموح (ثانية) لاعتبار الإيقاف مطابقاً للهدف
SW_ATTEMPTS = 2        # عدد المحاولات كل 24 ساعة
MATCH_COMPETITIONS = "PL,PD,SA,BL1,FL1,CL"   # الدوريات الخمسة الكبرى + دوري الأبطال
MATCH_MIN_STAKE = 5    # أقل مبلغ مشاركة (كوينز)
MATCH_REMIND_MINUTES = 10   # التذكير قبل صافرة البداية (بالدقائق)
PURCHASE_COINS = 10    # كوينز عند كل عملية شراء
REF_COINS = 10         # كوينز لصاحب الرابط عن كل صديق ينضم
REF_COINS_DAILY_CAP = 20   # أقصى عدد إحالات تمنح كوينز يومياً لكل زبون (حماية من الحسابات الوهمية)
# منتجاتك الخاصة المخفية دائماً (Prime Video: يُباع من المورّد فقط). لإرجاع منتج احذفه من هنا.
REMOVED_OWN = {"capcut_1m", "n8n_starter_12m", "office365_1y", "elevenlabs_3m", "duolingo_12m", "duolingo_link_12m"}   # منتجات محذوفة نهائياً من القوائم ولوحة الأدمن (تبقى في الكود لأجل الطلبات القديمة)
OWN_ALWAYS_HIDDEN = {"capcut_1m", "n8n_starter_12m", "office365_1y", "elevenlabs_3m", "duolingo_12m", "duolingo_link_12m", "amazon_prime_6m", "prime_video_ultra_6m", "chatgpt_plus_1m", "chatgpt_k12_edu",
                     "claude_100_30d", "claude_10m_1d"}   # Claude القديم (قبل الربط بالمورّد) محذوف نهائياً من القائمة
VENTE_MARGIN_PCT = 30       # نسبة ربحك فوق سعر المورّد (%)
# استثناءات نسبة الربح بالاسم (regex ← %): Higgsfield بربح 25% بدل 30%
VENTE_MARGIN_OVERRIDE = [(r"higgsfield", 25)]
# منتجات supplier_api المسموح بيعها (جُرّب Gemini Plus 6: يرجع COMPLETED فوراً مع رابط في account_data بدون بيانات من الزبون)
VENTE_API_OK = [r"gemini plus 6", r"apple music", r"picsart", r"higgsfield"]
VENTE_MAX_QTY = 3           # أقصى كمية في منتجات المورّد
VENTE_REFRESH_SECONDS = 300 # تحديث الكتالوج كل كم ثانية
VENTE_LOW_BALANCE = 10      # تنبيه إذا نزل رصيدك عند المورّد عن هذا ($)
# منتجات المورّد المخفية افتراضياً (regex على الاسم). يمكن إظهارها بـ /vente_show ID
# منتجات تتطلب من الزبون تفعيل كود على حسابه (مخفية بطلبك)
VENTE_HIDE_ACTIVATE = [r"^jam\b", r"^gamma\b", r"posthog", r"^supercut", r"^airtable", r"^runway", r"quizlet"]
VENTE_DEFAULT_HIDE = VENTE_HIDE_ACTIVATE + [r"mobbin\s*pro\s*1\s*year", r"railway.*hobby", r"crunchyroll.*link"]
# ربط Gemini الافتراضي: منتجك الخاص ← رقم منتج Gemini عند المورّد (يغيّره /vente_link)
VENTE_DEFAULT_LINK = {"gemini_18m": 28}
# منتجاتك التي يحلّ محلها منتج المورّد (إذا وُجد عنده منتج مطابق للاسم) — تتغيّر بـ /vente_replace
VENTE_REPLACE_DEFAULT = {
    "capcut_1m": r"capcut", "duolingo_12m": r"duolingo", "duolingo_link_12m": r"duolingo", "nordvpn_3m": r"nord",
    "n8n_starter_12m": r"n8n", "office365_1y": r"office|microsoft", "elevenlabs_3m": r"eleven",
    "chatgpt_plus_1m": r"chatgpt", "chatgpt_k12_edu": r"chatgpt",
}
REDOTPAY_ID = "1947886487"   # معرّف حسابك في RedotPay الذي يستقبل التحويلات اليدوية
REDOTPAY_PCT = 3       # كاش باك المنتجات العادية عند الدفع عبر RedotPay فقط (بدل 5%)
REDOTPAY_GIFT_PCT = 1  # كاش باك بطاقات الهدايا عند الدفع عبر RedotPay فقط (بدل 2%)
MATCH_BONUS_PCT = 50   # مكافأة تلقائية للفائز في التوقعات: نسبة من مبلغ مشاركته

# ===== المنتجات الجديدة (تسليم يدوي) =====
_CLAUDE_URL = "https://docs.google.com/document/d/1yxSEreqNY9VaqCa5Whzv2Q_Z7-0RDKdKk0csM5l7aIw/edit?usp=sharing"
_MIRAI_DOC = "https://docs.google.com/document/d/16smXXteTwJYdrxTfdZlJvOkSEFkVL_6UBxoXcXZH6Gc/edit?tab=t.tbg84q5rs9yi"

NEW_PRODUCTS = [
    {
        "id": "prime_video_ultra_6m",
        "name": "PRIME VIDEO ULTRA 6M 6 PROFILE",
        "price": "$5.00",
        "stock": 10,
        "icon": "📺",
        "description": "📺 PRIME VIDEO ULTRA 6 أشهر - 6 بروفايلات\n\nالمدة: 180 يوماً ⭐️\n\nالباقة: بدون إعلانات 4K ✅\n\nوصول كامل وخاص بالكامل 🔒\n\nممنوع الاستئجار أو شراء أي شيء ❌\n\nممنوع القيام بأي نشاط غير معتاد ❌\n\nبدون ضمان",
    },
    {
        "id": "amazon_prime_6m",
        "name": "Amazon prime 6 months video 6 profile",
        "price": "$5.00",
        "stock": 10,
        "icon": "📦",
        "description": "أمازون برايم فيديو – 6 أشهر\n\nاستمتع بـ 6 أشهر من Amazon Prime Video وشاهد آلاف الأفلام الشهيرة والبرامج التلفزيونية وإنتاجات Amazon Originals والمحتوى الحصري.\n\nالميزات:\n\n- 🎬 وصول غير محدود إلى مكتبة Prime Video الواسعة\n- ⭐ مسلسلات وأفلام Amazon Original الحصرية\n- 👥 6 ملفات تعريف – إنشاء وإدارة ما يصل إلى 6 ملفات تعريف فردية\n- 🔒 تغيير أسماء ملفات التعريف وإعداد حماية برمز PIN لكل ملف تعريف\n- 📱 المشاهدة على أجهزة متعددة مدعومة\n- ⬇️ تنزيل المحتوى للمشاهدة دون اتصال بالإنترنت\n- 🎥 البث بدقة HD و 4K Ultra HD (حيثما يتوفر)\n- 🌍 شاهد في أي وقت وفي أي مكان باستخدام حساب Amazon الخاص بك",
    },
    {
        "id": "claude_100_30d",
        "name": "Claude 100$ Api 30 D warranty",
        "price": "$3.10",
        "stock": 10,
        "icon": "🧠",
        "description": "🔑 100$ API Claude - 30 يوماً\n• يعمل مع جميع التطبيقات: 9router، claude code، codex، cursor، إلخ.\n• ضمان كامل (BHF).\nالتفعيل ومفتاح API: https://api.mwapi.dev/\n• دليل مفصل: " + _CLAUDE_URL,
    },
    {
        "id": "claude_10m_1d",
        "name": "API 10M Token Claude 1Day Warranty",
        "price": "$2.25",
        "stock": 10,
        "icon": "🧠",
        "description": "🔑 API CLAUDE - 10 مليون رمز - يوم واحد\n⚡ متوافق بسلاسة مع جميع الأدوات وبيئات التطوير: 9router، Claude Dev، Cursor، VS Code، إلخ.\n⏳ الصلاحية: يوم واحد\n\n📋 تعليمات الإعداد السريع:\n🔹 الخطوة 1: قم بزيارة 👉 https://miraiapi.com/usage/#redeem لاسترداد رمزك (أدخل الرمز المقدم في تفاصيل طلبك).\n🔹 الخطوة 2: قم بزيارة 👉 https://miraiapi.com/usage/#config لتكوين مفتاح API الخاص بك، واختيار التطبيق المستهدف، وتحديد النموذج المثالي.\n✨ كل شيء جاهز للبرمجة!\n\n🌐 عنوان URL الأساسي: https://api.miraiapi.com/v1\n🔑 مفتاح API: sk-...\n🤖 النماذج المتاحة:\n  ⚡ claude-opus-4.6\n  ⚡ claude-opus-4.7\n  ⚡ claude-opus-4.8\n  👑 claude-opus-5\n  🚀 claude-sonnet-5\n📊 تحقق من رصيد حصتك وتاريخ انتهاء الصلاحية على: 🔗 https://miraiapi.com/usage/\n\n📖 الوثائق والدليل المفصل: 🔗 " + _MIRAI_DOC + "\n\n⚠️ ملاحظة مهمة: تبدأ فترة الصلاحية فقط بمجرد تفعيل رمز الاسترداد. يمكنك تخزين الرمز أو إعادة بيعه لمدة تصل إلى 30 يوماً.",
    },
    {
        "id": "chatgpt_plus_1m",
        "name": "Chatgpt plus 1M (Google pay)Gmail NW",
        "price": "$9.00",
        "stock": 10,
        "icon": "🤖",
        "description": "ChatGPT Plus لمدة شهر - حساب خاص\nكل الحسابات مجرّبة وتعمل\nGmail أو @googlemail.com\nبدون ضمان\nتسجيل الدخول إلى ChatGPT\nالصيغة: الإيميل / كلمة المرور / 2FA\nموقع 2FA: https://2fa-auth.com\n⁉️ ملاحظة: يجب على الزبون تثبيت مفتاح مرور (passkey) وتغيير كلمة المرور و2FA وإيميل الحساب مباشرة بعد الشراء.\nغيّر 2FA خلال ساعة واحدة\nتحقق من حسابك خلال ساعة واحدة",
    },
    {
        "id": "chatgpt_k12_edu",
        "name": "ChatGPT - GPT K12 Edu (W5H)",
        "price": "$5.00",
        "stock": 10,
        "icon": "🎓",
        "description": "N/A",
    },
    {
        "id": "office365_1y",
        "name": "Microsoft Office 365 Plus 1 year",
        "price": "$2.00",
        "stock": 10,
        "icon": "🛍️",
        "description": "🛍️ مايكروسوفت أوفيس 365 بلس لمدة سنة واحدة\n\nالتطبيقات المشمولة:\n\nWord · Excel · PowerPoint · OneNote · Forms\nالتخزين السحابي:\n\n100 جيجابايت ون درايف متضمنة\nالتوافق:\n\nWindows · macOS · Android · iOS\nطريقة العمل:\n\nبعد الدفع، ستتلقى بيانات تسجيل الدخول (اسم المستخدم / كلمة المرور) لتفعيل أوفيس 365 على أجهزتك.\nمدة الاشتراك: 12 شهراً\n⚠️ قم بتغيير كلمة المرور عند تسجيل الدخول لأول مرة\n🔗 تسجيل الدخول: https://portal.office.com",
    },
    {
        "id": "elevenlabs_3m",
        "name": "ElevenLabs Creator 3 Months",
        "price": "$16.00",
        "stock": 10,
        "icon": "🎙️",
        "description": "• يتم استرداد القسيمة على صفحة دفع Stripe\n• تُسترد على حسابك الخاص\n• تمنح 121 ألف رصيد شهرياً\n• الضمان بعد التفعيل - شهر واحد\n• يجب استردادها خلال 7 أيام من الشراء\n• يمكنك أيضاً استردادها عبر: https://elevenlabs.io/signup?coupon=YOURCODE",
    },
    {
        "id": "iptv_14m",
        "name": "IPTV 14 شهراً",
        "price": "$14.99",
        "stock": 1,
        "icon": "📡",
        "description": '📺 IPTV لمدة 14 شهراً\n\n• Android TV / الشاشات الذكية 📺\n\nافتح Google Play 🔍\nحمّل التطبيق\n🔗 NEXT+\n\nفي خانة الاسم ✏️ اكتب أي اسم عشوائي\nثم أدخل اسم المستخدم + كلمة المرور 🔑\n\nفي خانة السيرفر 🖥 اكتب 5544\n\n──────────────\nخيار بديل 🔁\n\nافتح Google Play 🔍\nحمّل تطبيق Downloadr 🟡\n\nافتح التطبيق وأدخل هذا الرقم 🔗\n2231346\n\nحمّل السيرفر على شاشتك 📡\nسجّل الدخول باسم المستخدم + كلمة المرور 🔑\n──────────────\n\nيعمل على جميع الأجهزة\nعلى iPhone: حمّل تطبيق VAR\nرابط السيرفر:\n\nhttps://device.sabplayer.com/list/',
    },
]

NEW_TRANSLATIONS = {
    "prime_video_ultra_6m": {
        "en": {"description": "📺PRIME VIDEO ULTRA 6M 6 PROFILE\n\nDURATION : 180 DAYS⭐️\n\nPLAN : ADS FREE 4K ✅\n\nFULL ACCESS FULL PRIVATE🔒\n\nDO NOT RENT OR PURCHASE ANYTHING ❌\n\nDO NOT DO ANY UNSUAL ACTIVITIES ❌\n\n No warranty"},
        "fr": {"description": "📺 PRIME VIDEO ULTRA 6 mois - 6 profils\n\nDURÉE : 180 JOURS ⭐️\n\nFORFAIT : SANS PUB 4K ✅\n\nACCÈS COMPLET ET 100 % PRIVÉ 🔒\n\nNE LOUEZ NI N'ACHETEZ RIEN ❌\n\nN'EFFECTUEZ AUCUNE ACTIVITÉ INHABITUELLE ❌\n\nSans garantie"},
    },
    "amazon_prime_6m": {
        "en": {"description": "Amazon Prime Video – 6 months\n\nEnjoy 6 months of Amazon Prime Video and watch thousands of popular movies, TV shows, Amazon Originals and exclusive content.\n\nFeatures:\n\n- 🎬 Unlimited access to the vast Prime Video library\n- ⭐ Exclusive Amazon Original series and movies\n- 👥 6 profiles – create and manage up to 6 individual profiles\n- 🔒 Rename profiles and protect each profile with a PIN\n- 📱 Watch on multiple supported devices\n- ⬇️ Download content to watch offline\n- 🎥 Stream in HD and 4K Ultra HD (where available)\n- 🌍 Watch anytime, anywhere with your Amazon account"},
        "fr": {"description": "Amazon Prime Video – 6 mois\n\nProfitez de 6 mois d'Amazon Prime Video et regardez des milliers de films populaires, d'émissions TV, de productions Amazon Originals et de contenus exclusifs.\n\nCaractéristiques :\n\n- 🎬 Accès illimité à la vaste bibliothèque Prime Video\n- ⭐ Séries et films exclusifs Amazon Original\n- 👥 6 profils – créez et gérez jusqu'à 6 profils individuels\n- 🔒 Renommez les profils et protégez chaque profil par un code PIN\n- 📱 Visionnage sur plusieurs appareils compatibles\n- ⬇️ Téléchargement du contenu pour un visionnage hors ligne\n- 🎥 Streaming en HD et 4K Ultra HD (selon disponibilité)\n- 🌍 Regardez à tout moment et en tout lieu avec votre compte Amazon"},
    },
    "claude_100_30d": {
        "en": {"description": "🔑 100$ Claude API - 30 days\n• Works with all apps: 9router, claude code, codex, cursor, etc.\n• Full warranty (BHF).\nActivation and API key: https://api.mwapi.dev/\n• Detailed guide: " + _CLAUDE_URL},
        "fr": {"description": "🔑 API Claude 100$ - 30 jours\n• Fonctionne avec toutes les applications : 9router, claude code, codex, cursor, etc.\n• Garantie complète (BHF).\nActivation et clé API : https://api.mwapi.dev/\n• Guide détaillé : " + _CLAUDE_URL},
    },
    "claude_10m_1d": {
        "en": {"description": "🔑 CLAUDE API - 10 million tokens - 1 day\n⚡ Works seamlessly with all tools and development environments: 9router, Claude Dev, Cursor, VS Code, etc.\n⏳ Validity: 1 day\n\n📋 Quick setup instructions:\n🔹 Step 1: Visit 👉 https://miraiapi.com/usage/#redeem to redeem your token (enter the code provided in your order details).\n🔹 Step 2: Visit 👉 https://miraiapi.com/usage/#config to configure your API key, choose the target application and select the ideal model.\n✨ Everything is ready for coding!\n\n🌐 Base URL: https://api.miraiapi.com/v1\n🔑 API key: sk-...\n🤖 Available models:\n  ⚡ claude-opus-4.6\n  ⚡ claude-opus-4.7\n  ⚡ claude-opus-4.8\n  👑 claude-opus-5\n  🚀 claude-sonnet-5\n📊 Check your quota balance and expiry date at: 🔗 https://miraiapi.com/usage/\n\n📖 Documentation and detailed guide: 🔗 " + _MIRAI_DOC + "\n\n⚠️ Important note: the validity period only starts once the redeem code is activated. You can store the code or resell it for up to 30 days."},
        "fr": {"description": "🔑 API CLAUDE - 10 millions de tokens - 1 jour\n⚡ Compatible avec tous les outils et environnements de développement : 9router, Claude Dev, Cursor, VS Code, etc.\n⏳ Validité : 1 jour\n\n📋 Instructions de configuration rapide :\n🔹 Étape 1 : Rendez-vous sur 👉 https://miraiapi.com/usage/#redeem pour utiliser votre jeton (saisissez le code fourni dans les détails de votre commande).\n🔹 Étape 2 : Rendez-vous sur 👉 https://miraiapi.com/usage/#config pour configurer votre clé API, choisir l'application cible et sélectionner le modèle idéal.\n✨ Tout est prêt pour coder !\n\n🌐 URL de base : https://api.miraiapi.com/v1\n🔑 Clé API : sk-...\n🤖 Modèles disponibles :\n  ⚡ claude-opus-4.6\n  ⚡ claude-opus-4.7\n  ⚡ claude-opus-4.8\n  👑 claude-opus-5\n  🚀 claude-sonnet-5\n📊 Vérifiez le solde de votre quota et la date d'expiration sur : 🔗 https://miraiapi.com/usage/\n\n📖 Documentation et guide détaillé : 🔗 " + _MIRAI_DOC + "\n\n⚠️ Remarque importante : la période de validité ne commence qu'à l'activation du code de remboursement (redeem). Vous pouvez conserver le code ou le revendre pendant 30 jours maximum."},
    },
    "chatgpt_plus_1m": {
        "en": {"description": "Chat gpt plus 1 month  private \nall tested and working\nGmail or @googlemail.com\nNo warranty \nLogin chatgpt \nFormat:Email/password/2fe\n2fe:https://2fa-auth.com\n⁉️ Note: Customers are required to install a passkey to change their password, 2FA, and email account immediately after purchase.\nChange your 2fe within 1 h\nCheck your account within 1 h"},
        "fr": {"description": "ChatGPT Plus 1 mois - compte privé\nTous les comptes sont testés et fonctionnels\nGmail ou @googlemail.com\nSans garantie\nConnexion à ChatGPT\nFormat : e-mail / mot de passe / 2FA\nSite 2FA : https://2fa-auth.com\n⁉️ Remarque : le client doit installer une clé d'accès (passkey) et changer immédiatement après l'achat son mot de passe, son 2FA et l'e-mail du compte.\nChangez votre 2FA dans l'heure qui suit\nVérifiez votre compte dans l'heure qui suit"},
    },
    "office365_1y": {
        "en": {"description": "🛍️ Microsoft Office 365 Plus for 1 year\n\nIncluded apps:\n\nWord · Excel · PowerPoint · OneNote · Forms\nCloud storage:\n\n100 GB OneDrive included\nCompatibility:\n\nWindows · macOS · Android · iOS\nHow it works:\n\nAfter payment, you will receive your login details (username / password) to activate Office 365 on your devices.\nSubscription duration: 12 months\n⚠️ Change the password when you log in for the first time\n🔗 Login: https://portal.office.com"},
        "fr": {"description": "🛍️ Microsoft Office 365 Plus pour 1 an\n\nApplications incluses :\n\nWord · Excel · PowerPoint · OneNote · Forms\nStockage cloud :\n\n100 Go OneDrive inclus\nCompatibilité :\n\nWindows · macOS · Android · iOS\nFonctionnement :\n\nAprès le paiement, vous recevrez vos identifiants (nom d'utilisateur / mot de passe) pour activer Office 365 sur vos appareils.\nDurée de l'abonnement : 12 mois\n⚠️ Changez le mot de passe lors de la première connexion\n🔗 Connexion : https://portal.office.com"},
    },
    "elevenlabs_3m": {
        "en": {"description": "• The voucher is redeemed on the Stripe checkout page\n• It is redeemed on your own account\n• Gives 121K credits per month\n• Warranty after activation - 1 month\n• Must be redeemed within 7 days of purchase\n• You can also redeem it via: https://elevenlabs.io/signup?coupon=YOURCODE"},
        "fr": {"description": "• Le bon est utilisé sur la page de paiement Stripe\n• Il est utilisé sur votre propre compte\n• Donne 121 000 crédits par mois\n• Garantie après activation - 1 mois\n• À utiliser dans les 7 jours suivant l'achat\n• Vous pouvez aussi l'utiliser via : https://elevenlabs.io/signup?coupon=YOURCODE"},
    },
    "iptv_14m": {
        "en": {"name": "IPTV 14 months", "description": '📺 IPTV 14 months\n\n• Android TV / Smart Screen 📺\n\nOpen Google Play 🔍\nDownload the app\n🔗 NEXT+\n\nIn the name field ✏️ enter any random name\nThen enter your Username + Password 🔑\n\nIn the server field 🖥 type 5544\n\n──────────────\nAlternative option 🔁\n\nOpen Google Play 🔍\nDownload the Downloadr app 🟡\n\nOpen the app and enter this number 🔗\n2231346\n\nLoad the server on your screen 📡\nSign in with your Username + Password 🔑\n──────────────\n\nWorks on all devices\nOn iPhone, download the VAR app\nServer link:\n\nhttps://device.sabplayer.com/list/'},
        "fr": {"name": "IPTV 14 mois", "description": "📺 IPTV 14 mois\n\n• Android TV / Écran connecté 📺\n\nOuvrez Google Play 🔍\nTéléchargez l'application\n🔗 NEXT+\n\nDans le champ du nom ✏️ saisissez un nom aléatoire\nPuis saisissez votre nom d'utilisateur + mot de passe 🔑\n\nDans le champ serveur 🖥 tapez 5544\n\n──────────────\nOption alternative 🔁\n\nOuvrez Google Play 🔍\nTéléchargez l'application Downloadr 🟡\n\nOuvrez l'application et saisissez ce numéro 🔗\n2231346\n\nChargez le serveur sur votre écran 📡\nConnectez-vous avec votre nom d'utilisateur + mot de passe 🔑\n──────────────\n\nFonctionne sur tous les appareils\nSur iPhone, téléchargez l'application VAR\nLien du serveur :\n\nhttps://device.sabplayer.com/list/"},
    },
}

# ===== بطاقات الهدايا الجديدة (تسليم تلقائي من FAZER) =====
NEW_GIFT_VARIANTS = {
    "apple_gift_us": [("2 USD", "2.15"), ("5 USD", "5.15"), ("10 USD", "10.20"), ("20 USD", "20.50"), ("30 USD", "31.00")],
    "gplay_us": [("5 USD", "5.20"), ("10 USD", "10.70"), ("15 USD", "15.70"), ("20 USD", "20.81"), ("50 USD", "53.00"), ("100 USD", "103.00")],
    "gplay_fr": [("10 EUR", "12.00"), ("15 EUR", "18.00"), ("25 EUR", "30.10"), ("50 EUR", "60.00"), ("100 EUR", "119.00")],
    "gplay_br": [("10 BRL", "2.20"), ("30 BRL", "5.90"), ("50 BRL", "11.00"), ("100 BRL", "22.10"), ("150 BRL", "34.00")],
    "gplay_in": [("10 INR", "0.71"), ("50 INR", "0.98"), ("100 INR", "1.37"), ("1000 INR", "11.11"), ("1500 INR", "18.00")],
    "gplay_tr": [("50 TRY", "1.31"), ("100 TRY", "2.30"), ("250 TRY", "5.50"), ("500 TRY", "12.00")],
    "steam_us": [("5 USD", "5.80"), ("20 USD", "23.20"), ("25 USD", "29.00"), ("30 USD", "33.00"), ("50 USD", "54.00"), ("100 USD", "110.00")],
    "steam_id": [("6000 IDR", "1.00"), ("8000 IDR", "1.10"), ("12000 IDR", "1.30"), ("45000 IDR", "3.60"), ("60000 IDR", "5.00")],
    "psn_us": [("1 USD", "1.26"), ("2 USD", "2.24"), ("4 USD", "4.04"), ("10 USD", "10.03"), ("25 USD", "23.70"), ("50 USD", "47.38"), ("100 USD", "96.48"), ("150 USD", "142.13")],
    "psn_fr": [("10 EUR", "11.53"), ("20 EUR", "22.92"), ("50 EUR", "57.18"), ("60 EUR", "68.77"), ("80 EUR", "91.56"), ("100 EUR", "114.42"), ("200 EUR", "228.89")],
    "psn_tr": [("250 TRY", "5.22"), ("500 TRY", "10.45"), ("750 TRY", "15.66"), ("1000 TRY", "20.89"), ("1500 TRY", "31.33"), ("2000 TRY", "41.77"), ("2500 TRY", "52.21"), ("3000 TRY", "63.15"), ("4000 TRY", "83.53"), ("5000 TRY", "104.41")],
    "psn_br": [("60 BRL", "11.11"), ("100 BRL", "18.52"), ("150 BRL", "27.79"), ("250 BRL", "46.58"), ("300 BRL", "55.57"), ("360 BRL", "66.68"), ("400 BRL", "74.53"), ("530 BRL", "98.17")],
    "pubg_uc": [("60 UC", "1.14"), ("325 UC", "4.77"), ("660 UC", "9.30"), ("1800 UC", "23.23"), ("3850 UC", "47.12"), ("8100 UC", "93.98")],
    "fc26_points": [("1050 FC Points", "9.62"), ("2800 FC Points", "22.66"), ("5900 FC Points", "48.14"), ("12000 FC Points", "96.27")],
    "pubg_gcoin": [("100 G-Coin", "1.20"), ("500 + 10 G-Coin", "5.00"), ("1000 + 50 G-Coin", "9.80"), ("2500 + 200 G-Coin", "24.00")],
    "freefire_codes": [("100 + 10 💎", "1.40"), ("210 + 21 💎", "2.40"), ("530 + 53 💎", "5.10"), ("1080 + 108 💎", "10.30"), ("2200 + 220 💎", "20.00")],
}

def _gift_price_range(pid):
    vals = [float(p) for _, p in NEW_GIFT_VARIANTS[pid]]
    return f"${min(vals):.2f} - ${max(vals):.2f}"

# ---- نصوص الأوصاف (3 لغات) ----
_APPLE_US_DESC = {
    "ar": "🍎 Apple Gift Card 🇺🇸 — أمريكا\n\nبطاقات مخصّصة لمتجر App Store الأمريكي 📱\n✅ للايفون والايباد (حسابات Apple ID الأمريكية فقط).\n💳 عند الدفع يصلك كود التفعيل مباشرة.\n\n🛡️ الضمان: ساعة واحدة من وقت الشراء.\n(لم يسبق أن واجهتنا أي مشكلة مع الأكواد.)",
    "en": "🍎 Apple Gift Card 🇺🇸 — USA\n\nCards for the US App Store 📱\n✅ For iPhone and iPad (US Apple ID accounts only).\n💳 After payment you receive the activation code immediately.\n\n🛡️ Warranty: one hour from the time of purchase.\n(We have never had any problem with the codes.)",
    "fr": "🍎 Apple Gift Card 🇺🇸 — États-Unis\n\nCartes destinées à l'App Store américain 📱\n✅ Pour iPhone et iPad (comptes Apple ID américains uniquement).\n💳 Après le paiement, vous recevez immédiatement le code d'activation.\n\n🛡️ Garantie : une heure à partir de l'achat.\n(Nous n'avons jamais eu de problème avec les codes.)",
}

def _gplay_desc(flag, c_ar, c_en, c_fr):
    return {
        "ar": f"🤖 Google Play Gift Card {flag} — {c_ar}\n\nرصيد لمتجر Google Play الخاص بـ{c_ar} 📱\n✅ صالحة لهواتف Android فقط (لا تعمل على iPhone).\n🌍 تعمل فقط مع حسابات Google Play المسجّلة في {c_ar}، تأكد من بلد حسابك قبل الشراء.\n\n🛒 تصلح لشراء التطبيقات والألعاب والاشتراكات والمشتريات داخل التطبيقات.\n\n📩 طريقة الطلب:\n1️⃣ اختر القيمة من الأزرار أدناه\n2️⃣ اختر الكمية (حتى 3) ثم ادفع\n3️⃣ يصلك الكود مباشرة بعد الدفع\n4️⃣ التفعيل: Google Play ← صورة حسابك ← المدفوعات والاشتراكات ← استرداد رمز الهدية (Redeem)",
        "en": f"🤖 Google Play Gift Card {flag} — {c_en}\n\nCredit for the {c_en} Google Play store 📱\n✅ Valid for Android devices only (does not work on iPhone).\n🌍 Works only with Google Play accounts registered in {c_en}, check your account country before buying.\n\n🛒 Good for apps, games, subscriptions and in-app purchases.\n\n📩 How to order:\n1️⃣ Choose the value from the buttons below\n2️⃣ Choose the quantity (up to 3) and pay\n3️⃣ You receive the code right after payment\n4️⃣ To redeem: Google Play → your profile picture → Payments and subscriptions → Redeem gift code",
        "fr": f"🤖 Google Play Gift Card {flag} — {c_fr}\n\nCrédit pour le Google Play {c_fr} 📱\n✅ Valable uniquement sur Android (ne fonctionne pas sur iPhone).\n🌍 Fonctionne uniquement avec les comptes Google Play enregistrés en {c_fr}, vérifiez le pays de votre compte avant d'acheter.\n\n🛒 Utile pour les applications, jeux, abonnements et achats intégrés.\n\n📩 Comment commander :\n1️⃣ Choisissez la valeur avec les boutons ci-dessous\n2️⃣ Choisissez la quantité (jusqu'à 3) puis payez\n3️⃣ Vous recevez le code juste après le paiement\n4️⃣ Pour l'utiliser : Google Play → votre photo de profil → Paiements et abonnements → Utiliser un code cadeau",
    }

def _steam_desc(flag, c_ar, c_en, c_fr, cur):
    return {
        "ar": f"🎮 Steam Wallet {flag} — {c_ar}\n\nرصيد لمحفظة Steam بعملة {cur} 💰\n🌍 صالحة فقط لحسابات Steam ذات منطقة {c_ar}، تأكد من منطقة حسابك قبل الشراء.\n\n🛒 تصلح لشراء الألعاب والإضافات والعناصر داخل متجر Steam.\n\n📩 طريقة الطلب:\n1️⃣ اختر القيمة من الأزرار أدناه\n2️⃣ اختر الكمية (حتى 3) ثم ادفع\n3️⃣ يصلك الكود مباشرة بعد الدفع\n4️⃣ التفعيل: تطبيق Steam ← اسم حسابك ← تفاصيل الحساب ← إضافة رصيد ← استرداد بطاقة هدية Steam أو رمز المحفظة",
        "en": f"🎮 Steam Wallet {flag} — {c_en}\n\nSteam Wallet credit in {cur} 💰\n🌍 Valid only for Steam accounts in the {c_en} region, check your account region before buying.\n\n🛒 Good for games, DLC and items in the Steam store.\n\n📩 How to order:\n1️⃣ Choose the value from the buttons below\n2️⃣ Choose the quantity (up to 3) and pay\n3️⃣ You receive the code right after payment\n4️⃣ To redeem: Steam app → your account name → Account details → Add funds → Redeem a Steam Gift Card or Wallet Code",
        "fr": f"🎮 Steam Wallet {flag} — {c_fr}\n\nCrédit Steam Wallet en {cur} 💰\n🌍 Valable uniquement pour les comptes Steam de la région {c_fr}, vérifiez la région de votre compte avant d'acheter.\n\n🛒 Utile pour les jeux, DLC et objets du magasin Steam.\n\n📩 Comment commander :\n1️⃣ Choisissez la valeur avec les boutons ci-dessous\n2️⃣ Choisissez la quantité (jusqu'à 3) puis payez\n3️⃣ Vous recevez le code juste après le paiement\n4️⃣ Pour l'utiliser : application Steam → nom du compte → Détails du compte → Ajouter des fonds → Utiliser une carte cadeau ou un code Steam",
    }

def _psn_desc(flag, c_ar, c_en, c_fr, cur, reg):
    return {
        "ar": f"🎮 PlayStation Gift Card {flag} — {c_ar}\n\nرصيد لمتجر PlayStation Store بعملة {cur} 💰\n\n⚠️ مهم جداً:\n🌍 البطاقة تعمل فقط مع حساب PSN منطقته {reg}. إذا كان حسابك من منطقة أخرى فلن تعمل، تأكد من منطقة حسابك قبل الشراء.\n🔎 كيف تتأكد؟ حسابك على PlayStation لازم يكون مفتوحاً (مسجّلاً) في بلد {reg}. تحقق من بلد الحساب في: الإعدادات ← المستخدمون والحسابات ← الحساب ← الملف الشخصي، فإن كان البلد {reg} فالبطاقة تعمل بإذن الله، وإن كان غير ذلك فلا تشترِ.\n🚫 الكود لا يمكن استرجاعه أو استبداله بعد تسليمه.\n\n🛒 تصلح لشراء الألعاب والإضافات والاشتراكات (مثل PS Plus) من PlayStation Store.\n\n📩 طريقة الطلب:\n1️⃣ اختر القيمة من الأزرار أدناه\n2️⃣ اختر الكمية (حتى 3) ثم ادفع\n3️⃣ يصلك الكود مباشرة بعد الدفع\n4️⃣ التفعيل: PlayStation Store ← … ← استرداد رمز (Redeem Codes) ← أدخل الكود",
        "en": f"🎮 PlayStation Gift Card {flag} — {c_en}\n\nCredit for the PlayStation Store in {cur} 💰\n\n⚠️ Very important:\n🌍 The card works only with a PSN account of the {reg} region. It will not work on an account from another region, so check your account region before buying.\n🔎 How to check? Your PlayStation account must be registered in the {reg} country/region. Look at it in: Settings → Users and Accounts → Account → Profile. If it shows {reg}, the card will work; if not, please do not buy.\n🚫 The code cannot be refunded or exchanged once delivered.\n\n🛒 Good for games, add-ons and subscriptions (such as PS Plus) on the PlayStation Store.\n\n📩 How to order:\n1️⃣ Choose the value from the buttons below\n2️⃣ Choose the quantity (up to 3) and pay\n3️⃣ You receive the code right after payment\n4️⃣ To redeem: PlayStation Store → … → Redeem Codes → enter the code",
        "fr": f"🎮 PlayStation Gift Card {flag} — {c_fr}\n\nCrédit pour le PlayStation Store en {cur} 💰\n\n⚠️ Très important :\n🌍 La carte fonctionne uniquement avec un compte PSN de la région {reg}. Elle ne marchera pas sur un compte d'une autre région, vérifiez la région de votre compte avant d'acheter.\n🔎 Comment vérifier ? Votre compte PlayStation doit être créé dans le pays/la région {reg}. Consultez-le dans : Paramètres → Utilisateurs et comptes → Compte → Profil. S'il indique {reg}, la carte fonctionnera ; sinon, n'achetez pas.\n🚫 Le code ne peut être ni remboursé ni échangé après la livraison.\n\n🛒 Utile pour les jeux, extensions et abonnements (comme PS Plus) sur le PlayStation Store.\n\n📩 Comment commander :\n1️⃣ Choisissez la valeur avec les boutons ci-dessous\n2️⃣ Choisissez la quantité (jusqu'à 3) puis payez\n3️⃣ Vous recevez le code juste après le paiement\n4️⃣ Pour l'utiliser : PlayStation Store → … → Utiliser un code → entrez le code",
    }

_PUBG_DESC = {
    "ar": "🔫 PUBG: BATTLEGROUNDS — G-Coin (Global) 🌍\n\nأكواد G-Coin عالمية (Global) لشحن عملة اللعبة 💰\n⚠️ مهم: هذه لنسخة PUBG: BATTLEGROUNDS (كمبيوتر وأجهزة الكونسول المدعومة) وليست لـ PUBG Mobile (التي عملتها UC).\n\n🛒 تصلح لشراء السكنات والعناصر وباتل باس داخل اللعبة.\n\n📩 طريقة الطلب:\n1️⃣ اختر الباقة من الأزرار أدناه\n2️⃣ اختر الكمية (حتى 3) ثم ادفع\n3️⃣ يصلك الكود مباشرة بعد الدفع\n4️⃣ التفعيل: ادخل لصفحة استرداد الأكواد الرسمية لـ PUBG بحسابك على KRAFTON ID وأدخل الكود، ثم تجد الرصيد في اللعبة",
    "en": "🔫 PUBG: BATTLEGROUNDS — G-Coin (Global) 🌍\n\nGlobal G-Coin codes to top up the in-game currency 💰\n⚠️ Important: this is for PUBG: BATTLEGROUNDS (PC and supported consoles), not PUBG Mobile (whose currency is UC).\n\n🛒 Good for skins, items and the battle pass in the game.\n\n📩 How to order:\n1️⃣ Choose the pack from the buttons below\n2️⃣ Choose the quantity (up to 3) and pay\n3️⃣ You receive the code right after payment\n4️⃣ To redeem: open the official PUBG code redemption page with your KRAFTON ID, enter the code, then find the balance in the game",
    "fr": "🔫 PUBG: BATTLEGROUNDS — G-Coin (Global) 🌍\n\nCodes G-Coin mondiaux pour recharger la monnaie du jeu 💰\n⚠️ Important : pour PUBG: BATTLEGROUNDS (PC et consoles compatibles), pas pour PUBG Mobile (dont la monnaie est l'UC).\n\n🛒 Utile pour les skins, objets et le battle pass du jeu.\n\n📩 Comment commander :\n1️⃣ Choisissez le pack avec les boutons ci-dessous\n2️⃣ Choisissez la quantité (jusqu'à 3) puis payez\n3️⃣ Vous recevez le code juste après le paiement\n4️⃣ Pour l'utiliser : ouvrez la page officielle d'échange de codes PUBG avec votre KRAFTON ID, entrez le code, puis retrouvez le solde dans le jeu",
}

_PUBGM_DESC = {
    "ar": "🔫 PUBG Mobile — أكواد UC (Global) 🌍\n\nأكواد UC عالمية (Global) لشحن PUBG Mobile 💎\n⚡ يصلك كود تفعّله بنفسك على موقع Midasbuy.\n\nℹ️ هذا منتج مختلف عن «شحن UC بالـ ID» الموجود في المتجر: هنا تستلم كوداً وتشحنه بنفسك.\n🚫 الكود لا يمكن استرجاعه أو استبداله بعد تسليمه.\n\n📩 طريقة الطلب:\n1️⃣ اختر الباقة من الأزرار أدناه\n2️⃣ اختر الكمية (حتى 3) ثم ادفع\n3️⃣ يصلك الكود مباشرة بعد الدفع\n4️⃣ التفعيل: ادخل لموقع Midasbuy.com، اختر PUBG Mobile، سجّل الدخول بمعرّف اللاعب (Player ID)، ثم اختر الدفع بالكود (Redeem Code) وأدخل الكود لتصلك الـ UC",
    "en": "🔫 PUBG Mobile — UC codes (Global) 🌍\n\nGlobal UC codes to top up PUBG Mobile 💎\n⚡ You receive a code that you redeem yourself on Midasbuy.\n\nℹ️ This is separate from the «UC top-up by ID» product in the store: here you receive a code and redeem it yourself.\n🚫 The code cannot be refunded or exchanged once delivered.\n\n📩 How to order:\n1️⃣ Choose the pack from the buttons below\n2️⃣ Choose the quantity (up to 3) and pay\n3️⃣ You receive the code right after payment\n4️⃣ To redeem: open Midasbuy.com, pick PUBG Mobile, log in with your Player ID, choose the code payment (Redeem Code) and enter the code to receive the UC",
    "fr": "🔫 PUBG Mobile — Codes UC (Global) 🌍\n\nCodes UC mondiaux pour recharger PUBG Mobile 💎\n⚡ Vous recevez un code que vous utilisez vous-même sur Midasbuy.\n\nℹ️ Produit distinct de «Recharge UC par ID» déjà disponible dans la boutique : ici vous recevez un code et l’utilisez vous-même.\n🚫 Le code ne peut être ni remboursé ni échangé après la livraison.\n\n📩 Comment commander :\n1️⃣ Choisissez le pack avec les boutons ci-dessous\n2️⃣ Choisissez la quantité (jusqu'à 3) puis payez\n3️⃣ Vous recevez le code juste après le paiement\n4️⃣ Pour l'utiliser : ouvrez Midasbuy.com, choisissez PUBG Mobile, connectez-vous avec votre Player ID, choisissez le paiement par code (Redeem Code) et entrez le code pour recevoir les UC",
}

_FC26_DESC = {
    "ar": "⚽ EA SPORTS FC™ 26 — نقاط FC (Global) 🌍\n\nبطاقات EA لنقاط EA SPORTS FC™ 26 (EA Gift Cards) ⚽\n⚡ يصلك كود تفعّله بنفسك على حساب EA.\n🗂️ يمكن حفظ الكود بأمان وتفعيله لاحقاً.\n🚫 الكود لا يمكن استرجاعه أو استبداله بعد تسليمه.\n\n📩 طريقة الطلب:\n1️⃣ اختر الباقة من الأزرار أدناه\n2️⃣ اختر الكمية (حتى 3) ثم ادفع\n3️⃣ يصلك الكود مباشرة بعد الدفع\n4️⃣ التفعيل: استرداد الكود (Redeem) على حساب EA الخاص بك",
    "en": "⚽ EA SPORTS FC™ 26 — FC Points (Global) 🌍\n\nEA gift cards for EA SPORTS FC™ 26 Points ⚽\n⚡ You receive a code that you redeem yourself on your EA account.\n🗂️ The code can be safely stored and redeemed later.\n🚫 The code cannot be refunded or exchanged once delivered.\n\n📩 How to order:\n1️⃣ Choose the pack from the buttons below\n2️⃣ Choose the quantity (up to 3) and pay\n3️⃣ You receive the code right after payment\n4️⃣ To redeem: redeem the code on your own EA account",
    "fr": "⚽ EA SPORTS FC™ 26 — Points FC (Global) 🌍\n\nCartes cadeaux EA pour les points EA SPORTS FC™ 26 ⚽\n⚡ Vous recevez un code que vous utilisez vous-même sur votre compte EA.\n🗂️ Le code peut être conservé en toute sécurité et utilisé plus tard.\n🚫 Le code ne peut être ni remboursé ni échangé après la livraison.\n\n📩 Comment commander :\n1️⃣ Choisissez le pack avec les boutons ci-dessous\n2️⃣ Choisissez la quantité (jusqu'à 3) puis payez\n3️⃣ Vous recevez le code juste après le paiement\n4️⃣ Pour l'utiliser : utilisez le code sur votre propre compte EA",
}

_FF_DESC = {
    "ar": "🔥 Free Fire — أكواد جواهر 💎 (Global) 🌍\n\nأكواد جواهر Garena Free Fire عالمية (Global) 💎\n⚡ يصلك كود تشحنه بنفسك على حسابك.\n\n📩 طريقة الطلب:\n1️⃣ اختر الباقة من الأزرار أدناه\n2️⃣ اختر الكمية (حتى 3) ثم ادفع\n3️⃣ يصلك الكود مباشرة بعد الدفع\n4️⃣ التفعيل: ادخل لموقع شحن Garena الرسمي (shop.garena.sg/app)، اختر Free Fire، سجّل الدخول بمعرّف اللاعب (Player ID) أو حسابك المرتبط، اختر Garena Voucher وأدخل الكود، ثم اضغط Redeem وتصلك الجواهر\n\nℹ️ هذا منتج منفصل عن «Free Fire Diamonds» (الشحن بالـ ID) الموجود في المتجر.",
    "en": "🔥 Free Fire — Diamond codes 💎 (Global) 🌍\n\nGlobal Garena Free Fire diamond codes 💎\n⚡ You receive a code that you redeem yourself on your account.\n\n📩 How to order:\n1️⃣ Choose the pack from the buttons below\n2️⃣ Choose the quantity (up to 3) and pay\n3️⃣ You receive the code right after payment\n4️⃣ To redeem: open the official Garena top-up site (shop.garena.sg/app), pick Free Fire, log in with your Player ID or linked account, choose Garena Voucher, enter the code and press Redeem\n\nℹ️ This is separate from the «Free Fire Diamonds» (top-up by ID) product in the store.",
    "fr": "🔥 Free Fire — Codes de diamants 💎 (Global) 🌍\n\nCodes de diamants Garena Free Fire mondiaux (Global) 💎\n⚡ Vous recevez un code que vous utilisez vous-même sur votre compte.\n\n📩 Comment commander :\n1️⃣ Choisissez le pack avec les boutons ci-dessous\n2️⃣ Choisissez la quantité (jusqu'à 3) puis payez\n3️⃣ Vous recevez le code juste après le paiement\n4️⃣ Pour l'utiliser : ouvrez le site de recharge officiel Garena (shop.garena.sg/app), choisissez Free Fire, connectez-vous avec votre Player ID ou compte lié, choisissez Garena Voucher, entrez le code et appuyez sur Redeem\n\nℹ️ Produit distinct de «Free Fire Diamonds» (recharge par ID) déjà disponible dans la boutique.",
}

# (id, icon, name ar, name en, name fr, descriptions)
_GIFT_DEFS = [
    ("apple_gift_us", "🍎", "Apple Gift Card 🇺🇸 أمريكية", "Apple Gift Card 🇺🇸 American", "Apple Gift Card 🇺🇸 Américaine", _APPLE_US_DESC),
    ("gplay_us", "🤖", "Google Play 🇺🇸 أمريكية", "Google Play 🇺🇸 American", "Google Play 🇺🇸 Américaine", _gplay_desc("🇺🇸", "أمريكا", "USA", "États-Unis")),
    ("gplay_fr", "🤖", "Google Play 🇫🇷 فرنسية", "Google Play 🇫🇷 French", "Google Play 🇫🇷 Française", _gplay_desc("🇫🇷", "فرنسا", "France", "France")),
    ("gplay_br", "🤖", "Google Play 🇧🇷 برازيلية", "Google Play 🇧🇷 Brazilian", "Google Play 🇧🇷 Brésilienne", _gplay_desc("🇧🇷", "البرازيل", "Brazil", "Brésil")),
    ("gplay_in", "🤖", "Google Play 🇮🇳 هندية", "Google Play 🇮🇳 Indian", "Google Play 🇮🇳 Indienne", _gplay_desc("🇮🇳", "الهند", "India", "Inde")),
    ("gplay_tr", "🤖", "Google Play 🇹🇷 تركية", "Google Play 🇹🇷 Turkish", "Google Play 🇹🇷 Turque", _gplay_desc("🇹🇷", "تركيا", "Turkey", "Turquie")),
    ("steam_us", "🎮", "Steam Wallet 🇺🇸 أمريكية", "Steam Wallet 🇺🇸 American", "Steam Wallet 🇺🇸 Américaine", _steam_desc("🇺🇸", "أمريكا (US)", "US", "États-Unis (US)", "USD")),
    ("steam_id", "🎮", "Steam Wallet 🇮🇩 إندونيسية", "Steam Wallet 🇮🇩 Indonesian", "Steam Wallet 🇮🇩 Indonésienne", _steam_desc("🇮🇩", "إندونيسيا", "Indonesia", "Indonésie", "IDR")),
    ("psn_us", "🎮", "PlayStation 🇺🇸 (US)", "PlayStation 🇺🇸 (US)", "PlayStation 🇺🇸 (US)", _psn_desc("🇺🇸", "أمريكا (US)", "USA (US)", "États-Unis (US)", "USD", "US")),
    ("psn_fr", "🎮", "PlayStation 🇫🇷 (FR)", "PlayStation 🇫🇷 (FR)", "PlayStation 🇫🇷 (FR)", _psn_desc("🇫🇷", "فرنسا (FR)", "France (FR)", "France (FR)", "EUR", "FR")),
    ("psn_tr", "🎮", "PlayStation 🇹🇷 (TR)", "PlayStation 🇹🇷 (TR)", "PlayStation 🇹🇷 (TR)", _psn_desc("🇹🇷", "تركيا (TR)", "Turkey (TR)", "Turquie (TR)", "TRY", "TR")),
    ("psn_br", "🎮", "PlayStation 🇧🇷 (BR)", "PlayStation 🇧🇷 (BR)", "PlayStation 🇧🇷 (BR)", _psn_desc("🇧🇷", "البرازيل (BR)", "Brazil (BR)", "Brésil (BR)", "BRL", "BR")),
    ("pubg_gcoin", "🔫", "PUBG G-Coin 🖥️ PC & Console", "PUBG G-Coin 🖥️ PC & Console", "PUBG G-Coin 🖥️ PC & Console", _PUBG_DESC),
    ("fc26_points", "⚽", "EA SPORTS FC 26", "EA SPORTS FC 26", "EA SPORTS FC 26", _FC26_DESC),
    ("pubg_uc", "📱", "PUBG Mobile 📱", "PUBG Mobile 📱", "PUBG Mobile 📱", _PUBGM_DESC),
    ("freefire_codes", "🔥", "Free Fire Codes 💎 Global", "Free Fire Codes 💎 Global", "Free Fire Codes 💎 Global", _FF_DESC),
]

NEW_GIFT_PRODUCTS = []
for _gid, _icon, _n_ar, _n_en, _n_fr, _d in _GIFT_DEFS:
    NEW_GIFT_PRODUCTS.append({
        "id": _gid, "name": _n_ar, "price": _gift_price_range(_gid),
        "stock": "♾️", "icon": _icon, "description": _d["ar"],
    })
    NEW_TRANSLATIONS[_gid] = {
        "en": {"name": _n_en, "description": _d["en"]},
        "fr": {"name": _n_fr, "description": _d["fr"]},
    }

# فواصل الأزرار الطويلة
_GIFT_SEPS = [
    ("sep_apple", "⬇️ Apple gift card ⬇️", "⬇️ Apple gift card ⬇️", "⬇️ Apple gift card ⬇️"),
    ("sep_google", "⬇️ Google gift card ⬇️", "⬇️ Google gift card ⬇️", "⬇️ Google gift card ⬇️"),
    ("sep_steam", "⬇️ Steam gift card ⬇️", "⬇️ Steam gift card ⬇️", "⬇️ Steam gift card ⬇️"),
    ("sep_psn", "⬇️ PlayStation gift card ⬇️", "⬇️ PlayStation gift card ⬇️", "⬇️ PlayStation gift card ⬇️"),
    ("sep_games", "⬇️ 🎮 بطاقات الألعاب (Global) ⬇️", "⬇️ 🎮 Game Cards (Global) ⬇️", "⬇️ 🎮 Cartes de jeux (Global) ⬇️"),
]
for _sid, _t_ar, _t_en, _t_fr in _GIFT_SEPS:
    NEW_GIFT_PRODUCTS.append({"type": "separator", "id": _sid, "text": _t_ar})
    NEW_TRANSLATIONS[_sid] = {"en": {"text": _t_en}, "fr": {"text": _t_fr}}

# تغيير اسم فاصل «بطاقات الهداية» القديم إلى «اشتراكات متنوعة» (يُستعمل الآن في الصفحة الأولى)
NEW_TRANSLATIONS["sep_gift_cards"] = {
    "en": {"text": "⬇️ Various Subscriptions ⬇️"},
    "fr": {"text": "⬇️ Abonnements divers ⬇️"},
}


BASE_FILE = os.environ.get("BOT_BASE_FILE", "bot_base.py")
if not os.path.exists(BASE_FILE):
    sys.exit("❌ لم أجد bot_base.py — أعد تسمية main.py القديم إلى bot_base.py ثم ضع هذا الملف باسم main.py")

src = open(BASE_FILE, encoding="utf-8").read().replace("\r\n", "\n")
_errors = []

def patch(old, new, name):
    global src
    n = src.count(old)
    if n != 1:
        _errors.append(f"[{name}] وجدت {n} تطابق (المطلوب 1)")
        return
    src = src.replace(old, new, 1)

# وصف Canva Edu Pro 500: السعر 4.99$ + مدة اللوحة 3 سنوات + ضمان شهر (ar/en/fr)
patch(r"""📦 السعة: 500 مقعد\n💰 السعر: 10$ فقط\n⚠️ مهم: المنتج بدون ضمان.""",
      r"""📦 السعة: 500 مقعد\n⏳ مدة اللوحة: 3 سنوات\n💰 السعر: 4.99$ فقط\n🛡️ الضمان: شهر واحد""", "canva500_desc_ar")
patch(r"""📦 Capacity: 500 seats\n💰 Price: only 10$\n⚠️ Important: no warranty on this product.""",
      r"""📦 Capacity: 500 seats\n⏳ Panel duration: 3 years\n💰 Price: only 4.99$\n🛡️ Warranty: 1 month""", "canva500_desc_en")
patch(r"""📦 Capacité : 500 places\n💰 Prix : seulement 10$\n⚠️ Important : produit sans garantie.""",
      r"""📦 Capacité : 500 places\n⏳ Durée du panel : 3 ans\n💰 Prix : seulement 4,99$\n🛡️ Garantie : 1 mois""", "canva500_desc_fr")

# FAZER: عند تطابق عرضين (قسم عادي + قسم instant_use) اختر الأرخص المتوفر بدل التوقف بـ ambiguous
patch(r"""    if len(uniq) > 1:
        return None, "ambiguous"
    c, o = next(iter(uniq.values()))
    return _mapping(c, o), "auto"
""", r"""    if len(uniq) > 1:
        _pk = _pick_instant(uniq)
        if _pk is None:
            return None, "ambiguous"
        uniq = {_pk: uniq[_pk]}
    c, o = next(iter(uniq.values()))
    return _mapping(c, o), "auto"
""", "fazer_pick_instant_base")

# Apple India: رفع سعر 1000 و1500 INR لهامش ربح ~15% (كان ~11%)
patch("""("500 INR", "6.90"), ("1000 INR", "12.00"), ("1500 INR", "18.00"),""",
      """("500 INR", "6.90"), ("1000 INR", "12.60"), ("1500 INR", "18.90"),""", "apple_in_prices")

# إخفاء المنتجات المحذوفة من لوحة الأدمن (الأسعار/المخزون، الأوصاف، البث)
patch("""        if p.get("type") == "separator" or p["id"] not in (price_ids | stock_ids):
            continue""", """        if p.get("type") == "separator" or p["id"] not in (price_ids | stock_ids) or p["id"] in REMOVED_OWN:
            continue""", "removed_price_list")
patch("""    return [p for p in products if p.get("type") != "separator"]

def _retry_after""", """    return [p for p in products if p.get("type") != "separator" and p.get("id") not in REMOVED_OWN]

def _retry_after""", "removed_broadcast")

# Apple India 100 INR: ربح ثابت 0.30$ (التكلفة الحالية 1.2775$ ← 1.58$)
patch("""("100 INR", "1.40"), ("200 INR", "2.45"), ("250 INR", "3.05"),""",
      """("100 INR", "1.58"), ("200 INR", "2.45"), ("250 INR", "3.05"),""", "apple_in_100_price")

# رابط الدعم (اليوزر تغيّر)
patch('MY_PRIVATE_CHAT_LINK = "https://t.me/Raseedkom"',
      'MY_PRIVATE_CHAT_LINK = "https://t.me/Raseedkom_Support"', "support_link")

# وصف Netflix (بروفيل + حساب كامل): VPN مجاني + رابط الصورة (ar/en/fr) + ملاحظة كود الإيميل للبروفيل
patch(r""""description": "📦 حسابات نتفليكس بريميوم - شهرين\n\n✅ حسابات نتفليكس بريميوم\n❌ ممنوع تغيير الاسم و كلمة السر هاذا يتم طردك من الحساب مع عدم وجود ضمان\n✅ تسجيل الدخول بالبريد الإلكتروني وكلمة المرور\n🔵 أرخص سعر — 2.70$\n✅ يدعم البث بجودة عالية\n✅ يمكن استخدام بروفيل في حساب واحد\n✅ يعمل على الهاتف المحمول، الكمبيوتر المحمول، التابلت والتلفزيون الذكي\n✅ الدعم متاح عند الحاجة\n📊 المباعة: 216 حسابات",""",
      r""""description": "📦 حسابات نتفليكس بريميوم - شهرين (بروفيل خاص)\n\n✅ بروفيل خاص بك وحدك داخل حساب Netflix Premium\n✅ المدة: شهران كاملان + هدية تقارب شهراً إضافياً 🎁\n⚡ التفعيل برابط مباشر على الهاتف والحاسوب، بدون كلمة سر\n📺 التلفاز: يُفعَّل بكود من 8 أرقام يظهر لك في التطبيق، ترسله لنا في البوت ويفعّله فريقنا\n🌐 يعمل عبر VPN مجاني (أمريكا 🇺🇸 أو كندا 🇨🇦) مثل Proton VPN\n🛡️ ضمان لمدة شهر\n🎬 يدعم كل الأفلام والمسلسلات بجودة عالية\n💬 الدعم متاح عند الحاجة\n\n⚠️ مهم: ادخل فقط إلى البروفيل الخاص بك (اسمه يظهر في رسالة التسليم). الدخول إلى أي بروفيل آخر يؤدي إلى إخراجك من الحساب وفقدان الضمان.\n📊 المباعة: 216 حسابات\n\n🖼️ شرح التشغيل مع Proton VPN: https://drive.google.com/file/d/1IEg2wISdZ42ojqLLTTJkK6M4HesZQbFK/view?usp=sharing",""", "netflix_profile_desc_ar")
patch(r""""description": "📦 Netflix Premium accounts - 2 months\n\n✅ Netflix Premium accounts\n❌ Do not change the name or the password, otherwise you will be removed from the account with no warranty\n✅ Login with email and password\n🔵 Cheapest price — 2.30$\n✅ High-quality streaming\n✅ One profile on one account\n✅ Works on mobile, laptop, tablet and smart TV\n✅ Support available when needed\n📊 Sold: 216 accounts"}""",
      r""""description": "📦 Netflix Premium accounts - 2 months (private profile)\n\n✅ Your own private profile inside a Netflix Premium account\n✅ Duration: 2 full months + about 1 extra month as a gift 🎁\n⚡ Activation with a direct link on phone and computer, no password\n📺 TV: activated with an 8-digit code shown in the app, you send it to us in the bot and our team activates it\n🌐 Works with a free VPN (USA 🇺🇸 or Canada 🇨🇦) such as Proton VPN\n🛡️ 1-month warranty\n🎬 Supports all movies and series in high quality\n💬 Support available when needed\n\n⚠️ Important: enter ONLY your own profile (its name is shown in the delivery message). Entering any other profile gets you removed from the account and voids the warranty.\n📊 Sold: 216 accounts\n\n🖼️ Proton VPN setup guide: https://drive.google.com/file/d/1IEg2wISdZ42ojqLLTTJkK6M4HesZQbFK/view?usp=sharing"}""", "netflix_profile_desc_en")
patch(r""""description": "📦 Comptes Netflix Premium - 2 mois\n\n✅ Comptes Netflix Premium\n❌ Interdiction de changer le nom ou le mot de passe, sinon vous serez exclu du compte sans garantie\n✅ Connexion par e-mail et mot de passe\n🔵 Prix le plus bas — 2,30$\n✅ Streaming haute qualité\n✅ Un profil sur un compte\n✅ Fonctionne sur mobile, ordinateur portable, tablette et Smart TV\n✅ Support disponible en cas de besoin\n📊 Vendus : 216 comptes"}""",
      r""""description": "📦 Comptes Netflix Premium - 2 mois (profil privé)\n\n✅ Votre propre profil privé dans un compte Netflix Premium\n✅ Durée : 2 mois entiers + environ 1 mois offert 🎁\n⚡ Activation par lien direct sur téléphone et ordinateur, sans mot de passe\n📺 TV : activée avec un code à 8 chiffres affiché dans l'application, vous nous l'envoyez dans le bot et notre équipe l'active\n🌐 Fonctionne avec un VPN gratuit (USA 🇺🇸 ou Canada 🇨🇦) comme Proton VPN\n🛡️ Garantie d'un mois\n🎬 Compatible avec tous les films et séries en haute qualité\n💬 Support disponible en cas de besoin\n\n⚠️ Important : entrez UNIQUEMENT dans votre propre profil (son nom est indiqué dans le message de livraison). Entrer dans un autre profil vous fait exclure du compte et annule la garantie.\n📊 Vendus : 216 comptes\n\n🖼️ Guide Proton VPN : https://drive.google.com/file/d/1IEg2wISdZ42ojqLLTTJkK6M4HesZQbFK/view?usp=sharing"}""", "netflix_profile_desc_fr")
patch(r""""description": "📦 حسابات نتفليكس بريميوم - شهرين\n\n✅ حسابات نتفليكس بريميوم\n✅ تسجيل الدخول بالبريد الإلكتروني وكلمة المرور\n✅ ضمان لمدة شهر الأول\n🔵 أرخص سعر — 10$ يعني 5$ حساب كامل 😍\n✅ يدعم البث بجودة عالية\n✅ يمكن استخدام ما يصل إلى 5 ملفات شخصية و4 أجهزة\n✅ يعمل على الهاتف المحمول، الكمبيوتر المحمول، التابلت والتلفزيون الذكي\n✅ الدعم متاح 12/24 ساعة\n📊 المباعة: 432 حسابات",""",
      r""""description": "📦 حسابات نتفليكس بريميوم - شهرين (حساب كامل)\n\n✅ حساب كامل: نعطيك الإيميل وكلمة السر لتسجّل الدخول بهما\n✅ يمكنك تغيير كلمة السر بعد الدخول\n✅ مدة كاملة: شهرين كاملين\n🌐 يعمل عبر VPN مجاني (أمريكا 🇺🇸 أو كندا 🇨🇦) مثل Proton VPN\n🛡️ ضمان لمدة شهر\n🎬 يدعم كل الأفلام والمسلسلات بجودة عالية\n👥 يمكن استخدام ما يصل إلى 5 ملفات شخصية و4 أجهزة\n📱 يعمل على جميع الأجهزة: الهاتف، الكمبيوتر، التابلت والتلفزيون الذكي\n💬 الدعم متاح 12/24 ساعة\n📊 المباعة: 432 حسابات\n\n🖼️ شرح التشغيل مع Proton VPN: https://drive.google.com/file/d/1IEg2wISdZ42ojqLLTTJkK6M4HesZQbFK/view?usp=sharing",""", "netflix_full_desc_ar")
patch(r""""description": "📦 Netflix Premium accounts - 2 months\n\n✅ Netflix Premium accounts\n✅ Login with email and password\n✅ 1-month warranty\n🔵 Cheapest price — 10$ means 5$ for a full account 😍\n✅ High-quality streaming\n✅ Up to 5 profiles and 4 devices\n✅ Works on mobile, laptop, tablet and smart TV\n✅ Support available 12/24 hours\n📊 Sold: 432 accounts"}""",
      r""""description": "📦 Netflix Premium accounts - 2 months (full account)\n\n✅ Full account: we give you the email and password to log in\n✅ You can change the password after logging in\n✅ Full duration: 2 full months\n🌐 Works with a free VPN (USA 🇺🇸 or Canada 🇨🇦) such as Proton VPN\n🛡️ 1-month warranty\n🎬 Supports all movies and series in high quality\n👥 Up to 5 profiles and 4 devices\n📱 Works on all devices: mobile, laptop, tablet and smart TV\n💬 Support available 12/24 hours\n📊 Sold: 432 accounts\n\n🖼️ Proton VPN setup guide: https://drive.google.com/file/d/1IEg2wISdZ42ojqLLTTJkK6M4HesZQbFK/view?usp=sharing"}""", "netflix_full_desc_en")
patch(r""""description": "📦 Comptes Netflix Premium - 2 mois\n\n✅ Comptes Netflix Premium\n✅ Connexion par e-mail et mot de passe\n✅ Garantie d'un mois\n🔵 Prix le plus bas — 10$ soit 5$ le compte complet 😍\n✅ Streaming haute qualité\n✅ Jusqu'à 5 profils et 4 appareils\n✅ Fonctionne sur mobile, ordinateur portable, tablette et Smart TV\n✅ Support disponible 12/24 heures\n📊 Vendus : 432 comptes"}""",
      r""""description": "📦 Comptes Netflix Premium - 2 mois (compte complet)\n\n✅ Compte complet : nous vous donnons l'e-mail et le mot de passe pour vous connecter\n✅ Vous pouvez changer le mot de passe après la connexion\n✅ Durée complète : 2 mois entiers\n🌐 Fonctionne avec un VPN gratuit (USA 🇺🇸 ou Canada 🇨🇦) comme Proton VPN\n🛡️ Garantie d'un mois\n🎬 Compatible avec tous les films et séries en haute qualité\n👥 Jusqu'à 5 profils et 4 appareils\n📱 Fonctionne sur tous les appareils : mobile, ordinateur, tablette et Smart TV\n💬 Support disponible 12/24 heures\n📊 Vendus : 432 comptes\n\n🖼️ Guide Proton VPN : https://drive.google.com/file/d/1IEg2wISdZ42ojqLLTTJkK6M4HesZQbFK/view?usp=sharing"}""", "netflix_full_desc_fr")

# 0) إعادة تسمية دالتي منشورات المنتجات الأصليتين (نغلّفهما في NEW_BLOCK)
patch(r"""def send_channel_post(chat_id, item):""",
      r"""def _send_channel_post_orig(chat_id, item):""", "rename_scp")
patch(r"""def send_user_post(user_id, item):""",
      r"""def _send_user_post_orig(user_id, item):""", "rename_sup")

# 1) عنوان الفاتورة: لا نطبع label الافتراضي
patch(r"""{html.escape(tr(product, 'name', lang))} — {html.escape(invoice['label'])}""",
      r"""{html.escape(tr(product, 'name', lang))}{_lab_suffix(invoice)}""", "invoice_label")

# 2) إعادة إرسال رقم عملية لطلب يدوي منفّذ = مستعمل
patch(r"""            if existing.get("status") == "delivered":""",
      r"""            if existing.get("status") in ("delivered", "manual"):""", "settle_existing")

# 3) تنبيه الدفعة الناقصة للمراقب
patch(r"""            part_add(inv_id)
""", r"""            part_add(inv_id)
            _monitor_underpaid(invoice, uid, total, need)
""", "underpaid_alert")

# 4) فرع المنتجات اليدوية في التسليم
patch(r"""    # Gemini: تسليم من Upstash (بدون FAZER)""",
      r"""    # منتجات يدوية (A/B): تسجيل الطلب + جمع البيانات / إشعار الأدمن
    if pid in MANUAL_IDS:
        _fulfill_manual(chat_id, uid, lang, claim, canon, retry, mark, failed)
        return

    # Gemini: تسليم من Upstash (بدون FAZER)""", "fulfill_manual_branch")

# 5) الدفع من المحفظة: تحقق المخزون + اعتبار الطلب اليدوي ناجحاً
patch(r"""    pid, label = invoice["product_id"], invoice["label"]
""", r"""    pid, label = invoice["product_id"], invoice["label"]
    if pid in MANUAL_IDS and not _manual_in_stock(pid):
        bot.answer_callback_query(call.id, wt(lang, "wpay_out"), show_alert=True)
        return
""", "wallet_stock")
patch(r"""    if claim.get("status") == "delivered":""",
      r"""    if claim.get("fz_created") and claim.get("status") == "paid_pending":
        # طلب FAZER أُنشئ لكن الأكواد لم تصل بعد: لا نُرجع المال، والبوت يسلّم تلقائياً لاحقاً
        _safe_send(chat_id, t(lang, "processing"), reply_markup=support_markup(lang))
        monitor_send(f"⏳ <b>طلب بالمحفظة بانتظار أكواد FAZER</b> (لم يُرجع المبلغ)\n\n📦 {html.escape(invoice['product_name'])}\n👤 {_user_link(uid)}")
        return
    if claim.get("status") in ("delivered", "manual"):""", "wallet_ok")

# FAZER أنشأ الطلب بلا أكواد بعد: نعلّمه لكي لا تُرجَع المحفظة
patch(r"""        # الطلب مقبول لكن بلا أكواد بعد (نفس المفتاح يرجع نفس الطلب لاحقاً)""",
      r"""        # الطلب مقبول لكن بلا أكواد بعد (نفس المفتاح يرجع نفس الطلب لاحقاً)
        claim["fz_created"] = True""", "fz_created_flag")

# 6) صفحة المنتج: زر الشراء بدل الإحالة للخاص
patch(r"""    markup.add(InlineKeyboardButton(text=t(lang, "order_now"), url=MY_PRIVATE_CHAT_LINK))""",
      r"""    markup.add(InlineKeyboardButton(text=t(lang, "support_btn"), url=MY_PRIVATE_CHAT_LINK))""", "view_support_btn")
patch(r"""        caption_bottom = t(lang, "buy_hint")""",
      r"""        caption_bottom = _manual_buy_ui(markup, selected_product, lang)""", "view_buy_ui")

# 7) إشعار الجرس عند رجوع المخزون
patch(r"""def _stock_changed(pid, old, new):""",
      r"""def _stock_changed(pid, old, new):
    _restock_hook(pid, old, new)""", "stock_hook")

# 8) تسجيل المشتركين في الجرس
patch(r"""        notify_admin_interest(call.from_user, product, lang)""",
      r"""        notify_admin_interest(call.from_user, product, lang)
        _notify_subscribe(product_id, call.from_user.id)""", "notify_sub")

# 9) أزرار "طلباتي"
patch(r"""    if screen == "profile":""",
      r"""    if screen == "profile":
        m.add(InlineKeyboardButton(text=mt(lang, "btn_orders"), callback_data="pf_orders"))""", "pf_markup_profile")
patch(r"""        m.add(InlineKeyboardButton(text=wallet_label or wt(lang, "btn_wallet"), callback_data="pf_wallet"))""",
      r"""        m.add(InlineKeyboardButton(text=mt(lang, "btn_orders"), callback_data="pf_orders"))
        m.add(InlineKeyboardButton(text=wallet_label or wt(lang, "btn_wallet"), callback_data="pf_wallet"))""", "pf_markup_hist")

# 10) شاشة طلباتي
patch(r"""    if data != "pf_topo":""",
      r"""    if _pf_orders_view(call, uid, lang, data):
        return
    if data != "pf_topo":""", "pf_orders_view")

# 11) لوحة الأدمن
patch(r"""    markup.add(InlineKeyboardButton(text="👤 ملف زبون", callback_data="adm_view"))""",
      r"""    markup.add(InlineKeyboardButton(text=_maint_label(), callback_data="adm_maint"))
    _learn_admin_btn(markup)
    markup.add(InlineKeyboardButton(text="💰 ربح الصافي", callback_data="adm_profit"))
    markup.add(InlineKeyboardButton(text=f"📦 الطلبات المعلقة ({_ord_count()})", callback_data="adm_pend"))
    markup.add(InlineKeyboardButton(text=f"💳 الدفعات المعلقة ({_pp_count()})", callback_data="ap_l"))
    markup.add(InlineKeyboardButton(text="💳 شحن محفظة زبون", callback_data="ap_wt"))
    markup.add(InlineKeyboardButton(text="✏️ تعديل وصف منتج", callback_data="ap_dp"))
    markup.add(InlineKeyboardButton(text="⚙️ طرق الدفع", callback_data="ap_pm"))
    markup.add(InlineKeyboardButton(text="💲 المخزون / الأسعار", callback_data="adm_prices"))
    markup.add(InlineKeyboardButton(text="🔔 المهتمون (أعلمني)", callback_data="adm_interest"))
    markup.add(InlineKeyboardButton(text="💼 أرصدة الزبائن", callback_data="adm_wal"))
    markup.add(InlineKeyboardButton(text="🔧 المنتجات اليدوية / التلقائية", callback_data="adm_modes"))
    markup.add(InlineKeyboardButton(text="👤 ملف زبون", callback_data="adm_view"))""", "admin_buttons")
patch(r"""    if op not in ("use", "add", "buy", "view"):""",
      r"""    if _admin_panel_extra(call, op):
        return
    if op not in ("use", "add", "buy", "view"):""", "admin_extra")
patch(r"""    st = _adm_wait[aid]
""", r"""    st = _adm_wait[aid]
    if st.get("op") == "deliver":
        _adm_wait.pop(aid, None)
        ok, msg = deliver_manual_order(st["oid"], message.text)
        bot.send_message(message.chat.id, msg, parse_mode="HTML")
        return
""", "admin_deliver_wizard")

# 12) حفظ التسليم التلقائي في سجل الطلبات
patch(r"""    record_purchase(uid, GEMINI_ID, claim.get("product_name"), claim.get("price"), canon, via=claim.get("via", "binance"))""",
      r"""    record_purchase(uid, GEMINI_ID, claim.get("product_name"), claim.get("price"), canon, via=claim.get("via", "binance"))
    order_log_auto(uid, claim.get("product_name"), claim.get("price"), canon, "\n".join(links))
    profit_log(canon, GEMINI_ID, claim.get("product_name"), claim.get("price"), None)""", "log_gemini")
patch(r"""            record_purchase(uid, pid, claim.get("product_name"), claim.get("price"), canon, via=claim.get("via", "binance"))""",
      r"""            record_purchase(uid, pid, claim.get("product_name"), claim.get("price"), canon, via=claim.get("via", "binance"))
            order_log_auto(uid, claim.get("product_name"), claim.get("price"), canon, "\n".join(codes))
            profit_log(canon, pid, claim.get("product_name"), claim.get("price"), cost)""", "log_fazer")


# 15) كميات: Gemini حتى GEMINI_MAX_QTY، وبطاقات الهداية حتى GIFT_MAX_QTY
patch(r"""GEMINI_QTYS = (1, 2)""", r"""GEMINI_QTYS = tuple(range(1, GEMINI_MAX_QTY + 1))""", "gemini_qtys")
patch(r"""def fazer_order(category_id, card_id, idem_key):""",
      r"""def fazer_order(category_id, card_id, idem_key, quantity=1):""", "fazer_order_sig")
patch(r"""            json={"category_id": category_id, "card_id": card_id, "quantity": 1},""",
      r"""            json={"category_id": category_id, "card_id": card_id, "quantity": quantity},""", "fazer_order_qty")
patch(r"""status, data = fazer_order(mapping["category_id"], mapping["card_id"], idem_key)""",
      r"""status, data = fazer_order(mapping["category_id"], mapping["card_id"], idem_key, _gift_qty(label))""", "fazer_order_call")
patch(r"""    n = int(claim.get("idem_n", 0))""",
      r"""    if cost is not None:
        cost = cost * _gift_qty(label)
    n = int(claim.get("idem_n", 0))""", "fazer_cost_qty")
patch(r"""    manual = FAZER_MANUAL_MAP.get((product_id, label))""",
      r"""    manual = FAZER_MANUAL_MAP.get((product_id, re.sub(r"\s+x\d+$", "", label)))""", "manual_map_label")
patch(r"""            out = bool(mapping and mapping.get("stock") is not None and int(mapping["stock"]) <= 0)""",
      r"""            out = bool(mapping and mapping.get("stock") is not None and int(mapping["stock"]) < _gift_qty(label))""", "wallet_gift_stock")
patch(r"""    # إشعار الأدمن بالقيمة المختارة""",
      r"""    if _gift_ask_qty(call, product, product_id, idx, label, price, lang):
        return

    # إشعار الأدمن بالقيمة المختارة""", "gift_qty_step")


# 16) منتجات جديدة: ترجماتها + إدراجها في قائمة products
patch(r"""
products = [
    {
        "id": "gemini_18m",""",
      r"""
TRANSLATIONS.update(NEW_TRANSLATIONS)
GIFT_VARIANTS.update(NEW_GIFT_VARIANTS)

products = [
    {
        "id": "gemini_18m",""", "new_translations")
patch(r"""    {
        "type": "separator",
        "id": "sep_gift_cards",""",
      r"""    *NEW_PRODUCTS,
    {
        "type": "separator",
        "id": "sep_gift_cards",""", "new_products")
# 16b) بطاقات الهدايا الجديدة: إدراجها في قائمة products + إعادة تسمية الفاصل + زر العودة لصفحة البطاقات
patch(r"""    },
]

# ========== التحكم في الأسعار من تيليغرام (الأدمن فقط) ==========""",
      r"""    },
    *NEW_GIFT_PRODUCTS,
]

# ========== التحكم في الأسعار من تيليغرام (الأدمن فقط) ==========""", "new_gift_products")
patch(r""""text": "⬇️ بطقات الهداية ⬇️",""", r""""text": "⬇️ اشتراكات متنوعة ⬇️",""", "sep_rename")
patch(r"""    gift_markup.add(InlineKeyboardButton(text=t(lang, "back"), callback_data="back_to_main"))""",
      r"""    _gb = InlineKeyboardButton(text=t(lang, "back"), callback_data="gcp")
    _gb.icon_dyn = ICON_GIFT_BACK
    gift_markup.add(_gb)""", "gift_back_btn")


# 17) الرجوع من منتج تابع لمجموعة (Claude / Snapchat) يرجع لصفحة المجموعة
patch(r"""    send_card(call.message.chat.id, selected_product, caption, markup)""",
      r"""    _fix_group_back(selected_product["id"], markup)
    send_card(call.message.chat.id, selected_product, caption, markup)""", "group_back")


# 18) رسالة الترحيب مع عرض الكاش باك
patch(r""""welcome": "👋 مرحباً بك في متجر RASEEDKOM!\nاختر المنتج الذي تريده من القائمة أدناه:",""",
      r""""welcome": "👋 مرحباً بك في متجر RASEEDKOM!\nاختر المنتج الذي تريده من القائمة أدناه:\n🎁 و إستفد من عرض خاص :5% كاش باك في محفظتك على كل عملية شراء 🎉",""", "welcome_ar")
patch(r""""welcome": "👋 Welcome to the RASEEDKOM store!\nChoose the product you want from the list below:",""",
      r""""welcome": "👋 Welcome to the RASEEDKOM store!\nChoose the product you want from the list below:\n🎁 And enjoy a special offer: 5% cashback in your wallet on every purchase 🎉",""", "welcome_en")
patch(r""""welcome": "👋 Bienvenue dans la boutique RASEEDKOM !\nChoisissez le produit souhaité dans la liste ci-dessous :",""",
      r""""welcome": "👋 Bienvenue dans la boutique RASEEDKOM !\nChoisissez le produit souhaité dans la liste ci-dessous :\n🎁 Et profitez d'une offre spéciale : 5 % de cashback dans votre portefeuille sur chaque achat 🎉",""", "welcome_fr")


# 19) طرق الدفع الجديدة: إعادة تسمية واجهة Binance الأصلية + ربط المعالجات
patch(r"""def build_invoice_text(lang, invoice, product):""",
      r"""def _bn_invoice_text(lang, invoice, product):""", "rename_invoice_text")
patch(r"""def build_invoice_markup(lang, invoice_id, wallet=False):""",
      r"""def _bn_invoice_markup(lang, invoice_id, wallet=False):""", "rename_invoice_markup")
patch(r"""def get_photo_file_id(message):
    if str(message.chat.id) != str(ADMIN_CHAT_ID):
        return""",
      r"""def get_photo_file_id(message):
    if proof_photo(message):
        return
    if str(message.chat.id) != str(ADMIN_CHAT_ID):
        return""", "photo_proof")
patch(r"""    if data == "pf_top":
        _pf_show(call, wt(lang, "topup_pick"), _pf_markup(lang, "topup"))""",
      r"""    if data == "pf_top":
        topup_method_picker(call, lang)""", "topup_picker")
patch(r"""    _adm_wait.pop(message.from_user.id, None)
    _price_wait.pop(message.from_user.id, None)
    markup = InlineKeyboardMarkup()""",
      r"""    _adm_wait.pop(message.from_user.id, None)
    _price_wait.pop(message.from_user.id, None)
    _ap_wait.pop(message.from_user.id, None)
    markup = InlineKeyboardMarkup()""", "admin_clear_ap")


# 20) بوابة القناة + قائمة ابدأ + الإحالة
patch(r"""def send_welcome(message):
    register_user(message.from_user.id)""",
      r"""def send_welcome(message):
    if start_gate(message):
        return
    register_user(message.from_user.id)""", "gate_start")
patch(r"""def handle_kb_products(message):
    register_user(message.from_user.id)""",
      r"""def handle_kb_products(message):
    if not gate_ok(message.chat.id, message.from_user.id):
        return
    register_user(message.from_user.id)""", "gate_products")
patch(r"""    bot.send_message(message.chat.id, t(lang, "start_guide"))""",
      r"""    if not gate_ok(message.chat.id, message.from_user.id):
        return
    send_start_menu(message.chat.id, lang)""", "start_menu")
patch(r"""def refresh_for_user(chat_id, user_id):
    register_user(user_id)""",
      r"""def refresh_for_user(chat_id, user_id):
    if not gate_ok(chat_id, user_id):
        return
    register_user(user_id)""", "gate_refresh")


# 21) "اطلب الآن" في الإشعارات يفتح مسار الشراء مباشرة
patch(r"""    markup.add(InlineKeyboardButton(text="🛒 Buy now", url=BOT_LINK))""",
      r"""    markup.add(InlineKeyboardButton(text="🛒 Buy now", url=BOT_LINK + "?start=qb" + chr(95) + item["id"]))""", "channel_buy_link")
patch(r"""    markup.add(InlineKeyboardButton(text=t(lang, "order_now"), callback_data=f"buy_{item['id']}"))""",
      r"""    markup.add(InlineKeyboardButton(text=t(lang, "order_now"), callback_data="qb" + chr(95) + item["id"]))""", "user_buy_btn")
patch(r"""    send_persistent_menu(call.message.chat.id, lang)
    send_main_menu(call.message.chat.id, lang)
    bot.answer_callback_query(call.id)""",
      r"""    send_persistent_menu(call.message.chat.id, lang)
    send_main_menu(call.message.chat.id, lang)
    bot.answer_callback_query(call.id)
    _resume_quick_buy(call.message.chat.id, call.from_user)""", "resume_qb_after_lang")


# 22) كوينز الشراء + سطر الكوينز في المحفظة + أزرار الشراء اليدوي
patch(r"""        wlog_add(uid, "buy", cents, pname)""",
      r"""        wlog_add(uid, "buy", cents, pname)
        _purchase_coins_hook(uid)""", "purchase_coins")
patch(r"""GIFT_REWARD_PCT = 2    # مكافأة بطاقات الهداية""",
      r"""GIFT_REWARD_PCT = 1    # مكافأة بطاقات الهداية (1%)""", "gift_cashback_1")
patch(r"""                    pct=WALLET_PCT, gift_pct=GIFT_REWARD_PCT,
                )
                + "\n\n" + wt(lang, "wallet_note")""",
      r"""                    pct=WALLET_PCT, gift_pct=GIFT_REWARD_PCT,
                )
                + _coins_wallet_line(lang, uid)
                + "\n\n" + wt(lang, "wallet_note")""", "wallet_coins_line")
patch(r"""        ok, msg = add_manual_purchase(st["uid"], st["amount"], "" if text == "-" else text)
        bot.send_message(message.chat.id, msg, parse_mode="HTML")""",
      r"""        _mp_choose_mode(message.chat.id, st["uid"], st["amount"], "" if text == "-" else text)""", "manual_purchase_modes")

# 23) RedotPay: مسارات الويب هوك + الكاش باك المخفّض + مصدر الدفعة
patch(r"""@app.route('/')
def home():
    return "I'm alive!"
""",
      r"""@app.route('/')
def home():
    return "I'm alive!"

@app.route('/rdp/cb', methods=['POST'])
def _rdp_cb_route():
    from flask import request as _rq
    return _rdp_cb_impl(_rq)

@app.route('/rdp/done')
def _rdp_done_route():
    return _rdp_done_impl()
""", "rdp_routes")
patch(r"""            "via": "binance",
            "status": "claimed",""",
      r"""            "via": tx.get("via", "binance"),
            "status": "claimed",""", "claim_via")
patch(r"""        if via in ("binance", "manual"):
            pct = GIFT_REWARD_PCT if pid in GIFT_VARIANTS else WALLET_PCT
            reward_c = cents * pct // 100""",
      r"""        if via in ("binance", "manual"):
            pct = GIFT_REWARD_PCT if pid in GIFT_VARIANTS else WALLET_PCT
            reward_c = cents * pct // 100
        elif via == "redotpay":
            pct = REDOTPAY_GIFT_PCT if pid in GIFT_VARIANTS else REDOTPAY_PCT
            reward_c = cents * pct // 100""", "rdp_cashback")
patch(r"""            wallet_credit(uid, cents, "topup", "Binance")""",
      r"""            wallet_credit(uid, cents, "topup", "RedotPay" if tx.get("via") == "redotpay" else "Binance")""", "topup_label")

# 13) الكتلة الجديدة (قبل معالج رقم العملية ليكون لها الأولوية)
NEW_BLOCK = r'''# ============================================================
# ========== الطلبات اليدوية (A/B) + سجل الطلبات + جرس التوفر ==========
# ============================================================
MANUAL_A = {  # منتجات تحتاج بيانات من الزبون بعد الدفع
    "snapchat_3m": "username",
    "snapchat_6m": "username",
    "snapchat_12m": "username",
    "freefire_diamonds": "playerid",
    "canva_edu_5000": "email",
}
MANUAL_B = {  # منتجات يسلّمها الأدمن (حساب / كود) من لوحة الطلبات المعلقة
    "netflix_full", "netflix_profile", "capcut_1m", "duolingo_12m",
    "duolingo_link_12m", "nordvpn_3m", "n8n_starter_12m", "canva_edu_500",
    "prime_video_ultra_6m", "amazon_prime_6m", "claude_100_30d", "claude_10m_1d",
    "chatgpt_plus_1m", "chatgpt_k12_edu", "office365_1y", "elevenlabs_3m", "iptv_14m",
}
MANUAL_IDS = set(MANUAL_A) | set(MANUAL_B)
FREEFIRE_ID = "freefire_diamonds"
FREEFIRE_PACKS = [("110💎", "1.45"), ("231💎", "2.20"), ("583💎", "5.05"), ("1188💎", "10.10"), ("2420💎", "19.50")]
NORD_ID = "nordvpn_3m"
AUTOCONFIRM_SECONDS = 20 * 60
ORDSET_KEY = "rk:ordset"      # الطلبات المفتوحة (تنتظر بيانات / تنتظر الأدمن)
WAITSET_KEY = "rk:waitset"    # طلبات سُلّمت وتنتظر زر "استلمت"
OPEN_STATES = ("need_input", "confirm_input", "pending")
ORD_ICONS = {"need_input": "⏳", "confirm_input": "⌛", "pending": "🔔", "delivered_wait": "📬", "done": "✅"}
ADMIN_ST = {
    "need_input": "ينتظر بيانات الزبون", "confirm_input": "ينتظر تأكيد الزبون لبياناته",
    "pending": "جاهز للتنفيذ", "delivered_wait": "سُلّم — ينتظر استلام الزبون", "done": "مكتمل",
}
INPUT_LBL_AR = {"username": "اسم المستخدم", "playerid": "Player ID", "email": "البريد"}

MANUAL_TEXTS = {
    "ar": {
        "buy_btn": "🛒 اشتري الآن",
        "buy_hint": "💳 اضغط «اشتري الآن» ثم اختر طريقة الدفع المناسبة لك.",
        "pick_pack": "🛒 اختر الباقة لإنشاء فاتورة الدفع",
        "out": "❌ هذا المنتج غير متوفر حالياً.",
        "paid_b": "✅ تم استلام دفعك. طلبك قيد المعالجة وسيصلك هنا قريباً.\n\n📂 تجد كل طلباتك في: الملف الشخصي ← سجل المشتريات ← طلباتي",
        "ask_username": "✅ تم تأكيد الدفع ({product})\n\n👻 أرسل الآن <b>اسم المستخدم (Username)</b> لحسابك على سناب شات.",
        "ask_playerid": "✅ تم تأكيد الدفع ({product})\n\n🎮 أرسل الآن <b>Player ID</b> الخاص بحسابك في Free Fire (أرقام فقط).",
        "ask_email": "✅ تم تأكيد الدفع ({product})\n\n✉️ أرسل الآن <b>البريد الإلكتروني</b> لحسابك على Canva.",
        "bad_username": "❌ اسم مستخدم غير صالح (3-15 حرفاً، يبدأ بحرف، أحرف وأرقام ونقطة وشرطة والشرطة السفلية فقط). أعد الإرسال.",
        "bad_playerid": "❌ Player ID غير صالح (أرقام فقط، من 6 إلى 14 رقماً). أعد الإرسال.",
        "bad_email": "❌ بريد إلكتروني غير صالح. أعد الإرسال.",
        "lbl_username": "اسم المستخدم", "lbl_playerid": "Player ID", "lbl_email": "البريد الإلكتروني",
        "confirm_q": "🔎 تأكد من بياناتك:\n\n{label}: <code>{val}</code>\n\nهل هي صحيحة؟",
        "btn_confirm": "✅ تأكيد", "btn_edit": "✏️ تعديل",
        "input_saved_email": "✅ <b>تم التحقق من الدفع — تم تقديم طلبك!</b>\n\n🛍 المنتج: {product}\n💰 المبلغ: USDT {paid}\n📧 {label}: <code>{val}</code>\n\n⏱ <b>وقت التفعيل المتوقع:</b> من دقيقة واحدة إلى 53 دقيقة (حسب إحصائيات هذا الشهر).\n\nسيقوم فريقنا بتفعيل طلبك قريباً وسنُعلمك هنا فور اكتماله. شكراً لثقتك! 🤝",
        "input_saved": "✅ تم تأكيد بياناتك. طلبك قيد التنفيذ وسنُعلمك هنا فور اكتماله.",
        "queued": "ℹ️ سنطلب منك بيانات هذا الطلب بعد إنهاء الطلب الحالي.",
        "executed": "🎉 <b>تم تفعيل طلبك بنجاح!</b>\n\n📦 {product}\n\nشكراً لثقتك بنا 🤝\nقد يستغرق ظهور التفعيل في حسابك لحظات. وإذا واجهت أي مشكلة تواصل مع الدعم وسنساعدك فوراً 👇",
        "delivery": "📦 <b>طلبك جاهز</b>\n\n{product}\n\n{body}\n\n📌 احتفظ بهذه المعلومات في مكان آمن.\nاضغط «✅ استلمت» بعد التأكد (يتأكد الطلب تلقائياً بعد 20 دقيقة).",
        "btn_received": "✅ استلمت",
        "received_ok": "🙏 شكراً! تم تأكيد استلام طلبك.",
        "btn_orders": "📂 طلباتي",
        "orders_title": "📂 <b>طلباتي</b>\nاختر طلباً لعرض تفاصيله وبياناته:",
        "orders_empty": "📂 لا توجد طلبات بعد.",
        "order_detail": "📦 <b>{product}</b>\n💵 ${price}\n📅 {date}\n📌 {status}",
        "order_input": "\n🔤 {label}: <code>{val}</code>",
        "order_delivery": "\n\n🎁 البيانات:\n<code>{val}</code>",
        "restock": "🔔 <b>{product}</b> أصبح متوفراً الآن!",
        "open_btn": "🛒 افتح المنتج",
        "st_need_input": "⏳ بانتظار بياناتك", "st_confirm_input": "⌛ بانتظار تأكيدك",
        "st_pending": "🔔 قيد المعالجة", "st_delivered_wait": "📬 تم التسليم", "st_done": "✅ مكتمل",
    },
    "en": {
        "buy_btn": "🛒 Buy now",
        "buy_hint": "💳 Tap «Buy now», then choose the payment method that suits you.",
        "pick_pack": "🛒 Choose a package to create the invoice",
        "out": "❌ This product is currently unavailable.",
        "paid_b": "✅ Payment received. Your order is being processed and will be sent here soon.\n\n📂 Find all your orders in: Profile → Purchase history → My orders",
        "ask_username": "✅ Payment confirmed ({product})\n\n👻 Now send your Snapchat <b>Username</b>.",
        "ask_playerid": "✅ Payment confirmed ({product})\n\n🎮 Now send your Free Fire <b>Player ID</b> (digits only).",
        "ask_email": "✅ Payment confirmed ({product})\n\n✉️ Now send the <b>email</b> of your Canva account.",
        "bad_username": "❌ Invalid username (3-15 chars, starts with a letter, letters, digits, dot, dash and underscore only). Send it again.",
        "bad_playerid": "❌ Invalid Player ID (digits only, 6 to 14 digits). Send it again.",
        "bad_email": "❌ Invalid email. Send it again.",
        "lbl_username": "Username", "lbl_playerid": "Player ID", "lbl_email": "Email",
        "confirm_q": "🔎 Check your details:\n\n{label}: <code>{val}</code>\n\nIs it correct?",
        "btn_confirm": "✅ Confirm", "btn_edit": "✏️ Edit",
        "input_saved_email": "✅ <b>Payment verified — your order was submitted!</b>\n\n🛍 Product: {product}\n💰 Amount: USDT {paid}\n📧 {label}: <code>{val}</code>\n\n⏱ <b>Estimated activation time:</b> from 1 minute up to 53 minutes (based on this month's statistics).\n\nOur team will activate your order shortly and we will notify you here once it is done. Thank you for your trust! 🤝",
        "input_saved": "✅ Details confirmed. Your order is being fulfilled and we will notify you here once done.",
        "queued": "ℹ️ We'll ask for this order's details after you finish the current one.",
        "executed": "🎉 <b>Your order has been activated successfully!</b>\n\n📦 {product}\n\nThank you for your trust 🤝\nIt may take a few moments for the activation to appear on your account. If you have any problem, contact support and we will help you right away 👇",
        "delivery": "📦 <b>Your order is ready</b>\n\n{product}\n\n{body}\n\n📌 Keep this information in a safe place.\nTap «✅ Received» once checked (auto-confirmed after 20 minutes).",
        "btn_received": "✅ Received",
        "received_ok": "🙏 Thank you! Your order receipt is confirmed.",
        "btn_orders": "📂 My orders",
        "orders_title": "📂 <b>My orders</b>\nChoose an order to see its details:",
        "orders_empty": "📂 No orders yet.",
        "order_detail": "📦 <b>{product}</b>\n💵 ${price}\n📅 {date}\n📌 {status}",
        "order_input": "\n🔤 {label}: <code>{val}</code>",
        "order_delivery": "\n\n🎁 Details:\n<code>{val}</code>",
        "restock": "🔔 <b>{product}</b> is available again!",
        "open_btn": "🛒 Open product",
        "st_need_input": "⏳ Waiting for your details", "st_confirm_input": "⌛ Waiting for your confirmation",
        "st_pending": "🔔 Processing", "st_delivered_wait": "📬 Delivered", "st_done": "✅ Completed",
    },
    "fr": {
        "buy_btn": "🛒 Acheter maintenant",
        "buy_hint": "💳 Appuyez sur « Acheter maintenant », puis choisissez le mode de paiement qui vous convient.",
        "pick_pack": "🛒 Choisissez un pack pour créer la facture",
        "out": "❌ Ce produit est actuellement indisponible.",
        "paid_b": "✅ Paiement reçu. Votre commande est en cours de traitement et vous sera envoyée ici bientôt.\n\n📂 Retrouvez vos commandes dans : Profil → Historique d'achats → Mes commandes",
        "ask_username": "✅ Paiement confirmé ({product})\n\n👻 Envoyez maintenant votre <b>nom d'utilisateur</b> Snapchat.",
        "ask_playerid": "✅ Paiement confirmé ({product})\n\n🎮 Envoyez maintenant votre <b>Player ID</b> Free Fire (chiffres uniquement).",
        "ask_email": "✅ Paiement confirmé ({product})\n\n✉️ Envoyez maintenant l'<b>e-mail</b> de votre compte Canva.",
        "bad_username": "❌ Nom d'utilisateur invalide (3-15 caractères, commence par une lettre, lettres, chiffres, point, tiret et underscore uniquement). Renvoyez-le.",
        "bad_playerid": "❌ Player ID invalide (chiffres uniquement, 6 à 14 chiffres). Renvoyez-le.",
        "bad_email": "❌ E-mail invalide. Renvoyez-le.",
        "lbl_username": "Nom d'utilisateur", "lbl_playerid": "Player ID", "lbl_email": "E-mail",
        "confirm_q": "🔎 Vérifiez vos informations :\n\n{label} : <code>{val}</code>\n\nSont-elles correctes ?",
        "btn_confirm": "✅ Confirmer", "btn_edit": "✏️ Modifier",
        "input_saved_email": "✅ <b>Paiement vérifié — votre commande a été envoyée !</b>\n\n🛍 Produit : {product}\n💰 Montant : USDT {paid}\n📧 {label} : <code>{val}</code>\n\n⏱ <b>Délai d'activation estimé :</b> de 1 minute à 53 minutes (selon les statistiques de ce mois).\n\nNotre équipe activera votre commande très bientôt et nous vous préviendrons ici dès qu'elle sera terminée. Merci de votre confiance ! 🤝",
        "input_saved": "✅ Informations confirmées. Votre commande est en cours et nous vous préviendrons ici dès qu'elle sera terminée.",
        "queued": "ℹ️ Nous vous demanderons les informations de cette commande après la commande en cours.",
        "executed": "🎉 <b>Votre commande a été activée avec succès !</b>\n\n📦 {product}\n\nMerci de votre confiance 🤝\nL'activation peut mettre quelques instants à apparaître sur votre compte. En cas de problème, contactez l'assistance, nous vous aiderons tout de suite 👇",
        "delivery": "📦 <b>Votre commande est prête</b>\n\n{product}\n\n{body}\n\n📌 Conservez ces informations en lieu sûr.\nAppuyez sur « ✅ Reçu » après vérification (confirmation automatique après 20 minutes).",
        "btn_received": "✅ Reçu",
        "received_ok": "🙏 Merci ! La réception de votre commande est confirmée.",
        "btn_orders": "📂 Mes commandes",
        "orders_title": "📂 <b>Mes commandes</b>\nChoisissez une commande pour voir ses détails :",
        "orders_empty": "📂 Aucune commande pour le moment.",
        "order_detail": "📦 <b>{product}</b>\n💵 ${price}\n📅 {date}\n📌 {status}",
        "order_input": "\n🔤 {label} : <code>{val}</code>",
        "order_delivery": "\n\n🎁 Détails :\n<code>{val}</code>",
        "restock": "🔔 <b>{product}</b> est de nouveau disponible !",
        "open_btn": "🛒 Ouvrir le produit",
        "st_need_input": "⏳ En attente de vos infos", "st_confirm_input": "⌛ En attente de votre confirmation",
        "st_pending": "🔔 En cours", "st_delivered_wait": "📬 Livrée", "st_done": "✅ Terminée",
    },
}

NORD_GUIDE = {
    "ar": "🔗 رابط التفعيل: https://my.nordaccount.com/activate\n1️⃣ افتح الرابط\n2️⃣ الصق الكود أعلاه\n3️⃣ أدخل بريدك الإلكتروني ثم رمز التحقق\n4️⃣ في صفحة الدفع انزل للأسفل واضغط Skip",
    "en": "🔗 Activation link: https://my.nordaccount.com/activate\n1️⃣ Open the link\n2️⃣ Paste the code above\n3️⃣ Enter your email, then the verification code\n4️⃣ On the payment page scroll down and tap Skip",
    "fr": "🔗 Lien d'activation : https://my.nordaccount.com/activate\n1️⃣ Ouvrez le lien\n2️⃣ Collez le code ci-dessus\n3️⃣ Entrez votre e-mail puis le code de vérification\n4️⃣ Sur la page de paiement, faites défiler et appuyez sur Skip",
}

def mt(lang, key):
    ar = MANUAL_TEXTS["ar"]
    return MANUAL_TEXTS.get(lang, ar).get(key) or ar.get(key, "")

def _lab_suffix(invoice):
    lab = invoice.get("label")
    if lab in (None, "", "std"):
        return ""
    return " — " + html.escape(str(lab))

# ---------- تخزين الطلبات ----------
_mem_sets = {}

def _sadd(key, val):
    if db:
        try:
            db.sadd(key, val)
            return
        except Exception as e:
            print(f"_sadd error: {e}")
    _mem_sets.setdefault(key, set()).add(val)

def _srem(key, val):
    _mem_sets.get(key, set()).discard(val)
    if db:
        try:
            db.srem(key, val)
        except Exception as e:
            print(f"_srem error: {e}")

def _smembers(key):
    out = set(_mem_sets.get(key, set()))
    if db:
        try:
            out |= {str(x) for x in (db.smembers(key) or [])}
        except Exception as e:
            print(f"_smembers error: {e}")
    return list(out)

def order_save(o):
    kv_set(f"rk:ord:{o['oid']}", json.dumps(o, ensure_ascii=False))

def order_get(oid):
    try:
        return kv_get_json(f"rk:ord:{oid}")
    except StorageError:
        return None

def _oid_from(canon):
    return hashlib.sha1(str(canon).encode()).hexdigest()[:10]

def uord_add(uid, oid):
    if not db:
        return
    try:
        db.lpush(f"rk:uord:{uid}", oid)
        db.ltrim(f"rk:uord:{uid}", 0, 99)
    except Exception as e:
        print(f"uord_add error: {e}")

def uord_list(uid, n=12):
    if not db:
        return []
    try:
        return [str(x) for x in (db.lrange(f"rk:uord:{uid}", 0, n - 1) or [])]
    except Exception as e:
        print(f"uord_list error: {e}")
        return []

def order_log_auto(uid, pname, price, canon, delivery):
    # يحفظ التسليم التلقائي (Gemini / بطاقات الهداية) في سجل طلبات الزبون بشكل دائم
    try:
        oid = _oid_from(canon)
        if kv_get_json(f"rk:ord:{oid}") is not None:
            return
        order_save({
            "oid": oid, "user_id": uid, "product_id": "auto", "product_name": pname or "",
            "price": str(price), "paid": str(price), "via": "auto", "status": "done", "cat": "C",
            "ts": int(time.time()), "delivery": delivery,
        })
        uord_add(uid, oid)
    except Exception as e:
        print(f"order_log_auto error: {e}")

def _safe_send(chat_id, text, **kw):
    try:
        return bot.send_message(chat_id, text, **kw)
    except ApiTelegramException as e:
        print(f"_safe_send to {chat_id} failed ({e.error_code}): {e}")
        return None
    except Exception as e:
        print(f"_safe_send to {chat_id} failed: {e}")
        return None

def _edit_cb(call, text, markup=None):
    try:
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                              parse_mode="HTML", reply_markup=markup)
    except Exception as e:
        if "not modified" not in str(e).lower():
            print(f"_edit_cb failed: {e}")

# ---------- أزرار «تم» / «لم أفهم» تحت رسالة تقديم الطلب (منتجات التفعيل اليدوي) ----------
HOWTO_TX = {
    "ar": {
        "ok": "✅ تم", "no": "❓ لم أفهم",
        "ack": "👍 بالتوفيق! سنُعلمك هنا فور تفعيل طلبك.",
        "explain": "ℹ️ <b>كيف يتم تنفيذ طلبك؟</b>\n\nهذا المنتج (Canva، Snapchat، شحن Free Fire) <b>ليس تسليماً فورياً</b> مثل باقي منتجاتنا، بل يُفعَّل <b>يدوياً من فريق العمل</b>.\n\n👨‍💻 في هذه اللحظة قد يكون فريقنا قد اطّلع على طلبك وبدأ العمل عليه.\n\n⏳ ما عليك سوى الانتظار، وستصلك رسالة هنا فور <b>تفعيل طلبك</b>.\n\nشكراً لصبرك 🤝",
    },
    "en": {
        "ok": "✅ Got it", "no": "❓ I did not understand",
        "ack": "👍 All good! We will notify you here as soon as your order is activated.",
        "explain": "ℹ️ <b>How is your order processed?</b>\n\nThis product (Canva, Snapchat, Free Fire top-up) is <b>not instant delivery</b> like our other products. It is <b>activated manually by our team</b>.\n\n👨‍💻 Right now our team may already have seen your order and started working on it.\n\n⏳ Just wait, and you will receive a message here as soon as <b>your order is activated</b>.\n\nThank you for your patience 🤝",
    },
    "fr": {
        "ok": "✅ Compris", "no": "❓ Je n'ai pas compris",
        "ack": "👍 Parfait ! Nous vous préviendrons ici dès que votre commande sera activée.",
        "explain": "ℹ️ <b>Comment votre commande est-elle traitée ?</b>\n\nCe produit (Canva, Snapchat, recharge Free Fire) n'est <b>pas livré instantanément</b> comme nos autres produits. Il est <b>activé manuellement par notre équipe</b>.\n\n👨‍💻 En ce moment, notre équipe a peut-être déjà vu votre commande et travaille dessus.\n\n⏳ Il suffit d'attendre : vous recevrez un message ici dès que <b>votre commande sera activée</b>.\n\nMerci pour votre patience 🤝",
    },
}
def _hw(lang, key):
    return HOWTO_TX.get(lang, HOWTO_TX["ar"])[key]

def _howto_markup(lang):
    mk = InlineKeyboardMarkup(row_width=1)
    b_ok = InlineKeyboardButton(text=_hw(lang, "ok"), callback_data="hw_ok")
    b_no = InlineKeyboardButton(text=_hw(lang, "no"), callback_data="hw_no")
    b_ok.style = "success"
    b_no.style = "danger"
    mk.add(b_ok)
    mk.add(b_no)
    return mk

@bot.callback_query_handler(func=lambda c: c.data in ("hw_ok", "hw_no"))
def handle_howto(call):
    lang = get_lang(call.from_user.id)
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    except Exception:
        pass
    if call.data == "hw_ok":
        bot.answer_callback_query(call.id, _hw(lang, "ack"), show_alert=True)
        return
    bot.answer_callback_query(call.id)
    _safe_send(call.message.chat.id, _hw(lang, "explain"), parse_mode="HTML")

# ---------- مخزون المنتجات اليدوية ----------
def _manual_in_stock(pid):
    p = find_product(pid)
    if not p:
        return False
    sync_prices()
    sv = p["stock"]
    return sv == "♾️" or (isinstance(sv, int) and sv > 0)

def _manual_stock_dec(pid):
    p = find_product(pid)
    if not p or pid not in MANUAL_IDS:
        return
    try:
        sync_prices()
        old = p["stock"]
        if old == "♾️":
            return
        new = max(0, int(old) - 1)
        if _save_stock(pid, new):
            name = html.escape(p["name"])
            if new == 0:
                monitor_send(f"📭 <b>نفد مخزون</b> {name}\nزر 🔔 «أعلمني» ظهر للزبائن.", key=f"stk0_{pid}", cooldown=600)
            elif new <= 2:
                monitor_send(f"⚠️ <b>مخزون قارب النفاد</b>: {name} — {new} فقط", key=f"stklow_{pid}", cooldown=3600)
    except Exception as e:
        print(f"_manual_stock_dec error: {e}")

# ---------- جرس "أعلمني عند التوفر" ----------
def _notify_subscribe(pid, uid):
    _sadd(f"rk:notify:{pid}", str(uid))

def notify_restock(pid):
    p = find_product(pid)
    if not p:
        return
    subs = _smembers(f"rk:notify:{pid}")
    if not subs:
        return

    def _run():
        for uid in subs:
            lang = get_lang(uid)
            mk = InlineKeyboardMarkup()
            mk.add(InlineKeyboardButton(text=mt(lang, "open_btn"), callback_data=f"buy_{pid}"))
            _safe_send(int(uid), mt(lang, "restock").format(product=html.escape(tr(p, "name", lang))),
                       parse_mode="HTML", reply_markup=mk)
            _srem(f"rk:notify:{pid}", uid)
            time.sleep(0.05)
        monitor_send(f"🔔 <b>أُرسل إشعار التوفر</b> لـ {len(subs)} زبون — {html.escape(p['name'])}")

    threading.Thread(target=_run, daemon=True).start()

def _restock_hook(pid, old, new):
    try:
        if old == 0 and (new == "♾️" or (isinstance(new, int) and new > 0)):
            notify_restock(pid)
    except Exception as e:
        print(f"_restock_hook error: {e}")

# ---------- واجهة المنتج + الفاتورة ----------
def _manual_buy_ui(markup, product, lang):
    pid = product["id"]
    if pid not in MANUAL_IDS:
        return t(lang, "buy_hint")
    rows = []
    if pid == FREEFIRE_ID:
        for i, (lbl, pr) in enumerate(FREEFIRE_PACKS):
            rows.append([InlineKeyboardButton(text=f"💎 {lbl} | ${pr}", callback_data=f"mvar_{pid}_{i}")])
        hint = mt(lang, "pick_pack")
    else:
        rows.append([InlineKeyboardButton(text=mt(lang, "buy_btn"), callback_data=f"mbuy_{pid}")])
        hint = mt(lang, "buy_hint")
    markup.keyboard[0:0] = rows
    return hint

def _start_manual_invoice(call, pid, label=None, price=None):
    uid = call.from_user.id
    lang = get_lang(uid)
    product = find_product(pid)
    if not product or pid not in MANUAL_IDS:
        bot.answer_callback_query(call.id)
        return
    if not _manual_in_stock(pid):
        bot.answer_callback_query(call.id, mt(lang, "out"), show_alert=True)
        return
    if price is None:
        try:
            price = f"{_cur_price(product):.2f}"
        except Exception:
            bot.answer_callback_query(call.id, t(lang, "temp_error"), show_alert=True)
            return
        label = "std"
        full_name = product["name"]
    else:
        full_name = f"{product['name']} — {label}"
    if call.message.chat.type == "private":
        register_user(uid)
    try:
        invoice_id = create_invoice(uid, pid, label, price, full_name)
    except StorageError:
        bot.answer_callback_query(call.id, t(lang, "temp_error"), show_alert=True)
        return
    invoice = get_invoice(invoice_id) or {"label": label, "price_usdt": price}
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    sent = bot.send_message(
        call.message.chat.id,
        build_invoice_text(lang, invoice, product),
        parse_mode="HTML",
        reply_markup=build_invoice_markup(lang, invoice_id, _wallet_covers(uid, invoice.get("price_usdt"))),
    )
    attach_invoice_msg(invoice_id, sent)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data.startswith("mbuy_"))
def handle_manual_buy(call):
    _start_manual_invoice(call, call.data[5:])

@bot.callback_query_handler(func=lambda c: c.data.startswith("mvar_"))
def handle_manual_variant(call):
    try:
        pid, idx = call.data[5:].rsplit(chr(95), 1)
        if pid != FREEFIRE_ID:
            raise ValueError("bad product")
        label, price = FREEFIRE_PACKS[int(idx)]
    except Exception:
        bot.answer_callback_query(call.id)
        return
    _start_manual_invoice(call, pid, label, price)

def _monitor_underpaid(invoice, uid, total, need):
    monitor_send(
        f"⚠️ <b>دفعة ناقصة</b>\n\n📦 {html.escape(str(invoice.get('product_name', '')))}\n"
        f"👤 {_user_link(uid)}\n💵 مدفوع {total:.2f} من {need:.2f} USDT"
    )

# ---------- التنفيذ بعد الدفع (يُستدعى من _fulfill_locked) ----------
def _fulfill_manual(chat_id, uid, lang, claim, canon, retry, mark, failed):
    pid = claim["product_id"]
    pname = claim.get("product_name") or pid
    oid = _oid_from(canon)
    cat = "A" if pid in MANUAL_A else "B"
    try:
        if kv_get_json(f"rk:ord:{oid}") is not None:  # نُفّذ سابقاً: لا نكرر
            mark("manual")
            clear_pending(uid)
            return
        o = {
            "oid": oid, "user_id": uid, "product_id": pid, "product_name": pname,
            "price": str(claim.get("price")), "paid": str(claim.get("paid")), "via": claim.get("via", "binance"),
            "cat": cat, "status": "pending" if cat == "B" else "need_input",
            "ts": int(time.time()), "canon": canon,
        }
        order_save(o)
    except StorageError:
        failed(f"⚠️ <b>خطأ تخزين أثناء تسجيل طلب يدوي</b>\n👤 <code>{uid}</code>\n🧾 <code>{html.escape(canon)}</code>")
        return
    uord_add(uid, oid)
    mark("manual")
    clear_pending(uid)
    was_out = not _manual_in_stock(pid)
    record_purchase(uid, pid, pname, claim.get("price"), canon, via=claim.get("via", "binance"))
    profit_log(canon, pid, pname, claim.get("price"), None)
    _manual_stock_dec(pid)
    _sadd(ORDSET_KEY, oid)
    spname = html.escape(pname)
    if was_out:
        alert_admin(f"⚠️ <b>بيع بينما المخزون 0</b>\n📦 {spname}\n👤 <code>{uid}</code>")
    if cat == "B" and pid == IPTV_ID:
        acct = _iptv_pop()
        if acct:
            ok, msg = deliver_manual_order(oid, acct)
            if ok:
                _iptv_sync_stock()
                alert_admin(f"✅ <b>بيع IPTV تلقائي</b>\n📦 {spname}\n👤 <code>{uid}</code>\n🔑 المتبقي: {_iptv_count()}")
                return
            _iptv_push_back(acct)      # فشل الإرسال: يرجع الحساب للقائمة ويبقى الطلب يدوياً
            alert_admin(f"⚠️ <b>تعذّر التسليم التلقائي لـ IPTV</b> — الطلب بقي معلقاً للتسليم اليدوي\n👤 <code>{uid}</code>\n{msg}")
    if cat == "B" and pid in NETFLIX_TV:
        _safe_send(chat_id, _nfd(lang, "choose").format(product=spname), parse_mode="HTML", reply_markup=_nf_device_markup(lang, oid))
        monitor_send(f"💰 <b>دفع مقبول — بانتظار اختيار الجهاز</b>\n\n📦 {spname}\n👤 {_user_link(uid)}\n"
                     f"💵 {html.escape(str(claim.get('paid')))} USDT")
        return
    if cat == "B":
        _safe_send(chat_id, mt(lang, "paid_b"), reply_markup=support_markup(lang))
        txt = (f"📦 <b>طلب جديد (Pending)</b>\n\n📦 {spname}\n👤 {_user_link(uid)}\n"
               f"💵 {html.escape(str(claim.get('paid')))} USDT ({html.escape(str(claim.get('via')))})\n"
               f"📌 /admin ← 📦 الطلبات المعلقة")
        alert_admin(txt)
        monitor_send(txt)
    else:
        _begin_input(uid, oid, lang, chat_id)
        monitor_send(f"💰 <b>دفع مقبول — بانتظار بيانات الزبون</b>\n\n📦 {spname}\n👤 {_user_link(uid)}\n"
                     f"💵 {html.escape(str(claim.get('paid')))} USDT")

# ---------- جمع بيانات الزبون (الفئة A) ----------
def _validate_input(kind, text):
    s = (text or "").strip()
    if kind == "username":
        s = s.lstrip("@")
        return s if re.fullmatch(r"[A-Za-z][A-Za-z0-9._-]{2,14}", s) else None
    if kind == "playerid":
        s = s.replace(" ", "")
        return s if re.fullmatch(r"\d{6,14}", s) else None
    if kind == "email":
        s = s.lower()
        return s if len(s) <= 100 and re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", s) else None
    return None

def _ask_text(lang, o):
    kind = MANUAL_A[o["product_id"]]
    return mt(lang, "ask_" + kind).format(product=html.escape(o.get("product_name", "")))

def _begin_input(uid, oid, lang, chat_id):
    o = order_get(oid)
    if not o:
        return
    try:
        cur = kv_get(f"rk:inp:{uid}")
        cur_o = order_get(str(cur)) if cur else None
        if cur_o and str(cur) != oid and cur_o.get("status") in ("need_input", "confirm_input"):
            _safe_send(chat_id, mt(lang, "queued"))
            return
        kv_set(f"rk:inp:{uid}", oid)
    except StorageError:
        pass
    _safe_send(chat_id, _ask_text(lang, o), parse_mode="HTML")

def _next_input(uid, lang, chat_id):
    for oid in uord_list(uid, 20):
        o = order_get(oid)
        if o and o.get("status") == "need_input" and o.get("product_id") in MANUAL_A:
            _begin_input(uid, oid, lang, chat_id)
            return

def _awaiting_input(m):
    try:
        if not m.text or m.text.startswith("/") or m.chat.type != "private":
            return False
        if get_pending_invoice_id(m.from_user.id) is not None:  # عنده فاتورة دفع مفتوحة: رقم العملية أولاً
            return False
        oid = kv_get(f"rk:inp:{m.from_user.id}")
        if not oid:
            return False
        o = order_get(str(oid))
        return bool(o and o.get("status") == "need_input")
    except Exception:
        return False

@bot.message_handler(func=_awaiting_input, content_types=["text"])
def handle_input_text(message):
    uid = message.from_user.id
    lang = get_lang(uid)
    oid = str(kv_get(f"rk:inp:{uid}"))
    o = order_get(oid)
    if not o:
        return
    kind = MANUAL_A[o["product_id"]]
    val = _validate_input(kind, message.text)
    if val is None:
        bot.send_message(message.chat.id, mt(lang, "bad_" + kind))
        return
    o["input"] = val
    o["status"] = "confirm_input"
    order_save(o)
    mk = InlineKeyboardMarkup()
    mk.row(
        InlineKeyboardButton(text=mt(lang, "btn_confirm"), callback_data=f"inp_ok_{oid}"),
        InlineKeyboardButton(text=mt(lang, "btn_edit"), callback_data=f"inp_ed_{oid}"),
    )
    bot.send_message(
        message.chat.id,
        mt(lang, "confirm_q").format(label=mt(lang, "lbl_" + kind), val=html.escape(val)),
        parse_mode="HTML", reply_markup=mk,
    )

@bot.callback_query_handler(func=lambda c: c.data.startswith("inp_"))
def handle_input_cb(call):
    uid = call.from_user.id
    lang = get_lang(uid)
    parts = call.data.split(chr(95), 2)
    if len(parts) != 3:
        bot.answer_callback_query(call.id)
        return
    act, oid = parts[1], parts[2]
    o = order_get(oid)
    if not o or str(o.get("user_id")) != str(uid) or o.get("product_id") not in MANUAL_A:
        bot.answer_callback_query(call.id)
        return
    if act == "ed":
        if o.get("status") not in ("confirm_input", "need_input"):
            bot.answer_callback_query(call.id)
            return
        o["status"] = "need_input"
        order_save(o)
        kv_set(f"rk:inp:{uid}", oid)
        _edit_cb(call, _ask_text(lang, o))
        bot.answer_callback_query(call.id)
        return
    if act == "ok":
        if o.get("status") != "confirm_input":
            bot.answer_callback_query(call.id)
            return
        o["status"] = "pending"
        o["input_ts"] = int(time.time())
        order_save(o)
        try:
            kv_del(f"rk:inp:{uid}")
        except StorageError:
            pass
        if MANUAL_A[o["product_id"]] == "email":
            _edit_cb(call, mt(lang, "input_saved_email").format(product=html.escape(o.get("product_name", "")), label=mt(lang, "lbl_email"), val=html.escape(o.get("input", "")), paid=html.escape(str(o.get("paid", "")))), _howto_markup(lang))
        else:
            _edit_cb(call, mt(lang, "input_saved"), _howto_markup(lang))
        bot.answer_callback_query(call.id)
        kind = MANUAL_A[o["product_id"]]
        txt = (f"📦 <b>طلب جديد (Pending)</b>\n\n📦 {html.escape(o['product_name'])}\n👤 {_user_link(uid)}\n"
               f"🔤 {INPUT_LBL_AR[kind]}: <code>{html.escape(o['input'])}</code>\n"
               f"💵 {html.escape(str(o.get('paid')))} USDT\n📌 /admin ← 📦 الطلبات المعلقة")
        alert_admin(txt)
        monitor_send(txt)
        _next_input(uid, lang, call.message.chat.id)
        return
    bot.answer_callback_query(call.id)

# ---------- لوحة الأدمن: الطلبات المعلقة ----------
def _ord_count():
    n = 0
    try:
        for _oid in _smembers(ORDSET_KEY):
            _o = order_get(_oid)
            if _o and _o.get("status") in OPEN_STATES:
                n += 1
    except Exception as e:
        print(f"ord_count error: {e}")
    return n

def show_pending_orders(chat_id, msg_id=None):
    rows = []
    for oid in _smembers(ORDSET_KEY):
        o = order_get(oid)
        if not o or o.get("status") not in OPEN_STATES:
            _srem(ORDSET_KEY, oid)
            continue
        rows.append(o)
    rows.sort(key=lambda x: x.get("ts", 0))
    markup = InlineKeyboardMarkup(row_width=1)
    for o in rows[:40]:
        markup.add(InlineKeyboardButton(
            text=f"{ORD_ICONS.get(o['status'], '')} {o['product_name'][:28]} | {o['user_id']}",
            callback_data=f"ord_v_{o['oid']}",
        ))
    text = f"📦 <b>الطلبات المعلقة</b> ({len(rows)})\n🔔 جاهز | ⏳ ينتظر بيانات الزبون" if rows else "📦 لا توجد طلبات معلقة ✅"
    _pr_show(chat_id, msg_id, text, markup)

def order_admin_text(o):
    lines = [
        f"🧾 <b>طلب</b> <code>{o['oid']}</code>",
        f"📦 {html.escape(o.get('product_name', ''))}",
        f"👤 {_user_link(o['user_id'])}",
        f"💵 {html.escape(str(o.get('paid')))} USDT ({html.escape(str(o.get('via')))})",
        f"📅 {_fmt_date(o.get('ts'))}",
        f"📌 {ORD_ICONS.get(o.get('status'), '')} {ADMIN_ST.get(o.get('status'), '')}",
    ]
    if o.get("input"):
        lines.append(f"🔤 {INPUT_LBL_AR.get(MANUAL_A.get(o['product_id']), '')}: <code>{html.escape(o['input'])}</code>")
    if o.get("product_id") in NETFLIX_TV:
        _dv = {"phone": "📱 الهاتف", "pc": "💻 الحاسوب", "tv": "📺 التلفاز"}.get(o.get("device"), "⏳ لم يختر بعد")
        lines.append(f"🎯 الجهاز: {_dv}")
        if o.get("tv_code"):
            lines.append(f"🔢 كود التلفاز: <code>{html.escape(str(o['tv_code']))}</code>")
    return "\n".join(lines)

def mark_executed(oid):
    o = order_get(oid)
    if not o or o.get("status") != "pending" or o.get("cat") != "A":
        return False, "❌ هذا الطلب غير جاهز للتنفيذ (ربما نُفّذ من قبل)."
    o["status"] = "done"
    o["done_ts"] = int(time.time())
    o["confirmed_by"] = "admin"
    order_save(o)
    _srem(ORDSET_KEY, oid)
    uid = o["user_id"]
    lang = get_lang(uid)
    sent = _safe_send(uid, mt(lang, "executed").format(product=html.escape(o["product_name"])),
                      parse_mode="HTML", reply_markup=support_markup(lang))
    monitor_send(f"✅ <b>طلب نُفّذ</b>\n\n📦 {html.escape(o['product_name'])}\n👤 {_user_link(uid)}")
    return True, "✅ تم وسم الطلب كمنفّذ وأُبلغ الزبون." + ("" if sent else "\n⚠️ تعذر إبلاغ الزبون (ربما حظر البوت).")

# ---------- IPTV: تسليم تلقائي من قائمة حسابات في Upstash ----------
IPTV_ID = "iptv_14m"
IPTV_KEY = "rk:iptv:accts"

def _iptv_count():
    try:
        return int(db.llen(IPTV_KEY) or 0) if db else 0
    except Exception:
        return 0

def _iptv_pop():
    try:
        v = db.lpop(IPTV_KEY) if db else None
        if isinstance(v, (list, tuple)):
            v = v[0] if v else None
        return str(v).strip() if v else None
    except Exception as e:
        print(f"iptv pop error: {e}")
        return None

def _iptv_push_back(acct):
    try:
        db.lpush(IPTV_KEY, acct)
    except Exception as e:
        print(f"iptv push back error: {e}")

def _iptv_sync_stock():
    try:
        p = find_product(IPTV_ID)
        old = p["stock"] if p else 0
        n = _iptv_count()
        _save_stock(IPTV_ID, n)
        _restock_hook(IPTV_ID, old, n)
    except Exception as e:
        print(f"iptv sync stock error: {e}")

@bot.message_handler(commands=["addiptv", "iptvstock"])
def iptv_admin_command(message):
    if str(message.chat.id) != str(ADMIN_CHAT_ID):
        return
    cmd = (message.text or "").split()[0].lstrip("/").split("@")[0]
    if cmd == "iptvstock":
        bot.reply_to(message, f"📡 حسابات IPTV المخزّنة: <b>{_iptv_count()}</b>", parse_mode="HTML")
        return
    parts = (message.text or "").split(None, 1)
    body = parts[1] if len(parts) > 1 else ""
    if re.search(r"(?i)account created", body):
        # صيغة لوحة المورّد: كل حساب يبدأ بـ «✅ Account Created Successfully!» (نحذف هذا السطر ونحتفظ بالباقي)
        blocks = re.split(r"(?i)[^\S\n]*✅?[^\S\n]*account created successfully!?[^\S\n]*", body)
    elif re.search(r"\n\s*\n", body):
        blocks = re.split(r"\n\s*\n", body)          # حسابات متعددة الأسطر يفصلها سطر فارغ
    else:
        blocks = body.splitlines()                    # كل سطر حساب
    lines = [b.strip() for b in blocks if b and b.strip()]
    if not lines:
        bot.reply_to(message, "الاستعمال: أرسل /addiptv ثم الحساب (أو عدة حسابات).\nالحساب المتعدد الأسطر: افصل بين الحسابات بسطر فارغ، أو الصق الرسالة كما جاءت من المورّد.")
        return
    try:
        db.rpush(IPTV_KEY, *lines)
        _iptv_sync_stock()
        bot.reply_to(message, f"✅ أُضيف {len(lines)} حساب. المخزون الآن: <b>{_iptv_count()}</b>", parse_mode="HTML")
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ: {html.escape(str(e))[:200]}")

def deliver_manual_order(oid, text):
    o = order_get(oid)
    if not o or o.get("status") != "pending" or o.get("cat") != "B":
        return False, "❌ هذا الطلب غير جاهز للتسليم (ربما سُلّم من قبل)."
    text = (text or "").strip()
    if not text:
        return False, "❌ نص فارغ."
    if len(text) > 3000:
        return False, "❌ النص طويل جداً (الحد 3000 حرف)."
    uid = o["user_id"]
    lang = get_lang(uid)
    if o["product_id"] == NORD_ID:
        body = f"🔑 <code>{html.escape(text)}</code>\n\n{html.escape(NORD_GUIDE.get(lang, NORD_GUIDE['ar']))}"
    else:
        body = f"<code>{html.escape(text)}</code>"
    mk = InlineKeyboardMarkup()
    mk.row(
        InlineKeyboardButton(text=mt(lang, "btn_received"), callback_data=f"rcv_{oid}"),
        InlineKeyboardButton(text=t(lang, "support_btn"), url=MY_PRIVATE_CHAT_LINK),
    )
    if o["product_id"] in NETFLIX_TV:
        # بروفيل Netflix: نرسل نصك كما كتبته (بدون قالب)، وتحته زر «تم استلام الطلب» وزر فريق التفعيل
        mk = InlineKeyboardMarkup(row_width=1)
        b_rcv = InlineKeyboardButton(text=_nfd(lang, "recv"), callback_data=f"rcv_{oid}")
        b_rcv.style = "success"
        mk.add(b_rcv)
        mk.add(InlineKeyboardButton(text=_tv(lang, "team"), url=MY_PRIVATE_CHAT_LINK))
        out_text, out_pm = _nf_html(text, lang), "HTML"
    else:
        out_text, out_pm = mt(lang, "delivery").format(product=html.escape(o["product_name"]), body=body), "HTML"
    try:
        sent = bot.send_message(uid, out_text, parse_mode=out_pm, reply_markup=mk, disable_web_page_preview=True)
    except ApiTelegramException as e:
        if e.error_code == 403:
            return False, "🚫 الزبون حظر البوت — لم يُسلَّم الطلب وبقي في القائمة."
        return False, f"❌ فشل الإرسال: {html.escape(str(e))[:200]}"
    except Exception as e:
        return False, f"❌ فشل الإرسال: {html.escape(str(e))[:200]}"
    o.update({
        "status": "delivered_wait", "delivery": text, "delivered_at": time.time(),
        "chat_id": sent.chat.id, "message_id": sent.message_id,
    })
    order_save(o)
    _srem(ORDSET_KEY, oid)
    _sadd(WAITSET_KEY, oid)
    monitor_send(f"📬 <b>تم تسليم طلب</b> (ينتظر تأكيد الزبون 20 د)\n\n📦 {html.escape(o['product_name'])}\n👤 {_user_link(uid)}")
    return True, "✅ تم إرسال البيانات للزبون."

PROFIT_FIXED = {          # ربحك الثابت لكل طلبية (بالدولار) — يمكن تغييره بـ /setprofit
    "netflix_full": "1", "netflix_profile": "1",
    "canva_edu_500": "3",       # Canva Pro panel
    "canva_edu_5000": "0.20",   # Canva (الثاني)
    "iptv_14m": "5",
}

PROFIT_PCT = {            # منتجات ربحها 30% من سعر البيع
    "gemini_18m": 30, "capcut_1m": 30, "duolingo_12m": 30, "duolingo_link_12m": 30,
    "chatgpt_plus_1m": 30, "chatgpt_k12_edu": 30,
}

def _fixed_profit(pid):
    try:
        v = (_vt_conf().get("pf") or {}).get(pid)
        if v is None:
            v = PROFIT_FIXED.get(pid)
        return Decimal(str(v)) if v is not None else None
    except Exception:
        return None

def _pl_local(ts):
    return time.gmtime(int(ts) + 3600)      # توقيت الجزائر UTC+1

def _pl_mkey(ts):
    g = _pl_local(ts)
    return f"{g.tm_year}-{g.tm_mon:02d}"

def profit_log(canon, pid, pname, price, cost=None):
    """يسجل بيعة واحدة وربحها الصافي (آمن ضد التكرار). لا يكسر الشراء أبداً."""
    try:
        if not db:
            return
        if not kv_set(f"rk:plg:{canon}", "1", nx=True):
            return
        ts = int(time.time())
        pid_s = str(pid or "")
        pr = None
        pc = None
        try:
            pc = Decimal(str(price).replace("$", "").strip())
        except Exception:
            pc = None
        fx = _fixed_profit(pid_s)
        if fx is not None:
            pr = fx
        elif cost is not None and pc is not None:
            pr = pc - Decimal(str(cost))
        elif pid_s in PROFIT_PCT and pc is not None:
            pr = pc * Decimal(PROFIT_PCT[pid_s]) / Decimal(100)      # نسبة من سعر البيع
        elif pid_s.startswith("vt") and pc is not None:
            _m = Decimal(_vt_margin_for((_VT_PRODS.get(pid_s) or {}).get("name")))
            pr = pc * _m / (Decimal(100) + _m)
        rec = {"t": ts, "p": pid_s, "n": str(pname or "")[:60], "s": str(pc if pc is not None else price),
               "g": None if pr is None else float(round(pr, 4))}
        db.lpush(f"rk:pl:{_pl_mkey(ts)}", json.dumps(rec, ensure_ascii=False))
    except Exception as e:
        print(f"profit_log error: {e}")

def _pl_stats(mkey, day=None):
    """(عدد الطلبات، الربح الصافي، عدد الطلبات بلا ربح محدد)"""
    n, total, unk = 0, 0.0, 0
    try:
        for raw in (db.lrange(f"rk:pl:{mkey}", 0, -1) or []):
            try:
                r = raw if isinstance(raw, dict) else json.loads(raw)
            except Exception:
                continue
            if day is not None:
                g = _pl_local(r.get("t", 0))
                if (g.tm_year, g.tm_mon, g.tm_mday) != day:
                    continue
            n += 1
            if r.get("g") is None:
                unk += 1
            else:
                total += float(r["g"])
    except Exception as e:
        print(f"pl_stats error: {e}")
    return n, total, unk

def _profit_screen(which):
    now = int(time.time())
    g = _pl_local(now)
    cur = f"{g.tm_year}-{g.tm_mon:02d}"
    py, pm = (g.tm_year, g.tm_mon - 1) if g.tm_mon > 1 else (g.tm_year - 1, 12)
    prev = f"{py}-{pm:02d}"
    if which == "m":
        n, p, u = _pl_stats(cur)
        title = f"🗓️ <b>الشهر الحالي</b> ({cur})"
    elif which == "l":
        n, p, u = _pl_stats(prev)
        title = f"⏮️ <b>الشهر الماضي</b> ({prev})"
    else:
        n, p, u = _pl_stats(cur, day=(g.tm_year, g.tm_mon, g.tm_mday))
        title = f"📅 <b>اليوم</b> ({g.tm_year}-{g.tm_mon:02d}-{g.tm_mday:02d})"
    text = f"💰 <b>ربح الصافي</b>\n\n{title}\n🛒 الطلبيات المباعة: <b>{n}</b>\n💵 الربح الصافي: <b>{p:.2f}$</b>"
    if u:
        text += f"\n\n⚠️ {u} طلبية بلا ربح محدد (لم تُحسب). حدّد ربح المنتج بـ: /setprofit رمز_المنتج المبلغ"
    mk = InlineKeyboardMarkup(row_width=1)
    if which != "d":
        mk.add(InlineKeyboardButton(text="📅 ربح اليوم", callback_data="adm_profit"))
    if which != "m":
        mk.add(InlineKeyboardButton(text="🗓️ الشهر الحالي", callback_data="adm_profit_m"))
    if which != "l":
        mk.add(InlineKeyboardButton(text="⏮️ ربح الشهر الماضي", callback_data="adm_profit_l"))
    return text, mk

@bot.message_handler(commands=["setprofit"])
def setprofit_cmd(message):
    if str(message.chat.id) != str(ADMIN_CHAT_ID):
        return
    a = (message.text or "").split()
    if len(a) == 1:
        conf = _vt_conf().get("pf") or {}
        rows = {**PROFIT_FIXED, **conf}
        bot.reply_to(message, "💰 أرباح ثابتة لكل طلبية:\n" + "\n".join(f"• {k} = {v}$" for k, v in rows.items())
                     + "\n\nلتغيير: /setprofit رمز_المنتج المبلغ\nللحذف: /setprofit رمز_المنتج -")
        return
    if len(a) < 3:
        bot.reply_to(message, "الاستعمال: /setprofit رمز_المنتج المبلغ")
        return
    conf = dict(_vt_conf())
    pf = dict(conf.get("pf") or {})
    if a[2] == "-":
        pf.pop(a[1], None)
        PROFIT_FIXED.pop(a[1], None)
    else:
        try:
            pf[a[1]] = str(Decimal(a[2].replace(",", ".")))
        except Exception:
            bot.reply_to(message, "❌ مبلغ غير صالح")
            return
    conf["pf"] = pf
    _vt_conf_save(conf)
    bot.reply_to(message, "✅ تم الحفظ")

# ---------- قائمة المهتمين («أعلمني عند التوفر») للأدمن ----------
_PM_INTEREST_NAMES = {"bd": "بريدي موب", "fx": "Flixy", "rd": "RedotPay (يدوي)", "rp": "RedotPay", "bb": "Bybit"}

def _interest_name(key):
    try:
        if key == "rk:notify:api":
            return "🔌 API"
        rest = key[len("rk:notify:"):]
        if rest.startswith("g:"):
            _, pid, idx = rest.split(":")
            p = find_product(pid)
            label = GIFT_VARIANTS[pid][int(idx)][0]
            return f"{(p or {}).get('name', pid)} — {label}"
        p = find_product(rest) or _VT_PRODS.get(rest)
        if p:
            return p.get("name") or rest
        return rest
    except Exception:
        return key

def _interest_rows():
    keys = {k for k in _mem_sets if k.startswith("rk:notify:")}
    if db:
        try:
            keys |= {str(k) for k in (db.keys("rk:notify:*") or [])}
        except Exception as e:
            print(f"interest keys failed: {e}")
    rows = []
    for k in keys:
        n = len(_smembers(k))
        if n:
            rows.append((n, _interest_name(k)))
    for m, nm in _PM_INTEREST_NAMES.items():
        try:
            n = len(pmw_list(m))
        except Exception:
            n = 0
        if n:
            rows.append((n, f"💳 {nm}"))
    try:
        n = len(_smembers(MAINT_SUBS))
        if n:
            rows.append((n, "🛠️ عودة البوت (وضع التحديث)"))
    except Exception:
        pass
    rows.sort(key=lambda r: (-r[0], r[1]))
    return rows

def _interest_screen():
    rows = _interest_rows()
    if not rows:
        text = "🔔 <b>المهتمون</b>\n\nلا يوجد أحد ينتظر إشعار توفر حالياً."
    else:
        total = sum(n for n, _ in rows)
        lines = [f"\u200e{i}. \u2068{html.escape(name)}\u2069 \u2066({n}🔔)\u2069" for i, (n, name) in enumerate(rows, 1)]
        text = f"🔔 <b>المهتمون ({total})</b>\nالأكثر طلباً أولاً — يُحذف المنتج من القائمة عند توفره.\n\n" + "\n".join(lines)
        if len(text) > 3900:
            text = text[:3900].rsplit("\n", 1)[0] + "\n…"
    mk = InlineKeyboardMarkup(row_width=1)
    mk.add(InlineKeyboardButton(text="🔄 تحديث", callback_data="adm_interest"))
    mk.add(InlineKeyboardButton(text=t("ar", "back"), callback_data="adm_home"))
    return text, mk

WAL_PAGE = 25

def _avail_from_hash(h):
    def _i(k):
        try:
            return int(float(h.get(k, 0) or 0))
        except (ValueError, TypeError):
            return 0
    reward = _i("reward_c") if "reward_c" in h else _i("spent_c") * WALLET_PCT // 100
    return max(0, reward + _i("topup_c") - _i("redeemed_c") - _i("wspent_c"))

def _wallet_rows():
    """[(avail_cents, uid, name)] لمن رصيده > 0، من الأكبر للأصغر."""
    uids = sorted(known_users)
    hashes = None
    try:
        pipe = db.pipeline()
        for u in uids:
            pipe.hgetall(_prof_key(u))
        hashes = pipe.exec()
    except Exception as e:
        print(f"wallet_rows pipeline failed: {e}")
        hashes = None
    rows = []
    for i, u in enumerate(uids):
        try:
            if hashes is not None:
                raw = hashes[i]
                if isinstance(raw, (list, tuple)):
                    raw = dict(zip(raw[0::2], raw[1::2]))
                h = {str(a): str(b) for a, b in (raw or {}).items()}
            else:
                h = {str(a): str(b) for a, b in (db.hgetall(_prof_key(u)) or {}).items()}
            av = _avail_from_hash(h)
            if av > 0:
                rows.append((av, u, h.get("name", "")))
        except Exception:
            continue
    rows.sort(key=lambda r: -r[0])
    return rows

def _wallets_screen(offset=0):
    rows = _wallet_rows()
    if not rows:
        text = "💼 <b>أرصدة الزبائن</b>\n\nلا يوجد زبون عنده رصيد حالياً."
        total_pages = 1
    else:
        total = sum(r[0] for r in rows)
        offset = max(0, min(offset, max(0, len(rows) - 1)))
        chunk = rows[offset:offset + WAL_PAGE]
        lines = []
        for i, (av, u, nm) in enumerate(chunk, offset + 1):
            nm = html.escape(nm.strip()) if nm and nm.strip() else "—"
            lines.append(f"\u200e{i}. <b>${_money(av)}</b> — \u2068{nm}\u2069 — <code>{u}</code>")
        text = (f"💼 <b>أرصدة الزبائن</b>\n👥 {len(rows)} زبون · 💵 المجموع ${_money(total)}\n"
                f"الأكبر رصيداً أولاً (من رصيده 0 غير ظاهر)\n\n" + "\n".join(lines))
    mk = InlineKeyboardMarkup(row_width=2)
    nav = []
    if rows and offset > 0:
        nav.append(InlineKeyboardButton(text="⬅️ السابق", callback_data=f"adm_wal{max(0, offset - WAL_PAGE)}"))
    if rows and offset + WAL_PAGE < len(rows):
        nav.append(InlineKeyboardButton(text="التالي ➡️", callback_data=f"adm_wal{offset + WAL_PAGE}"))
    if nav:
        mk.row(*nav)
    mk.add(InlineKeyboardButton(text="🔄 تحديث", callback_data=f"adm_wal{offset}"))
    mk.add(InlineKeyboardButton(text=t("ar", "back"), callback_data="adm_home"))
    return text, mk

def _mode_of(pid):
    """للمنتج اليدوي المستبدَل بمنتج مورّد: 'auto' إذا غطّاه المورّد، 'manual' إذا رجع يدوياً."""
    return "auto" if _own_hidden(pid) else "manual"

def _mode_watch_pids():
    conf = _vt_conf()
    pids = set(VENTE_REPLACE_DEFAULT) | set(conf.get("replace", []))
    out = []
    for pid in sorted(pids):
        if pid in OWN_ALWAYS_HIDDEN or pid in REMOVED_OWN or str(pid).startswith("vt"):
            continue
        if _find_product_orig(pid) is None:
            continue
        out.append(pid)
    return out

def _mode_watch():
    """يُنبّه الأدمن عندما يتحوّل منتج بين تلقائي (مورّد) ويدوي (أنت). أول مرة: يسجّل الحالة بدون إشعار."""
    if not VENTE_KEY or not _VT_PRODS:
        return          # تعذّر جلب المورّد: لا نُنبّه خطأً
    for pid in _mode_watch_pids():
        try:
            mode = _mode_of(pid)
            key = f"rk:mode:{pid}"
            old = kv_get(key)
            if isinstance(old, bytes):
                old = old.decode()
            if old == mode:
                continue
            kv_set(key, mode)
            if old is None:
                continue
            nm = html.escape(str(_find_product_orig(pid).get("name", pid)))
            if mode == "manual":
                alert_admin(f"⚠️ <b>منتج صار يدوي</b>\n📦 {nm}\nالمورّد لم يعد يوفره الآن، فالطلبات عليه ستصلك كطلب يدوي تسلّمه أنت من «الطلبات المعلقة».")
            else:
                alert_admin(f"✅ <b>منتج عاد تلقائياً</b>\n📦 {nm}\nالمورّد وفّره من جديد، والتسليم صار تلقائياً.")
        except Exception as e:
            print(f"mode_watch failed for {pid}: {e}")

def _modes_screen():
    watch = set(_mode_watch_pids())
    manual_b, manual_a, auto_own, hidden = [], [], [], []
    for p in products:
        pid = p.get("id")
        if p.get("type") == "separator" or not pid:
            continue
        nm = html.escape(str(p.get("name", pid))[:44])
        if pid in REMOVED_OWN:
            continue
        if pid in OWN_ALWAYS_HIDDEN:
            hidden.append(nm)
            continue
        if pid in MANUAL_A:
            manual_a.append(f"• {nm}")
        elif pid in MANUAL_B:
            if _own_hidden(pid):
                hidden.append(nm + " (المورّد يغطيه)")
            else:
                tag = " ⚠️ <i>مؤقتاً: المورّد غير متوفر</i>" if pid in watch else ""
                manual_b.append(f"• {nm}{tag}")
        elif pid == GEMINI_ID:
            auto_own.append(f"• {nm} (روابط من مخزونك)")
    gift_n = len([k for k in GIFT_VARIANTS])
    vt_ok = sorted([p for p in _VT_PRODS.values() if _vt_listed(p) and p["stock"] > 0], key=lambda x: x["name"].lower())
    vt_out = len([p for p in _VT_PRODS.values() if _vt_listed(p) and p["stock"] <= 0])
    lines = ["🔧 <b>المنتجات اليدوية / التلقائية</b>", ""]
    lines.append(f"🖐 <b>يدوي: تسلّمه أنت ({len(manual_b)})</b>")
    lines += manual_b or ["—"]
    lines.append("")
    lines.append(f"📝 <b>يدوي: الزبون يرسل بياناته ثم يُفعَّل ({len(manual_a)})</b>")
    lines += manual_a or ["—"]
    lines.append("")
    lines.append("⚡ <b>تلقائي</b>")
    lines += auto_own
    lines.append(f"• بطاقات الهدايا: {gift_n} نوع (FAZER)")
    lines.append(f"• منتجات المورّد المتوفرة: {len(vt_ok)}" + (f" (+{vt_out} نافد)" if vt_out else ""))
    for p in vt_ok[:22]:
        lines.append(f"   · {html.escape(p['name'][:38])} — {p['stock']}")
    if len(vt_ok) > 22:
        lines.append(f"   … و{len(vt_ok) - 22} أخرى")
    if hidden:
        lines.append("")
        lines.append(f"🙈 <b>مخفي عن الزبائن ({len(hidden)})</b>")
        lines += [f"• {h}" for h in hidden]
    text = "\n".join(lines)
    if len(text) > 3900:
        text = text[:3890] + "…"
    mk = InlineKeyboardMarkup(row_width=1)
    mk.add(InlineKeyboardButton(text="🔄 تحديث", callback_data="adm_modes"))
    mk.add(InlineKeyboardButton(text=t("ar", "back"), callback_data="adm_home"))
    return text, mk

def _admin_panel_extra(call, op):
    if op == "modes":
        try:
            text, mk = _modes_screen()
        except Exception as e:
            print(f"modes_screen failed: {e}")
            bot.answer_callback_query(call.id, "❌ تعذّر جلب القائمة", show_alert=True)
            return True
        try:
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=mk, disable_web_page_preview=True)
        except Exception as e:
            if "not modified" not in str(e).lower():
                bot.send_message(call.message.chat.id, text, parse_mode="HTML", reply_markup=mk)
        bot.answer_callback_query(call.id)
        return True
    if op == "wal" or (op.startswith("wal") and op[3:].isdigit()):
        try:
            off = int(op[3:] or 0)
            text, mk = _wallets_screen(off)
        except Exception as e:
            print(f"wallets_screen failed: {e}")
            bot.answer_callback_query(call.id, "❌ تعذّر جلب الأرصدة", show_alert=True)
            return True
        try:
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=mk)
        except Exception as e:
            if "not modified" not in str(e).lower():
                bot.send_message(call.message.chat.id, text, parse_mode="HTML", reply_markup=mk)
        bot.answer_callback_query(call.id)
        return True
    if op == "interest":
        text, mk = _interest_screen()
        try:
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=mk)
        except Exception as e:
            if "not modified" not in str(e).lower():
                bot.send_message(call.message.chat.id, text, parse_mode="HTML", reply_markup=mk)
        bot.answer_callback_query(call.id)
        return True
    if op == "home":      # زر «رجوع» من شاشات الأدمن (طرق الدفع...) إلى لوحة الأدمن
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        admin_panel_cmd(_types.SimpleNamespace(from_user=call.from_user, chat=call.message.chat, text="/admin"))
        bot.answer_callback_query(call.id)
        return True
    if op == "maint":
        was = _maint_on()
        on = not was
        _maint_set(on)
        extra = ""
        if was and not on:
            extra = f"\n🔔 أُرسل إشعار العودة لـ {_maint_broadcast_back()} زبون."
        try:
            rm = call.message.reply_markup
            for row in rm.keyboard:
                for b in row:
                    if getattr(b, "callback_data", None) == "adm_maint":
                        b.text = _maint_label()
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=rm)
        except Exception as e:
            print(f"maint label update failed: {e}")
        bot.answer_callback_query(
            call.id,
            ("🛠️ تم تشغيل وضع التحديث: البوت متوقف عند الزبائن، وأنت تبقى تستعمله عادياً." if on
             else "✅ تم إيقاف وضع التحديث: البوت يعمل للجميع.") + extra,
            show_alert=True)
        return True
    if op in ("profit", "profit_m", "profit_l"):
        text, mk = _profit_screen({"profit": "d", "profit_m": "m", "profit_l": "l"}[op])
        try:
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=mk)
        except Exception as e:
            if "not modified" not in str(e).lower():
                bot.send_message(call.message.chat.id, text, parse_mode="HTML", reply_markup=mk)
        bot.answer_callback_query(call.id)
        return True
    if op == "pend":
        show_pending_orders(call.message.chat.id)
        bot.answer_callback_query(call.id)
        return True
    if op == "prices":
        show_price_list(call.message.chat.id)
        bot.answer_callback_query(call.id)
        return True
    return False

@bot.callback_query_handler(func=lambda c: c.data.startswith("ord_"))
def handle_order_admin(call):
    if not _is_admin_user(call.from_user.id):
        bot.answer_callback_query(call.id)
        return
    chat_id, msg_id = call.message.chat.id, call.message.message_id
    parts = call.data.split(chr(95), 2)
    act = parts[1] if len(parts) > 1 else ""
    oid = parts[2] if len(parts) > 2 else ""
    if act == "l":
        show_pending_orders(chat_id, msg_id)
        bot.answer_callback_query(call.id)
        return
    o = order_get(oid)
    if not o:
        bot.answer_callback_query(call.id, "❌ الطلب غير موجود", show_alert=True)
        return
    if act == "v":
        mk = InlineKeyboardMarkup(row_width=1)
        if o.get("status") == "pending" and o.get("product_id") in NETFLIX_TV and o.get("device") == "tv" and o.get("tv_code"):
            mk.add(InlineKeyboardButton(text="✅ تم تفعيل", callback_data=f"tva_{oid}"))
            mk.add(InlineKeyboardButton(text="📩 تواصل مع فريق التفعيل", callback_data=f"tvs_{oid}"))
        if o.get("status") == "pending" and o.get("cat") == "B":
            mk.add(InlineKeyboardButton(text="📤 إرسال بيانات الطلب للزبون", callback_data=f"ord_d_{oid}"))
        if o.get("status") == "pending" and o.get("cat") == "A":
            mk.add(InlineKeyboardButton(text="✅ تم التنفيذ", callback_data=f"ord_x_{oid}"))
        mk.add(InlineKeyboardButton(text="🗑️ حذف الطلب من القائمة", callback_data=f"ord_r_{oid}"))
        mk.add(InlineKeyboardButton(text="⬅️ القائمة", callback_data="ord_l_0"))
        if o.get("product_id") in NETFLIX_TV:
            # زر «مراسلة الزبون» يفتح دردشته مباشرة؛ إن منعته خصوصية الزبون نعرض الشاشة بدونه
            mk_chat = InlineKeyboardMarkup(row_width=1)
            mk_chat.add(InlineKeyboardButton(text="💬 مراسلة الزبون", url=f"tg://user?id={o['user_id']}"))
            for _row in mk.keyboard:
                mk_chat.keyboard.append(_row)
            try:
                _pr_show(chat_id, msg_id, order_admin_text(o), mk_chat)
            except Exception as e:
                print(f"order view with chat btn failed: {e}")
                _pr_show(chat_id, msg_id, order_admin_text(o), mk)
        else:
            _pr_show(chat_id, msg_id, order_admin_text(o), mk)
        bot.answer_callback_query(call.id)
        return
    if act == "d":
        if o.get("status") != "pending" or o.get("cat") != "B":
            bot.answer_callback_query(call.id, "❌ غير جاهز للتسليم", show_alert=True)
            return
        _price_wait.pop(call.from_user.id, None)
        _adm_wait[call.from_user.id] = {"op": "deliver", "oid": oid}
        hint = "\n(للنورد: أرسل الكود فقط، والبوت يضيف الرابط والخطوات)" if o["product_id"] == NORD_ID else ""
        bot.send_message(
            chat_id,
            f"✍️ أرسل الآن بيانات الطلب كرسالة واحدة (إيميل/باسوورد، كود، رابط...) لـ {html.escape(o['product_name'])}.{hint}\n(أو /admin للإلغاء)",
            parse_mode="HTML",
        )
        bot.answer_callback_query(call.id)
        return
    if act == "r":
        mk = InlineKeyboardMarkup(row_width=1)
        mk.add(InlineKeyboardButton(text="✅ نعم، احذف الطلب", callback_data=f"ord_y_{oid}"))
        mk.add(InlineKeyboardButton(text="⬅️ لا، رجوع", callback_data=f"ord_v_{oid}"))
        _pr_show(chat_id, msg_id,
                 order_admin_text(o) + "\n\n⚠️ <b>حذف نهائي من القائمة ومن سجل الزبون.</b>\nلا يُرجع المال تلقائياً: إذا لزم استعمل «إرجاع رصيد».", mk)
        bot.answer_callback_query(call.id)
        return
    if act == "y":
        try:
            kv_del(f"rk:ord:{oid}")
            _srem(ORDSET_KEY, oid)
            _srem(WAITSET_KEY, oid)
            try:
                db.lrem(f"rk:uord:{o.get('user_id')}", 0, oid)
            except Exception as e:
                print(f"uord lrem error: {e}")
        except Exception as e:
            bot.answer_callback_query(call.id, "❌ تعذّر الحذف (مشكلة تخزين)", show_alert=True)
            print(f"order delete error: {e}")
            return
        bot.answer_callback_query(call.id, "🗑️ تم حذف الطلب")
        show_pending_orders(chat_id, msg_id)
        return
    if act == "x":
        ok, msg = mark_executed(oid)
        bot.answer_callback_query(call.id, "✅" if ok else "❌")
        bot.send_message(chat_id, msg)
        show_pending_orders(chat_id, msg_id)
        return
    bot.answer_callback_query(call.id)

# ---------- تفعيل Netflix على التلفاز (الزبون يرسل كود 8 أرقام ← تأكيد ← الأدمن يدخله) ----------
NETFLIX_TV = {"netflix_profile"}
TV_TX = {
    "ar": {
        "btn": "📺 تفعيل على التلفاز",
        "team": "👨‍💻 فريق التفعيل",
        "team2": "👨‍💻 تواصل مع فريق التفعيل",
        "ok": "✅ تم",
        "ask": "📺 <b>تفعيل Netflix على التلفاز</b>\n\n1️⃣ افتح تطبيق Netflix في التلفاز، وسيظهر لك <b>كود من 8 أرقام</b>.\n2️⃣ أرسل الكود هنا الآن (أرقام فقط).\n\n⚠️ لا تغلق التلفاز ولا تخرج من تطبيق Netflix قبل التفعيل. إذا طالت المدة أو تغيّر الكود أو خرجت من التطبيق، تواصل مع فريق التفعيل.",
        "bad": "❌ الكود يجب أن يتكون من 8 أرقام فقط. أعد الإرسال.",
        "confirm_q": "🔎 تأكد من الكود:\n\n📺 الكود: <code>{code}</code>\n\nهل هو صحيح؟",
        "got": "✅ <b>تم استلام كود التلفاز!</b>\n\n🛍 المنتج: {product}\n💰 المبلغ: USDT {paid}\n📺 الكود: <code>{code}</code>\n\nسيقوم فريقنا بتفعيله على التلفاز خلال لحظات.\n\n⚠️ إذا تغيّر الكود في التلفاز قبل التفعيل، تواصل مع فريق التفعيل 👇",
        "done": "✅ <b>تم تجهيز حسابك بنجاح!</b>\n\n📺 تم تسجيل الدخول إلى حسابك على التلفاز. استمتع بالمشاهدة 🎉",
        "support": "📞 <b>فريق التفعيل يطلب منك التواصل معهم الآن</b>\n\nهم في انتظارك. اضغط الزر بالأسفل للتواصل معهم 👇",
        "ack": "👍 بالتوفيق! سنُعلمك هنا فور تفعيل التلفاز.",
    },
    "en": {
        "btn": "📺 Activate on TV",
        "team": "👨‍💻 Activation team",
        "team2": "👨‍💻 Contact the activation team",
        "ok": "✅ Got it",
        "ask": "📺 <b>Activate Netflix on your TV</b>\n\n1️⃣ Open the Netflix app on your TV, and an <b>8-digit code</b> will appear.\n2️⃣ Send the code here now (numbers only).\n\n⚠️ Do not turn off the TV or leave the Netflix app before the activation. If it takes long, the code changes, or you left the app, contact the activation team.",
        "bad": "❌ The code must be exactly 8 digits. Please send it again.",
        "confirm_q": "🔎 Please check the code:\n\n📺 Code: <code>{code}</code>\n\nIs it correct?",
        "got": "✅ <b>TV code received!</b>\n\n🛍 Product: {product}\n💰 Amount: USDT {paid}\n📺 Code: <code>{code}</code>\n\nOur team will activate it on your TV in a few moments.\n\n⚠️ If the code changes on the TV before the activation, contact the activation team 👇",
        "done": "✅ <b>Your account is ready!</b>\n\n📺 Your account is now signed in on your TV. Enjoy watching 🎉",
        "support": "📞 <b>The activation team asks you to contact them now</b>\n\nThey are waiting for you. Tap the button below to reach them 👇",
        "ack": "👍 All good! We will notify you here as soon as your TV is activated.",
    },
    "fr": {
        "btn": "📺 Activer sur la TV",
        "team": "👨‍💻 Équipe d'activation",
        "team2": "👨‍💻 Contacter l'équipe d'activation",
        "ok": "✅ Compris",
        "ask": "📺 <b>Activer Netflix sur votre TV</b>\n\n1️⃣ Ouvrez l'application Netflix sur votre TV, un <b>code à 8 chiffres</b> s'affichera.\n2️⃣ Envoyez le code ici maintenant (chiffres uniquement).\n\n⚠️ N'éteignez pas la TV et ne quittez pas l'application Netflix avant l'activation. Si cela tarde, si le code change ou si vous avez quitté l'application, contactez l'équipe d'activation.",
        "bad": "❌ Le code doit contenir exactement 8 chiffres. Renvoyez-le.",
        "confirm_q": "🔎 Vérifiez le code :\n\n📺 Code : <code>{code}</code>\n\nEst-il correct ?",
        "got": "✅ <b>Code TV reçu !</b>\n\n🛍 Produit : {product}\n💰 Montant : USDT {paid}\n📺 Code : <code>{code}</code>\n\nNotre équipe l'activera sur votre TV dans quelques instants.\n\n⚠️ Si le code change sur la TV avant l'activation, contactez l'équipe d'activation 👇",
        "done": "✅ <b>Votre compte est prêt !</b>\n\n📺 Votre compte est maintenant connecté sur votre TV. Bon visionnage 🎉",
        "support": "📞 <b>L'équipe d'activation vous demande de la contacter maintenant</b>\n\nElle vous attend. Appuyez sur le bouton ci-dessous pour la joindre 👇",
        "ack": "👍 Parfait ! Nous vous préviendrons ici dès que votre TV sera activée.",
    },
}
def _tv(lang, key):
    return TV_TX.get(lang, TV_TX["ar"])[key]

def _team_markup(lang, key="team"):
    mk = InlineKeyboardMarkup(row_width=1)
    mk.add(InlineKeyboardButton(text=_tv(lang, key), url=MY_PRIVATE_CHAT_LINK))
    return mk

def _support_tv(lang, o):
    if o and o.get("product_id") in NETFLIX_TV:
        return _team_markup(lang)
    return support_markup(lang)

def _tv_ask(uid, oid):
    kv_set(f"rk:tv:{uid}", oid, ex=1800)

@bot.callback_query_handler(func=lambda c: c.data.startswith("tv_"))
def handle_tv_btn(call):
    uid = call.from_user.id
    lang = get_lang(uid)
    oid = call.data[3:]
    o = order_get(oid)
    if not o or str(o.get("user_id")) != str(uid) or o.get("product_id") not in NETFLIX_TV:
        bot.answer_callback_query(call.id)
        return
    try:
        _tv_ask(uid, oid)
    except Exception:
        bot.answer_callback_query(call.id, t(lang, "temp_error"), show_alert=True)
        return
    bot.answer_callback_query(call.id)
    _safe_send(call.message.chat.id, _tv(lang, "ask"), parse_mode="HTML")

def _awaiting_tv(m):
    try:
        if not m.text or m.text.startswith("/") or m.chat.type != "private":
            return False
        if re.fullmatch(r"\d{10,}", re.sub(r"[\s-]", "", m.text)):   # رقم عملية Binance: لا نلتقطه
            return False
        return bool(kv_get(f"rk:tv:{m.from_user.id}"))
    except Exception:
        return False

@bot.message_handler(func=_awaiting_tv, content_types=["text"])
def handle_tv_code(message):
    uid = message.from_user.id
    lang = get_lang(uid)
    code = re.sub(r"[\s-]", "", message.text or "")
    if not re.fullmatch(r"\d{8}", code):
        bot.send_message(message.chat.id, _tv(lang, "bad"))
        return
    try:
        oid = str(kv_get(f"rk:tv:{uid}"))
        o = order_get(oid)
    except Exception:
        return
    if not o or str(o.get("user_id")) != str(uid):
        return
    o["tv_tmp"] = code
    try:
        order_save(o)
        kv_del(f"rk:tv:{uid}")
    except Exception:
        pass
    mk = InlineKeyboardMarkup()
    mk.row(
        InlineKeyboardButton(text=mt(lang, "btn_confirm"), callback_data=f"tvc_{oid}"),
        InlineKeyboardButton(text=mt(lang, "btn_edit"), callback_data=f"tve_{oid}"),
    )
    _safe_send(message.chat.id, _tv(lang, "confirm_q").format(code=code), parse_mode="HTML", reply_markup=mk)

@bot.callback_query_handler(func=lambda c: c.data.startswith(("tvc_", "tve_")))
def handle_tv_confirm(call):
    uid = call.from_user.id
    lang = get_lang(uid)
    act, oid = call.data[:3], call.data[4:]
    o = order_get(oid)
    if not o or str(o.get("user_id")) != str(uid) or o.get("product_id") not in NETFLIX_TV:
        bot.answer_callback_query(call.id)
        return
    if act == "tve":
        try:
            _tv_ask(uid, oid)
        except Exception:
            pass
        _edit_cb(call, _tv(lang, "ask"), _team_markup(lang))
        bot.answer_callback_query(call.id)
        return
    code = o.get("tv_tmp")
    if not code:
        bot.answer_callback_query(call.id)
        return
    o["tv_code"] = code
    o["tv_ts"] = int(time.time())
    o.pop("tv_tmp", None)
    try:
        order_save(o)
    except Exception:
        pass
    mk = InlineKeyboardMarkup(row_width=1)
    mk.add(InlineKeyboardButton(text=_tv(lang, "team"), url=MY_PRIVATE_CHAT_LINK))
    b_ok = InlineKeyboardButton(text=_tv(lang, "ok"), callback_data="tvok")
    b_ok.style = "success"
    mk.add(b_ok)
    _edit_cb(call, _tv(lang, "got").format(product=html.escape(o.get("product_name", "")),
                                          paid=html.escape(str(o.get("paid", ""))), code=code), mk)
    bot.answer_callback_query(call.id)
    amk = InlineKeyboardMarkup(row_width=1)
    amk.add(InlineKeyboardButton(text="✅ تم تفعيل", callback_data=f"tva_{oid}"))
    amk.add(InlineKeyboardButton(text="📩 تواصل مع فريق التفعيل", callback_data=f"tvs_{oid}"))
    _atxt = (f"📺 <b>كود تلفاز Netflix</b>\n\n📦 {html.escape(o.get('product_name', ''))}\n"
             f"🙋 {_user_link(uid)}\n🧾 طلب <code>{oid}</code>\n🔢 الكود: <code>{code}</code>")
    amk_chat = InlineKeyboardMarkup(row_width=1)
    amk_chat.add(InlineKeyboardButton(text="💬 مراسلة الزبون", url=f"tg://user?id={uid}"))
    for _row in amk.keyboard:
        amk_chat.keyboard.append(_row)
    try:
        bot.send_message(ADMIN_CHAT_ID, _atxt, parse_mode="HTML", reply_markup=amk_chat)
    except Exception as e:
        print(f"tv admin notify with chat btn failed: {e}")
        try:
            bot.send_message(ADMIN_CHAT_ID, _atxt, parse_mode="HTML", reply_markup=amk)
        except Exception as e2:
            print(f"tv admin notify failed: {e2}")

@bot.callback_query_handler(func=lambda c: c.data == "tvok")
def handle_tv_ok(call):
    lang = get_lang(call.from_user.id)
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=_team_markup(lang))
    except Exception:
        pass
    bot.answer_callback_query(call.id, _tv(lang, "ack"), show_alert=True)

@bot.callback_query_handler(func=lambda c: c.data.startswith(("tva_", "tvs_")))
def handle_tv_admin(call):
    if not _is_admin_user(call.from_user.id):
        bot.answer_callback_query(call.id)
        return
    act, oid = call.data[:3], call.data[4:]
    o = order_get(oid)
    if not o:
        bot.answer_callback_query(call.id, "❌ الطلب غير موجود", show_alert=True)
        return
    uid = o["user_id"]
    lang = get_lang(uid)
    base = call.message.html_text or ""
    if act == "tva":
        try:
            if o.get("status") in ("pending", "delivered_wait"):
                o["status"] = "done"
                o["confirmed_by"] = "admin"
                o["done_ts"] = int(time.time())
                order_save(o)
                _srem(ORDSET_KEY, oid)
                _srem(WAITSET_KEY, oid)
        except Exception as e:
            print(f"tv done mark failed: {e}")
        ok = _safe_send(uid, _tv(lang, "done"), parse_mode="HTML", reply_markup=_team_markup(lang, "team2"))
        try:
            bot.edit_message_text(base + "\n\n✅ <b>تم التفعيل وأُبلغ الزبون</b>", call.message.chat.id, call.message.message_id, parse_mode="HTML")
        except Exception:
            pass
        bot.answer_callback_query(call.id, "✅ أُبلغ الزبون" if ok else "⚠️ تعذر إبلاغ الزبون", show_alert=not ok)
        return
    ok = _safe_send(uid, _tv(lang, "support"), parse_mode="HTML", reply_markup=_team_markup(lang, "team2"))
    if "أُرسل للزبون" not in base:
        try:
            bot.edit_message_text(base + "\n\n📩 <i>أُرسل للزبون: تواصل مع فريق التفعيل</i>", call.message.chat.id, call.message.message_id,
                                  parse_mode="HTML", reply_markup=call.message.reply_markup)
        except Exception:
            pass
    bot.answer_callback_query(call.id, "📩 أُرسل للزبون" if ok else "⚠️ تعذر الإرسال", show_alert=not ok)

# ---------- Netflix بروفيل: اختيار الجهاز بعد الدفع ----------
NFD_TX = {
    "ar": {
        "choose": "✅ <b>تم استلام دفعك!</b>\n\n📦 {product}\n\n📍 <b>وين تحب تفعّل Netflix؟</b>\nاختر الجهاز من الأزرار بالأسفل 👇",
        "phone": "📱 تفعيل على الهاتف", "pc": "💻 تفعيل على الحاسوب", "tv": "📺 تفعيل على التلفاز",
        "dev_phone": "📱 الهاتف", "dev_pc": "💻 الحاسوب", "dev_tv": "📺 التلفاز",
        "got": "✅ <b>تم استلام طلبك!</b>\n\n📦 {product}\n🎯 الجهاز: {device}\n\nسيقوم فريقنا بتسليمك رابط التفعيل قريباً.\n\n⚠️ إذا واجهت أي مشكلة تواصل مع فريق التفعيل 👇",
        "recv": "✅ تم استلام الطلب",
        "copyhint": "💡 اضغط على الرابط لنسخه، ثم الصقه في المتصفح.",
        "ack": "👍 بالتوفيق! سنُرسل لك رابط التفعيل هنا قريباً.",
    },
    "en": {
        "choose": "✅ <b>Payment received!</b>\n\n📦 {product}\n\n📍 <b>Where do you want to activate Netflix?</b>\nChoose your device from the buttons below 👇",
        "phone": "📱 Activate on phone", "pc": "💻 Activate on computer", "tv": "📺 Activate on TV",
        "dev_phone": "📱 Phone", "dev_pc": "💻 Computer", "dev_tv": "📺 TV",
        "got": "✅ <b>Your order was received!</b>\n\n📦 {product}\n🎯 Device: {device}\n\nOur team will send you the activation link shortly.\n\n⚠️ If you have any problem, contact the activation team 👇",
        "recv": "✅ Order received",
        "copyhint": "💡 Tap the link to copy it, then paste it in your browser.",
        "ack": "👍 All good! We will send you the activation link here shortly.",
    },
    "fr": {
        "choose": "✅ <b>Paiement reçu !</b>\n\n📦 {product}\n\n📍 <b>Où voulez-vous activer Netflix ?</b>\nChoisissez votre appareil avec les boutons ci-dessous 👇",
        "phone": "📱 Activer sur téléphone", "pc": "💻 Activer sur ordinateur", "tv": "📺 Activer sur TV",
        "dev_phone": "📱 Téléphone", "dev_pc": "💻 Ordinateur", "dev_tv": "📺 TV",
        "got": "✅ <b>Votre commande a été reçue !</b>\n\n📦 {product}\n🎯 Appareil : {device}\n\nNotre équipe vous enverra le lien d'activation très bientôt.\n\n⚠️ En cas de problème, contactez l'équipe d'activation 👇",
        "recv": "✅ Commande reçue",
        "copyhint": "💡 Appuyez sur le lien pour le copier, puis collez-le dans votre navigateur.",
        "ack": "👍 Parfait ! Nous vous enverrons le lien d'activation ici très bientôt.",
    },
}
def _nfd(lang, key):
    return NFD_TX.get(lang, NFD_TX["ar"])[key]

def _nf_html(text, lang):
    """نصّك كما كتبتَه، وكل رابط يصير قابلاً للنسخ بنقرة (داخل <code>) + سطر تلميح."""
    esc = html.escape(text, quote=False)
    found = []
    def _wrap(m):
        u = m.group(0)
        tail = ""
        while u and u[-1] in ".,;:!?)":
            tail = u[-1] + tail
            u = u[:-1]
        found.append(u)
        return "<code>" + u + "</code>" + tail
    out = re.sub(r"https?://[^\s<>]+", _wrap, esc)
    if found:
        out += "\n\n" + _nfd(lang, "copyhint")
    return out

def _nf_device_markup(lang, oid):
    mk = InlineKeyboardMarkup(row_width=1)
    for key, code in (("phone", "p"), ("pc", "c"), ("tv", "t")):
        b = InlineKeyboardButton(text=_nfd(lang, key), callback_data=f"nfd_{oid}_{code}")
        b.style = "success"
        mk.add(b)
    return mk

@bot.callback_query_handler(func=lambda c: c.data.startswith("nfd_"))
def handle_nf_device(call):
    uid = call.from_user.id
    lang = get_lang(uid)
    try:
        oid, d = call.data[4:].rsplit("_", 1)
    except ValueError:
        bot.answer_callback_query(call.id)
        return
    o = order_get(oid)
    dev = {"p": "phone", "c": "pc", "t": "tv"}.get(d)
    if (not o or str(o.get("user_id")) != str(uid) or o.get("product_id") not in NETFLIX_TV
            or o.get("status") != "pending" or o.get("device") or not dev):
        bot.answer_callback_query(call.id)
        return
    o["device"] = dev
    order_save(o)
    spname = html.escape(o.get("product_name", ""))
    if dev == "tv":
        try:
            _tv_ask(uid, oid)
        except Exception:
            pass
        _edit_cb(call, _tv(lang, "ask"), _team_markup(lang))
        bot.answer_callback_query(call.id)
        monitor_send(f"🎯 <b>اختار التلفاز</b> — بانتظار كوده\n\n📦 {spname}\n👤 {_user_link(uid)}")
        return
    mk = InlineKeyboardMarkup(row_width=1)
    b_ok = InlineKeyboardButton(text=_nfd(lang, "recv"), callback_data="nfok")
    b_ok.style = "success"
    mk.add(b_ok)
    mk.add(InlineKeyboardButton(text=_tv(lang, "team"), url=MY_PRIVATE_CHAT_LINK))
    _edit_cb(call, _nfd(lang, "got").format(product=spname, device=_nfd(lang, "dev_" + dev)), mk)
    bot.answer_callback_query(call.id)
    txt = (f"📦 <b>طلب جديد (Pending)</b>\n\n📦 {spname}\n👤 {_user_link(uid)}\n"
           f"🎯 الجهاز: {_nfd('ar', 'dev_' + dev)}\n💵 {html.escape(str(o.get('paid')))} USDT\n📌 /admin ← 📦 الطلبات المعلقة")
    alert_admin(txt)
    monitor_send(txt)

@bot.callback_query_handler(func=lambda c: c.data == "nfok")
def handle_nf_ok(call):
    lang = get_lang(call.from_user.id)
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=_team_markup(lang))
    except Exception:
        pass
    bot.answer_callback_query(call.id, _nfd(lang, "ack"), show_alert=True)

# ---------- استلام الزبون + التأكيد التلقائي بعد 20 دقيقة ----------
@bot.callback_query_handler(func=lambda c: c.data.startswith("rcv_"))
def handle_received(call):
    oid = call.data[4:]
    o = order_get(oid)
    uid = call.from_user.id
    if not o or str(o.get("user_id")) != str(uid):
        bot.answer_callback_query(call.id)
        return
    lang = get_lang(uid)
    if o.get("status") == "delivered_wait":
        o["status"] = "done"
        o["confirmed_by"] = "user"
        o["done_ts"] = int(time.time())
        order_save(o)
        _srem(WAITSET_KEY, oid)
        monitor_send(f"✅ <b>الزبون أكد الاستلام</b>\n\n📦 {html.escape(o['product_name'])}\n👤 {_user_link(uid)}")
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=_support_tv(lang, o))
    except Exception:
        pass
    bot.answer_callback_query(call.id, mt(lang, "received_ok"), show_alert=True)

def autoconfirm_orders():
    for oid in _smembers(WAITSET_KEY):
        o = order_get(oid)
        if not o or o.get("status") != "delivered_wait":
            _srem(WAITSET_KEY, oid)
            continue
        if time.time() - float(o.get("delivered_at", 0)) < AUTOCONFIRM_SECONDS:
            continue
        o["status"] = "done"
        o["confirmed_by"] = "auto"
        o["done_ts"] = int(time.time())
        order_save(o)
        _srem(WAITSET_KEY, oid)
        try:
            bot.edit_message_reply_markup(o["chat_id"], o["message_id"], reply_markup=_support_tv(get_lang(o["user_id"]), o))
        except Exception:
            pass
        monitor_send(f"⏱️ <b>تأكيد تلقائي للطلب (20 دقيقة)</b>\n\n📦 {html.escape(o['product_name'])}\n👤 {_user_link(o['user_id'])}")

def order_autoconfirm_loop():
    time.sleep(30)
    while True:
        try:
            autoconfirm_orders()
        except Exception as e:
            print(f"order_autoconfirm_loop error: {e}")
        time.sleep(30)

# ---------- سجل طلباتي (دائم) في الملف الشخصي ----------
def user_order_text(lang, o):
    txt = mt(lang, "order_detail").format(
        product=html.escape(o.get("product_name", "")), price=html.escape(str(o.get("price", ""))),
        date=_fmt_date(o.get("ts")), status=mt(lang, "st_" + str(o.get("status", "done"))),
    )
    if o.get("input"):
        txt += mt(lang, "order_input").format(
            label=mt(lang, "lbl_" + MANUAL_A.get(o.get("product_id"), "username")), val=html.escape(o["input"]))
    if o.get("delivery"):
        txt += mt(lang, "order_delivery").format(val=html.escape(o["delivery"]))
    return txt

def _pf_orders_view(call, uid, lang, data):
    if data != "pf_orders" and not data.startswith("pf_ordv_"):
        return False
    try:
        m = InlineKeyboardMarkup(row_width=1)
        if data == "pf_orders":
            n = 0
            for oid in uord_list(uid, 12):
                o = order_get(oid)
                if not o:
                    continue
                n += 1
                m.add(InlineKeyboardButton(
                    text=f"{ORD_ICONS.get(o.get('status'), '•')} {o.get('product_name', '')[:30]} | {_fmt_date(o.get('ts'))[:11]}",
                    callback_data=f"pf_ordv_{oid}",
                ))
            m.add(InlineKeyboardButton(text=t(lang, "back"), callback_data="pf_hist"))
            text = mt(lang, "orders_title") if n else mt(lang, "orders_empty")
        else:
            o = order_get(data[8:])
            if not o or str(o.get("user_id")) != str(uid):
                bot.answer_callback_query(call.id)
                return True
            m.add(InlineKeyboardButton(text=t(lang, "back"), callback_data="pf_orders"))
            text = user_order_text(lang, o)
    except Exception as e:
        print(f"orders view error: {e}")
        bot.answer_callback_query(call.id, wt(lang, "unavailable"), show_alert=True)
        return True
    _pf_show(call, text, m)
    bot.answer_callback_query(call.id)
    return True


# ============================================================
# ========== بطاقات الهداية: اختيار الكمية (حتى GIFT_MAX_QTY) ==========
# ============================================================
MANUAL_TEXTS["ar"]["choose_qty"] = "🔢 اختر الكمية:\n📦 {product}"
MANUAL_TEXTS["en"]["choose_qty"] = "🔢 Choose the quantity:\n📦 {product}"
MANUAL_TEXTS["fr"]["choose_qty"] = "🔢 Choisissez la quantité :\n📦 {product}"

def _gift_qty(label):
    m = re.search(r"\sx(\d+)$", str(label))
    return int(m.group(1)) if m else 1

def _gift_stock(pid, label):
    # مخزون القيمة عند FAZER من الكاش (None = غير معروف)
    try:
        mapping = fazer_resolve(pid, re.sub(r"\s+x\d+$", "", str(label)), allow_fetch=False)
        if mapping and mapping.get("stock") is not None:
            return int(mapping["stock"])
    except Exception:
        pass
    return None

def _gift_ask_qty(call, product, pid, idx, label, price, lang):
    stock = _gift_stock(pid, label)
    maxq = GIFT_MAX_QTY if stock is None else min(GIFT_MAX_QTY, stock)
    if maxq <= 1:
        return False  # كمية واحدة فقط: المسار القديم مباشرة
    mk = InlineKeyboardMarkup(row_width=1)
    for q in range(1, maxq + 1):
        total = (Decimal(price) * q).quantize(Decimal("0.01"))
        mk.add(InlineKeyboardButton(text=f"{q} × {label} | ${total}", callback_data=f"gqt_{pid}_{idx}_{q}"))
    mk.add(InlineKeyboardButton(text=t(lang, "back"), callback_data=f"buy_{pid}"))
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    bot.send_message(
        call.message.chat.id,
        mt(lang, "choose_qty").format(product=html.escape(f"{tr(product, 'name', lang)} — {label}")),
        parse_mode="HTML", reply_markup=mk,
    )
    bot.answer_callback_query(call.id)
    return True

@bot.callback_query_handler(func=lambda c: c.data.startswith("gqt_"))
def handle_gift_qty(call):
    uid = call.from_user.id
    lang = get_lang(uid)
    try:
        head, q = call.data[4:].rsplit(chr(95), 1)
        pid, idx = head.rsplit(chr(95), 1)
        product = find_product(pid)
        label, price = GIFT_VARIANTS[pid][int(idx)]
        q = int(q)
        if not product or not 1 <= q <= GIFT_MAX_QTY:
            raise ValueError("bad qty")
    except Exception:
        bot.answer_callback_query(call.id)
        return
    stock = _gift_stock(pid, label)
    if stock is not None and stock < q:
        bot.answer_callback_query(call.id, t(lang, "out_variant"), show_alert=True)
        return
    total = str((Decimal(price) * q).quantize(Decimal("0.01")))
    lab = f"{label} x{q}"
    full_name = f"{product['name']} — {lab}"
    if call.message.chat.type == "private":
        register_user(uid)
    notify_admin(call.from_user, {"name": full_name, "price": f"${total}"}, lang)
    try:
        invoice_id = create_invoice(uid, pid, lab, total, full_name)
    except StorageError:
        bot.answer_callback_query(call.id, t(lang, "temp_error"), show_alert=True)
        return
    invoice = get_invoice(invoice_id) or {"label": lab, "price_usdt": total}
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    sent = bot.send_message(
        call.message.chat.id, build_invoice_text(lang, invoice, product), parse_mode="HTML",
        reply_markup=build_invoice_markup(lang, invoice_id, _wallet_covers(uid, invoice.get("price_usdt"))),
    )
    attach_invoice_msg(invoice_id, sent)
    bot.answer_callback_query(call.id)


# ============================================================
# ========== ترتيب القائمة الرئيسية: أزواج + مجموعة Claude ==========
# ============================================================
# كل عنصر: معرّف منتج (زر طويل) | tuple من منتجين (جنب بعض) | "grp:..." مجموعة | "sep:..." فاصل
STORE_SLOTS = [
    "vente:gem6",
    "gemini_18m", "capcut_1m",
    ("duolingo_12m", "duolingo_link_12m"),
    "row:prime_netflix",
    ("prime_video_ultra_6m", "amazon_prime_6m"),
    "grp:claude_api",
    ("chatgpt_plus_1m", "chatgpt_k12_edu"),
    ("office365_1y", "elevenlabs_3m"),
    "iptv_14m",
    "nordvpn_3m", "n8n_starter_12m",
    "grp:snapchat",
    "vente:all",
    ("canva_edu_500", "canva_edu_5000"),
    "freefire_diamonds",
    "next:gifts",
]

# صفحة بطاقات الهدايا (الصفحة الثانية): فواصل طويلة + بطاقات
GIFT_SLOTS = [
    "sep:sep_apple", "apple_gift_tr", "apple_gift_in", "apple_gift_fr", "apple_gift_us",
    "sep:sep_google", "gplay_us", "gplay_fr", "gplay_br", "gplay_in", "gplay_tr",
    "sep:sep_psn", "psn_us", "psn_fr", "psn_tr", "psn_br",
    "sep:sep_steam", "steam_us", "steam_id",
    "sep:sep_games", "freefire_codes", "pubg_gcoin", "pubg_uc", "fc26_points",
]
GIFT_NEXT_TEXT = {"ar": "🎁 بطاقات الهدايا — التالي ◀️", "en": "Next ▶️ 🎁 Gift Cards", "fr": "Suivant ▶️ 🎁 Cartes cadeaux"}
GIFT_BACK_TEXT = {"ar": "🔙 العودة", "en": "🔙 Back", "fr": "🔙 Retour"}

# شريط التنقل بين الصفحتين: [اشتراكات متنوعة] (يسار) | [بطاقات الهدايا] (يمين). الصفحة الحالية رمادية لا تفتح.
NAV_HEAD = {
    "subs": {"ar": "⬇️ اشتراكات متنوعة ⬇️", "en": "⬇️ Various Subscriptions ⬇️", "fr": "⬇️ Abonnements divers ⬇️"},
    "gifts": {"ar": "⬇️ بطاقات الهدايا ⬇️", "en": "⬇️ Gift Cards ⬇️", "fr": "⬇️ Cartes cadeaux ⬇️"},
}
NAV_BTN = {
    "subs": {"ar": "اشتراكات متنوعة", "en": "Subscriptions", "fr": "Abonnements"},
    "gifts": {"ar": "بطاقات الهدايا", "en": "Gift Cards", "fr": "Cartes cadeaux"},
}

def _nav_rows(mk, lang, current):
    """current = الصفحة التي نحن فيها الآن ('subs' أو 'gifts')."""
    other = "gifts" if current == "subs" else "subs"
    mk.add(InlineKeyboardButton(text=NAV_HEAD[other].get(lang, NAV_HEAD[other]["ar"]), callback_data="noop"))
    subs_t = NAV_BTN["subs"].get(lang, NAV_BTN["subs"]["ar"])
    gifts_t = NAV_BTN["gifts"].get(lang, NAV_BTN["gifts"]["ar"])
    # الأسهم تشير نحو حافة الهاتف: يسار ◀️ ويمين ▶️. العربية تُكتب من اليمين فترتيب النص المنطقي معكوس.
    if lang == "ar":
        subs_go = f"🛍️ {subs_t} ◀️"
        gifts_go = f"▶️ {gifts_t} 🎁"
    else:
        subs_go = f"◀️ 🛍️ {subs_t}"
        gifts_go = f"🎁 {gifts_t} ▶️"
    if current == "subs":
        left = InlineKeyboardButton(text=f"📍 {subs_t}", callback_data="noop")
        right = InlineKeyboardButton(text=gifts_go, callback_data="gcp")
    else:
        left = InlineKeyboardButton(text=subs_go, callback_data="back_to_main")
        right = InlineKeyboardButton(text=f"📍 {gifts_t}", callback_data="noop")
    try:
        if not _icons_off():
            if current == "subs":      # بطاقات الهدايا: سهم مخصص عند الحافة اليمنى + 🎁 عند اليسرى
                right._icon_orig_text = right.text
                right.text = f"{gifts_t} 🎁"
                right.icon_custom_emoji_id = ICON_ARROW_R
            else:                      # اشتراكات متنوعة: شعار مخصص عند اليمنى + ◀️ عند الحافة اليسرى
                left._icon_orig_text = left.text
                left.text = f"{subs_t} ◀️"
                left.icon_custom_emoji_id = ICON_SUBS
    except Exception as e:
        print(f"nav icons failed: {e}")
    try:
        if not _vt_conf().get("nostyle"):
            (right if current == "subs" else left).style = "success"   # الزر الذي يمكن الضغط عليه أخضر
    except Exception:
        pass
    mk.row(left, right)
GIFT_PAGE_TEXT = {
    "ar": "🎁 <b>بطاقات الهدايا</b>\n\n👇 اختر البطاقة التي تريدها:",
    "en": "🎁 <b>Gift Cards</b>\n\n👇 Choose the card you want:",
    "fr": "🎁 <b>Cartes cadeaux</b>\n\n👇 Choisissez la carte souhaitée :",
}

# مجموعات: زر واحد طويل يفتح صفحة فيها أزرار المنتجات
STORE_GROUPS = {
    "claude_api": {"name": "Claude API", "icon": "🧠", "members": ["claude_100_30d", "claude_10m_1d"]},
    "snapchat": {"name": "Snapchat Plus+", "icon": "👻", "members": ["snapchat_3m", "snapchat_6m", "snapchat_12m"]},
    "netflix": {"name": "Netflix", "icon": "🎞️", "members": ["netflix_full", "netflix_profile"]},
}

# أسماء قصيرة للأزرار الجنبية (تيليغرام يقص الأسماء الطويلة)
SHORT_NAMES = {
    "duolingo_12m": {"ar": "Duolingo سلوت", "en": "Duolingo Slot", "fr": "Duolingo Slot"},
    "duolingo_link_12m": {"ar": "Duolingo رابط", "en": "Duolingo Link", "fr": "Duolingo Lien"},
    "netflix_full": {"ar": "Netflix كامل", "en": "Netflix Full", "fr": "Netflix Complet"},
    "netflix_profile": {"ar": "Netflix بروفيل", "en": "Netflix Profile", "fr": "Netflix Profil"},
    "prime_video_ultra_6m": {"ar": "Prime Video 6M", "en": "Prime Video 6M", "fr": "Prime Video 6M"},
    "amazon_prime_6m": {"ar": "Amazon Prime 6M", "en": "Amazon Prime 6M", "fr": "Amazon Prime 6M"},
    "chatgpt_plus_1m": {"ar": "ChatGPT Plus 1M", "en": "ChatGPT Plus 1M", "fr": "ChatGPT Plus 1M"},
    "chatgpt_k12_edu": {"ar": "ChatGPT K12 Edu", "en": "ChatGPT K12 Edu", "fr": "ChatGPT K12 Edu"},
    "office365_1y": {"ar": "Office 365 1Y", "en": "Office 365 1Y", "fr": "Office 365 1A"},
    "elevenlabs_3m": {"ar": "ElevenLabs 3M", "en": "ElevenLabs 3M", "fr": "ElevenLabs 3M"},
}

GROUP_TEXTS = {
    "ar": "📁 <b>{name}</b>\n\n💰 السعر: {lo} — {hi}\n👇 اختر النسخة:",
    "en": "📁 <b>{name}</b>\n\n💰 Price: {lo} — {hi}\n👇 Choose your variant:",
    "fr": "📁 <b>{name}</b>\n\n💰 Prix : {lo} — {hi}\n👇 Choisissez votre variante :",
}

def _slot_button(item, lang):
    stock_display = item["stock"] if item["stock"] == "♾️" else f"📦 {item['stock']}"
    return InlineKeyboardButton(
        text=f"{item['icon']} {tr(item, 'name', lang)}‎ | {item['price']} | {stock_display}",   # علامة اتجاه تمنع تبعثر الكلمة العربية
        callback_data=f"buy_{item['id']}",
    )

def _pair_button(item, lang):
    names = SHORT_NAMES.get(item["id"], {})
    label = names.get(lang) or names.get("en") or tr(item, "name", lang)
    return InlineKeyboardButton(text=f"{item['icon']} {label}", callback_data=f"buy_{item['id']}")

def _group_range(gid):
    prices, stock, inf = [], 0, False
    for pid in STORE_GROUPS[gid]["members"]:
        p = find_product(pid)
        if not p:
            continue
        try:
            prices.append(Decimal(p["price"].lstrip("$")))
        except Exception:
            pass
        if p["stock"] == "♾️":
            inf = True
        elif isinstance(p["stock"], int):
            stock += p["stock"]
    if not prices:
        return "-", "-", ("♾️" if inf else stock)
    return f"${min(prices):.2f}", f"${max(prices):.2f}", ("♾️" if inf else stock)

# ---------- ألوان الأزرار (أخضر متوفر / أحمر نافد) + النافد يصعد للأعلى 3 في الصف ----------
_ikb_to_dict_orig = InlineKeyboardButton.to_dict
def _ikb_to_dict_styled(self):
    d = _ikb_to_dict_orig(self)
    st = getattr(self, "style", None)
    if st:
        d["style"] = st
    ic = getattr(self, "icon_custom_emoji_id", None)
    if ic:
        d["icon_custom_emoji_id"] = str(ic)
    else:
        try:
            hint = getattr(self, "icon_dyn", None)
            if hint and d.get("text") and not _icons_off():
                d["icon_custom_emoji_id"] = str(hint)
                d["text"] = _strip_emoji_edge(d["text"])
                r = None
            else:
                r = _dyn_icon(d.get("callback_data"), d.get("text"))
            if r:
                d["icon_custom_emoji_id"], d["text"] = r
        except Exception:
            pass
    return d
InlineKeyboardButton.to_dict = _ikb_to_dict_styled

# أيقونات تُطبَّق وقت الإرسال على أزرار محددة (ابدأ / اشتري الآن / اللغة / الدعم)
ICON_START = "5463392464314315076"
ICON_BUY = "5440841102871517055"
ICON_LANG = "5452069934089641166"
ICON_SUPPORT = "5244536513051516987"
_ICON_STATE = {"off": False}

def _icons_off():
    try:
        return bool(_ICON_STATE["off"] or _vt_conf().get("noicons"))
    except Exception:
        return bool(_ICON_STATE["off"])

def _strip_emoji_edge(text):
    """يحذف الإيموجي العادي من أول النص أو آخره (الرمز الذي بلا حروف/أرقام)."""
    parts = str(text).split(" ")
    if len(parts) > 1 and not re.search(r"\w", parts[0]):
        return " ".join(parts[1:])
    if len(parts) > 1 and not re.search(r"\w", parts[-1]):
        return " ".join(parts[:-1])
    return str(text)

def _kb_icon_for_text(text):
    for l in SUPPORTED_LANGS:
        tx = TEXTS.get(l, {})
        if text == tx.get("kb_start"):
            return ICON_START
        if text == tx.get("kb_support"):
            return ICON_SUPPORT
        if text == tx.get("kb_lang"):
            return ICON_LANG
        if text == tx.get("kb_update"):
            return ICON_REFRESH
    return None

ICON_REFRESH = "5451636889717062286"
ICON_REFERRAL = "5258203794772085854"
ICON_GAME = "5409125874651903587"
ICON_WALLET = "5443127283898405358"
ICON_BINANCE = "5454205576512818013"
ICON_CARD = "5472250091332993630"      # بريدي موب + RedotPay
ICON_FLIXY = "5440410042773824003"
ICON_BYBIT = "5249028722425612882"
ICON_CHAT = "5215334566549540768"
ICON_ARROW_R = "5406745015365943482"   # زر «بطاقات الهدايا»
ICON_SUBS = "5397782960512444700"       # زر «اشتراكات متنوعة»
ICON_TOPUP = "5456343516743483864"      # شحن المحفظة
ICON_CONTACT = "5220115526574950412"    # تواصل مع الدعم
ICON_HIST_W = "5231200819986047254"     # سجل المشتريات (صفحة المحفظة)
ICON_HIST_M = "5305265301917549162"     # سجل المشتريات (القائمة الرئيسية)
ICON_BACK = "5388781950305580591"       # رجوع / السابق
ICON_NEXT = "5294412516561018290"       # التالي
ICON_MONTH = "5296370519136812159"      # الشهر الماضي / هذا الشهر
ICON_DAILY = "5314665894406805639"      # الهدية اليومية
ICON_LB = "6145275873252612254"         # الترتيب الشهري
ICON_COINS = "5276071069176842299"      # محفظة الكوينز
ICON_MATCH = "5776422093302273080"      # ساحة المباريات
ICON_TIMER = "6003478739155949455"      # تحدي التوقيت
ICON_GIFT_BACK = "5294258473263978209"  # رجوع (صفحة بطاقات الهدايا)
ICON_GPLAY = "5373130604147654226"      # شعار Google Play
ICON_APPLE_GIFT = "5334955749409834455" # شعار Apple
ICON_STEAM_GIFT = "5373144051690258848" # شعار Steam
ICON_BC_CHEST = "6134110852363586757"   # صندوق BC (PUBG)
ICON_FF_CHEST = "6014802042474731668"   # صندوق Free Fire
ICON_MYPRED = "5472026645659401564"     # توقعاتي (تقويم)
ICON_BELL = "5458603043203327669"       # أعلمني بالمباريات الجديدة
ICON_NOTIF_OFF = "5240241223632954241"  # إيقاف الإشعارات
ICON_STOP_TIMER = "5359543311897998264" # إيقاف العداد
VS_EMOJI_ID = "5467412991790043938"     # VS بين الفريقين
LB_MEDAL_IDS = ("5440539497383087970", "5447203607294265305", "5453902265922376865")  # ميداليات الترتيب 1/2/3
ICON_LANG_GLOBE ="5224450179368767019"  # 🌍 عنوان اختيار اللغة
ICON_LANG_AR = "5269400778807720624"     # علم الجزائر
ICON_LANG_FR = "5202132623060640759"     # علم فرنسا
ICON_LANG_EN = "5458416160586342331"     # علم بريطانيا
ICON_MENU_GAME = "4972415571384599106"  # لعبة (القائمة الرئيسية)
ICON_MENU_API = "5271604874419647061"   # API
ICON_MENU_CHANNEL = "5424818078833715060"  # القناة الرئيسية
ICON_BARIDI = "6021623532872537088"     # بريدي موب
GIFT_BANNER_IDS = [
    "5422797979620755642", "5431452012304685092", "5393333662156604061", "5433670878309139413",
    "5206382428775532759", "5384215120169682553", "5386505875336744038", "5433739992922868816",
    "5386426160743729289",
]  # G I F T : C A R D

_DYN_CB_EXACT = {"mn_start": ICON_START, "mn_refresh": ICON_REFRESH, "pf_wallet": ICON_WALLET,
                 "pf_top": ICON_TOPUP, "pf_hist": ICON_HIST_W, "change_lang": ICON_LANG}
# قواعد نصية تُفحص أولاً (الرجوع/التالي/الألعاب...): (regex, icon, حذف الأسهم من النص)
_DYN_TEXT_FIRST = (
    (r"^\W*(رجوع|العودة|back|retour)(?!\w)", ICON_BACK, True),
    (r"^\W*(السابق|previous|précédent|precedent)(?!\w)", ICON_BACK, True),
    (r"^\W*(التالي|next|suivant)(?!\w)", ICON_NEXT, True),
    (r"الشهر الماضي|last month|mois dernier|هذا الشهر|this month|ce mois", ICON_MONTH, False),
    (r"الهدية اليومية|daily gift|cadeau quotidien", ICON_DAILY, False),
    (r"الترتيب الشهري|monthly leaderboard|classement mensuel", ICON_LB, False),
    (r"محفظة الكوينز|coins wallet|portefeuille de coins", ICON_COINS, False),
    (r"ساحة المباريات|match arena|arène des matchs|arene des matchs", ICON_MATCH, False),
    (r"تحدي التوقيت|timing challenge|défi chrono|defi chrono", ICON_TIMER, False),
    (r"إيقاف الإشعارات|turn off notifications|désactiver les notifications|desactiver les notifications", ICON_NOTIF_OFF, False),
    (r"أعلمني بالمباريات|notify me of new matches|avertir des nouveaux matchs", ICON_BELL, False),
    (r"توقعاتي|my predictions|mes pronostics", ICON_MYPRED, False),
    (r"إيقاف العداد|stop counter|arrêter le compteur|arreter le compteur", ICON_STOP_TIMER, False),
    (r"تواصل مع الدعم|contact support|contacter l'assistance", ICON_CONTACT, False),
    (r"^\W*buy now(?!\w)", ICON_BUY, False),
    (r"نسخ الرابط|copy link|copier le lien", "5386379624773066504", False),
    (r"إلى المحفظة|to wallet|au portefeuille", "5386380500946414098", False),
    (r"baridimob|بريدي\s*موب|بديدي\s*موب", ICON_BARIDI, False),
)

def _clean_arrows(s):
    for a in ("➡️", "⬅️", "▶️", "◀️", "➡", "⬅"):
        s = s.replace(a, " ")
    return re.sub(r"\s+", " ", s).strip()
_DYN_CB_PREFIX = (
    ("lang_en", ICON_LANG_EN), ("lang_ar", ICON_LANG_AR), ("lang_fr", ICON_LANG_FR),
    ("mbuy_", ICON_BUY), ("qb_", ICON_BUY), ("var_gplay_", ICON_GPLAY), ("var_apple_gift_", ICON_APPLE_GIFT), ("var_steam_", ICON_STEAM_GIFT), ("var_pubg_", ICON_BC_CHEST), ("var_freefire_", ICON_FF_CHEST), ("gno_gplay_", ICON_GPLAY), ("gno_apple_gift_", ICON_APPLE_GIFT), ("gno_steam_", ICON_STEAM_GIFT), ("gno_pubg_", ICON_BC_CHEST), ("gno_freefire_", ICON_FF_CHEST),
    ("pm_bn_", ICON_BINANCE), ("pm_bd_", ICON_CARD), ("pm_fx_", ICON_FLIXY),
    ("pm_rp_", ICON_CARD), ("pm_rd_", ICON_CARD), ("pm_soon_bb", ICON_BYBIT),
    ("wpay_", ICON_WALLET), ("rf_o", ICON_REFERRAL), ("gm_hub", ICON_GAME),
)
_DYN_TEXT = (
    (r"binance", ICON_BINANCE), (r"baridimob|بريدي\s*موب|بديدي\s*موب", ICON_CARD), (r"flixy", ICON_FLIXY),
    (r"redotpay", ICON_CARD), (r"bybit", ICON_BYBIT),
    (r"الشراء عبر الدردشة|buy via chat|acheter via le chat", ICON_CHAT),
)

def _dyn_icon(cb, text):
    if not text or _icons_off():
        return None
    cb = cb or ""
    if not cb.startswith(("buy_", "vgrp_", "grp_", "oos_", "noop", "gcp")):
        low0 = str(text).lower()
        for rx, e, clean in _DYN_TEXT_FIRST:
            if re.search(rx, low0):
                t2 = _strip_emoji_edge(text)
                if clean:
                    t2 = _clean_arrows(t2)
                return e, (t2 or str(text))
    eid = _DYN_CB_EXACT.get(cb)
    if not eid:
        for pre, e in _DYN_CB_PREFIX:
            if cb.startswith(pre):
                eid = e
                break
    if not eid and not cb.startswith(("buy_", "vgrp_", "grp_", "oos_")):
        low = str(text).lower()
        for rx, e in _DYN_TEXT:
            if re.search(rx, low):
                eid = e
                break
    if eid:
        return eid, _strip_emoji_edge(text)
    return None

_kbb_to_dict_orig = KeyboardButton.to_dict
def _kbb_to_dict_icon(self):
    d = _kbb_to_dict_orig(self)
    try:
        if isinstance(d, str):
            d = {"text": d}
        tx = d.get("text")
        eid = None if _icons_off() else _kb_icon_for_text(tx)
        if eid:
            d["icon_custom_emoji_id"] = eid
            d["text"] = _strip_emoji_edge(tx)
    except Exception:
        pass
    return d
KeyboardButton.to_dict = _kbb_to_dict_icon

# النص بلا إيموجي (بعد حذفه من الزر) يجب أن تعرفه معالجات لوحة المفاتيح السفلية
for _setname, _key in (("KB_START_TEXTS", "kb_start"), ("KB_SUPPORT_TEXTS", "kb_support"), ("KB_LANG_TEXTS", "kb_lang"), ("KB_UPDATE_TEXTS", "kb_update")):
    try:
        _s = globals().get(_setname)
        if _s is not None:
            _s.update({_strip_emoji_edge(TEXTS[_l][_key]) for _l in SUPPORTED_LANGS})
    except Exception as _e:
        print(f"kb text update {_setname} failed: {_e}")

# ---------- أيقونات الإيموجي المخصص أمام الأزرار (تحتاج Premium عند صاحب البوت) ----------
# (regex على نص الزر بالترتيب → معرّف الإيموجي). الترتيب مهم: الأخص أولاً.
BTN_ICON_IDS = [
    (r"snapchat", "5330248916224983855"),
    (r"free\s*fire", "6012423622730192070"),
    (r"pubg", "6323599384919413622"),
    (r"iptv", "5026268800509543248"),
    (r"amazon", "4995019580536524226"),
    (r"canva", "5076038705441932295"),
    (r"eleven\s*reader", "5949555742582251295"),
    (r"eleven\s*labs", "6219689196722854904"),
    (r"apple\s*music", "5292133684223157453"),
    (r"apple\s*gift", "5334955749409834455"),
    (r"google\s*play", "5373130604147654226"),
    (r"netflix", "5318911503938634641"),
    (r"chatgpt", "5359726582447487916"),
    (r"steam", "5373144051690258848"),
    (r"cap\s*cut", "5364339557712020484"),
    (r"nord", "5346134750417403743"),
    (r"n8n", "6133957427541843855"),
    (r"lovable", "6104729848675050039"),
    (r"duolingo", "5069087043175318384"),
    (r"claude", "6174520215376763867"),
    (r"playstation|psn", "5373306783706137993"),
    (r"ea\s*sports|fc\s*26", "5377605079601785754"),
    (r"codex", "5078234245479007184"),
    (r"muse\s*ai", "5891219692881714411"),
    (r"supabase", "6311992261571780495"),
    (r"pangram|pangeam", "5771692909107617185"),
    (r"wispr", "6296312164902772523"),
    (r"jetbrains", "5300959605793235101"),
    (r"crunchyroll|ᴄʀᴜɴᴄʜʏʀᴏʟʟ", "4958621463574741708"),
    (r"manus", "6311886927498846401"),
    (r"factory", "6311806809178905426"),
    (r"grok", "5319288443153445517"),
    (r"prime", "4961180134506758889"),
    (r"gemini|google\s*ai", "5321197740800120767"),
    (r"surfshark", "5816931709442068156"),
    (r"mobbin", "6312141558929956627"),
    (r"linear", "6134000510358789940"),
    (r"proton", "6237995064597945583"),
    (r"magic\s*patterns", "5373246052868571826"),
    (r"microsoft|office", "5372937764411031477"),
    (r"\bmiro\b", "5794356184513257269"),
    (r"ilovepdf", "5251558986443932784"),
    (r"framer", "5363810946022131056"),
    (r"figma", "5461087475625634452"),
    (r"bolt\.new", "5942592544033479493"),
    (r"cursor", "5384215120169682553"),
    (r"notion", "5364199932620194408"),
    (r"waking\s*up", "5301013374488814347"),
    (r"resend", "5373229590258925215"),
    (r"mercury", "6068962877157416767"),
    (r"customer\.io", "6134358500177880127"),
    (r"granola", "6312074909627457882"),
    (r"warp", "5363892211098339885"),
    (r"replit", "6269122883025378588"),
    (r"speechify", "5888548644130399040"),
    (r"arize", "4990421706377004842"),
    (r"readwise", "6282841072993312605"),
    (r"(^|\s)fin(\s|$|\||‎)", "5373145666597961572"),
    (r"descript", "5818857774641062590"),
    (r"gmail\s*2fa", "5008025248314950702"),     # Gmail 2FA
]

def _psn_amount_icons(mk):
    # أزرار قيم PlayStation (var_psn_*): نفس الإيموجي المخصص
    try:
        if _vt_conf().get("noicons"):
            return
        for row in mk.keyboard:
            for b in row:
                cb = getattr(b, "callback_data", None) or ""
                _eid = "5373306783706137993" if cb.startswith("var_psn_") else ("5377605079601785754" if cb.startswith("var_fc26_points_") else None)
                if _eid:
                    txt = getattr(b, "text", "") or ""
                    parts = txt.split(" ", 1)
                    b._icon_orig_text = txt
                    if len(parts) == 2 and not re.search(r"\w", parts[0]):
                        b.text = parts[1]
                    b.icon_custom_emoji_id = _eid
    except Exception as e:
        print(f"psn_amount_icons failed: {e}")

def _apply_icons(mk):
    try:
        conf = _vt_conf()
        if conf.get("noicons"):
            return
        for row in mk.keyboard:
            for b in row:
                cb = getattr(b, "callback_data", None) or ""
                if not cb.startswith(("buy_", "vgrp_", "grp_", "oos_")):
                    continue
                txt = getattr(b, "text", "") or ""
                low = txt.lower()
                for rx, eid in BTN_ICON_IDS:
                    if re.search(rx, low):
                        parts = txt.split(" ", 1)
                        b._icon_orig_text = txt
                        if len(parts) == 2 and not re.search(r"\w", parts[0]):
                            b.text = parts[1]          # نحذف الإيموجي العادي ليحل المخصص مكانه
                        b.icon_custom_emoji_id = eid
                        break
    except Exception as e:
        print(f"apply_icons failed: {e}")

def _strip_icons(rm):
    n = 0
    try:
        for row in getattr(rm, "keyboard", []) or []:
            for b in row:
                if getattr(b, "icon_custom_emoji_id", None):
                    b.icon_custom_emoji_id = None
                    if getattr(b, "_icon_orig_text", None):
                        b.text = b._icon_orig_text
                    n += 1
    except Exception:
        pass
    return n

def _wrap_icon_fallback(name):
    orig = getattr(bot, name, None)
    if not orig:
        return
    def w(*a, **k):
        try:
            return orig(*a, **k)
        except Exception as e:
            rm = k.get("reply_markup")
            msg = str(e).lower()
            if rm is not None and any(x in msg for x in ("icon", "emoji", "inline keyboard button", "button_")):
                _n = _strip_icons(rm)
                if _n or not _icons_off():
                    _ICON_STATE["off"] = True
                    try:
                        c = dict(_vt_conf())
                        c["noicons"] = True
                        _vt_conf_save(c)
                    except Exception:
                        pass
                    try:
                        monitor_send("⚠️ <b>رفض تيليغرام أيقونات الأزرار المخصصة</b> (غالباً انتهى Premium). تم إطفاؤها تلقائياً. بعد التجديد: /btn_icons on",
                                     key="icons_off", cooldown=3600)
                    except Exception:
                        pass
                    return orig(*a, **k)
            raise
    setattr(bot, name, w)

for _m in ("send_message", "edit_message_text", "edit_message_reply_markup", "send_photo"):
    try:
        _wrap_icon_fallback(_m)
    except Exception as _e:
        print(f"icon fallback wrap {_m} failed: {_e}")

@bot.message_handler(commands=["btn_icons"])
def btn_icons_command(message):
    if not is_admin_msg(message):
        return
    parts = (message.text or "").split()
    conf = dict(_vt_conf())
    if len(parts) > 1 and parts[1].lower() in ("on", "off"):
        conf["noicons"] = (parts[1].lower() == "off")
        _ICON_STATE["off"] = conf["noicons"]
        _vt_conf_save(conf)
    bot.reply_to(message, "🎨 أيقونات المنتجات: " + ("❌ مطفأة" if conf.get("noicons") else "✅ مفعّلة") + "\n/btn_icons on | off")

# ---------- شعار RASEEDKOM★ المضيء أعلى رسالة الترحيب (إيموجي مخصص) ----------
# الحروف بالترتيب: R A S E E D K O M ★
WELCOME_BANNER_IDS = [
    "5364023048687078741", "5357372145800334358", "5364149466754468020", "5361794927028096622",
    "5361794927028096622", "5359648590136361323", "5359549406456598104", "5375319963726793021",
    "5361625615122319358", "5402435230432775363",
]

WELCOME_BANNER_PAD = 5        # عدد الفراغات قبل الشعار في العربية (زدها لتحريكه نحو اليمين)
WELCOME_BANNER_PAD_LTR = 3    # في الإنجليزية/الفرنسية

def _u16(s):
    return len(str(s).encode("utf-16-le")) // 2

_send_main_menu_plain = send_main_menu

def send_main_menu(chat_id, lang):
    if _icons_off():
        return _send_main_menu_plain(chat_id, lang)
    # الشعار في آخر الرسالة ومتوسّط تقريباً: علامة اتجاه + فراغات بريل (لا تُحذف) قبل الإيموجي
    welcome = t(lang, "welcome")
    mark = "‎"   # اتجاه يسار→يمين دائماً حتى لا تنعكس الحروف
    pad = "⠀" * (WELCOME_BANNER_PAD if lang == "ar" else WELCOME_BANNER_PAD_LTR)
    head = welcome + "\n\n" + mark + pad
    caption = head + "⭐" * len(WELCOME_BANNER_IDS)
    mk = generate_store_keyboard(lang)
    try:
        base = _u16(head)
        ents = [telebot.types.MessageEntity("custom_emoji", base + i, 1, custom_emoji_id=eid)
                for i, eid in enumerate(WELCOME_BANNER_IDS)]
    except Exception as e:
        print(f"welcome banner entities failed: {e}")
        return _send_main_menu_plain(chat_id, lang)
    try:
        bot.send_photo(chat_id, UNIFIED_IMAGE_URL, caption=caption, caption_entities=ents, reply_markup=mk)
        return
    except Exception as e:
        print(f"welcome banner photo failed: {e}")
    try:
        bot.send_message(chat_id, caption, entities=ents, reply_markup=mk)
        return
    except Exception as e:
        print(f"welcome banner message failed: {e}")
    _send_main_menu_plain(chat_id, lang)

def _learn_admin_btn(markup):
    """زر تشغيل/إيقاف «تعلّم كيف تشتري» في لوحة الأدمن. يستبدله learn.py إن وُجد، وإلا لا يظهر شيء."""
    return None

# ---------- صفحة اختيار اللغة: إيموجي مخصص في العنوان (والأزرار تأخذ أعلامها من _dyn_icon) ----------
_send_language_menu_plain = send_language_menu

def send_language_menu(chat_id):
    if _icons_off():
        return _send_language_menu_plain(chat_id)
    try:
        rest = CHOOSE_LANG_TEXT
        if rest.startswith("🌐"):
            rest = rest[1:].lstrip()
        caption = "⭐ " + rest
        ents = [telebot.types.MessageEntity("custom_emoji", 0, 1, custom_emoji_id=ICON_LANG_GLOBE)]
        mk = InlineKeyboardMarkup()
        mk.row(
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
            InlineKeyboardButton(text="🇩🇿 العربية", callback_data="lang_ar"),
            InlineKeyboardButton(text="🇫🇷 Français", callback_data="lang_fr"),
        )
    except Exception as e:
        print(f"lang menu build failed: {e}")
        return _send_language_menu_plain(chat_id)
    try:
        bot.send_photo(chat_id, UNIFIED_IMAGE_URL, caption=caption, caption_entities=ents, reply_markup=mk)
        return
    except Exception as e:
        print(f"lang menu photo failed: {e}")
    try:
        bot.send_message(chat_id, caption, entities=ents, reply_markup=mk)
        return
    except Exception as e:
        print(f"lang menu message failed: {e}")
    _send_language_menu_plain(chat_id)

# ---------- بطاقة المنتج: إيموجي مخصص أمام «السعر» و«المتوفر» ----------
ICON_PRICE = "5197434882321567830"
ICON_STOCK = "5429518319243775957"
_send_card_orig = send_card

def _u16(s):
    return len(str(s).encode("utf-16-le")) // 2

# أعلام مخصصة (إيموجي) بدل أعلام النظام: تركيا، الهند، فرنسا، أمريكا، البرازيل، إندونيسيا
FLAG_IDS = {"🇹🇷": "5229155784192965272", "🇮🇳": "5445209411029050250", "🇫🇷": "5202132623060640759",
            "🇺🇸": "5202021044105257611", "🇧🇷": "6118655940829907978", "🇮🇩": "6215473823760780367"}
_FLAG_PUA = {f: chr(0xE000 + i) for i, f in enumerate(FLAG_IDS)}
_PUA_FLAG_ID = {_FLAG_PUA[f]: FLAG_IDS[f] for f in FLAG_IDS}

def _flags_pua(text):
    for f, ch in _FLAG_PUA.items():
        text = text.replace(f, ch)
    return text

def _flag_ents(text, base=0):
    """يستبدل كل علم بـ ⭐ ويعيد (نص جديد، entities) بإزاحة base."""
    out, ents = "", []
    for ch in _flags_pua(text):
        if ch in _PUA_FLAG_ID:
            ents.append(telebot.types.MessageEntity("custom_emoji", base + _u16(out), 1, custom_emoji_id=_PUA_FLAG_ID[ch]))
            out += "⭐"
        else:
            out += ch
    return out, ents

def _caption_to_entities(caption):
    """يحوّل نص Markdown البسيط (*غامق*) إلى نص + entities، ويضع إيموجي مخصصاً في سطري السعر والمتوفر."""
    labels = {}
    for l in SUPPORTED_LANGS:
        tx = TEXTS.get(l, {})
        for k, eid in (("price", ICON_PRICE), ("available", ICON_STOCK)):
            v = tx.get(k)
            if v:
                labels[v] = eid
    out, ents, pos = [], [], 0
    for line in str(caption).split("\n"):
        eid = None
        for _lp, _le in (("🤖 Google Play", ICON_GPLAY), ("🍎 Apple Gift Card", ICON_APPLE_GIFT), ("🎮 Steam Wallet", ICON_STEAM_GIFT), ("🔫 PUBG", ICON_BC_CHEST), ("🔥 Free Fire", ICON_FF_CHEST)):
            if line.startswith(_lp):
                line = "⭐" + line[len(_lp.split(" ", 1)[0]):]
                eid = _le
                break
        for lab, e in labels.items():
            if line.startswith(lab):
                head = lab.split(" ", 1)
                if len(head) == 2 and not re.search(r"\w", head[0]):
                    line = "⭐" + line[len(head[0]):]
                    eid = e
                break
        line = _flags_pua(line)
        res, last, bolds = "", 0, []
        for m in re.finditer(r"\*([^*\n]+)\*", line):
            res += line[last:m.start()]
            b0 = _u16(res)
            res += m.group(1)
            bolds.append((b0, _u16(m.group(1))))
            last = m.end()
        res += line[last:]
        fl, chars = [], []
        for ch in res:
            if ch in _PUA_FLAG_ID:
                fl.append((_u16("".join(chars)), _PUA_FLAG_ID[ch]))
                chars.append("⭐")
            else:
                chars.append(ch)
        res = "".join(chars)
        for off, fid in fl:
            ents.append(telebot.types.MessageEntity("custom_emoji", pos + off, 1, custom_emoji_id=fid))
        if eid:
            ents.append(telebot.types.MessageEntity("custom_emoji", pos, 1, custom_emoji_id=eid))
        for b0, bl in bolds:
            ents.append(telebot.types.MessageEntity("bold", pos + b0, bl))
        out.append(res)
        pos += _u16(res) + 1
    return "\n".join(out), ents

def send_card(chat_id, product, caption, markup):
    if _icons_off():
        return _send_card_orig(chat_id, product, caption, markup)
    try:
        text, ents = _caption_to_entities(caption)
    except Exception as e:
        print(f"card entities failed: {e}")
        return _send_card_orig(chat_id, product, caption, markup)
    if len(text) <= 1024:
        for photo in (product.get("image"), UNIFIED_IMAGE_URL):
            if not photo:
                continue
            try:
                bot.send_photo(chat_id, photo, caption=text, caption_entities=ents, reply_markup=markup)
                return
            except Exception as e:
                print(f"card photo failed: {e}")
    try:
        bot.send_message(chat_id, text, entities=ents, reply_markup=markup)
        return
    except Exception as e:
        print(f"card message failed: {e}")
    return _send_card_orig(chat_id, product, caption, markup)

# ---------- منشورات المنتجات الدورية (القناة/الزبائن): إيموجي مخصص كما في المتجر ----------
# (الأصلان يُعرَّفان لاحقاً في bot_base بعد إعادة تسميتهما عبر patch أعلاه)

def _logo_id(item):
    low = str(item.get("name") or "").lower()
    for rx, eid in BTN_ICON_IDS:
        if re.search(rx, low):
            return eid
    return None

def _lead_swap(label):
    """يحذف الإيموجي العادي من أول التسمية ('📦 المتوفر:' → 'المتوفر:')."""
    parts = str(label).split(" ", 1)
    if len(parts) == 2 and not re.search(r"\w", parts[0]):
        return parts[1]
    return str(label)

# شعار RASEEDKOM بحروف إيموجي مخصصة (R A S E E D K O M) يظهر أعلى كل منشور
BRAND_IDS = ["5328162635860948105", "5293991227513914037", "5332815043220225405",
             "5327938799345349736", "5327938799345349736", "5294029641701407930",
             "5330144144792763349", "5307644490461231051", "5330094426251344221"]

def _post_build(item, name, lbl_stock, stock_val, lbl_price, price_val):
    ents = []
    logo = _logo_id(item)
    text = ""
    for eid in BRAND_IDS:
        ents.append(telebot.types.MessageEntity("custom_emoji", _u16(text), 1, custom_emoji_id=eid))
        text += "⭐"
    text += "\n"
    if logo:
        ents.append(telebot.types.MessageEntity("custom_emoji", _u16(text), 1, custom_emoji_id=logo))
    text += ("⭐" if logo else str(item.get("icon") or "")) + " "
    b0 = _u16(text)
    name2, fents = _flag_ents(str(name), b0)
    text += name2
    ents.extend(fents)
    ents.append(telebot.types.MessageEntity("bold", b0, _u16(name2)))
    text += "\n\n"
    for eid, lbl, val in ((ICON_STOCK, lbl_stock, stock_val), (ICON_PRICE, lbl_price, price_val)):
        pos = _u16(text)
        text += "⭐ " + _lead_swap(lbl) + " " + str(val)
        ents.append(telebot.types.MessageEntity("custom_emoji", pos, 1, custom_emoji_id=eid))
        text += "\n"
    return text.rstrip("\n"), ents

def _send_post_ents(chat_id, item, text, ents, markup, fallback):
    photo = item.get("image", UNIFIED_IMAGE_URL)
    for _ in range(3):
        try:
            try:
                if len(text) > 1024:
                    bot.send_message(chat_id, text, entities=ents, reply_markup=markup)
                else:
                    bot.send_photo(chat_id, photo, caption=text, caption_entities=ents, reply_markup=markup)
            except ApiTelegramException as e:
                if e.error_code in (403, 429):
                    raise
                bot.send_message(chat_id, text, entities=ents, reply_markup=markup)
            return True
        except ApiTelegramException as e:
            if e.error_code == 429:
                time.sleep(_retry_after(e) + 1)
                continue
            if e.error_code == 403 or "chat not found" in str(e).lower():
                return False
            print(f"post entities failed: {e}")
            return fallback()
        except Exception as e:
            print(f"post entities failed: {e}")
            return fallback()
    return None

def send_channel_post(chat_id, item):
    if _icons_off():
        return _send_channel_post_orig(chat_id, item)
    try:
        sync_stock()
        sv = item["stock"] if item["stock"] == "♾️" else str(item["stock"])
        text, ents = _post_build(item, item["name"], "Current stock:", sv, "Price:", item["price"])
        mk = InlineKeyboardMarkup()
        mk.add(InlineKeyboardButton(text="🛒 Buy now", url=BOT_LINK + "?start=qb" + chr(95) + item["id"]))
        return _send_post_ents(chat_id, item, text, ents, mk, lambda: _send_channel_post_orig(chat_id, item))
    except Exception as e:
        print(f"channel post build failed: {e}")
        return _send_channel_post_orig(chat_id, item)

def send_user_post(user_id, item):
    if _icons_off():
        return _send_user_post_orig(user_id, item)
    try:
        sync_stock()
        lang = get_lang(user_id)
        sv = item["stock"] if item["stock"] == "♾️" else str(item["stock"])
        text, ents = _post_build(item, tr(item, "name", lang), t(lang, "available"), sv, t(lang, "price"), item["price"])
        mk = InlineKeyboardMarkup()
        mk.add(InlineKeyboardButton(text=t(lang, "order_now"), callback_data="qb" + chr(95) + item["id"]))
        return _send_post_ents(int(user_id), item, text, ents, mk, lambda: _send_user_post_orig(user_id, item))
    except Exception as e:
        print(f"user post build failed: {e}")
        return _send_user_post_orig(user_id, item)

def _own_oos(item):
    s = item.get("stock")
    return isinstance(s, int) and not isinstance(s, bool) and s <= 0

def _oos_button(item, lang):
    if _vt_is_pid(item["id"]):
        label = _vt_short(item["name"])
    else:
        names = SHORT_NAMES.get(item["id"], {})
        label = names.get(lang) or names.get("en") or tr(item, "name", lang)
    if len(label) > 16:
        label = label[:15].rstrip() + "…"
    return InlineKeyboardButton(text=f"{item['icon']} {label}", callback_data=f"oos_{item['id']}")

def _style_store(mk):
    """أخضر لكل منتج/مجموعة متوفرة، أحمر للنافد. تعطيل: /btn_style off"""
    _apply_icons(mk)
    try:
        if _vt_conf().get("nostyle"):
            return mk
        for row in mk.keyboard:
            for b in row:
                cb = getattr(b, "callback_data", None) or ""
                if cb.startswith("oos_") or getattr(b, "_oos_grp", False):
                    b.style = "danger"
                elif cb.startswith(("buy_", "vgrp_", "grp_")):
                    b.style = "success"
                elif cb == "gm_hub_m":
                    b.style = "danger"      # زر «لعبة · من سيفوز؟» أحمر
    except Exception as e:
        print(f"style_store failed: {e}")
    return mk

def _assemble_store(markup, oos):
    """النافد في الأعلى (3 في الصف) ثم باقي القائمة. حد تيليغرام 100 زر."""
    final = InlineKeyboardMarkup(row_width=2)
    total = sum(len(r) for r in markup.keyboard)
    room = max(0, 100 - total)
    oos = oos[:room]
    for i in range(0, len(oos), 3):
        final.row(*oos[i:i + 3])
    final.keyboard.extend(markup.keyboard)
    return _style_store(final)

@bot.callback_query_handler(func=lambda c: c.data.startswith("oos_"))
def handle_oos_button(call):
    lang = get_lang(call.from_user.id)
    # الزر الأحمر يفتح صفحة المنتج/المجموعة (الوصف + زر «أعلمني») بدل رسالة فقط
    try:
        _d = call.data
        if _d == "oos_netflix":
            call.data = "grp_netflix"
            return handle_store_group(call)
        if _d.startswith("oos_grp_"):
            call.data = "grp_" + _d[8:]
            return handle_store_group(call)
        if _d.startswith("oos_vg_"):
            call.data = "vgrp_" + _d[7:]
            return handle_vente_group(call)
        _pid = _d[4:]
        if find_product(_pid):
            return _qb_dispatch(call, _pid)
    except Exception as e:
        print(f"oos open failed: {e}")
    txt ={"ar": "❌ نفد المخزون حالياً", "en": "❌ Out of stock right now", "fr": "❌ Rupture de stock"}.get(lang, "❌ Out of stock")
    try:
        bot.answer_callback_query(call.id, txt)
    except Exception:
        pass

@bot.message_handler(commands=["btn_style"])
def btn_style_command(message):
    if not is_admin_msg(message):
        return
    parts = (message.text or "").split()
    conf = _vt_conf()
    if len(parts) > 1 and parts[1].lower() in ("on", "off"):
        conf["nostyle"] = (parts[1].lower() == "off")
        _vt_conf_save(conf)
    bot.reply_to(message, "🎨 ألوان الأزرار: " + ("❌ مطفأة" if conf.get("nostyle") else "✅ مفعّلة") + "\n/btn_style on | off")

def generate_store_keyboard(lang):
    sync_stock()
    markup = InlineKeyboardMarkup(row_width=2)
    oos = []
    shown = set()
    group_members = {m for g in STORE_GROUPS.values() for m in g["members"]}

    for slot in STORE_SLOTS:
        if isinstance(slot, tuple):
            items = [find_product(pid) for pid in slot]
            items = [i for i in items if i and not _own_hidden(i["id"])]
            shown.update(i["id"] for i in items)
            live = []
            for i in items:
                if _own_oos(i):
                    oos.append(_oos_button(i, lang))
                else:
                    live.append(i)
            if len(live) == 2:
                markup.row(_pair_button(live[0], lang), _pair_button(live[1], lang))
            elif live:
                markup.add(_slot_button(live[0], lang))
        elif slot == "row:prime_netflix":
            _g = STORE_GROUPS["netflix"]
            shown.update(_g["members"])
            _pc = None
            try:
                _pc = _vt_find_cell("prime")
            except Exception as e:
                print(f"prime cell failed: {e}")
            try:
                if _pc and any(c[0] == "prime" for c in _VT_OOSG):
                    _pc = None      # Prime كله نافد: يظهر مرة واحدة بالأحمر في الأعلى (لا زر أخضر مكرر)
            except Exception:
                pass
            lo, hi, stock = _group_range("netflix")
            if isinstance(stock, int) and stock <= 0:
                oos.append(InlineKeyboardButton(text=f"{_g['icon']} {_g['name']}", callback_data="oos_netflix"))
                if _pc:
                    markup.add(_vt_cell_button(_pc, lang, False))
            elif _pc:
                markup.row(_vt_cell_button(_pc, lang, True),
                           InlineKeyboardButton(text=f"{_g['icon']} {_g['name']} | {lo}+", callback_data="grp_netflix"))
            else:
                price = lo if lo == hi else f"{lo} - {hi}"
                stock_txt = stock if stock == "♾️" else f"📦 {stock}"
                markup.add(InlineKeyboardButton(text=f"{_g['icon']} {_g['name']} | {price} | {stock_txt}", callback_data="grp_netflix"))
        elif slot == "vente:gem6":
            try:
                _gc = _vt_find_cell("gem6")
                if _gc:
                    markup.add(_vt_cell_button(_gc, lang, False))
            except Exception as e:
                print(f"gem6 cell failed: {e}")
        elif slot == "vente:all":
            try:
                _vt_add_buttons(markup, lang, oos)
            except Exception as e:
                print(f"vente buttons failed: {e}")
        elif slot == "next:gifts":
            _nav_rows(markup, lang, "subs")
        elif slot.startswith("grp:"):
            gid = slot[4:]
            g = STORE_GROUPS.get(gid)
            if not g:
                continue
            if gid == "claude_api" and not _own_claude_shown():
                continue          # Claude/Codex عند المورّد داخل قائمته
            lo, hi, stock = _group_range(gid)
            if isinstance(stock, int) and stock <= 0:
                oos.append(InlineKeyboardButton(text=f"{g['icon']} {g['name']}", callback_data=f"oos_grp_{gid}"))
                continue
            price = lo if lo == hi else f"{lo} - {hi}"
            stock_txt = stock if stock == "♾️" else f"📦 {stock}"
            markup.add(InlineKeyboardButton(
                text=f"{g['icon']} {g['name']} | {price} | {stock_txt}",
                callback_data=f"grp_{gid}",
            ))
        elif slot.startswith("sep:"):
            item = find_product(slot[4:])
            if item:
                shown.add(item["id"])
                markup.add(InlineKeyboardButton(text=tr(item, "text", lang), callback_data="noop"))
        else:
            item = find_product(slot)
            if item and not _own_hidden(item["id"]):
                shown.add(item["id"])
                if _own_oos(item):
                    oos.append(_oos_button(item, lang))
                else:
                    markup.add(_slot_button(item, lang))

    # أي منتج يضيفه الأدمن لاحقاً ولم يوضع في الترتيب يظهر في الآخر
    for item in products:
        if item.get("type") == "separator" or item["id"] in shown or item["id"] in group_members or item["id"] in GIFT_VARIANTS or _own_hidden(item["id"]):
            continue
        if _own_oos(item):
            oos.append(_oos_button(item, lang))
        else:
            markup.add(_slot_button(item, lang))

    markup.row(
        InlineKeyboardButton(text=t(lang, "cmd_update"), callback_data="mn_refresh"),
        InlineKeyboardButton(text=smt(lang, "ref"), callback_data="rf_o_m"),
    )
    markup.row(
        InlineKeyboardButton(text=t(lang, "kb_start"), callback_data="mn_start"),
        InlineKeyboardButton(text=wt(lang, "btn_wallet"), callback_data="pf_wallet"),
    )
    markup.add(InlineKeyboardButton(text=smt(lang, "game"), callback_data="gm_hub_m"))
    return _assemble_store(markup, oos)

# ============================================================
# ========== صفحة بطاقات الهدايا (الصفحة الثانية) ==========
# ============================================================
def generate_gift_keyboard(lang):
    mk = InlineKeyboardMarkup(row_width=1)
    for slot in GIFT_SLOTS:
        if slot.startswith("sep:"):
            item = find_product(slot[4:])
            if item:
                mk.add(InlineKeyboardButton(text=tr(item, "text", lang), callback_data="noop"))
        else:
            item = find_product(slot)
            if item:
                if _own_oos(item):
                    _b = _slot_button(item, lang)
                    _b.callback_data = f"oos_{item['id']}"
                    mk.add(_b)
                else:
                    mk.add(_slot_button(item, lang))
    _nav_rows(mk, lang, "gifts")
    return _gift_outer_style(_style_store(mk))

@bot.callback_query_handler(func=lambda c: c.data == "gcp")
def handle_gift_page(call):
    lang = get_lang(call.from_user.id)
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    mk = generate_gift_keyboard(lang)
    base = GIFT_PAGE_TEXT.get(lang, GIFT_PAGE_TEXT["ar"])
    sent = False
    if not _icons_off():
        try:
            rest = re.sub(r"<[^>]+>", "", base).split("\n\n", 1)[1]
            head = "‎"
            text = head + "⭐" * len(GIFT_BANNER_IDS) + "\n\n" + rest
            ents = [telebot.types.MessageEntity("custom_emoji", _u16(head) + i, 1, custom_emoji_id=eid)
                    for i, eid in enumerate(GIFT_BANNER_IDS)]
            bot.send_message(call.message.chat.id, text, entities=ents, reply_markup=mk)
            sent = True
        except Exception as e:
            print(f"gift banner failed: {e}")
    if not sent:
        bot.send_message(call.message.chat.id, base, parse_mode="HTML", reply_markup=generate_gift_keyboard(lang))
    bot.answer_callback_query(call.id)


# ============================================================
# ========== FAZER: كتالوج أوسع + مطابقة Google/Steam/PUBG/Free Fire ==========
# ============================================================
FAZER_CAT_FILTER = re.compile(r"apple|itunes|google|steam|playstation|psn|ea\s*sports|pubg|battlegrounds|free\s*fire|garena", re.I)

def _fazer_fetch_catalog():
    from concurrent.futures import ThreadPoolExecutor
    cats = []
    cursor = None
    for _ in range(10):
        params = {"limit": 500}
        if cursor:
            params["cursor"] = cursor
        data = _fazer_get("/giftcards", params)
        cats.extend(data.get("items") or [])
        meta = data.get("meta") or {}
        if meta.get("has_more") and meta.get("next_cursor"):
            cursor = meta["next_cursor"]
        else:
            break
    wanted = [c for c in cats if FAZER_CAT_FILTER.search(f"{c.get('name','')} {c.get('note','')}")]
    prev = {c["category_id"]: c for c in (_catalog.get("cats") or [])}

    def one(c):
        cid = str(c.get("category_id"))
        try:
            d = _fazer_get("/giftcards/cards", {"category_id": c.get("category_id")})
        except Exception as e:
            print(f"fazer category {cid} failed: {e}")
            if cid in prev:
                return prev[cid]
            if re.search(r"apple|itunes", f"{c.get('name','')} {c.get('note','')}", re.I):
                raise
            return None
        return {
            "category_id": cid,
            "name": c.get("name") or "",
            "note": c.get("note") or "",
            "offers": d.get("offers") or [],
        }

    with ThreadPoolExecutor(max_workers=4) as ex:
        res = list(ex.map(one, wanted))
    return [r for r in res if r]

_US_RE = re.compile(r"\bus\b|\busa\b|united states|america|🇺🇸", re.I)
_GP_RE = re.compile(r"google", re.I)
_ST_RE = re.compile(r"steam", re.I)
_ANY_RE = re.compile(r"")
_PSN_RE = re.compile(r"playstation|\bpsn\b", re.I)
# product_id -> (فلتر القسم، فلتر البلد، استثناء اختياري)
FAZER_SPEC = {
    "apple_gift_us": (re.compile(r"apple|itunes", re.I), _US_RE, None),
    "gplay_us": (_GP_RE, _US_RE, None),
    "gplay_fr": (_GP_RE, re.compile(r"france|french|🇫🇷|\bfr\b", re.I), None),
    "gplay_br": (_GP_RE, re.compile(r"brazil|brasil|🇧🇷|\bbr\b|\bbrl\b", re.I), None),
    "gplay_in": (_GP_RE, re.compile(r"india|🇮🇳|\binr\b", re.I), None),
    "gplay_tr": (_GP_RE, re.compile(r"turk|türk|🇹🇷|\btr\b|\btry\b", re.I), None),
    "steam_us": (_ST_RE, _US_RE, None),
    "steam_id": (_ST_RE, re.compile(r"indonesia|🇮🇩|\bidr\b", re.I), None),
    "psn_us": (_PSN_RE, _US_RE, None),
    "psn_fr": (_PSN_RE, re.compile(r"france|french|🇫🇷|\bfr\b", re.I), None),
    "psn_tr": (_PSN_RE, re.compile(r"turk|türk|🇹🇷|\btr\b|\btry\b", re.I), None),
    "psn_br": (_PSN_RE, re.compile(r"brazil|brasil|🇧🇷|\bbr\b|\bbrl\b", re.I), None),
    "pubg_uc": (re.compile(r"pubg.*mobile|mobile.*pubg", re.I), _ANY_RE, None),
    "fc26_points": (re.compile(r"fc\W{0,3}26", re.I), _ANY_RE, None),
    "pubg_gcoin": (re.compile(r"pubg|battlegrounds", re.I), _ANY_RE, re.compile(r"mobile|\buc\b", re.I)),
    "freefire_codes": (re.compile(r"free\s*fire", re.I), _ANY_RE, None),
}

def _ff_re(usd, dia):
    # عرض Free Fire قد يُسمّى بالدولار (1 USD) أو بالجواهر (100+10)
    return re.compile(rf"(?<![\d.]){usd}\s*(?:usd|\$)|\$\s*{usd}(?![\d.])|(?<![\d.+]){dia}(?!\d)", re.I)

# مطابقة خاصة لاسم العرض عند FAZER (بدل رقم الاسم الأول)
FAZER_OFFER_RE = {
    ("pubg_gcoin", "100 G-Coin"): re.compile(r"(?<![\d.+])100(?!\d)(?!\s*\+)", re.I),
    ("pubg_gcoin", "500 + 10 G-Coin"): re.compile(r"(?<![\d.])500\s*\+\s*10(?!\d)", re.I),
    ("pubg_gcoin", "1000 + 50 G-Coin"): re.compile(r"(?<![\d.])1000\s*\+\s*50(?!\d)", re.I),
    ("pubg_gcoin", "2500 + 200 G-Coin"): re.compile(r"(?<![\d.])2500\s*\+\s*200(?!\d)", re.I),
    ("freefire_codes", "100 + 10 💎"): _ff_re(1, r"100\s*\+\s*10"),
    ("freefire_codes", "210 + 21 💎"): _ff_re(2, r"210\s*\+\s*21"),
    ("freefire_codes", "530 + 53 💎"): _ff_re(5, r"530\s*\+\s*53"),
    ("freefire_codes", "1080 + 108 💎"): _ff_re(10, r"1080\s*\+\s*108"),
    ("freefire_codes", "2200 + 220 💎"): _ff_re(20, r"2200\s*\+\s*220"),
}

def _pick_instant(uniq):
    """uniq: {(category_id, card_id): (cat, offer)}. إذا كانت كل الأقسام نفس القسم مع/بدون _instant_use
    يرجع مفتاح الأرخص المتوفر في المخزون (وإلا الأرخص). غير ذلك: None (يبقى ambiguous)."""
    try:
        bases = {re.sub(r"_instant_use$", "", str(k[0])) for k in uniq}
        if len(bases) != 1:
            return None
        def _cost(v):
            try:
                return Decimal(str(v[1].get("price_usd")))
            except Exception:
                return Decimal("999999")
        def _has(v):
            st = v[1].get("stock")
            try:
                return st is None or int(st) > 0
            except Exception:
                return True
        items = list(uniq.items())
        ok = [kv for kv in items if _has(kv[1])] or items
        return min(ok, key=lambda kv: _cost(kv[1]))[0]
    except Exception:
        return None

_fazer_match_orig = fazer_match

def fazer_match(product_id, label, cats):
    spec = FAZER_SPEC.get(product_id)
    if not spec:
        # بطاقات Apple القديمة: تبقى المطابقة داخل أقسام Apple فقط (حتى لا تختلط مع Google/Steam)
        if cats and not FAZER_MANUAL_MAP.get((product_id, re.sub(r"\s+x\d+$", "", str(label)))):
            cats = [c for c in cats if re.search(r"apple|itunes", f"{c['name']} {c['note']}", re.I)]
        return _fazer_match_orig(product_id, label, cats)
    base = re.sub(r"\s+x\d+$", "", str(label))
    if FAZER_MANUAL_MAP.get((product_id, base)):
        return _fazer_match_orig(product_id, label, cats)
    if not cats:
        return None, "no_catalog"
    cat_re, ctry_re, excl_re = spec
    num_re = FAZER_OFFER_RE.get((product_id, base))
    if num_re is None:
        num = base.split()[0]
        num_re = re.compile(rf"(?<![\d.]){re.escape(num)}(?!\d|\.\d)")
    found = []
    for c in cats:
        ctext = f"{c['name']} {c['note']}"
        if not cat_re.search(ctext) or (excl_re and excl_re.search(ctext)):
            continue
        cat_ok = bool(ctry_re.search(ctext))
        for o in c["offers"]:
            name = _norm_name(o.get("name"))
            if (cat_ok or ctry_re.search(name)) and num_re.search(name):
                found.append((c, o))
    uniq = {(c["category_id"], str(o.get("card_id"))): (c, o) for c, o in found}
    if not uniq:
        return None, "no_offer"
    if len(uniq) > 1:
        glob = {k: v for k, v in uniq.items() if re.search(r"global|\bww\b|worldwide", f"{v[0]['name']} {v[0]['note']} {v[1].get('name')}", re.I)}
        if len(glob) == 1:
            uniq = glob
        else:
            _pk = _pick_instant(uniq)
            if _pk is None:
                return None, "ambiguous"
            uniq = {_pk: uniq[_pk]}
    c, o = next(iter(uniq.values()))
    return _mapping(c, o), "auto"

# ---- تسعير تلقائي: تكلفة FAZER × 1.06 بحد أدنى ربح 0.25$ (Steam / PlayStation) ----
AUTO_PRICE_PIDS = ("steam_us", "steam_id", "psn_us", "psn_fr", "psn_tr", "psn_br", "pubg_uc", "fc26_points")
AUTO_PROFIT_PCT = 6
AUTO_MIN_PROFIT = Decimal("0.25")

def _auto_price(cost):
    cost = Decimal(str(cost))
    p = max(cost * (Decimal(100 + AUTO_PROFIT_PCT) / 100), cost + AUTO_MIN_PROFIT)
    return str(p.quantize(Decimal("0.01"), rounding=ROUND_CEILING))

# ---- تسعير تلقائي بنفس الهامش الحالي (Apple / Google Play) ----
# (التكلفة عند FAZER وقت الضبط، سعر البيع وقتها). النسبة بينهما = الهامش المحفوظ.
_RATIO_BASE = {
    "apple_gift_tr": {"10 TRY": ("0.1803", "1.00"), "50 TRY": ("0.8944", "1.35"), "100 TRY": ("1.8877", "2.50"),
                      "150 TRY": ("2.8314", "3.60"), "200 TRY": ("3.7752", "5.00"), "250 TRY": ("5.0047", "5.70")},
    "apple_gift_in": {"100 INR": ("1.2775", "1.58"), "200 INR": ("2.0351", "2.45"), "250 INR": ("2.5197", "3.05"),
                      "500 INR": ("5.3443", "6.90"), "1000 INR": ("10.6886", "12.60"), "1500 INR": ("16.0843", "18.90")},
    "apple_gift_fr": {"10 EUR": ("11.1625", "12.00"), "20 EUR": ("22.3250", "23.65"),
                      "50 EUR": ("55.8125", "59.00"), "100 EUR": ("111.6250", "116.22")},
    "apple_gift_us": {"2 USD": ("1.8810", "2.15"), "5 USD": ("4.7025", "5.15"), "10 USD": ("10.0750", "10.20"),
                      "20 USD": ("20.1500", "20.50"), "30 USD": ("29.8485", "31.00")},
    "gplay_us": {"5 USD": ("4.9474", "5.20"), "10 USD": ("9.8939", "10.70"), "15 USD": ("14.8424", "15.70"),
                 "20 USD": ("19.7888", "20.81"), "50 USD": ("49.4715", "53.00"), "100 USD": ("98.9428", "103.00")},
    "gplay_fr": {"10 EUR": ("11.1625", "12.00"), "15 EUR": ("16.7436", "18.00"), "25 EUR": ("27.9061", "30.10"),
                 "50 EUR": ("55.8125", "60.00"), "100 EUR": ("111.6250", "119.00")},
    "gplay_br": {"10 BRL": ("1.6109", "2.20"), "30 BRL": ("4.5644", "5.90"), "50 BRL": ("6.7123", "11.00"),
                 "100 BRL": ("18.0337", "22.10"), "150 BRL": ("27.0507", "34.00")},
    "gplay_in": {"10 INR": ("0.0947", "0.71"), "50 INR": ("0.3947", "0.98"), "100 INR": ("0.8947", "1.37"),
                 "1000 INR": ("10.6048", "11.11"), "1500 INR": ("15.9072", "18.00")},
    "gplay_tr": {"50 TRY": ("0.9399", "1.31"), "100 TRY": ("1.8799", "2.30"),
                 "250 TRY": ("4.4524", "5.50"), "500 TRY": ("9.9684", "12.00")},
}
_ratio_alerted = set()
# بطاقات بربح ثابت بالدولار (السعر = التكلفة + هذا الربح، يتبع FAZER صعوداً ونزولاً)
_FIXED_PROFIT = {("apple_gift_in", "100 INR"): Decimal("0.30")}

def _ratio_price(pid, label, cost):
    """سعر البيع الجديد بنفس الهامش. None = لا تغيّر السعر."""
    b = _RATIO_BASE.get(pid, {}).get(label)
    if not b:
        return None
    bc, bs = Decimal(b[0]), Decimal(b[1])
    cost = Decimal(str(cost))
    if cost <= 0:
        return None
    # تغيّر مفاجئ كبير في التكلفة = غالباً خلل في الكتالوج: لا نطبّق وننبّه الأدمن مرة واحدة
    if abs(cost - bc) / bc > Decimal("0.25") and abs(cost - bc) > Decimal("0.10"):
        if (pid, label) not in _ratio_alerted:
            _ratio_alerted.add((pid, label))
            try:
                alert_admin(f"⚠️ <b>تغيّر كبير في تكلفة FAZER</b>\n📦 {pid} — {html.escape(label)}\n"
                            f"كانت {bc}$ وأصبحت {cost}$.\nلم أغيّر سعر البيع تلقائياً، راجعها.")
            except Exception:
                pass
        return None
    _fx = _FIXED_PROFIT.get((pid, label))
    if _fx is not None:
        p = cost + _fx                # ربح ثابت محدد يدوياً
    elif bs / bc > Decimal("1.5"):
        p = cost + (bs - bc)          # بطاقات صغيرة: نفس الربح بالدولار
    else:
        p = cost * bs / bc            # نفس نسبة الهامش
    p = max(p, cost + Decimal("0.03"))
    return str(p.quantize(Decimal("0.01"), rounding=ROUND_CEILING))

def _ratio_reprice(cats):
    try:
        for pid in _RATIO_BASE:
            lst = GIFT_VARIANTS.get(pid)
            if not lst:
                continue
            for i, (label, old) in enumerate(list(lst)):
                if label not in _RATIO_BASE[pid]:
                    continue
                m, _r = fazer_match(pid, label, cats)
                if m and m.get("price_usd") is not None:
                    np_ = _ratio_price(pid, label, m["price_usd"])
                    if np_:
                        lst[i] = (label, np_)
            try:
                vals = [float(x[1]) for x in lst]
                for it in products:
                    if it.get("id") == pid:
                        it["price"] = f"${min(vals):.2f} - ${max(vals):.2f}"
            except Exception:
                pass
    except Exception as e:
        print("ratio_reprice failed:", e)

def _gift_reprice(cats):
    _ratio_reprice(cats)
    try:
        for pid in AUTO_PRICE_PIDS:
            lst = GIFT_VARIANTS.get(pid)
            if not lst:
                continue
            for i, (label, old) in enumerate(list(lst)):
                m, _r = fazer_match(pid, label, cats)
                if m and m.get("price_usd") is not None:
                    lst[i] = (label, _auto_price(m["price_usd"]))
    except Exception as e:
        print("gift_reprice failed:", e)

_fazer_load_orig = fazer_load_catalog

# ---- حالة كل قيمة عند FAZER: متوفر (أخضر + العدد) / نافد (أحمر) / غير معروف ----
def _gstate(pid, idx):
    cats = _catalog.get("cats")
    if not cats:
        return "unk", None
    try:
        label = GIFT_VARIANTS[pid][int(idx)][0]
        m, reason = fazer_match(pid, label, cats)
    except Exception:
        return "unk", None
    if not m:
        return ("out", 0) if reason == "no_offer" else ("unk", None)
    st = m.get("stock")
    if st is None:
        return "unk", None
    try:
        st = int(st)
    except Exception:
        return "unk", None
    return ("ok", st) if st > 0 else ("out", 0)

def _gift_amount_post(mk, pid):
    try:
        for row in mk.keyboard:
            for b in row:
                cb = getattr(b, "callback_data", None) or ""
                if not cb.startswith(f"var_{pid}_"):
                    continue
                idx = cb.rsplit("_", 1)[1]
                stt, n = _gstate(pid, idx)
                if stt == "ok":
                    b.style = "success"
                elif stt == "out":
                    b.style = "danger"
                    b.callback_data = f"gno_{pid}_{idx}"
    except Exception as e:
        print(f"gift_amount_post failed: {e}")

def _gift_outer_style(mk):
    # زر البطاقة يصير أحمر إذا كل قيمها نافدة
    try:
        for row in mk.keyboard:
            for b in row:
                cb = getattr(b, "callback_data", None) or ""
                if cb.startswith("buy_") and cb[4:] in GIFT_VARIANTS:
                    pid = cb[4:]
                    sts = [_gstate(pid, i)[0] for i in range(len(GIFT_VARIANTS[pid]))]
                    if sts and all(x == "out" for x in sts):
                        b.style = "danger"
    except Exception as e:
        print(f"gift_outer_style failed: {e}")
    return mk

GIFT_NOTIFY_TX = {
    "ar": "✅ تم! سنرسل لك إشعاراً أول ما تتوفر هذه القيمة.",
    "en": "✅ Done! We will message you as soon as this amount is available.",
    "fr": "✅ C'est noté ! Nous vous écrirons dès que ce montant sera disponible.",
}

@bot.callback_query_handler(func=lambda c: c.data.startswith("gno_"))
def handle_gift_out(call):
    uid = call.from_user.id
    lang = get_lang(uid)
    try:
        pid, idx = call.data[4:].rsplit("_", 1)
        product = find_product(pid)
        label, _price = GIFT_VARIANTS[pid][int(idx)]
        if not product:
            raise ValueError("no product")
    except Exception:
        bot.answer_callback_query(call.id)
        return
    mk = InlineKeyboardMarkup(row_width=1)
    mk.add(InlineKeyboardButton(text=t(lang, "notify_me"), callback_data=f"gnn_{pid}_{idx}"))
    mk.add(InlineKeyboardButton(text=t(lang, "back"), callback_data=f"buy_{pid}"))
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    bot.send_message(call.message.chat.id,
                     f"❌ {tr(product, 'name', lang)} — {label}\n\n{t(lang, 'out_variant')}",
                     reply_markup=mk)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data.startswith("gnn_"))
def handle_gift_notify(call):
    uid = call.from_user.id
    lang = get_lang(uid)
    try:
        pid, idx = call.data[4:].rsplit("_", 1)
        product = find_product(pid)
        label, _price = GIFT_VARIANTS[pid][int(idx)]
        if not product:
            raise ValueError("no product")
        _sadd(f"rk:notify:g:{pid}:{idx}", str(uid))
    except Exception:
        bot.answer_callback_query(call.id)
        return
    try:
        notify_admin_interest(call.from_user, {"name": f"{product['name']} — {label}", "price": "", "id": pid}, lang)
    except Exception:
        pass
    bot.answer_callback_query(call.id, GIFT_NOTIFY_TX.get(lang, GIFT_NOTIFY_TX["ar"]), show_alert=True)

def _gift_notify_restock(pid, idx):
    key = f"rk:notify:g:{pid}:{idx}"
    subs = _smembers(key)
    if not subs:
        return
    product = find_product(pid)
    if not product:
        return
    label = GIFT_VARIANTS[pid][int(idx)][0]

    def _run():
        for uid in subs:
            try:
                lang = get_lang(uid)
                mk = InlineKeyboardMarkup()
                mk.add(InlineKeyboardButton(text=mt(lang, "open_btn"), callback_data=f"buy_{pid}"))
                _safe_send(int(uid), mt(lang, "restock").format(
                    product=html.escape(f"{tr(product, 'name', lang)} — {label}")),
                    parse_mode="HTML", reply_markup=mk)
                _srem(key, uid)
                time.sleep(0.05)
            except Exception as e:
                print(f"gift restock notify failed: {e}")
        monitor_send(f"🔔 <b>أُرسل إشعار التوفر</b> لـ {len(subs)} زبون — {html.escape(product['name'])} {html.escape(label)}")

    threading.Thread(target=_run, daemon=True).start()

def _gift_states_snapshot():
    snap = {}
    try:
        for pid, lst in GIFT_VARIANTS.items():
            for i in range(len(lst)):
                snap[(pid, i)] = _gstate(pid, i)[0]
    except Exception:
        pass
    return snap

def fazer_load_catalog(force=False, allow_fetch=True):
    before = _catalog.get("ts")
    prev = _gift_states_snapshot()
    cats = _fazer_load_orig(force=force, allow_fetch=allow_fetch)
    if cats and _catalog.get("ts") != before:
        _gift_reprice(cats)
        try:
            for (pid, i), old in prev.items():
                if old == "out" and _gstate(pid, i)[0] == "ok":
                    _gift_notify_restock(pid, i)
        except Exception as e:
            print(f"gift restock check failed: {e}")
    return cats


# ============================================================
# ========== ربط API المورّد (VenteBot Reseller): تسليم تلقائي ==========
# ============================================================
VENTE_BASE = os.environ.get("VENTE_BASE_URL", "https://web-production-1c7b1.up.railway.app").rstrip("/")
VENTE_KEY = os.environ.get("VENTE_API_KEY", "").strip()
VENTE_CONF_KEY = "rk:vt:conf"

_VT = {"raw": {}, "etag": {}, "ts": 0.0, "err": None, "tried": 0.0, "lock": threading.Lock()}
_VT_PRODS = {}          # pid ("vt123") -> منتج جاهز للعرض
_VT_CONF = {"ts": 0.0, "data": {}}

VT_TEXTS = {
    "ar": {
        "delivered": "✅ تم تأكيد الدفع!\n\n📦 {product}\n—————————————\n{data}\n—————————————\n🛡️ الضمان: {warranty}\n📌 احتفظ بهذه المعلومات في مكان آمن\n\n🙏 شكراً لشرائك!",
        "warranty_days": "{n} يوم", "no_warranty": "بدون ضمان",
        "warranty_line": "🛡️ الضمان: {w}",
    },
    "en": {
        "delivered": "✅ Payment confirmed!\n\n📦 {product}\n—————————————\n{data}\n—————————————\n🛡️ Warranty: {warranty}\n📌 Keep this information in a safe place\n\n🙏 Thank you for your purchase!",
        "warranty_days": "{n} days", "no_warranty": "No warranty",
        "warranty_line": "🛡️ Warranty: {w}",
    },
    "fr": {
        "delivered": "✅ Paiement confirmé !\n\n📦 {product}\n—————————————\n{data}\n—————————————\n🛡️ Garantie : {warranty}\n📌 Conservez ces informations en lieu sûr\n\n🙏 Merci pour votre achat !",
        "warranty_days": "{n} jours", "no_warranty": "Sans garantie",
        "warranty_line": "🛡️ Garantie : {w}",
    },
}

def _vt_warranty(p, lang):
    tx = VT_TEXTS.get(lang, VT_TEXTS["ar"])
    d = int(p.get("warranty") or 0)
    return tx["warranty_days"].format(n=d) if d > 0 else tx["no_warranty"]

from decimal import ROUND_HALF_UP

# ---------- إعدادات الأدمن (إخفاء/ربط/استبدال) ----------
def _vt_conf():
    if time.time() - _VT_CONF["ts"] < 30:
        return _VT_CONF["data"]
    try:
        data = kv_get_json(VENTE_CONF_KEY) or {}
    except Exception:
        data = _VT_CONF["data"] or {}
    for k in ("hide", "show", "replace", "unreplace"):
        data.setdefault(k, [])
    data.setdefault("link", {})
    _VT_CONF["data"] = data
    _VT_CONF["ts"] = time.time()
    return data

def _vt_conf_save(data):
    kv_set(VENTE_CONF_KEY, json.dumps(data))
    _VT_CONF["data"] = data
    _VT_CONF["ts"] = time.time()

# ---------- الاتصال بالـAPI ----------
class VenteError(Exception):
    pass

def _vt_headers(extra=None):
    h = {"X-Reseller-Key": VENTE_KEY, "Accept": "application/json"}
    if extra:
        h.update(extra)
    return h

def vt_get(path, params=None, headers=None, timeout=20):
    return requests.get(VENTE_BASE + path, headers=_vt_headers(headers), params=params, timeout=timeout)

def vt_order(vid, qty, idem, ref):
    body = {"product_id": int(vid), "quantity": int(qty), "customer_reference": str(ref)[:120], "idempotency_key": str(idem)[:120]}
    try:
        r = requests.post(VENTE_BASE + "/api/reseller/orders",
                          headers=_vt_headers({"Content-Type": "application/json"}), json=body, timeout=45)
    except Exception as e:
        raise VenteError(f"network: {e}")
    try:
        data = r.json()
    except Exception:
        data = {"raw": (r.text or "")[:300]}
    return r.status_code, data, r

def vt_me():
    r = vt_get("/api/reseller/me", timeout=15)
    return r.status_code, (r.json() if r.content else {})

# ---------- تنظيف الأوصاف ----------
_VT_BAD_LINE = re.compile(r"قناة المبيعات|sales channel|canal de ventes|بشكل مجهول|anonymous", re.I)

def _vt_clean(text):
    s = str(text or "")
    for _ in range(2):
        s = html.unescape(s)
    s = re.sub(r"<[^>]*>", "", s)
    s = re.sub(r"Step number background\s*(\d+)", r"\1)", s)
    lines = [ln.rstrip() for ln in s.split("\n")]
    lines = [ln for ln in lines if not _VT_BAD_LINE.search(ln)]
    s = "\n".join(lines)
    s = re.sub(r"[*_`\[\]]", " ", s)
    s = re.sub(r"[ \t]{2,}", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s).strip()
    return s

def _vt_trunc(s, n=700):
    if len(s) <= n:
        return s
    cut = s[:n]
    k = max(cut.rfind("\n"), cut.rfind(" "))
    if k > n * 0.6:
        cut = cut[:k]
    return cut.rstrip() + "…"

_VT_ICONS = [
    ("chatgpt", "🤖"), ("gpt", "🤖"), ("claude", "🧠"), ("codex", "🧠"), ("gemini", "✨"), ("google", "✨"),
    ("capcut", "🎬"), ("canva", "🎨"), ("netflix", "🎞️"), ("prime", "📺"), ("duolingo", "🦉"), ("vpn", "🛡️"),
    ("proton", "🛡️"), ("hma", "🛡️"), ("office", "📎"), ("microsoft", "📎"), ("zoom", "🎥"), ("miro", "🧩"),
    ("quizlet", "📚"), ("scribd", "📚"), ("wordwall", "📚"), ("linear", "📐"), ("autodesk", "📐"),
    ("gamma", "🖼️"), ("ilovepdf", "📄"), ("spotify", "🎵"), ("youtube", "▶️"), ("grok", "⚡"),
    ("iptv", "📡"), ("magic", "🪄"), ("mobbin", "📱"),
]

def _vt_icon(name):
    n = str(name).lower()
    for k, ic in _VT_ICONS:
        if k in n:
            return ic
    return "🛍️"

VT_BRAND_ALIASES = [
    (r"\bprime\b", "prime"), (r"office|microsoft", "microsoft"), (r"nord", "nordvpn"),
    (r"notion", "notion"), (r"n8n", "n8n"), (r"eleven\s*labs", "elevenlabs"),
]
VT_BRAND_TITLES = {"prime": "Prime Video", "microsoft": "Microsoft Office", "nordvpn": "NordVPN", "notion": "Notion",
                   "n8n": "n8n", "elevenlabs": "ElevenLabs", "gemini": "Gemini", "claude": "Claude API"}

def _vt_brand(name):
    n = re.sub(r"[^a-z0-9 ]", " ", str(name).lower())
    if "gemini" in n or "google ai" in n:
        return "gemini"
    if "claude" in n or "codex" in n:
        return "claude"
    for _pat, _b in VT_BRAND_ALIASES:
        if re.search(_pat, n):
            return _b
    tok = n.split()
    return tok[0] if tok else str(name).lower()

_VT_KEEP_WORDS = {"month", "months", "mon", "year", "years", "day", "days", "pro", "plus", "max", "ultra",
                  "business", "team", "edu", "premium", "basic", "standard", "lite", "starter"}
_VT_UNIT_WORDS = {"month", "months", "mon", "year", "years", "day", "days", "m", "y", "d"}

def _vt_short(name):
    tok = str(name).split()
    if not tok:
        return str(name)[:22]
    keep = [tok[0]]
    i = 1
    while i < len(tok):
        w = tok[i]
        wl = w.lower().strip("()")
        if re.fullmatch(r"\d+(?:\.\d+)?(?:m|y|mo|d|gb|tb|x)", wl):
            keep.append(w)
        elif re.fullmatch(r"\d+", wl) and i + 1 < len(tok) and tok[i + 1].lower().strip("()") in _VT_UNIT_WORDS:
            keep.append(w + " " + tok[i + 1])
            i += 1
        elif wl in _VT_KEEP_WORDS:
            keep.append(w)
        i += 1
    s = " ".join(keep)
    if len(keep) <= 1:
        s = str(name)
    return s if len(s) <= 22 else s[:21].rstrip() + "…"

# ---------- جلب الكتالوج وبناء المنتجات ----------
def _vt_eligible(p):
    try:
        if p.get("price_usd") is None:
            return False
        if p.get("api_test"):
            return True          # منتج الاختبار: يظهر للأدمن فقط عبر /vente_test
        if p.get("stock") is None:
            return False
        if p.get("delivery_type") == "stock":
            return True
        if p.get("delivery_type") == "supplier_api":
            return any(re.search(pat, str(p.get("name", "")), re.I) for pat in VENTE_API_OK)
        return False
    except Exception:
        return False

def _vt_hidden(p):
    conf = _vt_conf()
    sid = str(p["id"])
    if sid in [str(x) for x in conf.get("show", [])]:
        return False
    if sid in [str(x) for x in conf.get("hide", [])]:
        return True
    return any(re.search(pat, str(p.get("name", "")), re.I) for pat in VENTE_DEFAULT_HIDE)

def _vt_margin_for(name):
    """نسبة الربح لمنتج المورّد: استثناء بالاسم إن وُجد، وإلا الافتراضية."""
    for pat, pct in VENTE_MARGIN_OVERRIDE:
        if re.search(pat, str(name or ""), re.I):
            return pct
    return VENTE_MARGIN_PCT

def _vt_sell_price(cost, name=None):
    c = Decimal(str(cost))
    s = (c * (Decimal(100) + Decimal(_vt_margin_for(name))) / Decimal(100)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return s if s >= Decimal("0.01") else Decimal("0.01")

def _vt_rebuild():
    ar = {int(p["id"]): p for p in (_VT["raw"].get("ar") or []) if isinstance(p, dict) and "id" in p}
    en = {int(p["id"]): p for p in (_VT["raw"].get("en") or []) if isinstance(p, dict) and "id" in p}
    fr = {int(p["id"]): p for p in (_VT["raw"].get("fr") or []) if isinstance(p, dict) and "id" in p}
    base = ar or en or fr
    out = {}
    for vid, p in base.items():
        try:
            cost = Decimal(str(p.get("price_usd")))
        except Exception:
            continue
        name = str(p.get("name") or ("#" + str(vid))).strip()
        d_ar = _vt_trunc(_vt_clean(p.get("description")))
        d_en = _vt_trunc(_vt_clean((en.get(vid) or p).get("description")))
        d_fr = _vt_trunc(_vt_clean((fr.get(vid) or p).get("description")))
        try:
            stock = int(p.get("stock")) if p.get("stock") is not None else (5 if p.get("api_test") else 0)
        except Exception:
            stock = 0
        out["vt" + str(vid)] = {
            "id": "vt" + str(vid), "vid": vid, "name": name, "price": "$" + str(_vt_sell_price(cost, name)),
            "cost": float(cost), "stock": max(0, stock), "icon": _vt_icon(name),
            "image": p.get("image_url") or None, "description": d_ar,
            "loc": {"en": {"name": name, "description": d_en or d_ar}, "fr": {"name": name, "description": d_fr or d_en or d_ar}},
            "warranty": int(p.get("warranty_days") or 0), "brand": _vt_brand(name),
            "delivery_type": p.get("delivery_type"), "api_test": bool(p.get("api_test")),
            "eligible": _vt_eligible(p), "raw_name": name,
        }
    _old_stock = {k: v.get("stock") for k, v in _VT_PRODS.items()}
    _VT_PRODS.clear()
    _VT_PRODS.update(out)
    # إشعار «أعلمني» لمنتجات المورّد عند رجوع المخزون
    for _k, _v in out.items():
        try:
            if _old_stock.get(_k) == 0 and _v["stock"] > 0:
                _restock_hook(_k, 0, _v["stock"])
        except Exception as e:
            print(f"vt restock hook failed: {e}")
    try:
        _mode_watch()
    except Exception as e:
        print(f"mode_watch hook failed: {e}")

def vt_refresh(force=False):
    """يحدّث الكتالوج (ar/en/fr) مع ETag. يرجع True إذا نجح جلب واحد على الأقل."""
    if not VENTE_KEY:
        return False
    with _VT["lock"]:
        now = time.time()
        if not force and _VT["raw"] and now - _VT["ts"] < VENTE_REFRESH_SECONDS:
            return True
        _VT["tried"] = now
        ok = False
        for lang in ("ar", "en", "fr"):
            try:
                hdr = {}
                et = _VT["etag"].get(lang)
                if et and not force and lang in _VT["raw"]:
                    hdr["If-None-Match"] = et
                r = vt_get("/api/reseller/products", {"lang": lang}, hdr, 20)
                if r.status_code == 304 and lang in _VT["raw"]:
                    ok = True
                    continue
                if r.status_code != 200:
                    raise VenteError(f"http {r.status_code}: {r.text[:200]}")
                data = r.json()
                _VT["raw"][lang] = data.get("products") or []
                _VT["etag"][lang] = r.headers.get("ETag")
                ok = True
            except Exception as e:
                _VT["err"] = str(e)[:300]
                print(f"vente refresh {lang} failed: {e}")
                if re.search(r"http (401|403)", str(e)):
                    monitor_send("🚨 <b>مفتاح VENTE_API_KEY مرفوض (401/403)</b>\nتحقق من المفتاح أو قيود IP.",
                                 key="vt_auth", cooldown=3600)
        if ok:
            _VT["err"] = None
            _VT["ts"] = time.time()
            try:
                _vt_rebuild()
            except Exception as e:
                print(f"vente rebuild failed: {e}")
        else:
            _VT["ts"] = time.time() - max(0, VENTE_REFRESH_SECONDS - 60)  # إعادة المحاولة بعد دقيقة
        return ok

def vt_refresh_loop():
    while True:
        try:
            vt_refresh(force=True)
        except Exception as e:
            print(f"vt_refresh_loop error: {e}")
        time.sleep(VENTE_REFRESH_SECONDS)

def _vt_kick():
    """تحديث غير حاجب إذا كان الكتالوج فارغاً."""
    if VENTE_KEY and not _VT_PRODS and time.time() - _VT["tried"] > 60:
        _VT["tried"] = time.time()
        threading.Thread(target=vt_refresh, kwargs={"force": True}, daemon=True).start()

# ---------- إدارة الظهور ----------
def _vt_link_map():
    m = dict(VENTE_DEFAULT_LINK)
    m.update(_vt_conf().get("link", {}))
    return {k: int(v) for k, v in m.items() if str(v).isdigit() and int(v) > 0}

def _vt_linked_vids():
    return set(_vt_link_map().values())

def _vt_replacing(p):
    """منتج مستبدِل لمنتجك وكل نظائره عند المورّد نفدت: يظهر كـ"نفد" (بدل رجوع منتجك). وإلا يُخفى النافد."""
    pats = [pat for pat in VENTE_REPLACE_DEFAULT.values() if re.search(pat, p["name"], re.I)]
    if not pats:
        return False
    for q in _VT_PRODS.values():
        if q is p or not q.get("eligible") or q.get("api_test") or q["stock"] <= 0:
            continue
        if _vt_hidden({"id": q["vid"], "name": q["name"]}) or q["vid"] in _vt_linked_vids():
            continue
        if any(re.search(pat, q["name"], re.I) for pat in pats):
            return False
    return True

def _vt_listed(p):
    """هل يظهر المنتج للزبائن في القائمة؟"""
    if not p.get("eligible") or p.get("api_test"):
        return False
    raw_p = {"id": p["vid"], "name": p["name"]}
    if _vt_hidden(raw_p) or p["vid"] in _vt_linked_vids():
        return False
    return p["stock"] > 0 or _vt_replacing(p)

def _vt_visible():
    return [p for p in _VT_PRODS.values() if _vt_listed(p)]

def _own_hidden(pid):
    """منتجك الخاص يُخفى إذا حلّ محله منتج من API."""
    if pid in OWN_ALWAYS_HIDDEN:
        return True
    if not VENTE_KEY or not _VT_PRODS:
        return False
    conf = _vt_conf()
    if pid in conf.get("unreplace", []):
        return False
    if pid in conf.get("replace", []):
        return True
    pat = VENTE_REPLACE_DEFAULT.get(pid)
    if not pat:
        return False
    return any(re.search(pat, p["name"], re.I) for p in _vt_visible())

# ---------- find_product / tr يعرفان منتجات API ----------
_find_product_orig = find_product
def find_product(product_id):
    p = _find_product_orig(product_id)
    if p is not None:
        return p
    return _VT_PRODS.get(product_id)

_tr_orig = tr
def tr(item, field, lang):
    loc = item.get("loc") if isinstance(item, dict) else None
    if loc and lang != "ar":
        v = (loc.get(lang) or {}).get(field)
        if v:
            return v
    return _tr_orig(item, field, lang)

def _vt_is_pid(pid):
    return bool(re.fullmatch(r"vt\d+", str(pid)))

def _vt_stock(pid):
    p = _VT_PRODS.get(pid)
    return int(p["stock"]) if p else 0

def _vt_qty(label):
    m = re.search(r"x(\d+)$", str(label))
    return int(m.group(1)) if m else 1

# ---------- أزرار الصفحة الرئيسية: نفس ترتيب متجر المورّد ----------
# كل صف: خلية واحدة (زر طويل) أو خليتان (زران جنب بعض). الخلية = (مفتاح, اسم المجموعة, regex على اسم المنتج).
# إذا طابقت الخلية عدة منتجات صار زر مجموعة يفتح خياراتها. الخلية الفارغة (غير موجود/نافد/مستبعد) تُتخطّى،
# والزوج الذي بقي منه منتج واحد يظهر زراً طويلاً. أي منتج جديد غير مذكور هنا يظهر في آخر القائمة.
VT_LAYOUT = [
    [("gem6", "Gemini Plus 6", r"gemini plus 6 months")],     # زر مستقل في أول القائمة (مطلوب كثيراً)
    [("gem", "Gemini", r"google ai|gemini")],
    [("chatgpt", "ChatGPT", r"chatgpt")],
    [("cap12", "CapCut", r"capcut\s*pro\s*12m")],
    [("cap1", "CapCut", r"capcut\s*pro\s*1m\b"), ("cap6", "CapCut", r"capcut\s*pro\s*6m")],
    [("claude", "Claude API", r"claude"), ("codex", "Codex API", r"codex")],
    [("linear", "Linear", r"linear"), ("mobbin10", "Mobbin", r"mobbin\s*10x")],
    [("nord", "NordVPN", r"nord"), ("proton", "Proton VPN", r"proton")],
    [("magic", "Magic Patterns", r"magic patterns"), ("scribd", "Scribd", r"scribd")],
    [("msoft", "Microsoft Office", r"microsoft|office")],
    [("prime", "Prime Video", r"\bprime\b")],
    [("zoom", "Zoom", r"zoom"), ("miro", "Miro", r"\bmiro\b")],
    [("quizlet", "Quizlet", r"quizlet"), ("wordwall", "Wordwall", r"wordwall")],
    [("duo", "Duolingo", r"duolingo"), ("ilovepdf", "iLovePDF", r"ilovepdf")],
    [("autodesk", "Autodesk", r"autodesk")],
    [("figma", "Figma", r"figma"), ("framer", "Framer", r"framer")],
    [("bolt", "bolt.new", r"bolt\.new")],
    [("jetbrains", "JetBrains", r"jetbrains")],
    [("descript", "Descript", r"descript")],
    [("readwise", "Readwise", r"readwise"), ("fin", "Fin", r"^fin\b")],
    [("speechify", "Speechify", r"speechify"), ("arize", "Arize", r"arize")],
    [("jam", "Jam", r"^jam\b")],
    [("posthog", "Posthog", r"posthog"), ("supercut", "Supercut", r"supercut")],
    [("replit", "Replit", r"replit")],
    [("warp", "Warp", r"^warp")],
    [("customerio", "customer.io", r"customer\.io"), ("granola", "Granola", r"granola")],
    [("n8n", "n8n", r"n8n")],
    [("airtable", "Airtable", r"airtable")],
    [("runway", "Runway", r"runway")],
    [("gamma", "Gamma", r"^gamma")],
    [("mercury", "Mercury", r"mercury")],
    [("stripe", "Stripe", r"stripe")],
    [("resend", "Resend", r"resend")],
    [("wakingup", "Waking Up", r"waking up")],
    [("notion", "Notion", r"notion")],
    [("elevenlabs", "ElevenLabs", r"eleven\s*labs")],
    [("railway", "Railway", r"railway")],
    [("lovable", "Lovable", r"lovable")],
    [("mobbinpro", "Mobbin", r"mobbin")],
    [("applemusic", "Apple Music", r"apple music"), ("youtube", "YouTube Premium", r"youtube")],
    [("surfshark", "Surfshark", r"surfshark")],
    [("elevenreader", "Eleven Reader", r"eleven reader")],
    [("cursor", "Cursor", r"cursor")],
    [("muse", "Muse AI", r"^muse")],
]

VT_SKIP_RENDER = {"prime", "gem6"}              # يُعرض بجانب Netflix في صف خاص
VT_USE_TITLE = {"prime"}                # زر قصير بالعنوان
VT_ALWAYS_GROUP = {"claude", "codex"}   # دائماً زر مجموعة حتى لو بقي خيار واحد

def _vt_pool():
    """كل منتجات المورّد الظاهرة + النافدة (النافد من مجموعة فيها متوفر يبقى داخلها بالأحمر)."""
    pool = {}
    for p in list(_vt_visible()) + list(_vt_oos_all()):
        pool[p["vid"]] = p
    return list(pool.values())

def _vt_cells():
    """يرجع (صفوف الخلايا حسب VT_LAYOUT, باقي المنتجات غير المذكورة).
    الخلية تظهر فقط إن كان فيها منتج متوفر؛ منتجاتها النافدة تبقى داخلها (أحمر)."""
    global _VT_OOSG
    pool = _vt_pool()
    used = set()
    rows = []
    oosg = []
    for row in VT_LAYOUT:
        cells = []
        for key, title, rx in row:
            its = sorted([p for p in pool if p["vid"] not in used and re.search(rx, p["name"], re.I)], key=lambda x: x["cost"])
            used.update(p["vid"] for p in its)
            if any(p["stock"] > 0 for p in its):
                cells.append((key, title, its))
            elif its and (len(its) > 1 or key in VT_ALWAYS_GROUP):
                oosg.append((key, title, its))    # مجموعة نفدت كلها: زر أحمر واحد في الأعلى
        if cells:
            rows.append(cells)
    _VT_OOSG = oosg
    left = [p for p in pool if p["vid"] not in used and p["stock"] > 0]
    return rows, left

_VT_OOSG = []

def _vt_grouped_vids():
    out = set()
    for cells in _vt_cells()[0]:
        for key, title, its in cells:
            if len(its) > 1 or key in VT_ALWAYS_GROUP:
                out.update(p["vid"] for p in its)
    return out

def _vt_price_txt(its):
    pr = [Decimal(p["price"].lstrip("$")) for p in its]
    lo, hi = min(pr), max(pr)
    return f"${lo}" if lo == hi else f"${lo} - ${hi}"

def _vt_cell_button(cell, lang, pair):
    key, title, its = cell
    if len(its) == 1 and key not in VT_ALWAYS_GROUP:
        p = its[0]
        if pair:
            _lbl = title if key in VT_USE_TITLE else _vt_short(p["name"])
            return InlineKeyboardButton(text=f"{p['icon']} {_lbl}", callback_data=f"buy_{p['id']}")
        return _slot_button(p, lang)
    ins =[p for p in its if p["stock"] > 0] or its
    stock = sum(p["stock"] for p in its)
    lo = min(Decimal(p["price"].lstrip("$")) for p in ins)
    text = f"{ins[0]['icon']} {title} | ${lo}+" if pair else f"{ins[0]['icon']} {title} | {_vt_price_txt(ins)} | 📦 {stock}"
    return InlineKeyboardButton(text=text, callback_data=f"vgrp_{key}")

def _vt_oos_items():
    """النافد الذي يظهر منفرداً في الأعلى (ما كان داخل مجموعة فيها متوفر يبقى داخلها)."""
    grouped = _vt_grouped_vids()
    for _k, _t, _its in _VT_OOSG:
        grouped = grouped | {p["vid"] for p in _its}
    return [p for p in _vt_oos_all() if p["vid"] not in grouped]

def _vt_oos_all():
    out = []
    for p in _VT_PRODS.values():
        if not p.get("eligible") or p.get("api_test") or p["stock"] > 0:
            continue
        if _vt_hidden({"id": p["vid"], "name": p["name"]}) or p["vid"] in _vt_linked_vids():
            continue
        out.append(p)
    return sorted(out, key=lambda x: x["name"].lower())

def _vt_add_buttons(markup, lang, oos=None):
    if oos is not None:
        for p in _vt_oos_items():
            oos.append(_oos_button(p, lang))
        for _k, _t, _its in _VT_OOSG:
            oos.append(InlineKeyboardButton(text=f"{_its[0]['icon']} {_t}", callback_data=f"oos_vg_{_k}"))
    rows, left = _vt_cells()
    for cells in rows:
        cells = [c for c in cells if c[0] not in VT_SKIP_RENDER]
        if not cells:
            continue
        if len(cells) == 2:
            markup.row(_vt_cell_button(cells[0], lang, True), _vt_cell_button(cells[1], lang, True))
        else:
            markup.add(_vt_cell_button(cells[0], lang, False))
    for p in left:
        markup.add(_slot_button(p, lang))

def _vt_find_cell(key):
    for cells in _vt_cells()[0]:
        for c in cells:
            if c[0] == key:
                return c
    for c in _VT_OOSG:      # مجموعة نفدت كلها (تُفتح لمعرفة العرض والضغط على «أعلمني»)
        if c[0] == key:
            return c
    return None

def _own_claude_shown():
    """منتجاتك القديمة (Claude API) تُحذف ما دام عند المورّد منتجات Claude. يرجعها /vente_unreplace claude_api"""
    return False      # Claude القديم محذوف نهائياً؛ كل Claude الآن من المورّد

def _vt_back_cb(p):
    for cells in _vt_cells()[0]:
        for key, title, its in cells:
            if (len(its) > 1 or key in VT_ALWAYS_GROUP) and any(x["vid"] == p["vid"] for x in its):
                return f"vgrp_{key}"
    for key, title, its in _VT_OOSG:
        if any(x["vid"] == p["vid"] for x in its):
            return f"vgrp_{key}"
    return "back_to_main"

@bot.callback_query_handler(func=lambda c: c.data.startswith("vgrp_"))
def handle_vente_group(call):
    lang = get_lang(call.from_user.id)
    cell = _vt_find_cell(call.data[5:])
    if not cell or len(cell[2]) < 1:
        bot.answer_callback_query(call.id)
        return
    key, title, items = cell
    _ins = [x for x in items if x["stock"] > 0] or items
    lo = min(Decimal(x["price"].lstrip("$")) for x in _ins)
    hi = max(Decimal(x["price"].lstrip("$")) for x in _ins)
    mk = InlineKeyboardMarkup(row_width=1)
    for p in items:
        _b = _slot_button(p, lang)
        if p["stock"] <= 0:
            _b.callback_data = f"oos_{p['id']}"      # يبقى داخل المجموعة بالأحمر
        mk.add(_b)
    mk.add(InlineKeyboardButton(text=t(lang, "back"), callback_data="back_to_main"))
    _style_store(mk)
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    bot.send_message(call.message.chat.id,
        GROUP_TEXTS.get(lang, GROUP_TEXTS["ar"]).format(name=html.escape(title), lo=f"${lo}", hi=f"${hi}"),
        parse_mode="HTML", reply_markup=mk)
    bot.answer_callback_query(call.id)

# ---------- صفحة المنتج وشراؤه ----------
def _vt_view(call, pid):
    p = _VT_PRODS.get(pid)
    uid = call.from_user.id
    lang = get_lang(uid)
    is_admin = str(uid) == str(ADMIN_CHAT_ID)
    if not p or not p.get("eligible") and not (p and p.get("api_test") and is_admin):
        bot.answer_callback_query(call.id)
        return True
    if p.get("api_test") and not is_admin:
        bot.answer_callback_query(call.id)
        return True
    if call.message.chat.type == "private":
        register_user(uid)
    notify_admin(call.from_user, p, lang)
    gt = GEMINI_TEXTS.get(lang, GEMINI_TEXTS["ar"])
    tx = VT_TEXTS.get(lang, VT_TEXTS["ar"])
    stock = p["stock"]
    mk = InlineKeyboardMarkup(row_width=1)
    if stock > 0:
        sell = Decimal(p["price"].lstrip("$"))
        for q in range(1, min(stock, VENTE_MAX_QTY) + 1):
            total = (sell * q).quantize(Decimal("0.01"))
            mk.add(InlineKeyboardButton(text=f"{q} × | ${total}", callback_data=f"vq_{p['vid']}_{q}"))
        bottom = gt["choose_qty"]
    else:
        bottom = t(lang, "out_of_stock")
        mk.add(InlineKeyboardButton(text=t(lang, "support_btn"), url=MY_PRIVATE_CHAT_LINK))
        mk.add(InlineKeyboardButton(text=t(lang, "notify_me"), callback_data=f"notify_{p['id']}"))
    mk.add(InlineKeyboardButton(text=t(lang, "back"), callback_data=_vt_back_cb(p)))
    caption = (
        f"{t(lang, 'chosen')} *{tr(p, 'name', lang)}*\n"
        f"{t(lang, 'price')} *{p['price']}*\n"
        f"{t(lang, 'available')} *{stock}*\n\n"
        f"{t(lang, 'description')}\n{tr(p, 'description', lang)}\n\n"
        f"{tx['warranty_line'].format(w=_vt_warranty(p, lang))}\n\n{bottom}"
    )
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    send_card(call.message.chat.id, p, caption, mk)
    bot.answer_callback_query(call.id)
    return True

@bot.callback_query_handler(func=lambda c: c.data.startswith("vq_"))
def handle_vente_qty(call):
    uid = call.from_user.id
    lang = get_lang(uid)
    try:
        vid_s, q_s = call.data[3:].rsplit(chr(95), 1)
        pid = "vt" + str(int(vid_s))
        q = int(q_s)
    except Exception:
        bot.answer_callback_query(call.id)
        return
    p = _VT_PRODS.get(pid)
    is_admin = str(uid) == str(ADMIN_CHAT_ID)
    if (not p or not 1 <= q <= VENTE_MAX_QTY or not (p.get("eligible") or (p.get("api_test") and is_admin))
            or (p.get("api_test") and not is_admin)):
        bot.answer_callback_query(call.id)
        return
    if p["stock"] < q:
        bot.answer_callback_query(call.id, t(lang, "out_variant"), show_alert=True)
        return
    price = str((Decimal(p["price"].lstrip("$")) * q).quantize(Decimal("0.01")))
    label = f"x{q}"
    full_name = f"{p['name']} — {label}"
    notify_admin(call.from_user, {"name": full_name, "price": f"${price}"}, lang)
    try:
        invoice_id = create_invoice(uid, pid, label, price, full_name)
    except StorageError:
        bot.answer_callback_query(call.id, t(lang, "temp_error"), show_alert=True)
        return
    invoice = get_invoice(invoice_id) or {"label": label, "price_usdt": price}
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    sent = bot.send_message(
        call.message.chat.id, build_invoice_text(lang, invoice, p), parse_mode="HTML",
        reply_markup=build_invoice_markup(lang, invoice_id, _wallet_covers(uid, invoice.get("price_usdt"))),
    )
    attach_invoice_msg(invoice_id, sent)
    bot.answer_callback_query(call.id)

# ---------- التسليم ----------
def _vt_err_text(data):
    if isinstance(data, dict):
        return f"{data.get('code', '')} {data.get('message', '')} {data.get('raw', '')}".strip()
    return str(data)[:200]

def _fulfill_vente(chat_id, uid, lang, claim, canon, retry, mark, failed, vid=None):
    pid = claim["product_id"]
    if vid is None:
        vid = int(str(pid)[2:])
    qty = _vt_qty(claim.get("label"))
    pname = html.escape(claim.get("product_name") or str(pid))
    price = _to_decimal(claim.get("price"))
    n = int(claim.get("idem_n", 0))
    base_key = f"rk-vt-{canon}" + (f"-{n}" if n else "")
    idem = base_key if len(base_key) <= 110 else "rk-vt-" + hashlib.sha1(base_key.encode()).hexdigest()
    claim["vt"] = vid
    try:
        status, data, resp = vt_order(vid, qty, idem, f"tg{uid}")
    except VenteError as e:
        failed(f"⚠️ <b>فشل الاتصال بالمورّد أثناء الشراء</b>\n\n📦 {pname}\n👤 <code>{uid}</code>\n"
               f"🧾 <code>{html.escape(canon)}</code>\n{html.escape(str(e))[:300]}\n\nالبوت سيعيد المحاولة تلقائياً بنفس المفتاح (آمن ضد التكرار).")
        return

    ok = status == 200 and isinstance(data, dict) and data.get("success") is not False and isinstance(data.get("order"), dict)
    if ok:
        order = data["order"]
        ost = str(order.get("status") or "")
        accts = [str(i.get("account_data")) for i in (order.get("items") or [])
                 if isinstance(i, dict) and i.get("account_data")]
        if ost == "COMPLETED" and accts:
            tx = VT_TEXTS.get(lang, VT_TEXTS["ar"])
            prod = _VT_PRODS.get("vt" + str(vid)) or {}
            data_html = "\n\n".join(f"<code>{html.escape(a)}</code>" for a in accts)
            text = tx["delivered"].format(product=pname, data=data_html, warranty=_vt_warranty(prod, lang))
            delivered_ok = True
            try:
                bot.send_message(chat_id, text, parse_mode="HTML", disable_web_page_preview=True)
            except Exception as e:
                delivered_ok = False
                alert_admin(f"⚠️ <b>تعذر إرسال الحساب للزبون</b> <code>{uid}</code>\n🧾 <code>{html.escape(canon)}</code>\n" + data_html)
                print(f"vente deliver failed: {e}")
            mark("delivered")
            clear_pending(uid)
            record_purchase(uid, pid, claim.get("product_name"), claim.get("price"), canon, via=claim.get("via", "binance"))
            order_log_auto(uid, claim.get("product_name"), claim.get("price"), canon, "\n".join(accts))
            if delivered_ok:
                try:
                    bot.send_message(chat_id, t(lang, "thanks"))
                except Exception as e:
                    print(f"thanks failed: {e}")
            try:
                prod = _VT_PRODS.get("vt" + str(vid))
                if prod:
                    prod["stock"] = max(0, int(prod["stock"]) - qty)
            except Exception:
                pass
            cost = None
            try:
                cost = Decimal(str(data.get("total"))) if data.get("total") is not None else Decimal(str(order.get("amount_usd")))
            except Exception:
                cost = None
            margin = ""
            if cost is not None and price:
                diff = price - cost
                margin = f"\n💹 الربح التقريبي: {diff:.2f}$" + (" ⚠️ خسارة!" if diff < 0 else "")
            profit_log(canon, pid, claim.get("product_name"), price, cost)
            if len(accts) < qty:
                alert_admin(f"⚠️ <b>وصل عدد حسابات أقل من المطلوب</b>\n📦 {pname}\n🧾 <code>{html.escape(canon)}</code>\nمطلوب {qty}، وصل {len(accts)}.")
            alert_admin(
                ("✅ <b>بيع تلقائي من المورّد (بعد إعادة المحاولة)</b>" if retry else "✅ <b>بيع تلقائي من المورّد</b>")
                + f"\n📦 {pname}\n👤 <code>{uid}</code>\n💵 مدفوع: {claim.get('paid')} USDT"
                + (f" | تكلفة: {cost}$" if cost is not None else "") + margin
            )
            monitor_send(f"✅ <b>شراء جديد</b>\n\n📦 {pname}\n👤 {_user_link(uid)}\n💵 {claim.get('paid')} USDT" + margin)
            try:
                bal = data.get("balance_after")
                if bal is not None and Decimal(str(bal)) < Decimal(str(VENTE_LOW_BALANCE)):
                    monitor_send(f"💸 <b>رصيدك عند المورّد منخفض</b>: {bal}$\nاشحن المحفظة (USDT BEP20) لكي لا تتوقف الطلبات.",
                                 key="vt_low_balance", cooldown=3600)
            except Exception:
                pass
            return
        if ost == "CANCELLED":
            claim["idem_n"] = n + 1
            failed(f"🚨 <b>المورّد ألغى الطلب</b>\n📦 {pname}\n👤 <code>{uid}</code>\n🧾 <code>{html.escape(canon)}</code>\n"
                   f"الحالة: {html.escape(ost)}\nسيعاد المحاولة تلقائياً.")
            return
        # قيد التسليم / بانتظار التفعيل: لا نُرجع المال ولا نعيد الشراء (نفس المفتاح يرجع نفس الطلب)
        claim["fz_created"] = True
        failed(f"⚠️ <b>طلب المورّد لم يكتمل بعد</b>\n📦 {pname}\n👤 <code>{uid}</code>\n🧾 <code>{html.escape(canon)}</code>\n"
               f"الحالة: <code>{html.escape(ost)}</code> | رقم الطلب: <code>{html.escape(str(order.get('id')))}</code>\n"
               f"البوت يتابعه تلقائياً ويسلّم عند الاكتمال.")
        return

    err = _vt_err_text(data)
    if status in (401, 403):
        claim["idem_n"] = n + 1
        monitor_send("🚨 <b>مفتاح المورّد مرفوض أثناء شراء</b>\nتحقق من VENTE_API_KEY وقيود IP.", key="vt_auth_order", cooldown=900)
    elif status == 402:
        claim["idem_n"] = n + 1
        monitor_send("🚨 <b>رصيدك عند المورّد غير كافٍ!</b>\nاشحن المحفظة (USDT BEP20)، والبوت يكمل الطلبات المعلّقة وحده.\n"
                     f"<code>{html.escape(err)[:200]}</code>", key="vt_balance", cooldown=1800)
    elif status in (400, 404, 409, 422):
        claim["idem_n"] = n + 1   # رفض واضح: لم يُنشأ طلب
    # 429 و5xx و غيرها: نفس المفتاح في المحاولة القادمة
    wait = ""
    try:
        if status == 429:
            wait = f"\nانتظر {resp.headers.get('Retry-After', '?')} ثانية."
    except Exception:
        pass
    failed(f"🚨 <b>فشل شراء من المورّد</b> (HTTP {status})\n📦 {pname}\n👤 <code>{uid}</code>\n"
           f"🧾 <code>{html.escape(canon)}</code>\n{html.escape(err)[:300]}{wait}")

# ---------- Gemini: مخزونك أولاً ثم المورّد ----------
_gemini_stock_orig = gemini_stock
_gemini_unit_price_orig = gemini_unit_price
_sync_stock_orig = sync_stock

def _gem_vid():
    if not VENTE_KEY:
        return None
    return _vt_link_map().get(GEMINI_ID)

def _gem_vprod():
    vid = _gem_vid()
    return _VT_PRODS.get(f"vt{vid}") if vid else None

def gemini_stock():
    own = _gemini_stock_orig()
    if own > 0:
        return own
    vp = _gem_vprod()
    return max(0, int(vp["stock"])) if vp else own

def gemini_unit_price():
    if _gemini_stock_orig() <= 0:
        vp = _gem_vprod()
        if vp:
            return _to_decimal(vp["price"].lstrip("$"))
    return _gemini_unit_price_orig()

def sync_stock():
    _sync_stock_orig()
    p = _find_product_orig(GEMINI_ID)
    if p and _gemini_stock_orig() <= 0:
        vp = _gem_vprod()
        if vp:
            p["price"] = vp["price"]

def _gem_use_vente(claim):
    if claim.get("vt"):
        return True
    if not _gem_vid():
        return False
    try:
        n = int(str(claim.get("label", "x1")).lstrip("x"))
    except ValueError:
        n = 1
    return _gemini_stock_orig() < n

# ---------- أوامر الأدمن ----------
def _vt_need_key(message):
    if not VENTE_KEY:
        bot.reply_to(message, "⚠️ لم يُضبط VENTE_API_KEY في Render بعد.")
        return False
    return True

def _own_similar(name):
    b = _vt_brand(name)
    hits = []
    for p in products:
        if p.get("type") == "separator" or str(p.get("id", "")).startswith("vt"):
            continue
        low = (str(p.get("name", "")) + " " + str(p.get("id", ""))).lower()
        if b and len(b) >= 4 and b in low:
            hits.append(p["id"])
    return hits[:3]

@bot.message_handler(commands=["vente_buytest"])
def vente_buytest_command(message):
    """للأدمن فقط: شراء تجريبي واحد (كمية 1) من المورّد لرؤية الرد الحقيقي، خاصة لمنتجات supplier_api.
    يخصم من رصيدك عند المورّد ويُرسل لك الرد كما هو. حد أقصى للتكلفة 1.00$ لتفادي الأخطاء."""
    if not is_admin_msg(message) or not _vt_need_key(message):
        return
    parts = (message.text or "").split()
    if len(parts) != 2 or not parts[1].isdigit():
        bot.reply_to(message, "الاستخدام: /vente_buytest رقم_المنتج_عند_المورد\nمثال: /vente_buytest 121\n(شراء حقيقي بكمية 1، حد أقصى للتكلفة 1.00$)")
        return
    vid = int(parts[1])
    if not _VT_PRODS:
        vt_refresh(force=True)
    p = _VT_PRODS.get("vt" + str(vid))
    if not p:
        bot.reply_to(message, "❌ هذا الرقم غير موجود في الكتالوج.")
        return
    if Decimal(str(p["cost"])) > Decimal("1.00"):
        bot.reply_to(message, f"❌ تكلفته {p['cost']}$ أكبر من حد الاختبار 1.00$. لم أشترِ شيئاً.")
        return
    if p["stock"] <= 0:
        bot.reply_to(message, "❌ مخزونه صفر عند المورّد. لم أشترِ شيئاً.")
        return
    idem = f"test-{vid}-{int(time.time())}"
    bot.reply_to(message, f"⏳ شراء تجريبي: {html.escape(p['name'])} (تكلفة {p['cost']}$)...")
    try:
        code, data, _r = vt_order(vid, 1, idem, f"admin_test_{message.from_user.id}")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ فشل الاتصال: {html.escape(str(e))[:300]}")
        return
    out = json.dumps(data, ensure_ascii=False, indent=1)[:3300]
    bot.send_message(message.chat.id, f"HTTP {code}\n<pre>{html.escape(out)}</pre>", parse_mode="HTML")
    try:
        oid = (data.get("order") or data).get("id") if isinstance(data, dict) else None
        if oid:
            time.sleep(6)
            r2 = vt_get(f"/api/reseller/orders/{oid}", timeout=20)
            out2 = json.dumps(r2.json(), ensure_ascii=False, indent=1)[:3300]
            bot.send_message(message.chat.id, f"📋 حالة الطلب بعد 6 ثوانٍ (HTTP {r2.status_code})\n<pre>{html.escape(out2)}</pre>", parse_mode="HTML")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ تعذر قراءة حالة الطلب: {html.escape(str(e))[:200]}")

@bot.message_handler(commands=["vente_catalog"])
def vente_catalog_command(message):
    if not is_admin_msg(message) or not _vt_need_key(message):
        return
    if not vt_refresh(force=True) and not _VT_PRODS:
        bot.reply_to(message, f"❌ تعذر جلب الكتالوج: {html.escape(str(_VT['err']))[:300]}")
        return
    parts = (message.text or "").split(maxsplit=1)
    q = parts[1].strip().lower() if len(parts) == 2 else ""
    conf = _vt_conf()
    linked = {v: k for k, v in _vt_link_map().items()}
    lines = [f"📦 كتالوج المورّد: {len(_VT_PRODS)} منتج | ربح {VENTE_MARGIN_PCT}%",
             "✅ معروض | 🙈 مخفي | ⛔ غير تلقائي (يحتاج بيانات/مورّد) | 🔗 مربوط | ❌ مخزون 0", ""]
    for p in sorted(_VT_PRODS.values(), key=lambda x: (x["brand"], x["cost"])):
        if q and q not in p["name"].lower() and q not in str(p["vid"]):
            continue
        raw_p = {"id": p["vid"], "name": p["name"]}
        if p["vid"] in linked:
            flag = f"🔗 {linked[p['vid']]}"
        elif p.get("api_test"):
            flag = "🧪"
        elif not p["eligible"]:
            flag = "⛔"
        elif _vt_hidden(raw_p):
            flag = "🙈"
        elif p["stock"] <= 0:
            flag = "❌"
        else:
            flag = "✅"
        sim = _own_similar(p["name"])
        extra = f" ≈ {','.join(sim)}" if sim else ""
        sell = p["price"]
        lines.append(f"{flag} {p['vid']} | {p['name'][:42]} | {p['cost']:.2f}→{sell} | 📦{p['stock']} | {p['delivery_type']} | 🛡️{p['warranty']}{extra}")
    send_long(message.chat.id, "\n".join(lines))

def _vt_arg_id(message):
    parts = (message.text or "").split()
    if len(parts) < 2 or not parts[1].isdigit():
        return None
    return int(parts[1])

@bot.message_handler(commands=["vente_hide", "vente_show"])
def vente_hide_show_command(message):
    if not is_admin_msg(message):
        return
    vid = _vt_arg_id(message)
    if vid is None:
        bot.reply_to(message, "الاستعمال: /vente_hide ID   أو   /vente_show ID  (ID من /vente_catalog)")
        return
    cmd = (message.text or "").split()[0].lstrip("/").split("@")[0]
    conf = dict(_vt_conf())
    hide = [x for x in conf.get("hide", []) if str(x) != str(vid)]
    show = [x for x in conf.get("show", []) if str(x) != str(vid)]
    if cmd == "vente_hide":
        hide.append(vid)
    else:
        show.append(vid)
    conf["hide"], conf["show"] = hide, show
    _vt_conf_save(conf)
    bot.reply_to(message, "🙈 تم إخفاؤه." if cmd == "vente_hide" else "👁️ تم إظهاره.")

@bot.message_handler(commands=["vente_link", "vente_unlink"])
def vente_link_command(message):
    if not is_admin_msg(message):
        return
    parts = (message.text or "").split()
    cmd = parts[0].lstrip("/").split("@")[0]
    conf = dict(_vt_conf())
    link = dict(conf.get("link", {}))
    if cmd == "vente_unlink":
        if len(parts) < 2:
            bot.reply_to(message, "الاستعمال: /vente_unlink gemini_18m")
            return
        link[parts[1]] = 0     # 0 = ملغى (يتجاوز الربط الافتراضي)
        conf["link"] = link
        _vt_conf_save(conf)
        bot.reply_to(message, "🔓 تم فك الربط.")
        return
    if len(parts) < 3 or not parts[2].isdigit() or not _find_product_orig(parts[1]):
        bot.reply_to(message, "الاستعمال: /vente_link gemini_18m ID  (منتجك الخاص ثم رقم المنتج عند المورّد). يعمل مع Gemini فقط حالياً.")
        return
    if parts[1] != GEMINI_ID:
        bot.reply_to(message, "الربط (مخزونك أولاً ثم المورّد) مفعّل لـ Gemini فقط. لباقي المنتجات استعمل /vente_replace.")
        return
    link[parts[1]] = int(parts[2])
    conf["link"] = link
    _vt_conf_save(conf)
    bot.reply_to(message, f"🔗 تم: {parts[1]} ← {parts[2]}. يبيع من مخزونك، وعند نفاده يشتري من المورّد.")

@bot.message_handler(commands=["vente_replace", "vente_unreplace"])
def vente_replace_command(message):
    if not is_admin_msg(message):
        return
    parts = (message.text or "").split()
    cmd = parts[0].lstrip("/").split("@")[0]
    if len(parts) < 2 or not _find_product_orig(parts[1]):
        bot.reply_to(message, "الاستعمال: /vente_replace own_id  (يخفي منتجك ويبقى منتج المورّد)\nأو /vente_unreplace own_id")
        return
    conf = dict(_vt_conf())
    rep = [x for x in conf.get("replace", []) if x != parts[1]]
    unrep = [x for x in conf.get("unreplace", []) if x != parts[1]]
    if cmd == "vente_replace":
        rep.append(parts[1])
    else:
        unrep.append(parts[1])
    conf["replace"], conf["unreplace"] = rep, unrep
    _vt_conf_save(conf)
    bot.reply_to(message, "✅ تم." )

def _has_custom_emoji(message):
    try:
        if not is_admin_msg(message):
            return False
        # أثناء كتابة بيانات تسليم طلب: لا تبتلع الرسالة (قد تحمل إيموجي مميز منسوخ من بوت المورّد)
        _w = _adm_wait.get(message.from_user.id)
        if _w and _w.get("op") == "deliver":
            return False
        ents = (message.entities or []) + (message.caption_entities or [])
        return any(getattr(e, "type", "") == "custom_emoji" for e in ents)
    except Exception:
        return False

@bot.message_handler(func=_has_custom_emoji, content_types=["text", "photo", "video", "document"])
def custom_emoji_ids_handler(message):
    """Admin: send a message containing custom emojis -> bot replies with their IDs."""
    ents = (message.entities or []) + (message.caption_entities or [])
    txt = message.text or message.caption or ""
    lines = []
    seen = set()
    for e in ents:
        if getattr(e, "type", "") != "custom_emoji":
            continue
        cid = str(getattr(e, "custom_emoji_id", "") or "")
        if not cid or cid in seen:
            continue
        seen.add(cid)
        try:
            u16 = txt.encode("utf-16-le")
            ch = u16[e.offset * 2:(e.offset + e.length) * 2].decode("utf-16-le")
        except Exception:
            ch = "•"
        lines.append(f"{ch} <code>{cid}</code>")
    bot.reply_to(message, "🆔 معرّفات الإيموجي:\n\n" + "\n".join(lines), parse_mode="HTML")

# يتقدم على معالجات «بانتظار إيميل/مبلغ...» حتى لا تبتلع رسالة الإيموجي
try:
    bot.message_handlers.insert(0, bot.message_handlers.pop())
except Exception as _e:
    print(f"emoji handler priority failed: {_e}")

@bot.message_handler(commands=["vente_balance"])
def vente_balance_command(message):
    if not is_admin_msg(message) or not _vt_need_key(message):
        return
    try:
        st, d = vt_me()
    except Exception as e:
        bot.reply_to(message, f"❌ {html.escape(str(e))[:300]}")
        return
    if st != 200:
        bot.reply_to(message, f"❌ HTTP {st}: {html.escape(_vt_err_text(d))[:300]}")
        return
    bot.reply_to(message, f"✅ الاتصال يعمل\n💰 رصيدك عند المورّد: {d.get('wallet_balance')}$\n🔑 {html.escape(str(d.get('key_name')))}")

@bot.message_handler(commands=["vente_test"])
def vente_test_command(message):
    if not is_admin_msg(message) or not _vt_need_key(message):
        return
    vt_refresh(force=True)
    tests = [p for p in _VT_PRODS.values() if p.get("api_test")]
    if not tests:
        bot.reply_to(message, "لا يوجد منتج اختبار في الكتالوج.")
        return
    mk = InlineKeyboardMarkup(row_width=1)
    for p in tests:
        mk.add(InlineKeyboardButton(text=f"🧪 {p['name']} | {p['price']}", callback_data=f"buy_{p['id']}"))
    bot.send_message(message.chat.id, "🧪 منتج اختبار API (يظهر لك أنت فقط):", reply_markup=mk)


@bot.callback_query_handler(func=lambda c: c.data.startswith("grp_"))
def handle_store_group(call):
    gid = call.data[4:]
    g = STORE_GROUPS.get(gid)
    if not g:
        bot.answer_callback_query(call.id)
        return
    lang = get_lang(call.from_user.id)
    sync_stock()
    lo, hi, _ = _group_range(gid)
    mk = InlineKeyboardMarkup(row_width=1)
    for pid in g["members"]:
        item = find_product(pid)
        if item:
            _b = _slot_button(item, lang)
            if _own_oos(item):
                _b.callback_data = f"oos_{item['id']}"   # يبقى داخل المجموعة بالأحمر
            mk.add(_b)
    mk.add(InlineKeyboardButton(text=t(lang, "back"), callback_data="back_to_main"))
    _style_store(mk)
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    bot.send_message(
        call.message.chat.id,
        GROUP_TEXTS.get(lang, GROUP_TEXTS["ar"]).format(name=html.escape(g["name"]), lo=lo, hi=hi),
        parse_mode="HTML", reply_markup=mk,
    )
    bot.answer_callback_query(call.id)


def _fix_group_back(pid, markup):
    """زر الرجوع في صفحة منتج تابع لمجموعة يرجع لصفحة المجموعة بدل القائمة الرئيسية."""
    for gid, g in STORE_GROUPS.items():
        if pid in g["members"]:
            for row in markup.keyboard:
                for btn in row:
                    if getattr(btn, "callback_data", None) == "back_to_main":
                        btn.callback_data = f"grp_{gid}"
            break
    return markup


# ============================================================
# ========== طرق الدفع: بريدي موب + Flixy (+ RedotPay/Bybit قريباً) ==========
# ============================================================
from decimal import ROUND_CEILING, ROUND_DOWN

SEP = chr(95)
BARIDI_RIP = "00799999002013573542"
FLEXY_NUMBER = "0699177640"
PM_DEFAULT_RATE = {"bd": Decimal("260"), "fx": Decimal("317.20")}
PM_ICON = {"bd": "🏦", "fx": "📱"}
PM_NAME = {
    "bd": {"ar": "بريدي موب", "en": "Baridimob", "fr": "Baridimob"},
    "fx": {"ar": "Flixy", "en": "Flixy", "fr": "Flixy"},
}

SOON_NAME = {"rp": "RedotPay", "bb": "Bybit"}
ALL_M = ("bd", "fx", "rp", "bb")

def _mname(m, lang):
    if m in PM_NAME:
        return PM_NAME[m][lang]
    return SOON_NAME.get(m, m)

PM_TEXTS = {
    "ar": {
        "pick_buy": "🛒 <b>طلب جديد</b>\n\n📦 {product}\n💵 المجموع: <b>{amount}$</b>\n\n💳 اختر طريقة الدفع:",
        "pick_topup": "➕ <b>شحن المحفظة</b>\n\n💳 اختر طريقة الدفع:",
        "btn_wallet": "💼 المحفظة (${bal})",
        "btn_binance": "الدفع عبر Binance",
        "btn_bd": "بريدي موب",
        "btn_fx": "Flixy +22%",
        "soon": "🔄 جاري التحديث، ستتوفر هذه الطريقة قريباً",
        "btn_chat": "💬 الشراء عبر الدردشة مع فريق الدعم",
        "notify_upd": "🔔 أعلمني عند التحديث",
        "full": "⛔ دفعات {method} ممتلئة مؤقتاً.\n\nيمكنك اختيار طريقة دفع أخرى، أو الضغط على الزر أدناه ليتم إعلامك عند توفرها.",
        "nt_ok": "✅ تم تسجيلك! سنعلمك فور توفر الدفع عبر {method}.",
        "avail": "✅ الدفع عبر <b>{method}</b> متاح الآن! 🛍️",
        "copy_bd": "📋 نسخ الـ RIP",
        "copy_fx": "📋 نسخ الرقم",
        "pay_bd": "🏦 <b>الدفع عبر بريدي موب</b>\n\n📦 {what}\n💵 السعر: <b>{usd}$</b>\n\n💱 سعر الصرف: 1$ = {rate} DA\n🧮 الحساب: {usd}$ × {rate} = <b>{da} DA</b>\n✅ المبلغ الواجب دفعه: <b>{da} DA</b>\n\n📋 الـ RIP:\n<code>{dest}</code>\n\n1️⃣ اضغط على زر «نسخ الـ RIP» أدناه وحوّل المبلغ\n2️⃣ ابعث هنا في الشات <b>لقطة شاشة</b> لوصل التحويل\n3️⃣ {after}",
        "pay_fx": "📱 <b>الدفع عبر Flixy</b>\n\n📦 {what}\n💵 السعر: <b>{usd}$</b>\n\n💱 سعر الصرف: 1$ = {rate} DA (يشمل رسوم +22%)\n🧮 الحساب: {usd}$ × {rate} = <b>{da} DA</b>\n✅ المبلغ الواجب إرساله: <b>{da} DA</b>\n\n📞 الرقم:\n<code>{dest}</code>\n\n1️⃣ اضغط على زر «نسخ الرقم» أدناه وأرسل الفليكسي بالمبلغ أعلاه\n2️⃣ ابعث هنا في الشات رسالة بهذا الشكل:\n<code>فليكسي\nالمبلغ : {da}Da\nالوقت : 12:33</code>\n3️⃣ {after}",
        "after_buy": "سيتم التحقق وإضافة الرصيد لمحفظتك في أقرب وقت، ثم ادخل المنتج واختر الدفع بالمحفظة 🛍️",
        "after_topup": "سيتم التحقق وإضافة الرصيد لمحفظتك في أقرب وقت 💼",
        "topup_amounts": "➕ <b>شحن المحفظة — {method}</b>\n\n💱 سعر الصرف: 1$ = {rate} DA\nاختر المبلغ:",
        "proof_ok": "✅ تم استلام الوصل. سيتم التحقق وإضافة الرصيد في أقرب وقت، وسيصلك إشعار هنا.",
        "proof_dup": "ℹ️ وصلك قيد المراجعة، يرجى الانتظار.",
        "proof_hint_bd": "📸 ابعث <b>لقطة شاشة</b> لوصل التحويل.",
        "proof_hint_fx": "✉️ ابعث رسالة نصية بهذا الشكل (يجب أن تحتوي على المبلغ والوقت):\n<code>فليكسي\nالمبلغ : 1000Da\nالوقت : 12:33</code>",
        "busy": "ℹ️ لديك دفعة قيد المراجعة بالفعل. انتظر تأكيدها قبل بدء دفعة جديدة.",
        "approved": "✅ <b>تم شحن رصيدك في محفظتك بنجاح!</b>\n\n💵 +{amount}$\n💼 الرصيد المتاح: <b>${avail}</b>\n\n🛍️ يمكنك الآن اختيار منتجك والدفع من المحفظة.",
        "rejected": "❌ <b>دفعة خاطئة</b>\n\nلم نتمكن من التحقق من دفعتك. إذا كنت تعتقد أن هذا خطأ، تواصل مع الدعم.",
    },
    "en": {
        "pick_buy": "🛒 <b>New order</b>\n\n📦 {product}\n💵 Total: <b>{amount}$</b>\n\n💳 Choose a payment method:",
        "pick_topup": "➕ <b>Top up wallet</b>\n\n💳 Choose a payment method:",
        "btn_wallet": "💼 Wallet (${bal})",
        "btn_binance": "Pay with Binance",
        "btn_bd": "Baridimob",
        "btn_fx": "Flixy +22%",
        "soon": "🔄 Updating, this method will be available soon",
        "btn_chat": "💬 Buy via chat with our support team",
        "notify_upd": "🔔 Notify me when updated",
        "full": "⛔ {method} payments are temporarily full.\n\nYou can choose another payment method, or tap the button below to be notified when it is available again.",
        "nt_ok": "✅ Registered! We'll notify you as soon as {method} payments are available.",
        "avail": "✅ Payment via <b>{method}</b> is available now! 🛍️",
        "copy_bd": "📋 Copy RIP",
        "copy_fx": "📋 Copy number",
        "pay_bd": "🏦 <b>Pay with Baridimob</b>\n\n📦 {what}\n💵 Price: <b>{usd}$</b>\n\n💱 Exchange rate: 1$ = {rate} DA\n🧮 Calculation: {usd}$ × {rate} = <b>{da} DA</b>\n✅ Amount to pay: <b>{da} DA</b>\n\n📋 RIP:\n<code>{dest}</code>\n\n1️⃣ Tap the «Copy RIP» button below and transfer the amount\n2️⃣ Send a <b>screenshot</b> of the transfer receipt here in the chat\n3️⃣ {after}",
        "pay_fx": "📱 <b>Pay with Flixy</b>\n\n📦 {what}\n💵 Price: <b>{usd}$</b>\n\n💱 Exchange rate: 1$ = {rate} DA (includes the +22% fee)\n🧮 Calculation: {usd}$ × {rate} = <b>{da} DA</b>\n✅ Amount to send: <b>{da} DA</b>\n\n📞 Number:\n<code>{dest}</code>\n\n1️⃣ Tap the «Copy number» button below and send the Flexy top-up with the amount above\n2️⃣ Send a message here in the chat in this format:\n<code>Flexy\nAmount : {da}Da\nTime : 12:33</code>\n3️⃣ {after}",
        "after_buy": "We will verify and add the balance to your wallet as soon as possible, then open the product and choose wallet payment 🛍️",
        "after_topup": "We will verify and add the balance to your wallet as soon as possible 💼",
        "topup_amounts": "➕ <b>Top up wallet — {method}</b>\n\n💱 Exchange rate: 1$ = {rate} DA\nChoose the amount:",
        "proof_ok": "✅ Receipt received. We will verify and add the balance as soon as possible, and you will get a notification here.",
        "proof_dup": "ℹ️ Your receipt is under review, please wait.",
        "proof_hint_bd": "📸 Please send a <b>screenshot</b> of the transfer receipt.",
        "proof_hint_fx": "✉️ Send a text message in this format (it must contain the amount and the time):\n<code>Flexy\nAmount : 1000Da\nTime : 12:33</code>",
        "busy": "ℹ️ You already have a payment under review. Wait for its confirmation before starting a new one.",
        "approved": "✅ <b>Your wallet has been topped up successfully!</b>\n\n💵 +{amount}$\n💼 Available balance: <b>${avail}</b>\n\n🛍️ You can now pick your product and pay from the wallet.",
        "rejected": "❌ <b>Incorrect payment</b>\n\nWe couldn't verify your payment. If you think this is a mistake, contact support.",
    },
    "fr": {
        "pick_buy": "🛒 <b>Nouvelle commande</b>\n\n📦 {product}\n💵 Total : <b>{amount}$</b>\n\n💳 Choisissez un mode de paiement :",
        "pick_topup": "➕ <b>Recharger le portefeuille</b>\n\n💳 Choisissez un mode de paiement :",
        "btn_wallet": "💼 Portefeuille (${bal})",
        "btn_binance": "Payer avec Binance",
        "btn_bd": "Baridimob",
        "btn_fx": "Flixy +22%",
        "soon": "🔄 Mise à jour en cours, ce mode de paiement sera bientôt disponible",
        "btn_chat": "💬 Acheter via le chat avec l'équipe d'assistance",
        "notify_upd": "🔔 M'avertir de la mise à jour",
        "full": "⛔ Les paiements {method} sont temporairement complets.\n\nVous pouvez choisir un autre mode de paiement, ou appuyer sur le bouton ci-dessous pour être averti dès qu'il sera de nouveau disponible.",
        "nt_ok": "✅ Enregistré ! Nous vous préviendrons dès que le paiement {method} sera disponible.",
        "avail": "✅ Le paiement via <b>{method}</b> est disponible ! 🛍️",
        "copy_bd": "📋 Copier le RIP",
        "copy_fx": "📋 Copier le numéro",
        "pay_bd": "🏦 <b>Paiement via Baridimob</b>\n\n📦 {what}\n💵 Prix : <b>{usd}$</b>\n\n💱 Taux de change : 1$ = {rate} DA\n🧮 Calcul : {usd}$ × {rate} = <b>{da} DA</b>\n✅ Montant à payer : <b>{da} DA</b>\n\n📋 RIP :\n<code>{dest}</code>\n\n1️⃣ Appuyez sur le bouton « Copier le RIP » ci-dessous et effectuez le virement\n2️⃣ Envoyez ici dans le chat une <b>capture d'écran</b> du reçu\n3️⃣ {after}",
        "pay_fx": "📱 <b>Paiement via Flixy</b>\n\n📦 {what}\n💵 Prix : <b>{usd}$</b>\n\n💱 Taux de change : 1$ = {rate} DA (frais +22% inclus)\n🧮 Calcul : {usd}$ × {rate} = <b>{da} DA</b>\n✅ Montant à envoyer : <b>{da} DA</b>\n\n📞 Numéro :\n<code>{dest}</code>\n\n1️⃣ Appuyez sur le bouton « Copier le numéro » ci-dessous et envoyez le Flexy avec le montant ci-dessus\n2️⃣ Envoyez ici dans le chat un message sous cette forme :\n<code>Flexy\nMontant : {da}Da\nHeure : 12:33</code>\n3️⃣ {after}",
        "after_buy": "Nous vérifierons et ajouterons le solde à votre portefeuille dans les meilleurs délais, puis ouvrez le produit et choisissez le paiement par portefeuille 🛍️",
        "after_topup": "Nous vérifierons et ajouterons le solde à votre portefeuille dans les meilleurs délais 💼",
        "topup_amounts": "➕ <b>Recharger le portefeuille — {method}</b>\n\n💱 Taux de change : 1$ = {rate} DA\nChoisissez le montant :",
        "proof_ok": "✅ Reçu reçu. Nous vérifierons et ajouterons le solde dans les meilleurs délais, vous recevrez une notification ici.",
        "proof_dup": "ℹ️ Votre reçu est en cours de vérification, veuillez patienter.",
        "proof_hint_bd": "📸 Envoyez une <b>capture d'écran</b> du reçu de virement.",
        "proof_hint_fx": "✉️ Envoyez un message texte sous cette forme (il doit contenir le montant et l'heure) :\n<code>Flexy\nMontant : 1000Da\nHeure : 12:33</code>",
        "busy": "ℹ️ Vous avez déjà un paiement en cours de vérification. Attendez sa confirmation avant d'en démarrer un nouveau.",
        "approved": "✅ <b>Votre portefeuille a été rechargé avec succès !</b>\n\n💵 +{amount}$\n💼 Solde disponible : <b>${avail}</b>\n\n🛍️ Vous pouvez maintenant choisir votre produit et payer avec le portefeuille.",
        "rejected": "❌ <b>Paiement incorrect</b>\n\nNous n'avons pas pu vérifier votre paiement. Si vous pensez qu'il s'agit d'une erreur, contactez l'assistance.",
    },
}

def pmt(lang, key):
    return PM_TEXTS.get(lang, PM_TEXTS["ar"])[key]

# ============================================================
# ========== RedotPay (دفع حقيقي بالعملات الرقمية) ==========
# ============================================================
RDP_SANDBOX = (os.getenv("REDOTPAY_SANDBOX") or "1").strip() != "0"
RDP_BASE = (os.getenv("REDOTPAY_BASE_URL")
            or ("https://acquirersandbox.rp-2023app.com" if RDP_SANDBOX else "https://acquirer.redotpay.com")).rstrip("/")
RDP_APP_KEY = (os.getenv("REDOTPAY_APP_KEY") or "").strip()
RDP_PRIV_RAW = (os.getenv("REDOTPAY_PRIVATE_KEY") or "").strip()
RDP_PUB_RAW = (os.getenv("REDOTPAY_PLATFORM_PUBKEY") or "").strip()
RDP_KEY_VERSION = (os.getenv("REDOTPAY_KEY_VERSION") or "1").strip()
RDP_ORDER_MINUTES = 30
RDP_URI_CREATE = "/openapi/v2/order/create"

PM_TEXTS["ar"].update({
    "rdp_link": "💳 <b>الدفع عبر RedotPay</b>\n\n📦 {what}\n💵 المبلغ: <b>{usd}$</b>\n\nاضغط الزر أدناه لإتمام الدفع بالعملات الرقمية.\n⏳ الرابط صالح لمدة 30 دقيقة.\n{cash}\n✅ بعد نجاح الدفع يصلك طلبك تلقائياً هنا.",
    "rdp_cash": "\n⚠️ بسبب رسوم RedotPay، الكاش باك عند الدفع بها هو <b>{pct}%</b>.\n",
    "rdp_open": "💳 ادفع الآن عبر RedotPay",
    "rdp_fail": "⚠️ تعذّر إنشاء رابط الدفع الآن. حاول بعد قليل أو اختر طريقة دفع أخرى.",
    "rdp_amounts": "➕ <b>شحن المحفظة — RedotPay</b>\n\nاختر المبلغ:",
    "rdp_paid_topup": "✅ وصلت دفعتك عبر RedotPay.",
})
PM_TEXTS["en"].update({
    "rdp_link": "💳 <b>Pay with RedotPay</b>\n\n📦 {what}\n💵 Amount: <b>{usd}$</b>\n\nTap the button below to pay with crypto.\n⏳ The link is valid for 30 minutes.\n{cash}\n✅ Once the payment succeeds your order arrives here automatically.",
    "rdp_cash": "\n⚠️ Because of RedotPay fees, the cashback when paying with it is <b>{pct}%</b>.\n",
    "rdp_open": "💳 Pay now with RedotPay",
    "rdp_fail": "⚠️ Could not create the payment link right now. Try again shortly or choose another payment method.",
    "rdp_amounts": "➕ <b>Top up wallet — RedotPay</b>\n\nChoose the amount:",
    "rdp_paid_topup": "✅ Your RedotPay payment was received.",
})
PM_TEXTS["fr"].update({
    "rdp_link": "💳 <b>Paiement via RedotPay</b>\n\n📦 {what}\n💵 Montant : <b>{usd}$</b>\n\nAppuyez sur le bouton ci-dessous pour payer en crypto.\n⏳ Le lien est valable 30 minutes.\n{cash}\n✅ Une fois le paiement réussi, votre commande arrive automatiquement ici.",
    "rdp_cash": "\n⚠️ En raison des frais RedotPay, le cashback en payant avec ce mode est de <b>{pct}%</b>.\n",
    "rdp_open": "💳 Payer maintenant avec RedotPay",
    "rdp_fail": "⚠️ Impossible de créer le lien de paiement pour le moment. Réessayez bientôt ou choisissez un autre mode de paiement.",
    "rdp_amounts": "➕ <b>Recharger le portefeuille — RedotPay</b>\n\nChoisissez le montant :",
    "rdp_paid_topup": "✅ Votre paiement RedotPay a été reçu.",
})

PM_NAME["rd"] = {"ar": "RedotPay (يدوي)", "en": "RedotPay", "fr": "RedotPay"}
PM_ICON["rd"] = "💳"
PM_DEFAULT_RATE["rd"] = Decimal("1")   # بالدولار مباشرة
RDP_MANUAL_ID = REDOTPAY_ID
PM_TEXTS["ar"].update({
    "copy_rd": "📋 نسخ المعرّف",
    "pay_rd": "💳 <b>الدفع عبر RedotPay</b>\n\n📦 {what}\n💵 المبلغ: <b>{usd}$</b>\n\n1️⃣ افتح تطبيق RedotPay وحوّل <b>{usd}$</b> إلى المعرّف التالي:\n<code>{dest}</code>\n⚠️ تأكد أن المبلغ الواصل هو <b>{usd}$</b> بالضبط.\n\n2️⃣ بعد التحويل ابعث هنا <b>لقطة شاشة</b> للتحويل.\n\n{after}",
})
PM_TEXTS["en"].update({
    "copy_rd": "📋 Copy ID",
    "pay_rd": "💳 <b>Pay with RedotPay</b>\n\n📦 {what}\n💵 Amount: <b>{usd}$</b>\n\n1️⃣ Open the RedotPay app and send <b>{usd}$</b> to this ID:\n<code>{dest}</code>\n⚠️ Make sure the received amount is exactly <b>{usd}$</b>.\n\n2️⃣ After the transfer, send a <b>screenshot</b> of it here.\n\n{after}",
})
PM_TEXTS["fr"].update({
    "copy_rd": "📋 Copier l'ID",
    "pay_rd": "💳 <b>Paiement via RedotPay</b>\n\n📦 {what}\n💵 Montant : <b>{usd}$</b>\n\n1️⃣ Ouvrez l'application RedotPay et envoyez <b>{usd}$</b> à cet ID :\n<code>{dest}</code>\n⚠️ Assurez-vous que le montant reçu est exactement <b>{usd}$</b>.\n\n2️⃣ Après le transfert, envoyez ici une <b>capture d'écran</b>.\n\n{after}",
})

def _pp_amt(req):
    return f"${req['usd']}" if req.get("m") == "rd" else f"${req['usd']} = {req['da']} DA"

def rdp_ready():
    return bool(RDP_APP_KEY and RDP_PRIV_RAW)

def rdp_visible(uid):
    """RedotPay يظهر للجميع في الإنتاج فقط؛ في Sandbox (أموال وهمية) للأدمن فقط حتى لا يُسلَّم منتج حقيقي بدفعة تجريبية."""
    try:
        if not rdp_ready():
            return False
        return (not RDP_SANDBOX) or bool(_is_admin_user(uid))
    except Exception:
        return False

def _rdp_pem(raw, kind):
    raw = raw.replace("\\n", "\n").strip()
    if "BEGIN" in raw:
        return raw.encode()
    body = "".join(raw.split())
    lines = [body[i:i + 64] for i in range(0, len(body), 64)]
    return ("-----BEGIN %s-----\n%s\n-----END %s-----\n" % (kind, "\n".join(lines), kind)).encode()

def _rdp_sign(text):
    import base64
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    key = serialization.load_pem_private_key(_rdp_pem(RDP_PRIV_RAW, "PRIVATE KEY"), password=None)
    return base64.b64encode(key.sign(text.encode("utf-8"), padding.PKCS1v15(), hashes.SHA256())).decode()

def _rdp_headers(uri, body_str):
    ts = str(int(time.time() * 1000))
    h = {
        "Content-Type": "application/json", "accept": "application/json",
        "X-R-Ak": RDP_APP_KEY, "X-Merchant-Ak": RDP_APP_KEY,
        "X-R-Ts": ts, "X-R-Key-Version": RDP_KEY_VERSION,
    }
    try:
        h["X-R-Signature"] = _rdp_sign("POST %s\n%s.%s.%s" % (uri, RDP_APP_KEY, ts, body_str))
    except Exception as e:
        print(f"redotpay sign error: {e}")
        if not RDP_SANDBOX:
            raise
    return h

_RDP_SKIP = ("icon", "logo", "img", "image", "pic", "avatar")
_RDP_PREF = ("checkout", "cashier", "paylink", "h5", "pay", "redirect", "url", "link")

def _rdp_collect(node, key, out):
    if isinstance(node, dict):
        for k, v in node.items():
            _rdp_collect(v, str(k), out)
    elif isinstance(node, list):
        for v in node:
            _rdp_collect(v, key, out)
    elif isinstance(node, str) and node.startswith("http"):
        out.append((key, node))

def _rdp_find_url(data):
    out = []
    _rdp_collect(data, "", out)
    best, best_rank = None, 99
    for k, v in out:
        kl = k.lower()
        if any(s in kl for s in _RDP_SKIP) or re.search(r"\.(png|jpe?g|svg|gif|webp)(\?|$)", v, re.I):
            continue
        rank = 50
        for i, tok in enumerate(_RDP_PREF):
            if tok in kl:
                rank = i
                break
        if rank < best_rank:
            best, best_rank = v, rank
    return best

def _rdp_find_key(node, names):
    if isinstance(node, dict):
        for k, v in node.items():
            if k in names and isinstance(v, (str, int)):
                return str(v)
        for v in node.values():
            r = _rdp_find_key(v, names)
            if r:
                return r
    elif isinstance(node, list):
        for v in node:
            r = _rdp_find_key(v, names)
            if r:
                return r
    return None

def rdp_create_order(inv_id, invoice):
    """ينشئ طلباً في RedotPay ويرجع (رابط الدفع، رقم الطلب)."""
    amount = Decimal(str(invoice["price_usdt"])).quantize(Decimal("0.01"))
    name = str(invoice.get("product_name") or "Order")
    body = {
        "outerOrderSn": ("rk-%s" % inv_id)[:32],
        "outerUid": str(invoice.get("user_id"))[:32],
        "orderAmount": float(amount),
        "orderCurrency": "USD",
        "env": "WEB",
        "orderDesc": ("RASEEDKOM - " + name)[:100],
        "timeExpire": int(time.time() * 1000) + RDP_ORDER_MINUTES * 60 * 1000,
        "goods": [{
            "goodsType": "02", "goodsCategory": "6000", "goodsCode": str(inv_id)[:20],
            "goodsName": name[:30], "goodsCount": 1, "goodsAmount": float(amount), "goodsCoin": "USD",
        }],
    }
    base_url = (os.getenv("RENDER_EXTERNAL_URL") or "").strip().rstrip("/")
    if base_url:
        body["redirectUrl"] = base_url + "/rdp/done"
    body_str = json.dumps(body, separators=(",", ":"), ensure_ascii=False)
    r = requests.post(RDP_BASE + RDP_URI_CREATE, data=body_str.encode("utf-8"),
                      headers=_rdp_headers(RDP_URI_CREATE, body_str), timeout=25)
    if r.status_code != 200:
        raise RuntimeError("http %s: %s" % (r.status_code, r.text[:300]))
    data = r.json()
    print("redotpay create response: " + json.dumps(data)[:600])
    url = _rdp_find_url(data)
    if not url:
        raise RuntimeError("no checkout url in response: " + json.dumps(data)[:300])
    sn = _rdp_find_key(data, ("orderSn", "sn", "paymentSn", "paySn"))
    return url, sn

def _rdp_verify(headers, body_str):
    """True = توقيع صحيح | False = توقيع خاطئ | None = لا يوجد مفتاح المنصة للتحقق."""
    if not RDP_PUB_RAW:
        return None
    try:
        import base64
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding
        h = {str(k).lower(): v for k, v in headers.items()}
        sig = h.get("x-r-signature")
        if not sig:
            return False
        key = serialization.load_pem_public_key(_rdp_pem(RDP_PUB_RAW, "PUBLIC KEY"))
        data = ("%s.%s.%s" % (RDP_APP_KEY, h.get("x-r-ts", ""), body_str)).encode("utf-8")
        key.verify(base64.b64decode(sig), data, padding.PKCS1v15(), hashes.SHA256())
        return True
    except Exception as e:
        print(f"redotpay verify failed: {e}")
        return False

def _rdp_settle(inv_id, outer, amount):
    try:
        invoice = get_invoice(inv_id)
    except Exception as e:
        print(f"redotpay settle get_invoice error: {e}")
        invoice = None
    if not invoice:
        txt = ("⚠️ <b>دفعة RedotPay لفاتورة غير موجودة</b>\n\n🆔 %s\n💵 $%s\nراجع الدفعة يدوياً." % (html.escape(outer), amount))
        alert_admin(txt)
        monitor_send(txt)
        return
    uid = invoice["user_id"]
    lang = get_lang(uid)
    tx = {"tx_id": "rdp-%s" % outer, "amount": amount, "currency": "USDT",
          "time": int(time.time() * 1000), "via": "redotpay"}
    try:
        _settle_payment(uid, uid, lang, inv_id, invoice, tx)
    except Exception as e:
        print(f"redotpay settle error: {e}")
        alert_admin("⚠️ <b>خطأ في معالجة دفعة RedotPay</b>\n\n🆔 %s\n💵 $%s\n👤 %s\n%s" % (html.escape(outer), amount, _user_link(uid), html.escape(str(e))[:200]))
        return
    monitor_send("💳 <b>دفعة RedotPay</b>\n\n👤 %s\n💵 $%s\n🆔 %s" % (_user_link(uid), amount, html.escape(outer)))

def rdp_process_webhook(headers, body_bytes):
    """يرجع True إذا نقبل الإشعار (SUCCESS) و False ليعيد RedotPay المحاولة."""
    body_str = body_bytes.decode("utf-8", "replace")
    try:
        data = json.loads(body_str)
    except Exception:
        return False
    v = _rdp_verify(headers, body_str)
    if v is False:
        return False
    if data.get("actionType") != "ACQUIRER_PAY" or str(data.get("orderStatus")) != "2":
        return True
    outer = str(data.get("outerOrderSn") or "")
    if not outer.startswith("rk-"):
        return True
    inv_id = outer[3:]
    try:
        amount = Decimal(str(data.get("orderAmount")))
    except Exception:
        return False
    if str(data.get("orderCurrency") or "USD").upper() != "USD" or amount <= 0:
        alert_admin("⚠️ إشعار RedotPay بعملة/مبلغ غير متوقع: %s" % html.escape(body_str[:300]))
        return True
    if v is None:  # لا يوجد مفتاح المنصة: مسموح فقط في Sandbox لفواتير الأدمن
        ok = False
        if RDP_SANDBOX:
            try:
                inv = get_invoice(inv_id)
                ok = bool(inv and _is_admin_user(inv["user_id"]))
            except Exception:
                ok = False
        if not ok:
            alert_admin("⚠️ وصل إشعار RedotPay بدون إمكانية التحقق من توقيعه. أضف REDOTPAY_PLATFORM_PUBKEY في Render.")
            return False
    threading.Thread(target=_rdp_settle, args=(inv_id, outer, amount), daemon=True).start()
    return True

def _rdp_cb_impl(req):
    ok = False
    try:
        ok = rdp_process_webhook(dict(req.headers), req.get_data() or b"")
    except Exception as e:
        print(f"redotpay webhook error: {e}")
    payload = {"code": "SUCCESS" if ok else "FAIL", "requestId": uuid.uuid4().hex}
    if not ok:
        payload["msg"] = "rejected"
    return app.response_class(json.dumps(payload), mimetype="application/json")

def _rdp_done_impl():
    page = ("<html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'></head>"
            "<body style='font-family:sans-serif;text-align:center;padding:48px'>"
            "<h2>&#x2705; RedotPay</h2><p>ارجع إلى تيليجرام — سيصلك طلبك تلقائياً بعد تأكيد الدفع.<br>Return to Telegram: your order will arrive automatically.</p>"
            "<p><a href='" + BOT_LINK + "'>Open bot</a></p></body></html>")
    return app.response_class(page, mimetype="text/html")

def _rdp_cash_pct(inv):
    if inv.get("product_id") == TOPUP_PID:
        return None
    return REDOTPAY_GIFT_PCT if inv.get("product_id") in GIFT_VARIANTS else REDOTPAY_PCT

def _rdp_checkout(chat_id, lang, uid, inv_id, inv, call, back_cb):
    """ينشئ طلب RedotPay ويعرض زر الدفع."""
    try:
        url, sn = rdp_create_order(inv_id, inv)
    except Exception as e:
        print(f"redotpay create order failed: {e}")
        mk = InlineKeyboardMarkup(row_width=1)
        mk.add(InlineKeyboardButton(text=t(lang, "back"), callback_data=back_cb))
        if call:
            _pf_show(call, pmt(lang, "rdp_fail"), mk)
        else:
            bot.send_message(chat_id, pmt(lang, "rdp_fail"), reply_markup=mk)
        try:
            alert_admin("⚠️ فشل إنشاء طلب RedotPay: %s" % html.escape(str(e))[:300])
        except Exception:
            pass
        return
    try:
        kv_set("rk:rdpsn:%s" % inv_id, sn or "-", ex=4 * 3600)
        kv_set("rk:inv:%s" % inv_id, json.dumps(inv), ex=4 * 3600)  # تمديد صلاحية الفاتورة لحين وصول الإشعار
    except Exception as e:
        print(f"redotpay ttl extend error: {e}")
    clear_pending(uid)
    inv_live_remove(inv_id)
    pct = _rdp_cash_pct(inv)
    cash = pmt(lang, "rdp_cash").format(pct=pct) if pct is not None else ""
    text = pmt(lang, "rdp_link").format(what=html.escape(str(inv.get("product_name") or "")), usd=html.escape(str(inv["price_usdt"])), cash=cash)
    mk = InlineKeyboardMarkup(row_width=1)
    mk.add(InlineKeyboardButton(text=pmt(lang, "rdp_open"), url=url))
    mk.add(InlineKeyboardButton(text=t(lang, "back"), callback_data=back_cb))
    if call:
        _pf_show(call, text, mk)
    else:
        bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=mk)

def _rdp_topup_request(call, chat_id, uid, lang, amount):
    chat = chat_id or call.message.chat.id
    if call:
        try:
            bot.answer_callback_query(call.id)
        except Exception:
            pass
    if not rdp_visible(uid):
        bot.send_message(chat, pmt(lang, "soon"))
        return
    try:
        price = "%.2f" % Decimal(str(amount))
        inv_id = create_invoice(uid, TOPUP_PID, "topup", price, "💳 شحن المحفظة")
        inv = get_invoice(inv_id)
    except Exception as e:
        print(f"redotpay topup invoice error: {e}")
        bot.send_message(chat, t(lang, "temp_error"))
        return
    _rdp_checkout(chat, lang, uid, inv_id, inv, call, "pf_top")

@bot.message_handler(commands=["rdpsim"])
def rdp_sim_command(message):
    """للأدمن في Sandbox فقط: يحاكي وصول إشعار دفع RedotPay لفاتورة. الاستعمال: /rdpsim رقم_الطلب"""
    if not _is_admin_user(message.from_user.id):
        return
    if not RDP_SANDBOX:
        bot.reply_to(message, "⛔ هذا الأمر متاح في وضع Sandbox فقط.")
        return
    parts = (message.text or "").split()
    if len(parts) < 2:
        bot.reply_to(message, "الاستعمال: /rdpsim رقم_الطلب\nمثال: /rdpsim 2c319d9e09\n(رقم الطلب هو ما بعد rk- في صفحة الدفع)")
        return
    inv_id = parts[1].replace("rk-", "").strip()
    try:
        inv = get_invoice(inv_id)
    except Exception:
        inv = None
    if not inv:
        bot.reply_to(message, "❌ فاتورة غير موجودة أو منتهية. أنشئ طلب RedotPay جديداً ثم أعد المحاولة.")
        return
    try:
        amount = Decimal(str(inv["price_usdt"]))
    except Exception:
        bot.reply_to(message, "❌ مبلغ الفاتورة غير صالح.")
        return
    bot.reply_to(message, "🧪 جاري محاكاة دفعة RedotPay بقيمة $%s ..." % amount)
    threading.Thread(target=_rdp_settle, args=(inv_id, "rk-" + inv_id, amount), daemon=True).start()


# ---------- إعدادات (تفعيل/إيقاف + سعر الصرف) ----------
def pm_enabled(m):
    try:
        return str(kv_get(f"rk:pm:on:{m}")) != "0"
    except Exception:
        return True

def pm_rate(m):
    try:
        v = kv_get(f"rk:pm:rate:{m}")
        return Decimal(str(v)) if v else PM_DEFAULT_RATE[m]
    except Exception:
        return PM_DEFAULT_RATE[m]

def _fmt_rate(r):
    s = f"{Decimal(r):.2f}"
    return s[:-3] if s.endswith(".00") else s

def pm_da(usd, m):
    return int((Decimal(str(usd)) * pm_rate(m)).to_integral_value(rounding=ROUND_CEILING))

# ---------- قوائم "أعلمني عند التوفر" ----------
_mem_pmw = {"bd": set(), "fx": set(), "rd": set(), "rp": set(), "bb": set()}

def pmw_add(m, uid):
    if db:
        try:
            db.sadd(f"rk:pmwait:{m}", str(uid))
            return
        except Exception as e:
            print(f"pmw_add error: {e}")
    _mem_pmw[m].add(str(uid))

def pmw_list(m):
    ids = set(_mem_pmw[m])
    if db:
        try:
            ids |= {str(x) for x in (db.smembers(f"rk:pmwait:{m}") or [])}
        except Exception as e:
            print(f"pmw_list error: {e}")
    return sorted(ids)

def pmw_clear(m):
    _mem_pmw[m].clear()
    if db:
        try:
            db.delete(f"rk:pmwait:{m}")
        except Exception as e:
            print(f"pmw_clear error: {e}")

# ---------- طلبات الدفع (وصل بريدي موب / رسالة Flixy) ----------
_mem_pp = set()

def pp_get(rid):
    try:
        return kv_get_json(f"rk:pp:{rid}")
    except StorageError:
        return None

def pp_save(req):
    kv_set(f"rk:pp:{req['id']}", json.dumps(req, ensure_ascii=False), ex=30 * 86400)

def pp_set_add(rid):
    if db:
        try:
            db.sadd("rk:ppset", rid)
            return
        except Exception as e:
            print(f"pp_set_add error: {e}")
    _mem_pp.add(rid)

def pp_set_remove(rid):
    _mem_pp.discard(rid)
    if db:
        try:
            db.srem("rk:ppset", rid)
        except Exception as e:
            print(f"pp_set_remove error: {e}")

def pp_ids():
    ids = set(_mem_pp)
    if db:
        try:
            ids |= {str(x) for x in (db.smembers("rk:ppset") or [])}
        except Exception as e:
            print(f"pp_ids error: {e}")
    return list(ids)

def _pp_pending_list():
    out = []
    for rid in pp_ids():
        r = pp_get(rid)
        if r and r.get("status") == "pending":
            out.append(r)
        elif r and r.get("status") != "pending":
            pp_set_remove(rid)
    out.sort(key=lambda r: r.get("sub_ts", 0))
    return out

def _pp_count():
    try:
        return len(_pp_pending_list())
    except Exception:
        return 0

def _pp_active(uid):
    """طلب الدفع الحالي للزبون (بانتظار الوصل أو قيد المراجعة)."""
    try:
        rid = kv_get(f"rk:ppu:{uid}")
        req = pp_get(str(rid)) if rid else None
    except StorageError:
        return None
    if req and req.get("status") in ("awaiting", "pending"):
        return req
    return None

def _pm_busy(uid):
    req = _pp_active(uid)
    return bool(req and req.get("status") == "pending")

def _create_pp(uid, m, kind, what, usd, inv=None):
    usd = f"{Decimal(str(usd)):.2f}"
    req = {
        "id": uuid.uuid4().hex[:8], "uid": uid, "m": m, "kind": kind, "what": what,
        "usd": usd, "da": pm_da(usd, m), "rate": str(pm_rate(m)),
        "status": "awaiting", "ts": int(time.time()), "inv": inv,
    }
    pp_save(req)
    kv_set(f"rk:ppu:{uid}", req["id"], ex=6 * 3600)
    return req

# ---------- واجهة اختيار طريقة الدفع (عند الشراء) ----------
_bn_text_fn = None  # تُملأ لاحقاً

def build_invoice_text(lang, invoice, product):
    return pmt(lang, "pick_buy").format(
        product=f"{html.escape(tr(product, 'name', lang))}{_lab_suffix(invoice)}",
        amount=html.escape(str(invoice["price_usdt"])),
    )

def _pm_method_rows(lang, mk, ids):
    """ids: dict بأسماء callback لكل طريقة."""
    mk.add(InlineKeyboardButton(text=pmt(lang, "btn_binance"), callback_data=ids["bn"]))
    mk.add(InlineKeyboardButton(text=pmt(lang, "btn_bd"), callback_data=ids["bd"]))
    mk.add(InlineKeyboardButton(text=pmt(lang, "btn_fx"), callback_data=ids["fx"]))
    mk.add(InlineKeyboardButton(text="RedotPay", callback_data=ids["rp"]))
    mk.add(InlineKeyboardButton(text="Bybit", callback_data=ids["bb"]))
    mk.add(InlineKeyboardButton(text=pmt(lang, "btn_chat"), url=MY_PRIVATE_CHAT_LINK))

def build_invoice_markup(lang, invoice_id, wallet=False):
    inv = None
    try:
        inv = get_invoice(invoice_id)
    except StorageError:
        pass
    if not inv or inv.get("product_id") == TOPUP_PID:
        return _bn_invoice_markup(lang, invoice_id, wallet)
    bal = "0.00"
    try:
        if db:
            bal = _money(wallet_avail_c(prof_get(inv["user_id"])))
    except Exception:
        pass
    mk = InlineKeyboardMarkup(row_width=1)
    mk.add(InlineKeyboardButton(text=pmt(lang, "btn_wallet").format(bal=bal), callback_data=f"wpay_{invoice_id}"))
    _pm_method_rows(lang, mk, {
        "bn": f"pm_bn_{invoice_id}", "bd": f"pm_bd_{invoice_id}",
        "fx": f"pm_fx_{invoice_id}",
        "rp": (f"pm_rp_{invoice_id}" if rdp_visible(inv["user_id"]) else f"pm_rd_{invoice_id}"),
        "bb": f"pm_soon_bb_{invoice_id}",
    })
    mk.add(InlineKeyboardButton(text=t(lang, "cancel"), callback_data=f"cancel_{invoice_id}"))
    return mk

def topup_method_picker(call, lang):
    mk = InlineKeyboardMarkup(row_width=1)
    _pm_method_rows(lang, mk, {"bn": "pm_tbn", "bd": "pm_tbd", "fx": "pm_tfx", "rp": ("pm_trp" if rdp_visible(call.from_user.id) else "pm_trd"), "bb": "pm_tsoon_bb"})
    mk.add(InlineKeyboardButton(text=t(lang, "cancel"), callback_data="pf_wallet"))
    _pf_show(call, pmt(lang, "pick_topup"), mk)

# ---------- شاشات مساعدة ----------
def _pm_copy_button(lang, m, value):
    label = pmt(lang, "copy_" + m)
    if CopyTextButton is not None:
        try:
            return InlineKeyboardButton(text=label, copy_text=CopyTextButton(text=value))
        except Exception:
            pass
    return InlineKeyboardButton(text=label, callback_data=f"pm_cp_{m}")

def _pm_full_screen(call, lang, m, back_cb):
    mk = InlineKeyboardMarkup(row_width=1)
    mk.add(InlineKeyboardButton(text=t(lang, "notify_me"), callback_data=f"pm_nt_{m}"))
    mk.add(InlineKeyboardButton(text=t(lang, "back"), callback_data=back_cb))
    _pf_show(call, pmt(lang, "full").format(method=PM_NAME[m][lang]), mk)

def _pm_soon_screen(call, lang, back_cb, m=None):
    mk = InlineKeyboardMarkup(row_width=1)
    if m:
        mk.add(InlineKeyboardButton(text=pmt(lang, "notify_upd"), callback_data=f"pm_nt_{m}"))
    mk.add(InlineKeyboardButton(text=t(lang, "back"), callback_data=back_cb))
    _pf_show(call, pmt(lang, "soon"), mk)

def _pm_pay_text(lang, req):
    m = req["m"]
    dest = BARIDI_RIP if m == "bd" else (RDP_MANUAL_ID if m == "rd" else FLEXY_NUMBER)
    after = pmt(lang, "after_buy" if req["kind"] == "buy" else "after_topup")
    return pmt(lang, "pay_" + m).format(
        what=html.escape(req["what"]), usd=req["usd"], rate=_fmt_rate(req["rate"]),
        da=req["da"], dest=dest, after=after,
    ), dest

def _pm_pay_markup(lang, req, dest):
    mk = InlineKeyboardMarkup(row_width=1)
    mk.add(_pm_copy_button(lang, req["m"], dest))
    mk.add(InlineKeyboardButton(text=t(lang, "back"), callback_data=f"pm_rb_{req['id']}"))
    mk.add(InlineKeyboardButton(text=t(lang, "cancel"), callback_data=f"pmx_{req['id']}"))
    return mk

def _pm_show_pay(call, lang, req):
    text, dest = _pm_pay_text(lang, req)
    _pf_show(call, text, _pm_pay_markup(lang, req, dest))

def _pm_restore_invoice(uid, inv_id):
    """يعيد تفعيل الفاتورة (انتظار رقم عملية Binance + مراقبة الانتهاء) بعد الرجوع."""
    try:
        kv_set(f"rk:pend:{uid}", inv_id, ex=INVOICE_TTL + INVOICE_GRACE + 600)
        inv_live_add(inv_id)
    except Exception as e:
        print(f"restore invoice error: {e}")

def _pm_inv(call, inv_id, lang):
    try:
        inv = get_invoice(inv_id)
    except StorageError:
        bot.answer_callback_query(call.id, t(lang, "temp_error"), show_alert=True)
        return None
    if (not inv or str(inv.get("user_id")) != str(call.from_user.id)
            or inv.get("product_id") == TOPUP_PID
            or time.time() - inv["created_at"] > INVOICE_TTL):
        bot.answer_callback_query(call.id, wt(lang, "wpay_expired"), show_alert=True)
        return None
    return inv

_pm_wait = {}  # user_id -> طريقة (ينتظر مبلغ الشحن مكتوباً)

@bot.callback_query_handler(func=lambda c: c.data.startswith(("pm_", "pmx_")))
def handle_pm(call):
    uid = call.from_user.id
    lang = get_lang(uid)
    data = call.data
    _pm_wait.pop(uid, None)

    if data.startswith("pmx_"):  # إلغاء طلب دفع بريدي موب/Flixy
        rid = data[4:]
        req = pp_get(rid)
        if req and str(req.get("uid")) == str(uid):
            if req.get("status") == "pending":
                bot.answer_callback_query(call.id, pmt(lang, "proof_dup"), show_alert=True)
                return
            req["status"] = "cancelled"
            try:
                pp_save(req)
                kv_del(f"rk:ppu:{uid}")
            except StorageError:
                pass
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        send_main_menu(call.message.chat.id, lang)
        bot.answer_callback_query(call.id, t(lang, "cancelled"))
        return

    parts = data.split(SEP, 2)
    cmd = parts[1] if len(parts) > 1 else ""
    arg = parts[2] if len(parts) > 2 else ""

    if cmd == "cp":
        bot.answer_callback_query(call.id, BARIDI_RIP if arg == "bd" else (RDP_MANUAL_ID if arg == "rd" else FLEXY_NUMBER), show_alert=True)
        return

    if cmd == "nt":
        if arg in ALL_M:
            pmw_add(arg, uid)
            bot.answer_callback_query(call.id, pmt(lang, "nt_ok").format(method=_mname(arg, lang)), show_alert=True)
            monitor_send(
                f"🔔 <b>زبون طلب إعلامه بتوفر {_mname(arg, 'ar')}</b>\n\n👤 {_user_link(uid)}\n"
                f"⏳ عدد المنتظرين الآن: {len(pmw_list(arg))}"
            )
        else:
            bot.answer_callback_query(call.id)
        return

    # ----- الشراء -----
    if cmd == "back":
        inv = _pm_inv(call, arg, lang)
        if inv:
            product = find_product(inv["product_id"])
            _pf_show(call, build_invoice_text(lang, inv, product), build_invoice_markup(lang, arg, False))
            bot.answer_callback_query(call.id)
        return

    if cmd == "soon":
        m, _, ref = arg.partition(SEP)
        _pm_soon_screen(call, lang, f"pm_back_{ref}", m if m in SOON_NAME else None)
        bot.answer_callback_query(call.id)
        return

    if cmd == "rb":  # رجوع من شاشة بريدي موب/Flixy إلى اختيار الطريقة
        req = pp_get(arg)
        if not req or str(req.get("uid")) != str(uid):
            bot.answer_callback_query(call.id)
            return
        if req.get("status") == "pending":
            bot.answer_callback_query(call.id, pmt(lang, "proof_dup"), show_alert=True)
            return
        req["status"] = "cancelled"
        try:
            pp_save(req)
            kv_del(f"rk:ppu:{uid}")
        except StorageError:
            pass
        inv_id = req.get("inv")
        if inv_id:
            inv = _pm_inv(call, inv_id, lang)
            if not inv:
                return
            _pm_restore_invoice(uid, inv_id)
            product = find_product(inv["product_id"])
            _pf_show(call, build_invoice_text(lang, inv, product), build_invoice_markup(lang, inv_id, False))
        else:
            topup_method_picker(call, lang)
        bot.answer_callback_query(call.id)
        return

    if cmd == "rp":
        inv = _pm_inv(call, arg, lang)
        if not inv:
            return
        if not rdp_visible(uid):
            _pm_soon_screen(call, lang, f"pm_back_{arg}", "rp")
            bot.answer_callback_query(call.id)
            return
        bot.answer_callback_query(call.id)
        _rdp_checkout(call.message.chat.id, lang, uid, arg, inv, call, f"pm_back_{arg}")
        return

    if cmd == "trp":
        if not rdp_visible(uid):
            _pm_soon_screen(call, lang, "pf_top", "rp")
            bot.answer_callback_query(call.id)
            return
        mk = InlineKeyboardMarkup(row_width=2)
        mk.row(*[
            InlineKeyboardButton(text=f"{a}$", callback_data=f"pm_ta_rp_{a}")
            for a in TOPUP_AMOUNTS
        ])
        mk.add(InlineKeyboardButton(text=wt(lang, "btn_topup_other"), callback_data="pm_to_rp"))
        mk.add(InlineKeyboardButton(text=t(lang, "back"), callback_data="pf_top"))
        _pf_show(call, pmt(lang, "rdp_amounts"), mk)
        bot.answer_callback_query(call.id)
        return

    if cmd == "bn":
        inv = _pm_inv(call, arg, lang)
        if inv:
            product = find_product(inv["product_id"])
            _pm_restore_invoice(uid, arg)
            mk = _bn_invoice_markup(lang, arg, False)
            mk.add(InlineKeyboardButton(text=t(lang, "back"), callback_data=f"pm_back_{arg}"))
            _pf_show(call, _bn_invoice_text(lang, inv, product), mk)
            bot.answer_callback_query(call.id)
        return

    if cmd in ("bd", "fx", "rd"):
        inv = _pm_inv(call, arg, lang)
        if not inv:
            return
        if not pm_enabled(cmd):
            _pm_full_screen(call, lang, cmd, f"pm_back_{arg}")
            bot.answer_callback_query(call.id)
            return
        if _pm_busy(uid):
            bot.answer_callback_query(call.id, pmt(lang, "busy"), show_alert=True)
            return
        try:
            req = _create_pp(uid, cmd, "buy", inv["product_name"], inv["price_usdt"], arg)
        except StorageError:
            bot.answer_callback_query(call.id, t(lang, "temp_error"), show_alert=True)
            return
        clear_pending(uid)       # لا نريد أن يُفهم الوصل كرقم عملية Binance
        inv_live_remove(arg)     # لا إشعار انتهاء فاتورة فوق التعليمات
        _pm_show_pay(call, lang, req)
        bot.answer_callback_query(call.id)
        return

    # ----- شحن المحفظة -----
    if cmd == "tbn":
        _pf_show(call, wt(lang, "topup_pick"), _pf_markup(lang, "topup"))
        bot.answer_callback_query(call.id)
        return

    if cmd == "tsoon":
        _pm_soon_screen(call, lang, "pf_top", arg if arg in SOON_NAME else None)
        bot.answer_callback_query(call.id)
        return

    if cmd in ("tbd", "tfx", "trd"):
        m = cmd[1:]
        if not pm_enabled(m):
            _pm_full_screen(call, lang, m, "pf_top")
            bot.answer_callback_query(call.id)
            return
        mk = InlineKeyboardMarkup(row_width=2)
        mk.row(*[
            InlineKeyboardButton(text=(f"{a}$" if m == "rd" else f"{a}$ = {pm_da(a, m)} DA"), callback_data=f"pm_ta_{m}_{a}")
            for a in TOPUP_AMOUNTS
        ])
        mk.add(InlineKeyboardButton(text=wt(lang, "btn_topup_other"), callback_data=f"pm_to_{m}"))
        mk.add(InlineKeyboardButton(text=t(lang, "back"), callback_data="pf_top"))
        _pf_show(call, pmt(lang, "rdp_amounts" if m == "rd" else "topup_amounts").format(method=PM_NAME[m][lang], rate=_fmt_rate(pm_rate(m))), mk)
        bot.answer_callback_query(call.id)
        return

    if cmd == "to":
        if arg not in PM_NAME and not (arg == "rp" and rdp_visible(uid)):
            bot.answer_callback_query(call.id)
            return
        if not pm_enabled(arg):
            _pm_full_screen(call, lang, arg, "pf_top")
            bot.answer_callback_query(call.id)
            return
        _pm_wait[uid] = arg
        mk = InlineKeyboardMarkup()
        mk.add(InlineKeyboardButton(text=t(lang, "cancel"), callback_data="pf_top"))
        _pf_show(call, wt(lang, "topup_other_prompt").format(min=TOPUP_MIN, max=TOPUP_MAX), mk)
        bot.answer_callback_query(call.id)
        return

    if cmd == "ta":
        try:
            m, amt = arg.split(SEP, 1)
            amount = Decimal(amt)
            if (m not in PM_NAME and not (m == "rp" and rdp_visible(uid))) or amount not in [Decimal(a) for a in TOPUP_AMOUNTS]:
                raise ValueError("bad")
        except Exception:
            bot.answer_callback_query(call.id)
            return
        _pm_topup_request(call, None, uid, lang, m, amount)
        return

    bot.answer_callback_query(call.id)

def _pm_topup_request(call, chat_id, uid, lang, m, amount):
    """ينشئ طلب شحن (بريدي موب/Flixy) ويعرض التعليمات. call أو chat_id."""
    if m == "rp":
        _rdp_topup_request(call, chat_id, uid, lang, amount)
        return
    if not pm_enabled(m):
        if call:
            _pm_full_screen(call, lang, m, "pf_top")
            bot.answer_callback_query(call.id)
        return
    if _pm_busy(uid):
        if call:
            bot.answer_callback_query(call.id, pmt(lang, "busy"), show_alert=True)
        else:
            bot.send_message(chat_id, pmt(lang, "busy"))
        return
    try:
        req = _create_pp(uid, m, "topup", "💳 شحن المحفظة", amount)
    except StorageError:
        if call:
            bot.answer_callback_query(call.id, t(lang, "temp_error"), show_alert=True)
        else:
            bot.send_message(chat_id, t(lang, "temp_error"))
        return
    if call:
        _pm_show_pay(call, lang, req)
        bot.answer_callback_query(call.id)
    else:
        text, dest = _pm_pay_text(lang, req)
        bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=_pm_pay_markup(lang, req, dest))

def _awaiting_pm_amount(m):
    return (
        bool(m.text) and not m.text.startswith("/")
        and m.chat.type == "private" and m.from_user.id in _pm_wait
    )

@bot.message_handler(func=_awaiting_pm_amount, content_types=["text"])
def handle_pm_amount(message):
    uid = message.from_user.id
    lang = get_lang(uid)
    amount = _parse_price(message.text)
    if amount is None or amount < TOPUP_MIN or amount > TOPUP_MAX:
        bot.reply_to(message, wt(lang, "topup_bad").format(min=TOPUP_MIN, max=TOPUP_MAX))
        return
    m = _pm_wait.pop(uid)
    _pm_topup_request(None, message.chat.id, uid, lang, m, amount)

# ---------- استقبال الوصل من الزبون ----------
def _pp_notify(req):
    mname = PM_NAME[req["m"]]["ar"]
    kind = "شراء" if req["kind"] == "buy" else "شحن محفظة"
    txt = (
        f"💳 <b>دفعة {mname} معلقة</b> ({kind})\n\n👤 {_user_link(req['uid'])}\n"
        f"📦 {html.escape(req['what'])}\n💵 {_pp_amt(req)}\n🆔 #{req['id']}\n\n"
        f"ادخل /admin ← 💳 الدفعات المعلقة للتأكد."
    )
    alert_admin(txt)
    monitor_send(txt)

def _parse_flexy(txt):
    """يستخرج (المبلغ، الوقت) من رسالة Flixy. يرجع None إذا ناقص أحدهما."""
    tm = re.search(r"(?<!\d)([01]?\d|2[0-3])\s*[:hH]\s*([0-5]\d)(?!\d)", txt)
    if not tm:
        return None
    rest = txt[:tm.start()] + " " + txt[tm.end():]
    nums = re.findall(r"\d+(?:[.,]\d+)?", rest)
    if not nums:
        return None
    try:
        da = Decimal(nums[0].replace(",", "."))
    except InvalidOperation:
        return None
    if da <= 0:
        return None
    return da, f"{int(tm.group(1)):02d}:{tm.group(2)}"

def _pp_submit(message, photo):
    uid = message.from_user.id
    lang = get_lang(uid)
    req = _pp_active(uid)
    if not req:
        return False
    if req.get("status") == "pending":
        bot.send_message(message.chat.id, pmt(lang, "proof_dup"))
        return True
    if photo:
        if req["m"] == "fx":  # Flixy: نص فقط (مبلغ + وقت)
            bot.send_message(message.chat.id, pmt(lang, "proof_hint_fx"), parse_mode="HTML")
            return True
        req["file_id"] = message.photo[-1].file_id
    else:
        txt = (message.text or "").strip()
        if req["m"] in ("bd", "rd"):
            bot.send_message(message.chat.id, pmt(lang, "proof_hint_bd"), parse_mode="HTML")
            return True
        parsed = _parse_flexy(txt)
        if not parsed:
            bot.send_message(message.chat.id, pmt(lang, "proof_hint_fx"), parse_mode="HTML")
            return True
        req["text"] = txt[:500]
        req["claimed_da"] = str(parsed[0])
        req["claimed_time"] = parsed[1]
    req["status"] = "pending"
    req["sub_ts"] = int(time.time())
    try:
        pp_save(req)
    except StorageError:
        bot.send_message(message.chat.id, t(lang, "temp_error"))
        return True
    pp_set_add(req["id"])
    bot.send_message(message.chat.id, pmt(lang, "proof_ok"))
    _pp_notify(req)
    return True

def proof_photo(message):
    """يُستدعى من معالج الصور: يرجع True إذا كانت صورة وصل لطلب دفع نشط."""
    try:
        if message.chat.type != "private":
            return False
        return _pp_submit(message, True)
    except Exception as e:
        print(f"proof_photo error: {e}")
        return False

# ============================================================
# ========== أدوات الأدمن: الدفعات المعلقة، شحن محفظة، وصف المنتج، طرق الدفع ==========
# ============================================================
_ap_wait = {}  # admin_id -> حالة المعالج

def _parse_amount_input(text, rate):
    """نص الأدمن: رقم عادي = دينار، أو مع $ = دولار. يرجع (usd, da|None) أو None."""
    s = text.strip().lower().replace(",", ".").replace("،", ".")
    m = re.search(r"\d+(?:\.\d+)?", s)
    if not m:
        return None
    v = Decimal(m.group(0))
    if v <= 0:
        return None
    if "$" in s or "usd" in s or "دولار" in s:
        usd, da = v.quantize(Decimal("0.01"), rounding=ROUND_DOWN), None
    else:
        usd, da = (v / rate).quantize(Decimal("0.01"), rounding=ROUND_DOWN), v
    if usd <= 0:
        return None
    return usd, da

def _mp_choose_mode(chat_id, uid, amount, name):
    """بعد إدخال شراء يدوي: ثلاثة أزرار لطريقة إضافة الرصيد للمحفظة."""
    token = uuid.uuid4().hex[:8]
    kv_set(f"rk:mpm:{token}", json.dumps({"uid": str(uid), "amount": str(amount), "name": name}, ensure_ascii=False), ex=3600)
    cents = int((Decimal(str(amount)) * 100).to_integral_value())
    mk = InlineKeyboardMarkup(row_width=1)
    mk.add(InlineKeyboardButton(text="🎁 كاش باك 5%", callback_data=f"ap_pr5_{token}"))
    mk.add(InlineKeyboardButton(text="🎁 كاش باك 2%", callback_data=f"ap_pr2_{token}"))
    mk.add(InlineKeyboardButton(text="💵 حساب عام (المبلغ كما كتبته)", callback_data=f"ap_prg_{token}"))
    mk.add(InlineKeyboardButton(text="❌ إلغاء", callback_data="ap_prx"))
    bot.send_message(
        chat_id,
        f"➕ <b>شراء يدوي</b> للزبون <code>{uid}</code>\n📦 {html.escape(name or 'شراء يدوي')}\n💵 المبلغ: <b>${Decimal(str(amount)):.2f}</b>\n\n"
        f"اختر طريقة إضافة الرصيد للمحفظة:\n"
        f"• كاش باك 5% ← يُضاف <b>${_money(cents * 5 // 100)}</b>\n"
        f"• كاش باك 2% ← يُضاف <b>${_money(cents * 2 // 100)}</b>\n"
        f"• حساب عام ← يُضاف <b>${_money(cents)}</b> بالضبط",
        parse_mode="HTML", reply_markup=mk,
    )

def add_manual_purchase_mode(token, mode):
    """mode: '5' | '2' | 'g'. يسجل الشراء في السجل ويضيف رصيد المحفظة حسب الطريقة."""
    data = kv_get_json(f"rk:mpm:{token}")
    if not data:
        return False, "⚠️ انتهت صلاحية العملية، أعد تسجيل الشراء."
    if not kv_set(f"rk:mpm:done:{token}", "1", ex=3600, nx=True):
        return False, "⚠️ هذه العملية تمت معالجتها مسبقاً."
    uid, name = data["uid"], (data.get("name") or "").strip() or "شراء يدوي"
    err = _adm_precheck(uid)
    if err:
        kv_del(f"rk:mpm:done:{token}")
        return False, err
    amount = Decimal(str(data["amount"]))
    cents = int((amount * 100).to_integral_value())
    try:
        # via غير (binance/manual) = بدون مكافأة تلقائية؛ نضيف المبلغ بأنفسنا حسب الطريقة
        record_purchase(uid, None, name, amount, f"manual:{uuid.uuid4().hex[:12]}", via="manual_nr")
        reward_c = cents * 5 // 100 if mode == "5" else cents * 2 // 100 if mode == "2" else cents
        if reward_c > 0:
            _ensure_reward_field(uid)
            db.hincrby(_prof_key(uid), "reward_c", reward_c)
            wlog_add(uid, "reward", reward_c, name)
        p = prof_get(uid)
    except Exception as e:
        kv_del(f"rk:mpm:done:{token}")
        return False, f"❌ خطأ: {str(e)[:150]}"
    label = {"5": "كاش باك 5%", "2": "كاش باك 2%", "g": "حساب عام"}[mode]
    monitor_send(
        f"➕ <b>شراء يدوي مسجل</b> ({label})\n\n👤 {_user_link(uid)}\n📦 {html.escape(name)}\n💵 ${amount:.2f}\n"
        f"🎁 أُضيف للمحفظة: ${_money(reward_c)}\n💼 المتاح الآن: ${_money(wallet_avail_c(p))}"
    )
    return True, (
        f"✅ سُجل شراء للزبون <code>{uid}</code>: {html.escape(name)} — ${amount:.2f}\n"
        f"🎁 {label}: أُضيف <b>${_money(reward_c)}</b> إلى المحفظة\n"
        f"🛒 مجموع مشترياته: {p['buys']} | 💵 ${_money(p['spent_c'])}\n"
        f"💼 الرصيد المتاح: <b>${_money(wallet_avail_c(p))}</b>"
    )

def _ap_set(aid, **kw):
    kw["t"] = time.time()
    _ap_wait[aid] = kw

def show_pp_list(chat_id, msg_id=None):
    pend = _pp_pending_list()
    mk = InlineKeyboardMarkup(row_width=1)
    for r in pend[:40]:
        mk.add(InlineKeyboardButton(
            text=f"{PM_ICON[r['m']]} #{r['id']} | ${r['usd']} | {r['uid']}",
            callback_data=f"ap_v_{r['id']}",
        ))
    mk.add(InlineKeyboardButton(text="🔄 تحديث", callback_data="ap_l"))
    text = f"💳 <b>الدفعات المعلقة</b> ({len(pend)})" if pend else "💳 لا توجد دفعات معلقة حالياً."
    _pr_show(chat_id, msg_id, text, mk)

def _pp_detail_text(req):
    kind = "شراء منتج" if req["kind"] == "buy" else "شحن محفظة"
    s = (
        f"{PM_ICON[req['m']]} <b>دفعة {PM_NAME[req['m']]['ar']}</b> — {kind}\n\n"
        f"🆔 #{req['id']}\n👤 {_user_link(req['uid'])} (<code>{req['uid']}</code>)\n"
        f"📦 {html.escape(req['what'])}\n💵 " + (f"<b>${req['usd']}</b>" if req["m"] == "rd" else f"${req['usd']} = <b>{req['da']} DA</b> (1$ = {_fmt_rate(req['rate'])})") + "\n"
        f"🕒 {_fmt_date(req.get('sub_ts', 0))}"
    )
    if req.get("claimed_da"):
        try:
            low = Decimal(req["claimed_da"]) < Decimal(str(req["da"]))
        except InvalidOperation:
            low = False
        s += (f"\n\n🔎 المطلوب: <b>{req['da']} DA</b> | كتب الزبون: <b>{html.escape(req['claimed_da'])} DA</b>"
              f"{' ⚠️ أقل من المطلوب' if low else ''}\n🕒 الوقت المكتوب: <b>{html.escape(req.get('claimed_time', ''))}</b>")
    if req.get("text"):
        s += f"\n\n📝 رسالة الزبون:\n<code>{html.escape(req['text'])}</code>"
    return s

def show_pp_view(chat_id, rid):
    req = pp_get(rid)
    if not req or req.get("status") != "pending":
        bot.send_message(chat_id, "⚠️ هذه الدفعة غير موجودة أو تمت معالجتها.")
        return
    bad = "❌ دفعة مزورة" if req["m"] == "bd" else "❌ دفعة غير موجودة"
    mk = InlineKeyboardMarkup(row_width=1)
    mk.add(InlineKeyboardButton(text="✅ دفعة صحيحة", callback_data=f"ap_ok_{rid}"))
    mk.add(InlineKeyboardButton(text=bad, callback_data=f"ap_no_{rid}"))
    mk.add(InlineKeyboardButton(text="⬅️ القائمة", callback_data="ap_l"))
    text = _pp_detail_text(req)
    if req.get("file_id"):
        try:
            bot.send_photo(chat_id, req["file_id"], caption=text, parse_mode="HTML", reply_markup=mk)
            return
        except Exception as e:
            print(f"pp photo send failed: {e}")
            text += "\n\n⚠️ تعذر عرض الصورة."
    bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=mk)

def _ap_credit_wallet(uid, amount, note):
    """يشحن محفظة زبون (بدون مكافأة) ويبلغه. يرجع (ok, msg)."""
    err = _adm_precheck(uid)
    if err:
        return False, err
    cents = int((amount * 100).to_integral_value())
    if cents <= 0:
        return False, "❌ مبلغ غير صالح."
    try:
        wallet_credit(uid, cents, "topup", note)
        avail = _money(wallet_avail_c(prof_get(uid)))
    except Exception as e:
        return False, f"❌ خطأ: {str(e)[:150]}"
    lang = get_lang(uid)
    mk = InlineKeyboardMarkup()
    mk.add(InlineKeyboardButton(text=t(lang, "kb_products"), callback_data="back_to_main"))
    try:
        bot.send_message(int(uid), pmt(lang, "approved").format(amount=_money(cents), avail=avail),
                         parse_mode="HTML", reply_markup=mk)
    except Exception as e:
        print(f"wallet credit notice failed: {e}")
    monitor_send(
        f"💳 <b>شحن محفظة</b> ({html.escape(note)})\n\n👤 {_user_link(uid)}\n💵 +${_money(cents)}\n💼 المتاح الآن: ${avail}"
    )
    return True, f"✅ تم شحن ${_money(cents)} في محفظة <code>{uid}</code>\n💼 الرصيد المتاح الآن: <b>${avail}</b>"

def _ap_approve(rid, amount):
    req = pp_get(rid)
    if not req or req.get("status") != "pending":
        return False, "⚠️ هذه الدفعة تمت معالجتها مسبقاً."
    if not kv_set(f"rk:ppdone:{rid}", "1", ex=30 * 86400, nx=True):
        return False, "⚠️ هذه الدفعة تمت معالجتها مسبقاً."
    ok, msg = _ap_credit_wallet(req["uid"], amount, PM_NAME[req["m"]]["ar"])
    if not ok:
        kv_del(f"rk:ppdone:{rid}")
        return False, msg
    req["status"] = "approved"
    req["credited"] = str(amount)
    try:
        pp_save(req)
        kv_del(f"rk:ppu:{req['uid']}")
    except StorageError:
        pass
    pp_set_remove(rid)
    return True, msg

def _ap_reject(rid):
    req = pp_get(rid)
    if not req or req.get("status") != "pending":
        return False, "⚠️ هذه الدفعة تمت معالجتها مسبقاً."
    if not kv_set(f"rk:ppdone:{rid}", "1", ex=30 * 86400, nx=True):
        return False, "⚠️ هذه الدفعة تمت معالجتها مسبقاً."
    req["status"] = "rejected"
    try:
        pp_save(req)
        kv_del(f"rk:ppu:{req['uid']}")
    except StorageError:
        pass
    pp_set_remove(rid)
    lang = get_lang(req["uid"])
    try:
        bot.send_message(int(req["uid"]), pmt(lang, "rejected"), parse_mode="HTML", reply_markup=support_markup(lang))
    except Exception as e:
        print(f"reject notice failed: {e}")
    monitor_send(f"❌ <b>دفعة {PM_NAME[req['m']]['ar']} مرفوضة</b>\n\n👤 {_user_link(req['uid'])}\n💵 ${req['usd']}")
    return True, f"❌ تم رفض الدفعة #{rid} وأُبلغ الزبون."

# ---------- تعديل وصف المنتج ----------
_DESC_CACHE = {"ts": 0, "data": {}}
DESC_KEY = "rk:desc"

def _desc_all():
    if time.time() - _DESC_CACHE["ts"] > 20:
        _DESC_CACHE["ts"] = time.time()
        if db:
            try:
                _DESC_CACHE["data"] = {str(k): str(v) for k, v in (db.hgetall(DESC_KEY) or {}).items()}
            except Exception as e:
                print(f"desc cache error: {e}")
    return _DESC_CACHE["data"]

def _desc_set(pid, lang, text):
    field = f"{pid}:{lang}"
    if db:
        if text is None:
            db.hdel(DESC_KEY, field)
        else:
            db.hset(DESC_KEY, field, text)
    if text is None:
        _DESC_CACHE["data"].pop(field, None)
    else:
        _DESC_CACHE["data"][field] = text

_base_tr = tr

def tr(item, field, lang):
    if field == "description":
        ov = _desc_all().get(f"{item.get('id')}:{lang}")
        if ov:
            return ov
    return _base_tr(item, field, lang)

def show_desc_products(chat_id, msg_id=None):
    mk = InlineKeyboardMarkup(row_width=1)
    for p in products:
        if p.get("type") == "separator" or p.get("id") in REMOVED_OWN:
            continue
        mk.add(InlineKeyboardButton(text=f"{p['icon']} {p['name'][:40]}", callback_data=f"ap_ds_{p['id']}"))
    _pr_show(chat_id, msg_id, "✏️ <b>تعديل وصف منتج</b>\nاختر المنتج:", mk)

def show_desc_langs(chat_id, msg_id, pid):
    p = find_product(pid)
    if not p:
        return show_desc_products(chat_id, msg_id)
    mk = InlineKeyboardMarkup(row_width=3)
    mk.row(*[InlineKeyboardButton(text=n, callback_data=f"ap_dl_{pid}_{c}")
             for c, n in (("ar", "🇩🇿 عربي"), ("en", "🇬🇧 English"), ("fr", "🇫🇷 Français"))])
    mk.add(InlineKeyboardButton(text="⬅️ القائمة", callback_data="ap_dp"))
    _pr_show(chat_id, msg_id, f"✏️ <b>{html.escape(p['name'])}</b>\nاختر لغة الوصف:", mk)

# ---------- طرق الدفع (تفعيل/إيقاف/سعر الصرف) ----------
def show_pm_settings(chat_id, msg_id=None):
    lines = ["⚙️ <b>طرق الدفع</b>\n"]
    mk = InlineKeyboardMarkup(row_width=2)
    for m in ("bd", "fx", "rd"):
        on = pm_enabled(m)
        lines.append(
            f"{PM_ICON[m]} <b>{PM_NAME[m]['ar']}</b>: {'✅ مفعّلة' if on else '⛔ موقوفة'} | "
            + ("بالدولار مباشرة" if m == "rd" else f"1$ = {_fmt_rate(pm_rate(m))} DA") + f" | ⏳ {len(pmw_list(m))} ينتظرون"
        )
        _b_on = InlineKeyboardButton(text=f"✅ تفعيل {PM_NAME[m]['ar']}", callback_data=f"ap_on_{m}")
        _b_on.style = "success"      # التفعيل أخضر
        _b_off = InlineKeyboardButton(text=f"⛔ إيقاف {PM_NAME[m]['ar']}", callback_data=f"ap_off_{m}")
        _b_off.style = "danger"      # الإيقاف أحمر
        mk.row(_b_on, _b_off)
        if m != "rd":
            mk.add(InlineKeyboardButton(text=f"💱 سعر صرف {PM_NAME[m]['ar']}", callback_data=f"ap_rt_{m}"))
    for m in ("rp", "bb"):
        n = len(pmw_list(m))
        if m == "rp" and rdp_ready():
            lines.append(f"💳 <b>RedotPay</b>: {'🧪 Sandbox (للأدمن فقط)' if RDP_SANDBOX else '✅ مفعّلة'} | ⏳ {n} ينتظرون")
        else:
            lines.append(f"🔄 <b>{SOON_NAME[m]}</b>: قريباً | ⏳ {n} ينتظرون")
        if n:
            mk.add(InlineKeyboardButton(text=f"📢 إعلام منتظري {SOON_NAME[m]} (متاح الآن)", callback_data=f"ap_wn_{m}"))
    mk.add(InlineKeyboardButton(text=t("ar", "back"), callback_data="adm_home"))     # رجوع إلى لوحة الأدمن
    _pr_show(chat_id, msg_id, "\n".join(lines), mk)

def _pm_notify_waiters(m):
    ids = pmw_list(m)
    pmw_clear(m)

    def _run():
        sent = 0
        for u in ids:
            lang = get_lang(u)
            mk = InlineKeyboardMarkup()
            mk.add(InlineKeyboardButton(text=t(lang, "kb_products"), callback_data="back_to_main"))
            try:
                bot.send_message(int(u), pmt(lang, "avail").format(method=_mname(m, lang)),
                                 parse_mode="HTML", reply_markup=mk)
                sent += 1
            except Exception as e:
                print(f"pm waiter notify failed: {e}")
            time.sleep(0.05)
        monitor_send(f"🔔 <b>أُعلم {sent} زبون بتوفر {_mname(m, 'ar')}</b>")

    threading.Thread(target=_run, daemon=True).start()
    return len(ids)

# ---------- معالج أزرار الأدمن ap_ ----------
@bot.callback_query_handler(func=lambda c: c.data.startswith("ap_"))
def handle_ap(call):
    if not _is_admin_user(call.from_user.id):
        bot.answer_callback_query(call.id)
        return
    aid = call.from_user.id
    chat_id, msg_id = call.message.chat.id, call.message.message_id
    _ap_wait.pop(aid, None)
    parts = call.data.split(SEP, 2)
    cmd = parts[1] if len(parts) > 1 else ""
    arg = parts[2] if len(parts) > 2 else ""

    if cmd == "l":
        show_pp_list(chat_id, msg_id)
    elif cmd == "v":
        show_pp_view(chat_id, arg)
    elif cmd == "ok":
        req = pp_get(arg)
        if not req or req.get("status") != "pending":
            bot.answer_callback_query(call.id, "⚠️ تمت معالجتها", show_alert=True)
            return
        _ap_set(aid, op="credit", rid=arg)
        mk = InlineKeyboardMarkup(row_width=1)
        mk.add(InlineKeyboardButton(text=(f"✅ مبلغ الطلب كاملاً: {req['usd']}$" if req["m"] == "rd" else f"✅ مبلغ الطلب كاملاً: {req['da']} DA = {req['usd']}$"),
                                    callback_data=f"ap_amt_{arg}_{req['usd']}"))
        mk.add(InlineKeyboardButton(text="❌ إلغاء", callback_data="ap_l"))
        bot.send_message(
            chat_id,
            f"💵 أرسل المبلغ الذي وصلك لشحن محفظة الزبون <code>{req['uid']}</code>:\n"
            + (f"• أرسل المبلغ بالدولار: <code>5</code>" if req["m"] == "rd" else (f"• بالدينار: <code>500</code>\n• أو بالدولار: <code>5$</code>\n\n"
            f"💱 سعر الصرف المعتمد: 1$ = {_fmt_rate(req['rate'])} DA")),
            parse_mode="HTML", reply_markup=mk,
        )
    elif cmd == "amt":
        try:
            rid, usd = arg.rsplit(SEP, 1)
            ok, msg = _ap_approve(rid, Decimal(usd))
        except Exception as e:
            ok, msg = False, f"❌ خطأ: {str(e)[:150]}"
        bot.send_message(chat_id, msg, parse_mode="HTML")
    elif cmd == "cf":
        try:
            rid, usd = arg.rsplit(SEP, 1)
            ok, msg = _ap_approve(rid, Decimal(usd))
        except Exception as e:
            ok, msg = False, f"❌ خطأ: {str(e)[:150]}"
        bot.send_message(chat_id, msg, parse_mode="HTML")
    elif cmd == "no":
        ok, msg = _ap_reject(arg)
        bot.send_message(chat_id, msg, parse_mode="HTML")
    elif cmd == "wt":
        _ap_set(aid, op="wtop", step="id")
        bot.send_message(chat_id, "🆔 أرسل ID الزبون الذي تريد شحن محفظته:\n(أو /admin للإلغاء)")
    elif cmd == "dp":
        show_desc_products(chat_id, msg_id)
    elif cmd == "ds":
        show_desc_langs(chat_id, msg_id, arg)
    elif cmd in ("dl", "dr"):
        try:
            pid, lg = arg.rsplit(SEP, 1)
            p = find_product(pid)
            if not p or lg not in SUPPORTED_LANGS:
                raise ValueError("bad")
        except Exception:
            bot.answer_callback_query(call.id)
            return
        if cmd == "dr":
            try:
                _desc_set(pid, lg, None)
            except Exception as e:
                bot.answer_callback_query(call.id, f"خطأ: {str(e)[:120]}", show_alert=True)
                return
            bot.answer_callback_query(call.id, "↩️ رجع الوصف الأصلي", show_alert=True)
            show_desc_langs(chat_id, msg_id, pid)
            return
        cur = _base_tr(p, "description", lg)
        shown = _desc_all().get(f"{pid}:{lg}")
        _ap_set(aid, op="desc", pid=pid, lang=lg)
        mk = InlineKeyboardMarkup(row_width=1)
        mk.add(InlineKeyboardButton(text="↩️ استرجاع الأصلي", callback_data=f"ap_dr_{pid}_{lg}"))
        mk.add(InlineKeyboardButton(text="❌ إلغاء", callback_data=f"ap_ds_{pid}"))
        bot.send_message(
            chat_id,
            f"✏️ <b>{html.escape(p['name'])}</b> ({lg})\n\n"
            f"📄 الوصف الحالي{' (معدّل)' if shown else ''}:\n<pre>{html.escape((shown or cur)[:900])}</pre>\n\n"
            f"أرسل الوصف الجديد كرسالة واحدة.\n⚠️ الأفضل أن لا يتجاوز 1000 حرف.",
            parse_mode="HTML", reply_markup=mk,
        )
    elif cmd in ("on", "off"):
        if arg in PM_NAME:
            was = pm_enabled(arg)
            kv_set(f"rk:pm:on:{arg}", "1" if cmd == "on" else "0")
            monitor_send(f"⚙️ <b>{PM_NAME[arg]['ar']}</b>: {'✅ تم التفعيل' if cmd == 'on' else '⛔ تم الإيقاف'}")
            if cmd == "on" and not was:
                n = _pm_notify_waiters(arg)
                bot.send_message(chat_id, f"✅ تم تفعيل {PM_NAME[arg]['ar']}. أُعلم {n} زبون كانوا ينتظرون.")
            show_pm_settings(chat_id, msg_id)
    elif cmd == "rt":
        if arg in PM_NAME:
            _ap_set(aid, op="rate", m=arg)
            bot.send_message(
                chat_id,
                f"💱 أرسل سعر الصرف الجديد لـ {PM_NAME[arg]['ar']} (الحالي: {_fmt_rate(pm_rate(arg))} DA لكل 1$)\nمثال: <code>260</code>",
                parse_mode="HTML",
            )
    elif cmd in ("pr5", "pr2", "prg"):
        ok, msg = add_manual_purchase_mode(arg, {"pr5": "5", "pr2": "2", "prg": "g"}[cmd])
        bot.send_message(chat_id, msg, parse_mode="HTML")
    elif cmd == "prx":
        bot.send_message(chat_id, "❌ أُلغي تسجيل الشراء.")
    elif cmd == "wn":
        if arg in SOON_NAME:
            n = _pm_notify_waiters(arg)
            bot.send_message(chat_id, f"📢 جاري إعلام {n} زبون بتوفر {SOON_NAME[arg]}.")
            show_pm_settings(chat_id, msg_id)
    elif cmd == "pm":
        show_pm_settings(chat_id, msg_id)
    bot.answer_callback_query(call.id)

def _awaiting_ap(m):
    try:
        if (not m.text or m.text.startswith("/") or m.chat.type != "private"
                or not _is_admin_user(m.from_user.id)):
            return False
        st = _ap_wait.get(m.from_user.id)
        if not st:
            return False
        if time.time() - st.get("t", 0) > 900:
            _ap_wait.pop(m.from_user.id, None)
            return False
        return True
    except Exception:
        return False

@bot.message_handler(func=_awaiting_ap, content_types=["text"])
def handle_ap_text(message):
    aid = message.from_user.id
    st = _ap_wait[aid]
    text = message.text.strip()
    op = st["op"]

    if op == "credit":
        req = pp_get(st["rid"])
        if not req or req.get("status") != "pending":
            _ap_wait.pop(aid, None)
            bot.reply_to(message, "⚠️ هذه الدفعة تمت معالجتها.")
            return
        rate = Decimal(str(req.get("rate") or pm_rate(req["m"])))
        parsed = _parse_amount_input(text, rate)
        if not parsed:
            bot.reply_to(message, "❌ مبلغ غير صالح. أرسل مثلاً: 500 (دينار) أو 5$ (دولار)")
            return
        usd, da = parsed
        _ap_wait.pop(aid, None)
        calc = (f"{da} DA ÷ {_fmt_rate(rate)} = <b>{usd}$</b>" if da is not None else f"<b>{usd}$</b>")
        mk = InlineKeyboardMarkup(row_width=1)
        mk.add(InlineKeyboardButton(text=f"✅ تأكيد شحن {usd}$", callback_data=f"ap_cf_{st['rid']}_{usd}"))
        mk.add(InlineKeyboardButton(text="❌ إلغاء", callback_data=f"ap_v_{st['rid']}"))
        bot.send_message(
            message.chat.id,
            f"🧮 {calc}\n\nسيُضاف <b>{usd}$</b> إلى محفظة الزبون <code>{req['uid']}</code>. تأكيد؟",
            parse_mode="HTML", reply_markup=mk,
        )
        return

    if op == "wtop":
        if st["step"] == "id":
            if not text.isdigit():
                bot.reply_to(message, "❌ ID غير صالح، أرسل أرقاماً فقط.")
                return
            err = _adm_precheck(text)
            if err:
                bot.reply_to(message, err)
                return
            st["uid"] = text
            st["step"] = "amount"
            st["t"] = time.time()
            bot.reply_to(message, "💵 أرسل المبلغ بالدولار (مثال: 5):")
            return
        amount = _parse_price(text)
        if amount is None:
            bot.reply_to(message, "❌ مبلغ غير صالح. أرسل مثلاً: 5")
            return
        _ap_wait.pop(aid, None)
        ok, msg = _ap_credit_wallet(st["uid"], amount, "شحن من الأدمن")
        bot.send_message(message.chat.id, msg, parse_mode="HTML")
        return

    if op == "desc":
        _ap_wait.pop(aid, None)
        try:
            _desc_set(st["pid"], st["lang"], text)
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ خطأ في الحفظ: {str(e)[:150]}")
            return
        warn = "\n⚠️ الوصف طويل (أكثر من 1000 حرف)، سيظهر بدون صورة." if len(text) > 1000 else ""
        bot.send_message(message.chat.id, f"✅ تم حفظ الوصف ({st['lang']}) وهو ظاهر للزبائن الآن.{warn}")
        monitor_send(f"✏️ <b>تعديل وصف</b>: {html.escape(st['pid'])} ({st['lang']})")
        return

    if op == "rate":
        try:
            rate = Decimal(text.replace(",", ".").replace("،", "."))
            if rate <= 0 or rate > 100000:
                raise InvalidOperation
        except InvalidOperation:
            bot.reply_to(message, "❌ رقم غير صالح. أرسل مثلاً: 260")
            return
        _ap_wait.pop(aid, None)
        kv_set(f"rk:pm:rate:{st['m']}", str(rate))
        bot.send_message(message.chat.id,
                         f"✅ سعر صرف {PM_NAME[st['m']]['ar']} الآن: 1$ = {_fmt_rate(rate)} DA")
        monitor_send(f"💱 <b>سعر صرف {PM_NAME[st['m']]['ar']}</b>: 1$ = {_fmt_rate(rate)} DA")
        return

# ---------- نص الزبون (رسالة Flixy) ----------
def _awaiting_proof_text(m):
    try:
        if not m.text or m.text.startswith("/") or m.chat.type != "private":
            return False
        return _pp_active(m.from_user.id) is not None
    except Exception:
        return False

@bot.message_handler(func=_awaiting_proof_text, content_types=["text"])
def handle_proof_text(message):
    _pp_submit(message, False)



# ============================================================
# ========== بوابة القناة + قائمة "ابدأ" + نظام الإحالة ==========
# ============================================================
CHANNEL_NAME = "Raseedkom store"
REF_NEED_U = int(REF_NEED_USERS)
REF_NEED_C = int(Decimal(str(REF_NEED_USD)) * 100)       # بالسنت
REF_REWARD_C = int(Decimal(str(REF_REWARD_USD)) * 100)   # بالسنت

GATE_TEXT = (
    "👋 Welcome to RASEEDKOM store!\n\n"
    "📢 To use the bot, you must join our official channel first.\n\n"
    "1️⃣ Tap «Raseedkom store» below and join the channel\n"
    "2️⃣ Come back here and tap «✅ Verify»"
)
GATE_FAIL = "❌ You haven't joined the channel yet. Please join it first, then tap Verify."

def channel_id():
    try:
        v = kv_get("rk:channel_id")
        return int(v) if v else None
    except Exception:
        return None

def gate_enabled():
    try:
        return str(kv_get("rk:gate:off")) != "1"
    except Exception:
        return True

def _is_member(chat_id, uid):
    """True / False، أو None عند تعذر التحقق (البوت ليس أدمن مثلاً)."""
    try:
        st = bot.get_chat_member(chat_id, uid)
        if st.status in ("member", "administrator", "creator"):
            return True
        if st.status == "restricted" and getattr(st, "is_member", False):
            return True
        return False
    except Exception as e:
        print(f"get_chat_member error: {e}")
        monitor_send(
            "🚨 <b>تعذر التحقق من اشتراك القناة</b>\nتأكد أن البوت أدمن في القناة.\n"
            f"<code>{html.escape(str(e))[:200]}</code>", key="gate_err", cooldown=3600)
        return None

def _gate_markup():
    mk = InlineKeyboardMarkup(row_width=1)
    mk.add(InlineKeyboardButton(text=f"📢 {CHANNEL_NAME}", url=CHANNEL_LINK))
    mk.add(InlineKeyboardButton(text="✅ Verify", callback_data="gate_verify"))
    return mk

def gate_ok(chat_id, uid):
    """True = يُسمح له بالمتابعة. وإلا نرسل رسالة الاشتراك."""
    try:
        if str(uid) == str(ADMIN_CHAT_ID) or not gate_enabled():
            return True
        cid = channel_id()
        if not cid:
            return True
        res = _is_member(cid, uid)
        if res is None or res:
            return True
        bot.send_message(chat_id, GATE_TEXT, reply_markup=_gate_markup())
        return False
    except Exception as e:
        print(f"gate_ok error: {e}")
        return True

# ---------- الإحالة: التسجيل ----------
def _ref_capture(message):
    """يحفظ المُحيل لزبون جديد فقط (أول رابط فقط، ولا يتبدل)."""
    try:
        uid = message.from_user.id
        parts = (message.text or "").split(maxsplit=1)
        if len(parts) < 2 or not parts[1].startswith("ref" + SEP):
            return
        rid = parts[1][4:]
        if not rid.isdigit() or int(rid) == uid:
            return
        if str(uid) in known_users or str(uid) in user_lang:
            return  # ليس جديداً
        if str(rid) not in known_users and str(rid) not in user_lang:
            return
        kv_set(f"rk:refp:{uid}", rid, ex=30 * 86400, nx=True)
    except Exception as e:
        print(f"ref capture error: {e}")

def _ref_finalize(uid):
    try:
        rid = kv_get(f"rk:refp:{uid}")
        if not rid:
            return
        rid = str(rid)
        if kv_set(f"rk:ref:of:{uid}", rid, nx=True):
            _sadd(f"rk:ref:list:{rid}", str(uid))
            _ref_grant_coins(rid, uid)
        kv_del(f"rk:refp:{uid}")
    except Exception as e:
        print(f"ref finalize error: {e}")

def start_gate(message):
    """يُستدعى أول /start: True = أوقف المعالجة (ظهرت رسالة الاشتراك أو فُتح مسار الشراء)."""
    uid = message.from_user.id
    _ref_capture(message)
    qb = _qb_param(message)
    if qb:
        try:
            kv_set(f"rk:qb:{uid}", qb, ex=3600)
        except Exception:
            pass
    ok = gate_ok(message.chat.id, uid)
    if not ok:
        return True
    _ref_finalize(uid)
    if qb and str(uid) in user_lang:
        register_user(uid)
        ensure_profile(uid, message.from_user.first_name)
        send_persistent_menu(message.chat.id, get_lang(uid))
        _resume_quick_buy(message.chat.id, message.from_user)
        return True
    return False

@bot.callback_query_handler(func=lambda c: c.data == "gate_verify")
def handle_gate_verify(call):
    uid = call.from_user.id
    cid = channel_id()
    res = _is_member(cid, uid) if cid else True
    if res is False and str(uid) != str(ADMIN_CHAT_ID):
        bot.answer_callback_query(call.id, GATE_FAIL, show_alert=True)
        return
    _ref_finalize(uid)
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    bot.answer_callback_query(call.id)
    refresh_for_user(call.message.chat.id, uid)
    if str(uid) in user_lang:
        _resume_quick_buy(call.message.chat.id, call.from_user)

# ---------- ضبط القناة تلقائياً + حظر البوت ----------
try:
    @bot.channel_post_handler(func=lambda m: True)
    def handle_channel_post(message):
        try:
            txt = (message.text or "").strip()
            if channel_id() is None or txt.startswith("/setchannel"):
                kv_set("rk:channel_id", str(message.chat.id))
                alert_admin(f"✅ <b>تم ضبط القناة</b>\n{html.escape(message.chat.title or '')}\n<code>{message.chat.id}</code>\n"
                            "بوابة الاشتراك والإحالات تعمل الآن.")
        except Exception as e:
            print(f"channel post error: {e}")
except AttributeError:
    print("channel_post_handler unavailable")

try:
    @bot.my_chat_member_handler(func=lambda m: True)
    def handle_my_chat_member(update):
        try:
            if update.chat.type != "private":
                return
            uid = update.from_user.id
            st = update.new_chat_member.status
            if st in ("kicked", "left"):
                kv_set(f"rk:blocked:{uid}", "1")
            elif st == "member":
                kv_del(f"rk:blocked:{uid}")
        except Exception as e:
            print(f"my_chat_member error: {e}")
except AttributeError:
    print("my_chat_member_handler unavailable")

@bot.message_handler(commands=["gate", "gateon", "gateoff"])
def gate_command(message):
    if not is_admin_msg(message):
        return
    cmd = message.text.split()[0].lstrip("/").split("@")[0]
    if cmd == "gateon":
        kv_set("rk:gate:off", "0")
    elif cmd == "gateoff":
        kv_set("rk:gate:off", "1")
    bot.reply_to(message, f"🚪 البوابة: {'✅ مفعّلة' if gate_enabled() else '⛔ موقوفة'}\n📢 القناة: {channel_id() or 'غير مضبوطة (أرسل أي رسالة في القناة)'}")

# ---------- نصوص ----------
SM_TEXTS = {
    "ar": {
        "menu": "🎉 مرحباً بك! 🎉\n\n🎯 دليل سريع:\n1. اضغط على «🛒 شراء»\n2. اختر المنتج الذي تريده\n3. أكمل الدفع\n4. بعد الدفع، أرسل رقم الطلب للتحقق\n\n🎯 اختر خياراً:",
        "buy": "🏪 شراء", "game": "🎮 لعبة · من سيفوز؟", "ref": "👥 الإحالة", "api": "🔌 API", "channel": "📢 القناة الرئيسية",
    },
    "en": {
        "menu": "🎉 Welcome! 🎉\n\n🎯 Quick guide:\n1. Tap «🛒 Buy»\n2. Choose the product you want\n3. Complete the payment\n4. After payment, send the order number for verification\n\n🎯 Choose an option:",
        "buy": "🏪 Buy", "game": "🎮 Game · Who will win?", "ref": "👥 Referral", "api": "🔌 API", "channel": "📢 Main channel",
    },
    "fr": {
        "menu": "🎉 Bienvenue ! 🎉\n\n🎯 Guide rapide :\n1. Appuyez sur « 🛒 Acheter »\n2. Choisissez le produit souhaité\n3. Effectuez le paiement\n4. Après le paiement, envoyez le numéro de commande pour vérification\n\n🎯 Choisissez une option :",
        "buy": "🏪 Acheter", "game": "🎮 Jeu · Qui va gagner ?", "ref": "👥 Parrainage", "api": "🔌 API", "channel": "📢 Canal principal",
    },
}

def smt(lang, key):
    return SM_TEXTS.get(lang, SM_TEXTS["ar"])[key]

REF_TEXTS = {
    "ar": {
        "page": "👥 <b>برنامج الإحالة</b>\n\nادعُ أصدقاءك عبر رابطك الخاص، واحصل على <b>{reward}$</b> في محفظتك عند استيفاء الشرطين التاليين:\n• أن يبلغ عدد المُحالين النشطين <b>{need_u}</b> عضواً.\n• أن يبلغ مجموع مشترياتهم <b>{need_usd}$</b>.\n\n🔗 رابطك الخاص:\n<code>{link}</code>\n\n📊 <b>إحصائياتك:</b>\n👥 عدد المُحالين: <b>{total}</b>\n✅ المُحالون النشطون: <b>{active} / {need_u}</b>\n💵 مجموع مشترياتهم: <b>{spent}$ / {need_usd}$</b>\n\nℹ️ المُحال النشط هو من بقي مشتركاً في القناة ولم يحظر البوت. تُمنح المكافأة مرة واحدة فقط لكل مستخدم.",
        "claimed": "\n\n✅ تم استلام المكافأة.",
        "copy": "📋 نسخ الرابط",
        "claim": "🎁 إضافة {reward}$ إلى المحفظة",
        "ok": "✅ تمت إضافة {reward}$ إلى محفظتك بنجاح.",
        "already": "ℹ️ سبق أن استلمت هذه المكافأة.",
        "missing": "⚠️ لم تكتمل الشروط بعد.",
        "m_users": "• ينقصك {n} إحالة نشطة",
        "m_spent": "• ينقصك {x}$ من مشتريات المُحالين",
        "error": "⚠️ حدث خطأ مؤقت، حاول لاحقاً.",
    },
    "en": {
        "page": "👥 <b>Referral program</b>\n\nInvite your friends with your personal link and get <b>{reward}$</b> in your wallet once both conditions are met:\n• Your active referrals reach <b>{need_u}</b> members.\n• Their total purchases reach <b>{need_usd}$</b>.\n\n🔗 Your personal link:\n<code>{link}</code>\n\n📊 <b>Your stats:</b>\n👥 Referred users: <b>{total}</b>\n✅ Active referrals: <b>{active} / {need_u}</b>\n💵 Their total purchases: <b>{spent}$ / {need_usd}$</b>\n\nℹ️ An active referral is someone who is still subscribed to the channel and has not blocked the bot. The reward is granted only once per user.",
        "claimed": "\n\n✅ Reward claimed.",
        "copy": "📋 Copy link",
        "claim": "🎁 Add {reward}$ to wallet",
        "ok": "✅ {reward}$ has been added to your wallet.",
        "already": "ℹ️ You have already claimed this reward.",
        "missing": "⚠️ The conditions are not met yet.",
        "m_users": "• You need {n} more active referrals",
        "m_spent": "• You need {x}$ more in referral purchases",
        "error": "⚠️ Temporary error, try again later.",
    },
    "fr": {
        "page": "👥 <b>Programme de parrainage</b>\n\nInvitez vos amis avec votre lien personnel et recevez <b>{reward}$</b> dans votre portefeuille lorsque les deux conditions sont remplies :\n• Vos filleuls actifs atteignent <b>{need_u}</b> membres.\n• Le total de leurs achats atteint <b>{need_usd}$</b>.\n\n🔗 Votre lien personnel :\n<code>{link}</code>\n\n📊 <b>Vos statistiques :</b>\n👥 Filleuls : <b>{total}</b>\n✅ Filleuls actifs : <b>{active} / {need_u}</b>\n💵 Total de leurs achats : <b>{spent}$ / {need_usd}$</b>\n\nℹ️ Un filleul actif est une personne toujours abonnée au canal et n'ayant pas bloqué le bot. La récompense n'est accordée qu'une seule fois par utilisateur.",
        "claimed": "\n\n✅ Récompense récupérée.",
        "copy": "📋 Copier le lien",
        "claim": "🎁 Ajouter {reward}$ au portefeuille",
        "ok": "✅ {reward}$ ont été ajoutés à votre portefeuille.",
        "already": "ℹ️ Vous avez déjà récupéré cette récompense.",
        "missing": "⚠️ Les conditions ne sont pas encore remplies.",
        "m_users": "• Il vous manque {n} filleuls actifs",
        "m_spent": "• Il vous manque {x}$ d'achats de vos filleuls",
        "error": "⚠️ Erreur temporaire, réessayez plus tard.",
    },
}

def rft(lang, key):
    return REF_TEXTS.get(lang, REF_TEXTS["ar"])[key]

# ---------- قائمة "ابدأ" ----------
def start_menu_markup(lang):
    def _h(b, eid):
        b.icon_dyn = eid     # أيقونة مخصصة لهذه القائمة (تُطبّق وقت الإرسال)
        return b
    mk = InlineKeyboardMarkup(row_width=2)
    mk.add(_h(InlineKeyboardButton(text=smt(lang, "buy"), callback_data="back_to_main"), ICON_BUY))
    mk.add(InlineKeyboardButton(text=wt(lang, "btn_wallet"), callback_data="pf_wallet"))
    mk.add(_h(InlineKeyboardButton(text=smt(lang, "game"), callback_data="sm_game"), ICON_MENU_GAME))
    try:
        if not _vt_conf().get("nostyle"):
            mk.keyboard[0][0].style = "success"    # شراء أخضر
            mk.keyboard[2][0].style = "danger"     # لعبة · من سيفوز؟ أحمر
    except Exception:
        pass
    mk.row(InlineKeyboardButton(text=wt(lang, "btn_profile"), callback_data="pf_profile"),
           _h(InlineKeyboardButton(text=wt(lang, "btn_history"), callback_data="pf_hist"), ICON_HIST_M))
    mk.row(_h(InlineKeyboardButton(text=t(lang, "kb_support"), url=MY_PRIVATE_CHAT_LINK), ICON_SUPPORT),
           InlineKeyboardButton(text=smt(lang, "ref"), callback_data="rf_o_s"))
    mk.add(_h(InlineKeyboardButton(text=smt(lang, "api"), callback_data="sm_api"), ICON_MENU_API))
    mk.add(_h(InlineKeyboardButton(text=smt(lang, "channel"), url=CHANNEL_LINK), ICON_MENU_CHANNEL))
    mk.add(InlineKeyboardButton(text=t(lang, "change_lang"), callback_data="change_lang"))
    return mk

def send_start_menu(chat_id, lang):
    bot.send_message(chat_id, smt(lang, "menu"), reply_markup=start_menu_markup(lang))

@bot.callback_query_handler(func=lambda c: c.data in ("sm_home", "sm_game", "sm_api"))
def handle_sm(call):
    lang = get_lang(call.from_user.id)
    if call.data == "sm_home":
        _pf_show(call, smt(lang, "menu"), start_menu_markup(lang))
    elif call.data == "sm_game" and db:
        try:
            register_user(call.from_user.id)
            gm_hub(call, lang, "s")
        except Exception as e:
            print(f"hub error: {e}")
    else:
        mk = InlineKeyboardMarkup(row_width=1)
        mk.add(InlineKeyboardButton(text=t(lang, "notify_me"), callback_data="api_nt"))
        mk.add(InlineKeyboardButton(text=t(lang, "back"), callback_data="sm_home"))
        _pf_show(call, pmt(lang, "soon"), mk)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == "api_nt")
def handle_api_notify(call):
    lang = get_lang(call.from_user.id)
    try:
        _sadd("rk:notify:api", str(call.from_user.id))
    except Exception as e:
        print(f"api notify failed: {e}")
    bot.answer_callback_query(call.id, GIFT_NOTIFY_TX.get(lang, GIFT_NOTIFY_TX["ar"]).replace("هذه القيمة", "خدمة API").replace("this amount", "the API service").replace("ce montant", "le service API"), show_alert=True)

# ---------- الإحالة: الإحصائيات والصفحة ----------
_act_cache = {}

def _ref_active(r):
    try:
        if str(kv_get(f"rk:blocked:{r}")) == "1":
            return False
    except Exception:
        pass
    cid = channel_id()
    if not cid or not gate_enabled():
        return True
    c = _act_cache.get(r)
    if c and time.time() - c[0] < 120:
        return c[1]
    res = _is_member(cid, int(r))
    ok = True if res is None else bool(res)  # عند الخطأ لا نظلم المُحيل
    _act_cache[r] = (time.time(), ok)
    return ok

def _spent_c(r):
    if not db:
        return 0
    try:
        return int(float(db.hget(_prof_key(r), "spent_c") or 0))
    except Exception:
        return 0

def ref_stats(uid):
    members = sorted(_smembers(f"rk:ref:list:{uid}"))[:300]
    active = spent = 0
    for r in members:
        if _ref_active(r):
            active += 1
        spent += _spent_c(r)
    return len(members), active, spent

def _ref_link(uid):
    return f"{BOT_LINK}?start=ref{SEP}{uid}"

@bot.message_handler(commands=["refstats"])
def refstats_command(message):
    """للأدمن: إحصائيات إحالة أي شخص (صانع محتوى) بلا حد 300."""
    if str(message.chat.id) != str(ADMIN_CHAT_ID):
        return
    a = (message.text or "").split()
    if len(a) < 2 or not a[1].isdigit():
        bot.reply_to(message, "الاستعمال: /refstats ID\nمثال: /refstats 8491461365")
        return
    rid = a[1]
    ph = bot.reply_to(message, "⏳ جاري الحساب...")
    try:
        from concurrent.futures import ThreadPoolExecutor
        members = sorted(_smembers(f"rk:ref:list:{rid}"))
        with ThreadPoolExecutor(max_workers=8) as ex:
            act = list(ex.map(lambda r: bool(_ref_active(r)), members))
        spent_each = [_spent_c(r) for r in members]
        total = len(members)
        active = sum(1 for x in act if x)
        buyers = sum(1 for s in spent_each if s > 0)
        spent_all = sum(spent_each)
        spent_active = sum(s for s, x in zip(spent_each, act) if x)
        text = (
            f"📊 <b>إحصائيات الإحالة</b>\n🆔 <code>{rid}</code>\n\n"
            f"👥 عدد المُحالين: <b>{total}</b>\n"
            f"✅ النشطون: <b>{active}</b>\n"
            f"🛒 اشترى منهم: <b>{buyers}</b>\n"
            f"💵 مجموع مشترياتهم: <b>{_money(spent_all)}$</b>\n"
            f"💵 مشتريات النشطين فقط: <b>{_money(spent_active)}$</b>\n\n"
            f"🔗 <code>{_ref_link(rid)}</code>"
        )
    except Exception as e:
        text = f"❌ خطأ: {html.escape(str(e))[:200]}"
    try:
        bot.edit_message_text(text, message.chat.id, ph.message_id, parse_mode="HTML")
    except Exception:
        bot.send_message(message.chat.id, text, parse_mode="HTML")

def _ref_show(call, lang, src):
    uid = call.from_user.id
    total, active, spent_c = ref_stats(uid)
    claimed = kv_get(f"rk:ref:claimed:{uid}") is not None
    text = rft(lang, "page").format(
        reward=_money(REF_REWARD_C), need_u=REF_NEED_U, need_usd=_money(REF_NEED_C),
        link=_ref_link(uid), total=total, active=active, spent=_money(spent_c),
    )
    plain_text = text
    if not _icons_off():
        for _em, _id in (("🔗", "5271604874419647061"), ("📊", "5386367538735104399"), ("👥", "4909043075529048789"),
                         ("✅", "5463122435425448565"), ("💵", "5357484575159244309")):
            text = text.replace("\n" + _em + " ", f'\n<tg-emoji emoji-id="{_id}">{_em}</tg-emoji> ')
    if claimed:
        text += rft(lang, "claimed")
        plain_text += rft(lang, "claimed")
    mk = InlineKeyboardMarkup(row_width=1)
    link = _ref_link(uid)
    btn = None
    if CopyTextButton is not None:
        try:
            btn = InlineKeyboardButton(text=rft(lang, "copy"), copy_text=CopyTextButton(text=link))
        except Exception:
            btn = None
    mk.add(btn or InlineKeyboardButton(text=rft(lang, "copy"), callback_data="rf_cp"))
    mk.add(InlineKeyboardButton(text=rft(lang, "claim").format(reward=_money(REF_REWARD_C)), callback_data=f"rf_c_{src}"))
    mk.add(InlineKeyboardButton(text=t(lang, "back"), callback_data="back_to_main" if src == "m" else "sm_home"))
    try:
        _pf_show(call, text, mk)
    except Exception as e:
        print(f"ref page custom emoji failed: {e}")
        _pf_show(call, plain_text, mk)

@bot.callback_query_handler(func=lambda c: c.data.startswith("rf_"))
def handle_referral(call):
    uid = call.from_user.id
    lang = get_lang(uid)
    parts = call.data.split(SEP, 2)
    cmd = parts[1] if len(parts) > 1 else ""
    src = parts[2] if len(parts) > 2 and parts[2] in ("m", "s") else "m"
    if not db:
        bot.answer_callback_query(call.id, wt(lang, "unavailable"), show_alert=True)
        return
    register_user(uid)
    ensure_profile(uid, call.from_user.first_name)

    if cmd == "cp":
        bot.answer_callback_query(call.id, _ref_link(uid), show_alert=True)
        return
    if cmd == "o":
        _ref_show(call, lang, src)
        bot.answer_callback_query(call.id)
        return
    if cmd == "c":
        if kv_get(f"rk:ref:claimed:{uid}") is not None:
            bot.answer_callback_query(call.id, rft(lang, "already"), show_alert=True)
            return
        total, active, spent_c = ref_stats(uid)
        miss = []
        if active < REF_NEED_U:
            miss.append(rft(lang, "m_users").format(n=REF_NEED_U - active))
        if spent_c < REF_NEED_C:
            miss.append(rft(lang, "m_spent").format(x=_money(REF_NEED_C - spent_c)))
        if miss:
            bot.answer_callback_query(call.id, rft(lang, "missing") + "\n" + "\n".join(miss), show_alert=True)
            return
        if not kv_set(f"rk:ref:claimed:{uid}", "1", nx=True):
            bot.answer_callback_query(call.id, rft(lang, "already"), show_alert=True)
            return
        try:
            wallet_credit(uid, REF_REWARD_C, "referral", "referral")
        except Exception as e:
            print(f"referral credit error: {e}")
            kv_del(f"rk:ref:claimed:{uid}")
            bot.answer_callback_query(call.id, rft(lang, "error"), show_alert=True)
            return
        bot.answer_callback_query(call.id, rft(lang, "ok").format(reward=_money(REF_REWARD_C)), show_alert=True)
        monitor_send(f"🎁 <b>مكافأة إحالة</b>\n\n👤 {_user_link(uid)}\n👥 نشطون: {active} | 💵 مشتريات: ${_money(spent_c)}\n➕ ${_money(REF_REWARD_C)} في المحفظة")
        _ref_show(call, lang, src)
        return
    bot.answer_callback_query(call.id)

# ============================================================
# ========== "اطلب الآن" من الإشعارات + القائمة السفلية + أزرار المنتجات ==========
# ============================================================
import types as _types

_orig_answer_cq = bot.answer_callback_query

def _safe_answer_cq(callback_query_id, *a, **k):
    if str(callback_query_id) == "qb":   # نداء داخلي (رابط /start) لا يملك callback حقيقي
        return True
    return _orig_answer_cq(callback_query_id, *a, **k)

bot.answer_callback_query = _safe_answer_cq

def _qb_dispatch(call, pid):
    """يفتح مسار الشراء مباشرة: طرق الدفع، أو اختيار الكمية/القيمة أولاً."""
    try:
        if _maint_blocked_user(call.from_user):          # وضع التحديث: لا شراء مباشر
            _lg = get_lang(call.from_user.id) if str(call.from_user.id) in user_lang else "ar"
            send_maintenance(call.message.chat.id, _lg)
            bot.answer_callback_query(call.id)
            return
    except Exception as e:
        print(f"maint qb check failed: {e}")
    product = find_product(pid)
    if not product or product.get("type") == "separator":
        bot.answer_callback_query(call.id)
        return
    sync_prices()
    call.data = f"buy{SEP}{pid}"
    if pid == GEMINI_ID:
        handle_gemini_select(call)
    elif pid in GIFT_VARIANTS:
        handle_gift_card_select(call)
    elif pid in MANUAL_IDS and pid != FREEFIRE_ID and _manual_in_stock(pid):
        _start_manual_invoice(call, pid)
    else:
        handle_product_view(call)   # Free Fire (الباقات) أو منتج نفد (زر أعلمني)

def _qb_run(chat_id, from_user, pid):
    try:
        ph = bot.send_message(chat_id, "⏳")
        fake = _types.SimpleNamespace(id="qb", from_user=from_user, message=ph, data="")
        _qb_dispatch(fake, pid)
    except Exception as e:
        print(f"quick buy error: {e}")

def _qb_param(message):
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) > 1 and parts[1].startswith("qb" + SEP):
        return parts[1][3:]
    return None

def _resume_quick_buy(chat_id, from_user):
    try:
        pid = kv_get(f"rk:qb:{from_user.id}")
        if pid:
            kv_del(f"rk:qb:{from_user.id}")
            _qb_run(chat_id, from_user, str(pid))
    except Exception as e:
        print(f"resume quick buy error: {e}")

@bot.callback_query_handler(func=lambda c: c.data.startswith("qb" + SEP))
def handle_quick_buy(call):
    _qb_dispatch(call, call.data[3:])

@bot.callback_query_handler(func=lambda c: c.data in ("mn_refresh", "mn_start"))
def handle_mn(call):
    uid = call.from_user.id
    lang = get_lang(uid)
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    bot.answer_callback_query(call.id)
    if call.data == "mn_refresh":
        refresh_for_user(call.message.chat.id, uid)
    elif gate_ok(call.message.chat.id, uid):
        send_start_menu(call.message.chat.id, lang)

def build_reply_keyboard(lang):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton(t(lang, "kb_start")), KeyboardButton(t(lang, "kb_products")))
    markup.row(KeyboardButton(t(lang, "kb_update")), KeyboardButton(t(lang, "kb_lang")))
    markup.row(KeyboardButton(t(lang, "kb_support")))
    return markup


# ============================================================
# ========== الألعاب: Raseedkom Coins + الهدية اليومية + الترتيب الشهري ==========
# ============================================================
LB_TOP_N = 10
LB_MASK_NAMES = False   # True = إخفاء جزء من الأسماء (مثل Ah***)

def _now_dz():
    return time.time() + 3600   # توقيت الجزائر UTC+1

def _day_key():
    return time.strftime("%Y-%m-%d", time.gmtime(_now_dz()))

def _month_key(back=0):
    g = time.gmtime(_now_dz())
    y, m = g.tm_year, g.tm_mon - back
    while m < 1:
        m += 12
        y -= 1
    return f"{y}-{m:02d}"

def _secs_to_midnight():
    return int(86400 - (_now_dz() % 86400))

# ---------- محفظة الكوينز (Upstash) ----------
def _ck(uid):
    return f"rk:coin:{uid}"

def coins_get(uid):
    try:
        return int(float(db.hget(_ck(uid), "bal") or 0))
    except Exception:
        return 0

def lb_score_add(uid, n):
    """يضيف نقاطاً إلى ترتيب الشهر الحالي (الألعاب تمرر صافي الربح)."""
    if n and int(n) > 0:
        db.zincrby(f"rk:lb:{_month_key()}", int(n), str(uid))

def _coin_log(uid, n, note):
    try:
        key = f"rk:coinlog:{uid}"
        db.lpush(key, json.dumps({"n": int(n), "w": note, "t": int(time.time())}, ensure_ascii=False))
        db.ltrim(key, 0, 29)
    except Exception as e:
        print(f"coin log error: {e}")

def coins_add(uid, n, note="", score=True):
    """يضيف كوينز (ويرفع نقاط الشهر إن score). يرجع الرصيد الجديد."""
    n = int(n)
    new = int(db.hincrby(_ck(uid), "bal", n))
    if n > 0:
        db.hincrby(_ck(uid), "earned", n)
        if score:
            lb_score_add(uid, n)
    _coin_log(uid, n, note)
    return new

def coins_take(uid, n, note=""):
    """يخصم كوينز إن كان الرصيد يكفي. يرجع True/False."""
    n = int(n)
    new = int(db.hincrby(_ck(uid), "bal", -n))
    if new < 0:
        db.hincrby(_ck(uid), "bal", n)
        return False
    _coin_log(uid, -n, note)
    return True

def _gift_claim(uid):
    """يرجع (True, الرصيد الجديد) أو (False, None) إذا استلمها اليوم."""
    key = f"rk:coin:gift:{uid}:{_day_key()}"
    if not kv_set(key, "1", ex=3 * 86400, nx=True):
        return False, None
    try:
        return True, coins_add(uid, DAILY_GIFT_COINS, "daily")
    except Exception as e:
        print(f"gift error: {e}")
        kv_del(key)
        raise

def _gift_claimed_today(uid):
    try:
        return kv_get(f"rk:coin:gift:{uid}:{_day_key()}") is not None
    except Exception:
        return False

# ---------- الترتيب الشهري ----------
def _parse_zr(res):
    out = []
    if not res:
        return out
    if isinstance(res[0], (list, tuple)):
        for it in res:
            out.append((str(it[0]), float(it[1])))
    else:
        for i in range(0, len(res) - 1, 2):
            out.append((str(res[i]), float(res[i + 1])))
    return out

def lb_all(month):
    pairs = _parse_zr(db.zrange(f"rk:lb:{month}", 0, -1, withscores=True))
    pairs.sort(key=lambda p: (-p[1], p[0]))
    return pairs

def _lb_touch(user):
    try:
        db.hset("rk:lbname", str(user.id), (user.first_name or "Player")[:24])
    except Exception:
        pass

def _lb_name(uid):
    try:
        n = db.hget("rk:lbname", str(uid)) or "Player"
    except Exception:
        n = "Player"
    n = str(n)
    if LB_MASK_NAMES:
        n = n[:2] + "***"
    return html.escape(n)

G_MONTHS = {
    "ar": ["يناير", "فبراير", "مارس", "أبريل", "ماي", "جوان", "جويلية", "أوت", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"],
    "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    "fr": ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"],
}

def _month_label(month, lang):
    y, m = month.split("-")
    return f"{G_MONTHS.get(lang, G_MONTHS['ar'])[int(m) - 1]} {y}"

G_TEXTS = {
    "ar": {
        "hub": "🎮 <b>ساحة الألعاب</b>\n\nتنافس واجمع <b>Raseedkom Coins</b> 🪙 وتصدّر الترتيب الشهري!\n\n💰 رصيدك: <b>{bal}</b> 🪙\n🎁 الهدية اليومية: {gift}\n\n⚽ <b>ساحة المباريات</b> — توقّع نتائج المباريات وشارك بكوينزك.\n⏱️ <b>تحدي التوقيت اليومي</b> — أوقف العداد عند هدف اليوم واربح <b>{prize}</b> 🪙.\n\n🪙 <b>كيف تكسب الكوينز؟</b>\n• 🎁 الهدية اليومية\n• 🛒 {pc} كوينز عند كل عملية شراء\n• 👥 {rc} كوينز عن كل صديق ينضم عبر رابط الإحالة\n• 🎮 الفوز في الألعاب\n\n🏆 أفضل 3 في الترتيب الشهري يفوزون بمنتجات مجانية 🆓\n\nℹ️ الكوينز افتراضية للتسلية فقط، بلا قيمة نقدية ولا يمكن سحبها.",
        "gift_yes": "✅ متاحة الآن (+{n} 🪙)",
        "gift_no": "⏳ تم استلامها — عد بعد {h}س {m}د",
        "btn_gift": "🎁 استلام الهدية اليومية (+{n})",
        "btn_wallet": "🪙 محفظة الكوينز",
        "btn_lb": "🏆 الترتيب الشهري",
        "btn_soon_pred": "⚽ ساحة المباريات",
        "btn_soon_sw": "⏱️ تحدي التوقيت اليومي",
        "btn_hub": "🎮 ساحة الألعاب",
        "btn_prev": "📅 الشهر الماضي",
        "btn_cur": "📅 هذا الشهر",
        "gift_ok": "✅ تمت إضافة {n} Raseedkom Coins إلى رصيدك!",
        "gift_done": "ℹ️ استلمت هديتك اليوم. عد بعد {h}س {m}د.",
        "wallet": "🪙 <b>محفظة Raseedkom Coins</b>\n\n💰 الرصيد: <b>{bal}</b> 🪙\n📈 نقاطك هذا الشهر: <b>{pts}</b>\n🏅 ترتيبك: <b>{rank}</b>\n🎁 الهدية اليومية: {gift}\n\nℹ️ الكوينز افتراضية للتسلية فقط، بلا قيمة نقدية ولا يمكن سحبها.",
        "lb": "🏆 <b>الترتيب الشهري — {month}</b>\n\n{rows}\n\n📍 ترتيبك: <b>{rank}</b> | نقاطك: <b>{pts}</b>\nيُعاد ضبط الترتيب مطلع كل شهر.",
        "lb_empty": "لا يوجد مشاركون بعد. كن أول المتصدرين!",
        "soon": "🔄 جاري التحديث، ستتوفر هذه اللعبة قريباً",
        "unavailable": "⚠️ الخدمة غير متاحة حالياً، حاول لاحقاً.",
    },
    "en": {
        "hub": "🎮 <b>Games Arena</b>\n\nCompete, collect <b>Raseedkom Coins</b> 🪙 and top the monthly leaderboard!\n\n💰 Your balance: <b>{bal}</b> 🪙\n🎁 Daily gift: {gift}\n\n⚽ <b>Match Arena</b> — predict match results and stake your coins.\n⏱️ <b>Daily Timing Challenge</b> — stop the counter at today's target and win <b>{prize}</b> 🪙.\n\n🪙 <b>How to earn coins?</b>\n• 🎁 The daily gift\n• 🛒 {pc} coins on every purchase\n• 👥 {rc} coins for every friend who joins with your referral link\n• 🎮 Winning games\n\n🏆 The top 3 of the monthly leaderboard win free products 🆓\n\nℹ️ Coins are virtual, for fun only, with no cash value and no withdrawal.",
        "gift_yes": "✅ available now (+{n} 🪙)",
        "gift_no": "⏳ claimed — come back in {h}h {m}m",
        "btn_gift": "🎁 Claim daily gift (+{n})",
        "btn_wallet": "🪙 Coins wallet",
        "btn_lb": "🏆 Monthly leaderboard",
        "btn_soon_pred": "⚽ Match Arena",
        "btn_soon_sw": "⏱️ Daily Timing Challenge",
        "btn_hub": "🎮 Games Arena",
        "btn_prev": "📅 Last month",
        "btn_cur": "📅 This month",
        "gift_ok": "✅ {n} Raseedkom Coins were added to your balance!",
        "gift_done": "ℹ️ You already claimed today's gift. Come back in {h}h {m}m.",
        "wallet": "🪙 <b>Raseedkom Coins wallet</b>\n\n💰 Balance: <b>{bal}</b> 🪙\n📈 Your points this month: <b>{pts}</b>\n🏅 Your rank: <b>{rank}</b>\n🎁 Daily gift: {gift}\n\nℹ️ Coins are virtual, for fun only, with no cash value and no withdrawal.",
        "lb": "🏆 <b>Monthly leaderboard — {month}</b>\n\n{rows}\n\n📍 Your rank: <b>{rank}</b> | Your points: <b>{pts}</b>\nThe leaderboard resets at the start of every month.",
        "lb_empty": "No players yet. Be the first on the board!",
        "soon": "🔄 Updating, this game will be available soon",
        "unavailable": "⚠️ Service unavailable right now, try again later.",
    },
    "fr": {
        "hub": "🎮 <b>Espace Jeux</b>\n\nParticipez, gagnez des <b>Raseedkom Coins</b> 🪙 et prenez la tête du classement mensuel !\n\n💰 Votre solde : <b>{bal}</b> 🪙\n🎁 Cadeau quotidien : {gift}\n\n⚽ <b>Arène des matchs</b> — pronostiquez les résultats et misez vos coins.\n⏱️ <b>Défi chrono quotidien</b> — stoppez le compteur sur l'objectif du jour et gagnez <b>{prize}</b> 🪙.\n\n🪙 <b>Comment gagner des coins ?</b>\n• 🎁 Le cadeau quotidien\n• 🛒 {pc} coins à chaque achat\n• 👥 {rc} coins pour chaque ami qui rejoint via votre lien de parrainage\n• 🎮 Gagner aux jeux\n\n🏆 Les 3 premiers du classement mensuel gagnent des produits gratuits 🆓\n\nℹ️ Les coins sont virtuels, pour le plaisir uniquement, sans valeur monétaire ni retrait possible.",
        "gift_yes": "✅ disponible (+{n} 🪙)",
        "gift_no": "⏳ récupéré — revenez dans {h}h {m}min",
        "btn_gift": "🎁 Récupérer le cadeau quotidien (+{n})",
        "btn_wallet": "🪙 Portefeuille de coins",
        "btn_lb": "🏆 Classement mensuel",
        "btn_soon_pred": "⚽ Arène des matchs",
        "btn_soon_sw": "⏱️ Défi chrono quotidien",
        "btn_hub": "🎮 Espace Jeux",
        "btn_prev": "📅 Mois dernier",
        "btn_cur": "📅 Ce mois-ci",
        "gift_ok": "✅ {n} Raseedkom Coins ont été ajoutés à votre solde !",
        "gift_done": "ℹ️ Vous avez déjà récupéré le cadeau du jour. Revenez dans {h}h {m}min.",
        "wallet": "🪙 <b>Portefeuille Raseedkom Coins</b>\n\n💰 Solde : <b>{bal}</b> 🪙\n📈 Vos points ce mois-ci : <b>{pts}</b>\n🏅 Votre rang : <b>{rank}</b>\n🎁 Cadeau quotidien : {gift}\n\nℹ️ Les coins sont virtuels, pour le plaisir uniquement, sans valeur monétaire ni retrait possible.",
        "lb": "🏆 <b>Classement mensuel — {month}</b>\n\n{rows}\n\n📍 Votre rang : <b>{rank}</b> | Vos points : <b>{pts}</b>\nLe classement est remis à zéro au début de chaque mois.",
        "lb_empty": "Aucun joueur pour le moment. Soyez le premier du classement !",
        "soon": "🔄 Mise à jour en cours, ce jeu sera bientôt disponible",
        "unavailable": "⚠️ Service indisponible pour le moment, réessayez plus tard.",
    },
}

G_TEXTS["ar"].update({"btn_next": "التالي ➡️ (11-20)", "btn_first": "⬅️ السابق (1-10)"})
G_TEXTS["en"].update({"btn_next": "Next ➡️ (11-20)", "btn_first": "⬅️ Previous (1-10)"})
G_TEXTS["fr"].update({"btn_next": "Suivant ➡️ (11-20)", "btn_first": "⬅️ Précédent (1-10)"})
LB_PAGE = 10        # عدد اللاعبين في كل صفحة
LB_MAX_PAGES = 2    # أقصى عدد صفحات (الأولى 1-10 والثانية 11-20)

def gt(lang, key):
    return G_TEXTS.get(lang, G_TEXTS["ar"])[key]

def _gift_state(lang, uid):
    if _gift_claimed_today(uid):
        left = _secs_to_midnight()
        return gt(lang, "gift_no").format(h=left // 3600, m=(left % 3600) // 60)
    return gt(lang, "gift_yes").format(n=DAILY_GIFT_COINS)

def _my_rank(pairs, uid):
    for i, (u, s) in enumerate(pairs, 1):
        if u == str(uid):
            return f"#{i}", int(s)
    return "—", 0

_hub_src = {}   # من أين فتح الزبون الساحة: "m" صفحة المنتجات | "s" قائمة ابدأ

def gm_hub(call, lang, src=None):
    uid = call.from_user.id
    if src in ("m", "s"):
        _hub_src[uid] = src
    back_cb = "back_to_main" if _hub_src.get(uid) == "m" else "sm_home"
    _lb_touch(call.from_user)
    mk = InlineKeyboardMarkup(row_width=1)
    mk.add(InlineKeyboardButton(text=gt(lang, "btn_gift").format(n=DAILY_GIFT_COINS), callback_data="gm_gift"))
    mk.row(InlineKeyboardButton(text=gt(lang, "btn_wallet"), callback_data="gm_wallet"),
           InlineKeyboardButton(text=gt(lang, "btn_lb"), callback_data="gm_lb_cur"))
    mk.add(InlineKeyboardButton(text=gt(lang, "btn_soon_pred"), callback_data="gm_ar_0"))
    mk.add(InlineKeyboardButton(text=gt(lang, "btn_soon_sw"), callback_data="gm_sw_h"))
    mk.add(InlineKeyboardButton(text=t(lang, "back"), callback_data=back_cb))
    _pf_show(call, gt(lang, "hub").format(bal=coins_get(uid), gift=_gift_state(lang, uid), prize=SW_PRIZE_COINS,
                                                pc=PURCHASE_COINS, rc=REF_COINS), mk)

def gm_wallet(call, lang):
    uid = call.from_user.id
    pairs = lb_all(_month_key())
    rank, pts = _my_rank(pairs, uid)
    mk = InlineKeyboardMarkup(row_width=1)
    mk.add(InlineKeyboardButton(text=gt(lang, "btn_gift").format(n=DAILY_GIFT_COINS), callback_data="gm_gift"))
    mk.add(InlineKeyboardButton(text=gt(lang, "btn_lb"), callback_data="gm_lb_cur"))
    mk.add(InlineKeyboardButton(text=gt(lang, "btn_hub"), callback_data="gm_hub"))
    _pf_show(call, gt(lang, "wallet").format(bal=coins_get(uid), pts=pts, rank=rank, gift=_gift_state(lang, uid)), mk)

def gm_leaderboard(call, lang, which, page=0):
    uid = call.from_user.id
    month = _month_key(1 if which == "prev" else 0)
    pairs = lb_all(month)
    page = max(0, min(int(page), LB_MAX_PAGES - 1))
    if page * LB_PAGE >= len(pairs):
        page = 0
    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    _plain_medals = dict(medals)
    if not _icons_off():
        for _n, _mid in ((1, LB_MEDAL_IDS[0]), (2, LB_MEDAL_IDS[1]), (3, LB_MEDAL_IDS[2])):
            medals[_n] = f'<tg-emoji emoji-id="{_mid}">{_plain_medals[_n]}</tg-emoji>'
    chunk = pairs[page * LB_PAGE:(page + 1) * LB_PAGE]
    def _lb_rows(md):
        out = []
        for i, (u, s) in enumerate(chunk, page * LB_PAGE + 1):
            out.append(f"{md.get(i, f'#{i}')} {_lb_name(u)}\n└ 🪙 <b>{int(s)}</b> Raseedkom Coins")
        return out
    rows = _lb_rows(medals)
    rank, pts = _my_rank(pairs, uid)
    mk = InlineKeyboardMarkup(row_width=1)
    if page + 1 < LB_MAX_PAGES and len(pairs) > (page + 1) * LB_PAGE:
        mk.add(InlineKeyboardButton(text=gt(lang, "btn_next"), callback_data=f"gm_lb_{which}{page + 1}"))
    if page > 0:
        mk.add(InlineKeyboardButton(text=gt(lang, "btn_first"), callback_data=f"gm_lb_{which}{page - 1 if page - 1 else ''}"))
    mk.add(InlineKeyboardButton(text=gt(lang, "btn_cur" if which == "prev" else "btn_prev"),
                                callback_data="gm_lb_cur" if which == "prev" else "gm_lb_prev"))
    mk.add(InlineKeyboardButton(text=gt(lang, "btn_hub"), callback_data="gm_hub"))
    try:
        _pf_show(call, gt(lang, "lb").format(
            month=_month_label(month, lang), rows="\n\n".join(rows) or gt(lang, "lb_empty"), rank=rank, pts=pts), mk)
    except Exception as e:
        print(f"leaderboard custom medals failed: {e}")
        _pf_show(call, gt(lang, "lb").format(
            month=_month_label(month, lang), rows="\n\n".join(_lb_rows(_plain_medals)) or gt(lang, "lb_empty"), rank=rank, pts=pts), mk)

@bot.callback_query_handler(func=lambda c: c.data.startswith("gm" + SEP))
def handle_games(call):
    now_ms = int(time.time() * 1000)   # أول سطر: لحظة وصول الضغطة (مهم لزر الإيقاف)
    uid = call.from_user.id
    lang = get_lang(uid)
    if not db:
        bot.answer_callback_query(call.id, gt(lang, "unavailable"), show_alert=True)
        return
    parts = call.data.split(SEP, 2)
    cmd = parts[1] if len(parts) > 1 else ""
    arg = parts[2] if len(parts) > 2 else ""
    register_user(uid)
    try:
        if cmd == "hub":
            gm_hub(call, lang, arg if arg in ("m", "s") else None)
        elif cmd == "wallet":
            gm_wallet(call, lang)
        elif cmd == "lb":
            _which = "prev" if arg.startswith("prev") else "cur"
            _pg = arg[len(_which):]
            gm_leaderboard(call, lang, _which, int(_pg) if _pg.isdigit() else 0)
        elif cmd == "soon":
            bot.answer_callback_query(call.id, gt(lang, "soon"), show_alert=True)
            return
        elif cmd == "ar":
            ar_list(call, lang, int(arg) if arg.isdigit() else 0)
        elif cmd == "mt":
            ar_match(call, lang, arg)
        elif cmd == "mp":
            ar_stake(call, lang, arg)
        elif cmd == "mk":
            ar_pick(call, lang, arg)
        elif cmd == "mc":
            ar_custom(call, lang, arg)
        elif cmd == "mo":
            ar_place(call, lang, arg)
        elif cmd == "ms":
            ar_toggle_sub(call, lang)
            return
        elif cmd == "mine":
            ar_mine(call, lang)
        elif cmd == "sw":
            sw_intro(call, lang, "m" if arg == "m" else "h")
        elif cmd == "swgo":
            sw_go(call, lang, "m" if arg == "m" else "h")
            return
        elif cmd == "swstop":
            sw_stop(call, lang, now_ms)
            return
        elif cmd == "gift":
            ok, _ = _gift_claim(uid)
            if ok:
                _lb_touch(call.from_user)
                bot.answer_callback_query(call.id, gt(lang, "gift_ok").format(n=DAILY_GIFT_COINS), show_alert=True)
            else:
                left = _secs_to_midnight()
                bot.answer_callback_query(call.id, gt(lang, "gift_done").format(h=left // 3600, m=(left % 3600) // 60),
                                          show_alert=True)
            gm_hub(call, lang)
            return
    except Exception as e:
        print(f"games error: {e}")
        bot.answer_callback_query(call.id, gt(lang, "unavailable"), show_alert=True)
        return
    bot.answer_callback_query(call.id)

# ---------- أدوات الأدمن ----------
@bot.message_handler(commands=["coins", "coinsadd"])
def coins_admin(message):
    if not is_admin_msg(message):
        return
    cmd = message.text.split()[0].lstrip("/").split("@")[0]
    a = message.text.split()[1:]
    if not db:
        bot.reply_to(message, "⚠️ Upstash غير متصل.")
        return
    if not a or not a[0].isdigit():
        bot.reply_to(message, "الاستعمال: /coins ID  أو  /coinsadd ID العدد")
        return
    uid = a[0]
    if cmd == "coinsadd":
        try:
            n = int(a[1])
        except (IndexError, ValueError):
            bot.reply_to(message, "الاستعمال: /coinsadd ID العدد")
            return
        if n >= 0:
            coins_add(uid, n, "admin", score=False)
        elif not coins_take(uid, -n, "admin"):
            bot.reply_to(message, "❌ الرصيد أقل من المبلغ المطلوب خصمه.")
            return
    rank, pts = _my_rank(lb_all(_month_key()), uid)
    bot.reply_to(message, f"🪙 الزبون {uid}\nالرصيد: {coins_get(uid)}\nنقاط الشهر: {pts} | الترتيب: {rank}")

# ---------- إشعار نهاية الشهر لبوت المراقبة ----------
def _month_watch_loop():
    time.sleep(90)
    while True:
        try:
            cur = _month_key()
            last = kv_get("rk:lb:last")
            if last and str(last) != cur:
                top = lb_all(str(last))[:3]
                lines = [f"{['🥇','🥈','🥉'][i]} {_lb_name(u)} (<code>{u}</code>) — {int(s)}" for i, (u, s) in enumerate(top)]
                monitor_send(f"🏆 <b>انتهى ترتيب شهر {_month_label(str(last), 'ar')}</b>\n\n" + ("\n".join(lines) or "لا مشاركين"))
            if str(last) != cur:
                kv_set("rk:lb:last", cur)
        except Exception as e:
            print(f"month watch error: {e}")
        time.sleep(1800)

if db:
    threading.Thread(target=_month_watch_loop, daemon=True).start()


# ============================================================
# ========== تحدي التوقيت اليومي ⏱️ ==========
# ============================================================
SW_ATT_TTL = 24 * 3600     # تتجدد المحاولات بعد 24 ساعة من أول محاولة
SW_RUN_TTL = 900           # مهلة الجلسة (إن لم يضغط إيقاف تُحتسب المحاولة)

SW_TEXTS = {
    "ar": {
        "intro": "⏱️ <b>تحدي التوقيت اليومي</b>\n\n🎯 هدف اليوم: <b>{target} ثانية</b>\n\nاضغط «ابدأ المؤقت»، سيعمل العداد بصمت، ثم اضغط «🛑 إيقاف العداد» حين تظن أنه مرّ <b>{target}</b> ثانية بالضبط. تُحتسب الإصابة إذا كان الفارق في حدود ±{tol} ثانية.\n\n🏆 الجائزة: <b>{prize}</b> Raseedkom Coins 🪙\n🎟️ محاولاتك: <b>{left} / {total}</b>{renew}\n\nℹ️ يتغير الهدف تلقائياً كل يوم. الكوينز افتراضية للتسلية فقط.",
        "renew": "\n🔄 تتجدد المحاولات بعد {h}س {m}د",
        "running": "⏱️ <b>العداد يعمل الآن...</b>\n\n🎯 أوقفه عند <b>{target}</b> ثانية بالضبط!\n\nاضغط «🛑 إيقاف العداد» عندما تكون جاهزاً.",
        "win": "🎉 <b>أحسنت! أصبت الهدف!</b>\n\n⏱️ وقتك: <b>{el} ثانية</b>\n🎯 الهدف: <b>{target} ثانية</b>\n📏 الفارق: {diff} ثانية\n\n🏆 ربحت <b>{prize}</b> Raseedkom Coins 🪙\n💰 رصيدك: <b>{bal}</b> 🪙\n🎟️ محاولاتك المتبقية: <b>{left}</b>{renew}",
        "lose": "❌ <b>لم تصب الهدف</b>\n\n⏱️ وقتك: <b>{el} ثانية</b>\n🎯 الهدف: <b>{target} ثانية</b>\n📏 الفارق: {diff} ثانية (المسموح ±{tol})\n\n🎟️ محاولاتك المتبقية: <b>{left}</b>{renew}\n{hint}",
        "hint_more": "💪 حاول مرة أخرى!",
        "hint_none": "🌙 حاول غداً!",
        "no_left": "🎟️ استنفدت محاولاتك. تتجدد بعد {h}س {m}د.",
        "expired": "⌛ انتهت جلسة العداد (احتُسبت المحاولة). ابدأ من جديد.",
        "btn_start": "▶️ ابدأ المؤقت",
        "btn_stop": "🛑 إيقاف العداد",
        "btn_again": "▶️ محاولة أخرى",
    },
    "en": {
        "intro": "⏱️ <b>Daily Timing Challenge</b>\n\n🎯 Today's target: <b>{target} seconds</b>\n\nTap «Start timer»: the counter runs silently. Then tap «🛑 Stop counter» when you think exactly <b>{target}</b> seconds have passed. You hit the target if you are within ±{tol} seconds.\n\n🏆 Prize: <b>{prize}</b> Raseedkom Coins 🪙\n🎟️ Your attempts: <b>{left} / {total}</b>{renew}\n\nℹ️ The target changes automatically every day. Coins are virtual, for fun only.",
        "renew": "\n🔄 Attempts renew in {h}h {m}m",
        "running": "⏱️ <b>The counter is running...</b>\n\n🎯 Stop it at exactly <b>{target}</b> seconds!\n\nTap «🛑 Stop counter» when you are ready.",
        "win": "🎉 <b>Well done! You hit the target!</b>\n\n⏱️ Your time: <b>{el} s</b>\n🎯 Target: <b>{target} s</b>\n📏 Difference: {diff} s\n\n🏆 You won <b>{prize}</b> Raseedkom Coins 🪙\n💰 Balance: <b>{bal}</b> 🪙\n🎟️ Attempts left: <b>{left}</b>{renew}",
        "lose": "❌ <b>You missed the target</b>\n\n⏱️ Your time: <b>{el} s</b>\n🎯 Target: <b>{target} s</b>\n📏 Difference: {diff} s (allowed ±{tol})\n\n🎟️ Attempts left: <b>{left}</b>{renew}\n{hint}",
        "hint_more": "💪 Try again!",
        "hint_none": "🌙 Try again tomorrow!",
        "no_left": "🎟️ You have used all your attempts. They renew in {h}h {m}m.",
        "expired": "⌛ The counter session expired (the attempt was counted). Start again.",
        "btn_start": "▶️ Start timer",
        "btn_stop": "🛑 Stop counter",
        "btn_again": "▶️ Another attempt",
    },
    "fr": {
        "intro": "⏱️ <b>Défi chrono quotidien</b>\n\n🎯 Objectif du jour : <b>{target} secondes</b>\n\nAppuyez sur « Démarrer le chrono » : le compteur tourne en silence. Puis appuyez sur « 🛑 Arrêter le compteur » quand vous pensez que <b>{target}</b> secondes se sont écoulées. L'objectif est atteint si vous êtes à ±{tol} seconde(s) près.\n\n🏆 Récompense : <b>{prize}</b> Raseedkom Coins 🪙\n🎟️ Vos tentatives : <b>{left} / {total}</b>{renew}\n\nℹ️ L'objectif change automatiquement chaque jour. Les coins sont virtuels, pour le plaisir uniquement.",
        "renew": "\n🔄 Les tentatives se renouvellent dans {h}h {m}min",
        "running": "⏱️ <b>Le compteur tourne...</b>\n\n🎯 Arrêtez-le à exactement <b>{target}</b> secondes !\n\nAppuyez sur « 🛑 Arrêter le compteur » quand vous êtes prêt.",
        "win": "🎉 <b>Bravo ! Objectif atteint !</b>\n\n⏱️ Votre temps : <b>{el} s</b>\n🎯 Objectif : <b>{target} s</b>\n📏 Écart : {diff} s\n\n🏆 Vous gagnez <b>{prize}</b> Raseedkom Coins 🪙\n💰 Solde : <b>{bal}</b> 🪙\n🎟️ Tentatives restantes : <b>{left}</b>{renew}",
        "lose": "❌ <b>Objectif manqué</b>\n\n⏱️ Votre temps : <b>{el} s</b>\n🎯 Objectif : <b>{target} s</b>\n📏 Écart : {diff} s (toléré ±{tol})\n\n🎟️ Tentatives restantes : <b>{left}</b>{renew}\n{hint}",
        "hint_more": "💪 Réessayez !",
        "hint_none": "🌙 Réessayez demain !",
        "no_left": "🎟️ Vous avez utilisé toutes vos tentatives. Elles se renouvellent dans {h}h {m}min.",
        "expired": "⌛ La session du compteur a expiré (la tentative est comptée). Recommencez.",
        "btn_start": "▶️ Démarrer le chrono",
        "btn_stop": "🛑 Arrêter le compteur",
        "btn_again": "▶️ Nouvelle tentative",
    },
}

def swt(lang, key):
    return SW_TEXTS.get(lang, SW_TEXTS["ar"])[key]

# ---------- الهدف اليومي: يبدأ 10.00 ثم يتحرك بين 5 و11 ثانية ----------
def _sw_raw_idx(n):
    return int(hashlib.sha256(f"sw{n}".encode()).hexdigest(), 16) % 13   # 13 قيمة: 5.0 ... 11.0 (خطوة 0.5)

def _sw_target(n):
    t = 10   # فهرس 10.0 (يوم الانطلاق)
    for i in range(1, n + 1):
        idx = _sw_raw_idx(i)
        if idx == t:
            idx = (idx + 1) % 13   # لا يتكرر نفس الهدف يومين متتاليين
        t = idx
    return Decimal(5) + Decimal("0.5") * t

def _sw_day_index():
    today = int(_now_dz() // 86400)
    d0 = kv_get("rk:sw:day0")
    if d0 is None:
        kv_set("rk:sw:day0", str(today), nx=True)
        d0 = kv_get("rk:sw:day0")
    return max(0, today - int(d0))

def _sw_today_target():
    return _sw_target(_sw_day_index())

def _sw_att_key(uid):
    return f"rk:sw:att:{uid}"

def _sw_run_key(uid):
    return f"rk:sw:run:{uid}"

def _sw_info(uid):
    """(المحاولات المتبقية، ثواني التجديد)"""
    try:
        used = int(kv_get(_sw_att_key(uid)) or 0)
    except Exception:
        used = 0
    left = max(0, SW_ATTEMPTS - used)
    ttl = 0
    if used:
        try:
            ttl = max(0, int(db.ttl(_sw_att_key(uid))))
        except Exception:
            ttl = SW_ATT_TTL
    return left, ttl

def _renew_txt(lang, ttl):
    if ttl <= 0:
        return ""
    return swt(lang, "renew").format(h=ttl // 3600, m=(ttl % 3600) // 60)

def sw_intro(call, lang, src):
    uid = call.from_user.id
    _lb_touch(call.from_user)
    left, ttl = _sw_info(uid)
    mk = InlineKeyboardMarkup(row_width=1)
    if left > 0 or kv_get_json(_sw_run_key(uid)):
        mk.add(InlineKeyboardButton(text=swt(lang, "btn_start"), callback_data=f"gm_swgo_{src}"))
    mk.add(InlineKeyboardButton(text=gt(lang, "btn_lb"), callback_data="gm_lb_cur"))
    mk.add(InlineKeyboardButton(text=t(lang, "back"), callback_data="gm_hub" if src == "h" else "back_to_main"))
    _pf_show(call, swt(lang, "intro").format(
        target=f"{_sw_today_target():.2f}", tol=f"{SW_TOLERANCE:.2f}", prize=SW_PRIZE_COINS,
        left=left, total=SW_ATTEMPTS, renew=_renew_txt(lang, ttl)), mk)

def _sw_running_screen(call, lang, target):
    mk = InlineKeyboardMarkup(row_width=1)
    mk.add(InlineKeyboardButton(text=swt(lang, "btn_stop"), callback_data="gm_swstop"))
    _pf_show(call, swt(lang, "running").format(target=target), mk)

def sw_go(call, lang, src):
    uid = call.from_user.id
    run = kv_get_json(_sw_run_key(uid))
    if run:   # عداد يعمل أصلاً: نعرض زر الإيقاف فقط
        _sw_running_screen(call, lang, run["target"])
        bot.answer_callback_query(call.id)
        return
    left, ttl = _sw_info(uid)
    if left <= 0:
        bot.answer_callback_query(call.id, swt(lang, "no_left").format(h=ttl // 3600, m=(ttl % 3600) // 60), show_alert=True)
        sw_intro(call, lang, src)
        return
    n = kv_incr_window(_sw_att_key(uid), SW_ATT_TTL)   # تُستهلك المحاولة عند البدء
    if n > SW_ATTEMPTS:
        bot.answer_callback_query(call.id, swt(lang, "no_left").format(h=ttl // 3600, m=(ttl % 3600) // 60), show_alert=True)
        return
    target = f"{_sw_today_target():.2f}"
    sess = {"start": int(time.time() * 1000), "target": target, "src": src}
    if not kv_set(_sw_run_key(uid), json.dumps(sess), ex=SW_RUN_TTL, nx=True):
        _sw_running_screen(call, lang, target)
        bot.answer_callback_query(call.id)
        return
    _sw_running_screen(call, lang, target)
    # نعيد ضبط لحظة البداية بعد وصول شاشة الإيقاف للزبون (أدق وأعدل)
    sess["start"] = int(time.time() * 1000)
    kv_set(_sw_run_key(uid), json.dumps(sess), ex=SW_RUN_TTL)
    bot.answer_callback_query(call.id)

def sw_stop(call, lang, now_ms):
    uid = call.from_user.id
    run = kv_get_json(_sw_run_key(uid))
    if not run:
        bot.answer_callback_query(call.id, swt(lang, "expired"), show_alert=True)
        sw_intro(call, lang, "h")
        return
    if not kv_set(f"rk:sw:fin:{uid}:{run['start']}", "1", ex=3600, nx=True):
        bot.answer_callback_query(call.id)   # ضغطة مزدوجة
        return
    kv_del(_sw_run_key(uid))
    elapsed = (now_ms - int(run["start"])) / 1000.0
    target = float(run["target"])
    diff = abs(elapsed - target)
    win = diff <= SW_TOLERANCE + 1e-9
    src = run.get("src", "h")
    left, ttl = _sw_info(uid)
    renew = _renew_txt(lang, ttl) if left == 0 else ""
    mk = InlineKeyboardMarkup(row_width=1)
    if left > 0:
        mk.add(InlineKeyboardButton(text=swt(lang, "btn_again"), callback_data=f"gm_swgo_{src}"))
    mk.add(InlineKeyboardButton(text=gt(lang, "btn_lb"), callback_data="gm_lb_cur"))
    mk.add(InlineKeyboardButton(text=t(lang, "back"), callback_data=f"gm_sw_{src}"))
    common = dict(el=f"{elapsed:.2f}", target=run["target"], diff=f"{diff:.2f}", left=left, renew=renew)
    if win:
        bal = coins_add(uid, SW_PRIZE_COINS, "stopwatch")
        text = swt(lang, "win").format(prize=SW_PRIZE_COINS, bal=bal, **common)
        monitor_send(f"⏱️ <b>فائز في تحدي التوقيت</b>\n\n👤 {_user_link(uid)}\n🎯 {run['target']}s | وقته: {elapsed:.2f}s\n➕ {SW_PRIZE_COINS} 🪙")
    else:
        text = swt(lang, "lose").format(tol=f"{SW_TOLERANCE:.2f}", hint=swt(lang, "hint_more" if left > 0 else "hint_none"), **common)
    _pf_show(call, text, mk)
    bot.answer_callback_query(call.id)


# ============================================================
# ========== الكوينز: شراء (+PURCHASE_COINS) وإحالة (+REF_COINS) وملاحظة المحفظة ==========
# ============================================================
COINS_NOTE = {
    "ar": f"🪙 <b>كيف تكسب Raseedkom Coins؟</b>\n• 🎁 هدية يومية من ساحة الألعاب\n• 🛒 {PURCHASE_COINS} كوينز عند كل عملية شراء\n• 👥 {REF_COINS} كوينز عن كل صديق ينضم عبر رابطك\n• 🎮 الفوز في الألعاب\n\nادخل «🚀 ابدأ» في الصفحة الرئيسية (تحت المنتجات)، ثم «🎮 لعبة · من سيفوز؟» واقرأ التعليمات.\n🏆 أفضل 3 في الترتيب الشهري يفوزون بمنتجات مجانية 🆓",
    "en": f"🪙 <b>How to earn Raseedkom Coins?</b>\n• 🎁 A daily gift from the Games Arena\n• 🛒 {PURCHASE_COINS} coins on every purchase\n• 👥 {REF_COINS} coins for every friend who joins with your link\n• 🎮 Winning games\n\nOpen «🚀 Start» on the main page (under the products), then «🎮 Game · Who will win?» and read the instructions.\n🏆 The top 3 of the monthly leaderboard win free products 🆓",
    "fr": f"🪙 <b>Comment gagner des Raseedkom Coins ?</b>\n• 🎁 Un cadeau quotidien dans l'Espace Jeux\n• 🛒 {PURCHASE_COINS} coins à chaque achat\n• 👥 {REF_COINS} coins pour chaque ami qui rejoint via votre lien\n• 🎮 Gagner aux jeux\n\nOuvrez « 🚀 Commencer » sur la page principale (sous les produits), puis « 🎮 Jeu · Qui va gagner ? » et lisez les instructions.\n🏆 Les 3 premiers du classement mensuel gagnent des produits gratuits 🆓",
}
for _l in ("ar", "en", "fr"):
    WALLET_TEXTS[_l]["wallet_note"] = COINS_NOTE[_l]

def _coins_wallet_line(lang, uid):
    label = {"ar": "رصيد Raseedkom Coins", "en": "Raseedkom Coins balance", "fr": "Solde Raseedkom Coins"}.get(lang, "Raseedkom Coins")
    try:
        return f"\n\n🪙 <b>{label}:</b> {coins_get(uid)}"
    except Exception:
        return ""

PC_TEXTS = {
    "ar": "🪙 <b>كسبت {n} Raseedkom Coins</b> على مشترياتك!\n💰 رصيدك: <b>{bal}</b> 🪙\n\nلكسب المزيد: اشترِ مجدداً، أو ادخل «🚀 ابدأ» في الصفحة الرئيسية (تحت المنتجات) ثم «🎮 لعبة · من سيفوز؟» واتبع التعليمات.\n🏆 أفضل 3 في الترتيب الشهري يفوزون بمنتجات مجانية 🆓",
    "en": "🪙 <b>You earned {n} Raseedkom Coins</b> for your purchase!\n💰 Balance: <b>{bal}</b> 🪙\n\nTo earn more: buy again, or open «🚀 Start» on the main page (under the products), then «🎮 Game · Who will win?» and follow the instructions.\n🏆 The top 3 of the monthly leaderboard win free products 🆓",
    "fr": "🪙 <b>Vous avez gagné {n} Raseedkom Coins</b> pour votre achat !\n💰 Solde : <b>{bal}</b> 🪙\n\nPour en gagner plus : achetez à nouveau, ou ouvrez « 🚀 Commencer » sur la page principale (sous les produits), puis « 🎮 Jeu · Qui va gagner ? » et suivez les instructions.\n🏆 Les 3 premiers du classement mensuel gagnent des produits gratuits 🆓",
}
RC_TEXTS = {
    "ar": "👥 <b>انضم صديق عبر رابطك!</b>\n🪙 +{n} Raseedkom Coins\n💰 رصيدك: <b>{bal}</b> 🪙",
    "en": "👥 <b>A friend joined through your link!</b>\n🪙 +{n} Raseedkom Coins\n💰 Balance: <b>{bal}</b> 🪙",
    "fr": "👥 <b>Un ami a rejoint via votre lien !</b>\n🪙 +{n} Raseedkom Coins\n💰 Solde : <b>{bal}</b> 🪙",
}

def _coins_notify(uid, texts, n, bal, with_games_btn=False):
    lang = get_lang(uid)
    mk = None
    if with_games_btn:
        mk = InlineKeyboardMarkup()
        mk.add(InlineKeyboardButton(text=smt(lang, "game"), callback_data="gm_hub_s"))
    try:
        bot.send_message(int(uid), texts.get(lang, texts["ar"]).format(n=n, bal=bal), parse_mode="HTML", reply_markup=mk)
    except Exception as e:
        print(f"coins notify failed: {e}")

def _purchase_coins_hook(uid):
    """يُستدعى من record_purchase (مرة واحدة لكل شراء): +PURCHASE_COINS كوينز ورسالة للزبون."""
    try:
        if not db:
            return
        bal = coins_add(uid, PURCHASE_COINS, "purchase")
        threading.Thread(target=_coins_notify, args=(uid, PC_TEXTS, PURCHASE_COINS, bal, True), daemon=True).start()
    except Exception as e:
        print(f"purchase coins error: {e}")

def _ref_grant_coins(rid, new_uid):
    """+REF_COINS كوينز لصاحب الرابط عند انضمام صديق (بحد أقصى REF_COINS_DAILY_CAP يومياً)."""
    try:
        if not db:
            return
        if kv_incr_window(f"rk:refcap:{rid}:{_day_key()}", 86400) > REF_COINS_DAILY_CAP:
            return
        bal = coins_add(rid, REF_COINS, "referral")
        threading.Thread(target=_coins_notify, args=(rid, RC_TEXTS, REF_COINS, bal), daemon=True).start()
    except Exception as e:
        print(f"referral coins error: {e}")


# ============================================================
# ========== ساحة المباريات ⚽ (football-data.org) ==========
# ============================================================
import calendar

FB_BASE = "https://api.football-data.org/v4"
FB_KEY = os.environ.get("FOOTBALL_API_KEY", "")
AR_PAGE = 8
STAKE_CHOICES = (10, 25, 50, 100)
_mp_wait = {}   # user_id -> match_id (ينتظر مبلغاً مكتوباً)

AT = {
    "ar": {
        "arena": "⚽ <b>ساحة المباريات</b>\n\nتوقّع نتيجة المباراة (فوز / تعادل / فوز)، شارك بكوينزك، وإذا أصبت تسترجع مبلغك + نصفه كمكافأة تلقائية، وتتقاسم مع الفائزين نقاط من أخطأ.\n\n💰 رصيدك: <b>{bal}</b> 🪙\n🔒 تُغلق المشاركة عند صافرة البداية.\n\n{body}",
        "none": "لا توجد مباريات متاحة الآن. فعّل 🔔 ليصلك إشعار عند نزول مباريات جديدة.",
        "pick": "اختر مباراة:",
        "mine": "📋 توقعاتي", "notify_on": "🔔 أعلمني بالمباريات الجديدة", "notify_off": "🔕 إيقاف الإشعارات",
        "sub_on": "✅ سنعلمك عند نزول مباريات جديدة.", "sub_off": "🔕 تم إيقاف الإشعارات.",
        "next": "التالي ➡️", "prev": "⬅️ السابق",
        "match": "⚽ <b>{home} 🆚 {away}</b>\n🏆 {comp}\n🕒 {time}\n\n👥 المشاركون: <b>{n}</b> | 💰 مجموع المشاركات: <b>{pool}</b> 🪙{your}",
        "your": "\n\n🎯 توقعك: <b>{pick}</b> — {stake} 🪙",
        "btn_join": "🎯 مشاركة",
        "stake": "💰 اختر مبلغ المشاركة\n(رصيدك: <b>{bal}</b> 🪙 | الحد الأدنى: {min})",
        "other": "✏️ مبلغ آخر",
        "stake_prompt": "✏️ أرسل مبلغ المشاركة (رقم من {min} إلى {max}):",
        "stake_bad": "❌ مبلغ غير صالح. أرسل رقماً من {min} إلى {max}.",
        "stake_low": "❌ رصيدك لا يكفي. استلم هديتك اليومية من ساحة الألعاب.",
        "outcome": "🎯 اختر توقعك:\n<b>{home} 🆚 {away}</b>\n💰 المبلغ: <b>{stake}</b> 🪙",
        "win_label": "فوز {team}", "draw_label": "تعادل",
        "placed": "✅ <b>تم تسجيل مشاركتك</b>\n\n⚽ {home} 🆚 {away}\n🎯 توقعك: <b>{pick}</b>\n💰 {stake} 🪙\n\n💼 رصيدك الآن: <b>{bal}</b> 🪙\nستصلك النتيجة هنا بعد نهاية المباراة.",
        "closed": "🔒 أُغلقت المشاركة في هذه المباراة.",
        "already": "ℹ️ شاركت في هذه المباراة من قبل.",
        "mine_head": "📋 <b>توقعاتي</b>\n\n{rows}",
        "mine_empty": "لم تقم بأي توقع بعد.",
        "mine_line": "{icon} {home} – {away}\n    {pick} | {stake} 🪙 {res}",
        "res_win": "→ +{p} 🪙", "res_lose": "→ −{s} 🪙", "res_wait": "⏳", "res_void": "↩️ استرداد",
        "r_win": "🎉 <b>توقعك صحيح!</b>\n\n⚽ {home} {score} {away}\n🎯 توقعك: {pick}\n💰 ربحت: <b>+{profit}</b> 🪙 (استلمت {payout})\n💼 رصيدك: <b>{bal}</b> 🪙",
        "r_even": "✅ <b>توقعك صحيح!</b>\n\n⚽ {home} {score} {away}\n🎯 {pick}\nاسترجعت مبلغك ({payout} 🪙) لأن الجميع أصاب.\n💼 رصيدك: <b>{bal}</b> 🪙",
        "r_lose": "❌ <b>توقعك خاطئ</b>\n\n⚽ {home} {score} {away}\n🎯 توقعك: {pick}\n💸 خسرت: <b>{stake}</b> 🪙\nحظاً أوفر في المباراة القادمة!",
        "r_void": "↩️ <b>أُلغيت المباراة / تأجلت</b>\n\n⚽ {home} 🆚 {away}\nأُعيد لك <b>{stake}</b> 🪙.",
        "new": "⚽ نزلت <b>{n}</b> مباريات جديدة للتوقع! شارك قبل صافرة البداية 🎯",
        "open_arena": "⚽ افتح الساحة",
        "remind": "⏰ <b>تبقى {min} دقائق على صافرة البداية!</b>\n\n⚽ {home} 🆚 {away}\n🏆 {comp}\n🕒 {time}\n\nصوّت الآن قبل إغلاق المشاركة 🎯",
        "vote_now": "🎯 صوّت الآن",
        "daily": "🎁 اكسب نقاط يومية (+{n})",
    },
    "en": {
        "arena": "⚽ <b>Match Arena</b>\n\nPredict the match result (win / draw / win), stake your coins, and if you are right you get your stake back + 50% of it as an automatic bonus, and you share the losers' coins with the other winners.\n\n💰 Your balance: <b>{bal}</b> 🪙\n🔒 Predictions close at kick-off.\n\n{body}",
        "none": "No matches available right now. Turn on 🔔 to be notified when new matches are posted.",
        "pick": "Choose a match:",
        "mine": "📋 My predictions", "notify_on": "🔔 Notify me of new matches", "notify_off": "🔕 Turn off notifications",
        "sub_on": "✅ We'll notify you when new matches are posted.", "sub_off": "🔕 Notifications turned off.",
        "next": "Next ➡️", "prev": "⬅️ Previous",
        "match": "⚽ <b>{home} 🆚 {away}</b>\n🏆 {comp}\n🕒 {time}\n\n👥 Players: <b>{n}</b> | 💰 Total staked: <b>{pool}</b> 🪙{your}",
        "your": "\n\n🎯 Your pick: <b>{pick}</b> — {stake} 🪙",
        "btn_join": "🎯 Join",
        "stake": "💰 Choose your stake\n(balance: <b>{bal}</b> 🪙 | minimum: {min})",
        "other": "✏️ Other amount",
        "stake_prompt": "✏️ Send your stake (a number from {min} to {max}):",
        "stake_bad": "❌ Invalid amount. Send a number from {min} to {max}.",
        "stake_low": "❌ Not enough coins. Claim your daily gift in the Games Arena.",
        "outcome": "🎯 Choose your prediction:\n<b>{home} 🆚 {away}</b>\n💰 Stake: <b>{stake}</b> 🪙",
        "win_label": "{team} win", "draw_label": "Draw",
        "placed": "✅ <b>Your entry is registered</b>\n\n⚽ {home} 🆚 {away}\n🎯 Your pick: <b>{pick}</b>\n💰 {stake} 🪙\n\n💼 Balance now: <b>{bal}</b> 🪙\nYou'll get the result here after the match.",
        "closed": "🔒 Predictions are closed for this match.",
        "already": "ℹ️ You already joined this match.",
        "mine_head": "📋 <b>My predictions</b>\n\n{rows}",
        "mine_empty": "You haven't made any prediction yet.",
        "mine_line": "{icon} {home} – {away}\n    {pick} | {stake} 🪙 {res}",
        "res_win": "→ +{p} 🪙", "res_lose": "→ −{s} 🪙", "res_wait": "⏳", "res_void": "↩️ refunded",
        "r_win": "🎉 <b>Your prediction was right!</b>\n\n⚽ {home} {score} {away}\n🎯 Your pick: {pick}\n💰 You won: <b>+{profit}</b> 🪙 (received {payout})\n💼 Balance: <b>{bal}</b> 🪙",
        "r_even": "✅ <b>Your prediction was right!</b>\n\n⚽ {home} {score} {away}\n🎯 {pick}\nYou got your stake back ({payout} 🪙) because everybody was right.\n💼 Balance: <b>{bal}</b> 🪙",
        "r_lose": "❌ <b>Wrong prediction</b>\n\n⚽ {home} {score} {away}\n🎯 Your pick: {pick}\n💸 You lost: <b>{stake}</b> 🪙\nBetter luck next match!",
        "r_void": "↩️ <b>Match cancelled / postponed</b>\n\n⚽ {home} 🆚 {away}\nYour <b>{stake}</b> 🪙 were refunded.",
        "new": "⚽ <b>{n}</b> new matches are open for predictions! Join before kick-off 🎯",
        "open_arena": "⚽ Open the arena",
        "remind": "⏰ <b>{min} minutes left until kick-off!</b>\n\n⚽ {home} 🆚 {away}\n🏆 {comp}\n🕒 {time}\n\nPredict now before entries close 🎯",
        "vote_now": "🎯 Predict now",
        "daily": "🎁 Earn daily coins (+{n})",
    },
    "fr": {
        "arena": "⚽ <b>Arène des matchs</b>\n\nPronostiquez le résultat (victoire / nul / victoire), misez vos coins, et si vous avez raison vous récupérez votre mise + 50 % de bonus automatique, et vous partagez les coins des perdants avec les autres gagnants.\n\n💰 Votre solde : <b>{bal}</b> 🪙\n🔒 Les pronostics ferment au coup d'envoi.\n\n{body}",
        "none": "Aucun match disponible pour le moment. Activez 🔔 pour être averti dès que de nouveaux matchs sont publiés.",
        "pick": "Choisissez un match :",
        "mine": "📋 Mes pronostics", "notify_on": "🔔 M'avertir des nouveaux matchs", "notify_off": "🔕 Désactiver les notifications",
        "sub_on": "✅ Nous vous préviendrons des nouveaux matchs.", "sub_off": "🔕 Notifications désactivées.",
        "next": "Suivant ➡️", "prev": "⬅️ Précédent",
        "match": "⚽ <b>{home} 🆚 {away}</b>\n🏆 {comp}\n🕒 {time}\n\n👥 Participants : <b>{n}</b> | 💰 Total misé : <b>{pool}</b> 🪙{your}",
        "your": "\n\n🎯 Votre choix : <b>{pick}</b> — {stake} 🪙",
        "btn_join": "🎯 Participer",
        "stake": "💰 Choisissez votre mise\n(solde : <b>{bal}</b> 🪙 | minimum : {min})",
        "other": "✏️ Autre montant",
        "stake_prompt": "✏️ Envoyez votre mise (un nombre de {min} à {max}) :",
        "stake_bad": "❌ Montant invalide. Envoyez un nombre de {min} à {max}.",
        "stake_low": "❌ Solde insuffisant. Récupérez votre cadeau quotidien dans l'Espace Jeux.",
        "outcome": "🎯 Choisissez votre pronostic :\n<b>{home} 🆚 {away}</b>\n💰 Mise : <b>{stake}</b> 🪙",
        "win_label": "Victoire {team}", "draw_label": "Match nul",
        "placed": "✅ <b>Votre participation est enregistrée</b>\n\n⚽ {home} 🆚 {away}\n🎯 Votre choix : <b>{pick}</b>\n💰 {stake} 🪙\n\n💼 Solde actuel : <b>{bal}</b> 🪙\nVous recevrez le résultat ici après le match.",
        "closed": "🔒 Les pronostics sont fermés pour ce match.",
        "already": "ℹ️ Vous participez déjà à ce match.",
        "mine_head": "📋 <b>Mes pronostics</b>\n\n{rows}",
        "mine_empty": "Vous n'avez fait aucun pronostic.",
        "mine_line": "{icon} {home} – {away}\n    {pick} | {stake} 🪙 {res}",
        "res_win": "→ +{p} 🪙", "res_lose": "→ −{s} 🪙", "res_wait": "⏳", "res_void": "↩️ remboursé",
        "r_win": "🎉 <b>Votre pronostic est bon !</b>\n\n⚽ {home} {score} {away}\n🎯 Votre choix : {pick}\n💰 Gain : <b>+{profit}</b> 🪙 (reçu {payout})\n💼 Solde : <b>{bal}</b> 🪙",
        "r_even": "✅ <b>Votre pronostic est bon !</b>\n\n⚽ {home} {score} {away}\n🎯 {pick}\nVotre mise vous est rendue ({payout} 🪙) car tout le monde a eu raison.\n💼 Solde : <b>{bal}</b> 🪙",
        "r_lose": "❌ <b>Pronostic raté</b>\n\n⚽ {home} {score} {away}\n🎯 Votre choix : {pick}\n💸 Perdu : <b>{stake}</b> 🪙\nPlus de chance au prochain match !",
        "r_void": "↩️ <b>Match annulé / reporté</b>\n\n⚽ {home} 🆚 {away}\nVos <b>{stake}</b> 🪙 ont été remboursés.",
        "new": "⚽ <b>{n}</b> nouveaux matchs sont ouverts aux pronostics ! Participez avant le coup d'envoi 🎯",
        "open_arena": "⚽ Ouvrir l'arène",
        "remind": "⏰ <b>Plus que {min} minutes avant le coup d'envoi !</b>\n\n⚽ {home} 🆚 {away}\n🏆 {comp}\n🕒 {time}\n\nPronostiquez maintenant avant la fermeture 🎯",
        "vote_now": "🎯 Pronostiquer",
        "daily": "🎁 Gagner des coins quotidiens (+{n})",
    },
}

def at(lang, key):
    v = AT.get(lang, AT["ar"])[key]
    if "🆚" in v and not _icons_off():
        v = v.replace("🆚", '<tg-emoji emoji-id="' + VS_EMOJI_ID + '">🆚</tg-emoji>')
    return v

# ---------- تخزين المباريات ----------
def _mk(mid):
    return f"rk:m:{mid}"

def m_get(mid):
    try:
        return kv_get_json(_mk(mid))
    except StorageError:
        return None

def m_save(m):
    kv_set(_mk(m["id"]), json.dumps(m, ensure_ascii=False), ex=45 * 86400)

def m_ids():
    try:
        return [str(x) for x in (db.smembers("rk:mset") or [])]
    except Exception as e:
        print(f"m_ids error: {e}")
        return []

def _preds(mid):
    try:
        raw = db.hgetall(f"rk:mp:{mid}") or {}
    except Exception:
        raw = {}
    out = {}
    for u, v in raw.items():
        try:
            out[str(u)] = v if isinstance(v, dict) else json.loads(v)
        except Exception:
            pass
    return out

def _ts(s):
    return calendar.timegm(time.strptime(s, "%Y-%m-%dT%H:%M:%SZ"))

def _local_time(ts):
    return time.strftime("%d/%m %H:%M", time.gmtime(ts + 3600))   # توقيت الجزائر

def _olabel(lang, m, o):
    if o == "H":
        return at(lang, "win_label").format(team=m["home"])
    if o == "A":
        return at(lang, "win_label").format(team=m["away"])
    return at(lang, "draw_label")

# ---------- عميل football-data ----------
def fb_get(path, params=None):
    if not FB_KEY:
        raise RuntimeError("FOOTBALL_API_KEY غير مضبوط في Render")
    r = requests.get(FB_BASE + path, headers={"X-Auth-Token": FB_KEY}, params=params, timeout=20)
    if r.status_code != 200:
        raise RuntimeError(f"football-data HTTP {r.status_code}: {r.text[:160]}")
    return r.json()

def _fb_outcome(x):
    sc = x.get("score") or {}
    ft = sc.get("regularTime") or sc.get("fullTime") or {}   # نتيجة الـ90 دقيقة
    h, a = ft.get("home"), ft.get("away")
    if h is None or a is None:
        return None, None
    return ("H" if h > a else "A" if a > h else "D"), f"{h}-{a}"

def fb_sync():
    """ينشر مباريات اليوم والغد من المسابقات المختارة. يرجع عدد المباريات الجديدة."""
    now = time.time()
    d1 = time.strftime("%Y-%m-%d", time.gmtime(now))
    d2 = time.strftime("%Y-%m-%d", time.gmtime(now + 2 * 86400))
    data = fb_get("/matches", {"dateFrom": d1, "dateTo": d2, "competitions": MATCH_COMPETITIONS})
    new = 0
    for x in data.get("matches", []):
        try:
            mid = str(x["id"])
            ts = _ts(x["utcDate"])
            st = x.get("status")
            m = m_get(mid)
            if m:
                if m["status"] == "open" and st in ("POSTPONED", "CANCELLED"):
                    void_match(mid)
                elif m["status"] == "open" and m["kickoff"] != ts and st in ("SCHEDULED", "TIMED"):
                    m["kickoff"] = ts
                    m_save(m)
                continue
            if st not in ("SCHEDULED", "TIMED") or ts <= now + 60 or ts > now + 49 * 3600:
                continue
            h, a = x.get("homeTeam") or {}, x.get("awayTeam") or {}
            comp = x.get("competition") or {}
            m = {"id": mid, "comp": comp.get("name", ""), "home": h.get("shortName") or h.get("name") or "?",
                 "away": a.get("shortName") or a.get("name") or "?", "kickoff": ts, "status": "open"}
            m_save(m)
            db.sadd("rk:mset", mid)
            new += 1
        except Exception as e:
            print(f"fb_sync item error: {e}")
    if new:
        _notify_new(new)
    return new

def _notify_new(n):
    monitor_send(f"⚽ <b>نُشرت {n} مباريات جديدة للتوقع</b>")
    try:
        subs = [str(x) for x in (db.smembers("rk:msub") or [])]
    except Exception:
        subs = []

    def _run():
        for u in subs:
            lang = get_lang(u)
            mk = InlineKeyboardMarkup()
            mk.add(InlineKeyboardButton(text=at(lang, "open_arena"), callback_data="gm_ar_0"))
            try:
                bot.send_message(int(u), at(lang, "new").format(n=n), parse_mode="HTML", reply_markup=mk)
            except Exception as e:
                print(f"new matches notify failed: {e}")
            time.sleep(0.05)

    if subs:
        threading.Thread(target=_run, daemon=True).start()

# ---------- الإغلاق والتسوية ----------
def fb_close_due():
    now = time.time()
    for mid in m_ids():
        m = m_get(mid)
        if not m or m["status"] != "open" or now < m["kickoff"]:
            continue
        preds = _preds(mid)
        pool = sum(int(p["s"]) for p in preds.values())
        dist = {"H": 0, "D": 0, "A": 0}
        for p in preds.values():
            dist[p["o"]] = dist.get(p["o"], 0) + int(p["s"])
        m["status"] = "closed"
        m_save(m)
        monitor_send(
            f"🔒 <b>أُغلقت المشاركة</b>\n\n⚽ {html.escape(m['home'])} 🆚 {html.escape(m['away'])}\n"
            f"👥 المشاركون: {len(preds)}\n💰 المجموع: {pool} 🪙\n"
            f"🏠 {dist['H']} | 🤝 {dist['D']} | ✈️ {dist['A']}"
        )
        if not preds:
            m["status"] = "settled"
            m_save(m)
            db.srem("rk:mset", mid)

def _send_user(uid, text):
    try:
        bot.send_message(int(uid), text, parse_mode="HTML")
    except Exception as e:
        print(f"arena notify failed: {e}")
    time.sleep(0.05)

def settle_match(mid, result, score=None):
    """تسوية: الفائز يسترجع رهانه + مكافأة تلقائية (نصف رهانه) + حصته من رهانات الخاسرين بنسبة رهانه. إذا لم يصب أحد يخسر الجميع."""
    if not kv_set(f"rk:msettle:{mid}", "1", ex=45 * 86400, nx=True):
        return "⚠️ تمت تسوية هذه المباراة سابقاً."
    m = m_get(mid)
    if not m:
        kv_del(f"rk:msettle:{mid}")
        return "❌ مباراة غير موجودة."
    preds = _preds(mid)
    pool = sum(int(p["s"]) for p in preds.values())
    win_stake = sum(int(p["s"]) for p in preds.values() if p["o"] == result)
    lose_stake = pool - win_stake
    score_txt = score or "🆚"
    winners = 0
    for uid, p in preds.items():
        lang = get_lang(uid)
        s = int(p["s"])
        pick = _olabel(lang, m, p["o"])
        names = dict(home=m["home"], away=m["away"], score=score_txt, pick=pick)
        if p["o"] == result:
            winners += 1
            bonus = s * MATCH_BONUS_PCT // 100
            payout = s + bonus + (s * lose_stake) // win_stake
            profit = payout - s
            bal = coins_add(uid, payout, "match", score=False)
            if profit > 0:
                lb_score_add(uid, profit)
            p["p"] = payout
            key = "r_win" if profit > 0 else "r_even"
            _send_user(uid, at(lang, key).format(profit=profit, payout=payout, bal=bal, **names))
        else:
            p["p"] = 0
            _send_user(uid, at(lang, "r_lose").format(stake=s, **names))
        try:
            db.hset(f"rk:mp:{mid}", uid, json.dumps(p))
        except Exception as e:
            print(f"pred update failed: {e}")
    m["status"] = "settled"
    m["result"] = result
    m["score"] = score_txt
    m_save(m)
    try:
        db.srem("rk:mset", mid)
    except Exception:
        pass
    monitor_send(
        f"✅ <b>تمت تسوية مباراة</b>\n\n⚽ {html.escape(m['home'])} {html.escape(score_txt)} {html.escape(m['away'])}\n"
        f"👥 {len(preds)} مشارك | 🏆 {winners} فائز\n💰 المجموع: {pool} 🪙"
        + ("\n⚠️ لم يصب أحد: خسر الجميع." if preds and winners == 0 else "")
    )
    return f"✅ سُوّيت: {len(preds)} مشارك، {winners} فائز، المجموع {pool} 🪙."

def void_match(mid):
    """مباراة ملغاة/مؤجلة: تُرجع كل الرهانات."""
    if not kv_set(f"rk:msettle:{mid}", "1", ex=45 * 86400, nx=True):
        return "⚠️ تمت معالجة هذه المباراة سابقاً."
    m = m_get(mid)
    if not m:
        kv_del(f"rk:msettle:{mid}")
        return "❌ مباراة غير موجودة."
    preds = _preds(mid)
    for uid, p in preds.items():
        s = int(p["s"])
        coins_add(uid, s, "match-refund", score=False)
        p["p"] = -1
        try:
            db.hset(f"rk:mp:{mid}", uid, json.dumps(p))
        except Exception:
            pass
        _send_user(uid, at(get_lang(uid), "r_void").format(home=m["home"], away=m["away"], stake=s))
    m["status"] = "void"
    m_save(m)
    try:
        db.srem("rk:mset", mid)
    except Exception:
        pass
    monitor_send(f"↩️ <b>مباراة ملغاة/مؤجلة</b>: {html.escape(m['home'])} 🆚 {html.escape(m['away'])}\nأُعيد لـ {len(preds)} مشارك رهاناتهم.")
    return f"↩️ أُرجعت رهانات {len(preds)} مشارك."

def fb_check_results():
    now = time.time()
    pend = []
    for mid in m_ids():
        m = m_get(mid)
        if m and m["status"] == "closed" and now >= m["kickoff"] + 100 * 60:
            pend.append(m)
    if not pend:
        return 0
    data = fb_get("/matches", {"ids": ",".join(m["id"] for m in pend)})
    done = 0
    by_id = {str(x["id"]): x for x in data.get("matches", [])}
    for m in pend:
        x = by_id.get(m["id"])
        if not x:
            continue
        st = x.get("status")
        if st == "FINISHED":
            res, score = _fb_outcome(x)
            if res:
                settle_match(m["id"], res, score)
                done += 1
        elif st in ("POSTPONED", "CANCELLED"):
            void_match(m["id"])
            done += 1
        elif now > m["kickoff"] + 12 * 3600:
            monitor_send(
                f"⏳ <b>نتيجة معلّقة</b>: {html.escape(m['home'])} 🆚 {html.escape(m['away'])}\n"
                f"سوّها يدوياً: <code>/matchresult {m['id']} H|D|A</code>",
                key=f"mres_{m['id']}", cooldown=6 * 3600)
    return done

def fb_remind_due():
    """تذكير قبل صافرة البداية بـ MATCH_REMIND_MINUTES دقائق لمن فعّل 🔔 ولم يشارك بعد."""
    now = time.time()
    due = []
    for mid in m_ids():
        m = m_get(mid)
        if not m or m["status"] != "open":
            continue
        left = m["kickoff"] - now
        if 0 < left <= MATCH_REMIND_MINUTES * 60 and kv_set(f"rk:mrem:{mid}", "1", ex=2 * 86400, nx=True):
            due.append(m)
    if not due:
        return
    try:
        subs = [str(x) for x in (db.smembers("rk:msub") or [])]
    except Exception:
        subs = []

    def _run(m):
        preds = _preds(m["id"])
        sent_n = 0
        for u in subs:
            if u in preds:
                continue
            lang = get_lang(u)
            mk = InlineKeyboardMarkup(row_width=1)
            mk.add(InlineKeyboardButton(text=at(lang, "vote_now"), callback_data=f"gm_mp_{m['id']}"))
            mk.add(InlineKeyboardButton(text=at(lang, "daily").format(n=DAILY_GIFT_COINS), callback_data="gm_gift"))
            try:
                bot.send_message(int(u), at(lang, "remind").format(
                    min=MATCH_REMIND_MINUTES, home=html.escape(m["home"]), away=html.escape(m["away"]),
                    comp=html.escape(m["comp"]), time=_local_time(m["kickoff"])), parse_mode="HTML", reply_markup=mk)
                sent_n += 1
            except Exception as e:
                print(f"match reminder failed: {e}")
            time.sleep(0.05)
        monitor_send(f"⏰ <b>تذكير قبل {MATCH_REMIND_MINUTES} دقائق</b>: {html.escape(m['home'])} 🆚 {html.escape(m['away'])}\nأُرسل لـ {sent_n} زبون.")

    for m in due:
        threading.Thread(target=_run, args=(m,), daemon=True).start()

def _arena_loop():
    time.sleep(90)
    last_sync = last_res = 0
    while True:
        try:
            fb_close_due()
            fb_remind_due()
            now = time.time()
            if FB_KEY and now - last_sync > 1800:
                last_sync = now
                fb_sync()
            if FB_KEY and now - last_res > 600:
                last_res = now
                fb_check_results()
        except Exception as e:
            print(f"arena loop error: {e}")
            monitor_send(f"🚨 <b>خطأ في ساحة المباريات</b>\n<code>{html.escape(str(e))[:250]}</code>", key="arena_err", cooldown=3600)
        time.sleep(60)

if db and FB_KEY:
    threading.Thread(target=_arena_loop, daemon=True).start()

# ---------- الواجهة ----------
def _open_matches():
    now = time.time()
    out = []
    for mid in m_ids():
        m = m_get(mid)
        if m and m["status"] == "open" and m["kickoff"] > now:
            out.append(m)
    out.sort(key=lambda m: m["kickoff"])
    return out

def ar_list(call, lang, page=0):
    uid = call.from_user.id
    _lb_touch(call.from_user)
    ms = _open_matches()
    pages = max(1, (len(ms) + AR_PAGE - 1) // AR_PAGE)
    page = max(0, min(page, pages - 1))
    mk = InlineKeyboardMarkup(row_width=1)
    for m in ms[page * AR_PAGE:(page + 1) * AR_PAGE]:
        mk.add(InlineKeyboardButton(text=f"🕒 {_local_time(m['kickoff'])[-5:]} | {m['home']} – {m['away']}",
                                    callback_data=f"gm_mt_{m['id']}"))
    if pages > 1:
        nav = []
        if page > 0:
            nav.append(InlineKeyboardButton(text=at(lang, "prev"), callback_data=f"gm_ar_{page - 1}"))
        if page < pages - 1:
            nav.append(InlineKeyboardButton(text=at(lang, "next"), callback_data=f"gm_ar_{page + 1}"))
        mk.row(*nav)
    try:
        subscribed = db.sismember("rk:msub", str(uid))
    except Exception:
        subscribed = False
    mk.add(InlineKeyboardButton(text=at(lang, "mine"), callback_data="gm_mine"))
    mk.add(InlineKeyboardButton(text=at(lang, "notify_off" if subscribed else "notify_on"), callback_data="gm_ms"))
    mk.add(InlineKeyboardButton(text=t(lang, "back"), callback_data="gm_hub"))
    body = at(lang, "pick") if ms else at(lang, "none")
    _pf_show(call, at(lang, "arena").format(bal=coins_get(uid), body=body), mk)

def ar_toggle_sub(call, lang):
    uid = str(call.from_user.id)
    if db.sismember("rk:msub", uid):
        db.srem("rk:msub", uid)
        msg = at(lang, "sub_off")
    else:
        db.sadd("rk:msub", uid)
        msg = at(lang, "sub_on")
        monitor_send(f"🔔 <b>زبون فعّل إشعارات المباريات</b>\n👤 {_user_link(uid)}")
    bot.answer_callback_query(call.id, msg, show_alert=True)
    ar_list(call, lang, 0)

def ar_match(call, lang, mid, answer=True):
    uid = call.from_user.id
    m = m_get(mid)
    if not m:
        ar_list(call, lang, 0)
        return
    preds = _preds(mid)
    mine = preds.get(str(uid))
    your = at(lang, "your").format(pick=_olabel(lang, m, mine["o"]), stake=mine["s"]) if mine else ""
    mk = InlineKeyboardMarkup(row_width=1)
    if m["status"] == "open" and m["kickoff"] > time.time() and not mine:
        mk.add(InlineKeyboardButton(text=at(lang, "btn_join"), callback_data=f"gm_mp_{mid}"))
    mk.add(InlineKeyboardButton(text=t(lang, "back"), callback_data="gm_ar_0"))
    _pf_show(call, at(lang, "match").format(
        home=html.escape(m["home"]), away=html.escape(m["away"]), comp=html.escape(m["comp"]),
        time=_local_time(m["kickoff"]), n=len(preds), pool=sum(int(p["s"]) for p in preds.values()), your=your), mk)

def _can_join(m):
    return bool(m) and m["status"] == "open" and m["kickoff"] > time.time()

def ar_stake(call, lang, mid):
    uid = call.from_user.id
    m = m_get(mid)
    if not _can_join(m):
        bot.answer_callback_query(call.id, at(lang, "closed"), show_alert=True)
        ar_list(call, lang, 0)
        return
    bal = coins_get(uid)
    if bal < MATCH_MIN_STAKE:
        bot.answer_callback_query(call.id, at(lang, "stake_low"), show_alert=True)
        return
    mk = InlineKeyboardMarkup(row_width=2)
    mk.row(*[InlineKeyboardButton(text=str(a), callback_data=f"gm_mk_{mid}_{a}") for a in STAKE_CHOICES if a <= bal])
    mk.add(InlineKeyboardButton(text=at(lang, "other"), callback_data=f"gm_mc_{mid}"))
    mk.add(InlineKeyboardButton(text=t(lang, "back"), callback_data=f"gm_mt_{mid}"))
    _pf_show(call, at(lang, "stake").format(bal=bal, min=MATCH_MIN_STAKE), mk)

def _outcome_screen(lang, m, mid, stake):
    mk = InlineKeyboardMarkup(row_width=1)
    for o in ("H", "D", "A"):
        icon = {"H": "🏠", "D": "🤝", "A": "✈️"}[o]
        mk.add(InlineKeyboardButton(text=f"{icon} {_olabel(lang, m, o)}", callback_data=f"gm_mo_{mid}_{o}_{stake}"))
    mk.add(InlineKeyboardButton(text=t(lang, "back"), callback_data=f"gm_mp_{mid}"))
    text = at(lang, "outcome").format(home=html.escape(m["home"]), away=html.escape(m["away"]), stake=stake)
    return text, mk

def ar_pick(call, lang, arg):
    mid, stake = arg.split(SEP, 1)
    m = m_get(mid)
    if not _can_join(m):
        bot.answer_callback_query(call.id, at(lang, "closed"), show_alert=True)
        ar_list(call, lang, 0)
        return
    text, mk = _outcome_screen(lang, m, mid, int(stake))
    _pf_show(call, text, mk)

def ar_custom(call, lang, mid):
    uid = call.from_user.id
    m = m_get(mid)
    if not _can_join(m):
        bot.answer_callback_query(call.id, at(lang, "closed"), show_alert=True)
        return
    bal = coins_get(uid)
    if bal < MATCH_MIN_STAKE:
        bot.answer_callback_query(call.id, at(lang, "stake_low"), show_alert=True)
        return
    _mp_wait[uid] = mid
    mk = InlineKeyboardMarkup()
    mk.add(InlineKeyboardButton(text=t(lang, "cancel"), callback_data=f"gm_mp_{mid}"))
    _pf_show(call, at(lang, "stake_prompt").format(min=MATCH_MIN_STAKE, max=bal), mk)

def place_prediction(uid, mid, outcome, stake):
    """يرجع (ok، مفتاح رسالة)."""
    m = m_get(mid)
    if not _can_join(m):
        return False, "closed"
    if outcome not in ("H", "D", "A") or stake < MATCH_MIN_STAKE:
        return False, "stake_bad"
    if db.hget(f"rk:mp:{mid}", str(uid)):
        return False, "already"
    if not coins_take(uid, stake, "match"):
        return False, "stake_low"
    if not db.hsetnx(f"rk:mp:{mid}", str(uid), json.dumps({"o": outcome, "s": stake, "p": None})):
        coins_add(uid, stake, "match-refund", score=False)
        return False, "already"
    try:
        db.lpush(f"rk:mu:{uid}", mid)
        db.ltrim(f"rk:mu:{uid}", 0, 39)
    except Exception as e:
        print(f"mu index error: {e}")
    return True, "placed"

def ar_place(call, lang, arg):
    try:
        mid, o, stake = arg.split(SEP, 2)
        stake = int(stake)
    except Exception:
        bot.answer_callback_query(call.id)
        return
    ok, key = place_prediction(call.from_user.id, mid, o, stake)
    if not ok:
        bot.answer_callback_query(call.id, at(lang, key).format(min=MATCH_MIN_STAKE, max=coins_get(call.from_user.id)), show_alert=True)
        ar_match(call, lang, mid)
        return
    m = m_get(mid)
    mk = InlineKeyboardMarkup(row_width=1)
    mk.add(InlineKeyboardButton(text=at(lang, "mine"), callback_data="gm_mine"))
    mk.add(InlineKeyboardButton(text=t(lang, "back"), callback_data="gm_ar_0"))
    _pf_show(call, at(lang, "placed").format(
        home=html.escape(m["home"]), away=html.escape(m["away"]), pick=_olabel(lang, m, o),
        stake=stake, bal=coins_get(call.from_user.id)), mk)

def ar_mine(call, lang):
    uid = call.from_user.id
    try:
        ids = [str(x) for x in (db.lrange(f"rk:mu:{uid}", 0, 14) or [])]
    except Exception:
        ids = []
    rows = []
    for mid in ids:
        m = m_get(mid)
        p = _preds(mid).get(str(uid))
        if not m or not p:
            continue
        s, pay = int(p["s"]), p.get("p")
        if pay is None:
            icon, res = "⏳", at(lang, "res_wait")
        elif pay == -1:
            icon, res = "↩️", at(lang, "res_void")
        elif pay > 0:
            icon, res = "✅", at(lang, "res_win").format(p=pay - s) if pay > s else "✅"
        else:
            icon, res = "❌", at(lang, "res_lose").format(s=s)
        rows.append(at(lang, "mine_line").format(icon=icon, home=html.escape(m["home"]), away=html.escape(m["away"]),
                                                  pick=_olabel(lang, m, p["o"]), stake=s, res=res))
    mk = InlineKeyboardMarkup(row_width=1)
    mk.add(InlineKeyboardButton(text=t(lang, "back"), callback_data="gm_ar_0"))
    _pf_show(call, at(lang, "mine_head").format(rows="\n\n".join(rows) or at(lang, "mine_empty")), mk)

def _awaiting_mp(m):
    return (bool(m.text) and not m.text.startswith("/") and m.chat.type == "private"
            and m.from_user.id in _mp_wait)

@bot.message_handler(func=_awaiting_mp, content_types=["text"])
def handle_mp_amount(message):
    uid = message.from_user.id
    lang = get_lang(uid)
    mid = _mp_wait[uid]
    bal = coins_get(uid)
    txt = message.text.strip()
    if not txt.isdigit() or not (MATCH_MIN_STAKE <= int(txt) <= bal):
        bot.reply_to(message, at(lang, "stake_bad").format(min=MATCH_MIN_STAKE, max=bal))
        return
    _mp_wait.pop(uid, None)
    m = m_get(mid)
    if not _can_join(m):
        bot.send_message(message.chat.id, at(lang, "closed"))
        return
    text, mk = _outcome_screen(lang, m, mid, int(txt))
    bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=mk)

# ---------- أوامر الأدمن ----------
@bot.message_handler(commands=["matchfetch", "matches", "matchresult", "matchvoid"])
def arena_admin(message):
    if not is_admin_msg(message):
        return
    cmd = message.text.split()[0].lstrip("/").split("@")[0]
    a = message.text.split()[1:]
    if cmd == "matchfetch":
        try:
            n = fb_sync()
            bot.reply_to(message, f"✅ الاتصال يعمل. نُشرت {n} مباراة جديدة. المفتوحة الآن: {len(_open_matches())}")
        except Exception as e:
            bot.reply_to(message, f"❌ {str(e)[:400]}")
    elif cmd == "matches":
        lines = []
        for mid in m_ids():
            m = m_get(mid)
            if m:
                lines.append(f"{m['id']} | {m['status']} | {_local_time(m['kickoff'])} | {m['home']}–{m['away']} | 👥{len(_preds(mid))}")
        bot.reply_to(message, "\n".join(lines[:40]) or "لا توجد مباريات نشطة.")
    elif cmd == "matchresult":
        if len(a) < 2 or a[1].upper() not in ("H", "D", "A"):
            bot.reply_to(message, "الاستعمال: /matchresult ID H|D|A   (H فوز الأول، D تعادل، A فوز الثاني)")
            return
        bot.reply_to(message, settle_match(a[0], a[1].upper()))
    elif cmd == "matchvoid":
        if not a:
            bot.reply_to(message, "الاستعمال: /matchvoid ID")
            return
        bot.reply_to(message, void_match(a[0]))

# ============================================================
# ========== وضع التحديث (صيانة): يوقف البوت عند الزبائن ويبقى للأدمن ==========
# ============================================================
MAINT_KEY = "rk:maint"
MAINT_SUBS = "rk:maint:subs"
_maint_cache = {"t": 0.0, "v": False}

def _maint_on():
    now = time.time()
    if now - _maint_cache["t"] < 3:
        return _maint_cache["v"]
    try:
        v = str(kv_get(MAINT_KEY)) == "1"
    except Exception:
        v = _maint_cache["v"]
    _maint_cache.update(t=now, v=v)
    return v

MAINT_END_KEY = "rk:maint:end"
_maint_end_cache = {"t": 0.0, "v": 0}

def _maint_end_ts():
    now = time.time()
    if now - _maint_end_cache["t"] < 60:
        return _maint_end_cache["v"]
    try:
        v = int(float(kv_get(MAINT_END_KEY) or 0))
    except Exception:
        v = _maint_end_cache["v"]
    _maint_end_cache.update(t=now, v=v)
    return v

def _maint_set(on):
    was = _maint_cache["v"]
    kv_set(MAINT_KEY, "1" if on else "0")
    _maint_cache.update(t=time.time(), v=bool(on))
    if was and not on:
        ts = int(time.time())
        try:
            kv_set(MAINT_END_KEY, str(ts))
        except Exception:
            pass
        _maint_end_cache.update(t=time.time(), v=ts)

def _maint_label():
    return "🛠️ وضع التحديث: " + ("✅ شغّال (اضغط للإيقاف)" if _maint_on() else "⛔ مطفأ (اضغط للتشغيل)")

MAINT_TEXTS = {
    "ar": {
        "msg": "{W}RASEEDKOM:{W}\n{H} [[b]]البوت قيد التحديث[[/b]] {S}\n\nمرحباً بك في RASEEDKOM!\nنعمل حالياً على تحديث جديد لنقدّم لك تجربة أفضل ومنتجات أكثر.\n\n{T} لن يستغرق التحديث وقتاً طويلاً، وسيعود البوت للعمل قريباً بإذن الله.\n\n{B} اضغط على زر «أعلمني عند البدء»، وسيصلك إشعار فور عودة البوت للعمل.\n\n{F} شكراً لصبرك وثقتك بنا {R}",
        "notify": "🔔 أعلمني عند البدء", "channel": "📢 القناة الرسمية", "support": "💬 الدعم",
        "ok": "✅ تم! سنخبرك فور عودة البوت للعمل.", "already": "✅ أنت مسجّل مسبقاً، سنخبرك فور عودة البوت.",
        "back": "{X} [[b]]عاد البوت للعمل![[/b]]\n\nاضغط على زر «{upd}» للبدء {Y}\n\n{Z} شكراً لصبرك {Z}",
        "go": "🔄 تحديث",
    },
    "en": {
        "msg": "{W}RASEEDKOM:{W}\n{H} [[b]]The bot is being updated[[/b]] {S}\n\nWelcome to RASEEDKOM!\nWe are working on a new update to bring you a better experience and more products.\n\n{T} The update won't take long, and the bot will be back soon, God willing.\n\n{B} Tap «Notify me when it starts» and you'll get a message as soon as the bot is back.\n\n{F} Thank you for your patience and trust {R}",
        "notify": "🔔 Notify me when it starts", "channel": "📢 Official channel", "support": "💬 Support",
        "ok": "✅ Done! We'll let you know as soon as the bot is back.", "already": "✅ You're already subscribed, we'll notify you when the bot is back.",
        "back": "{X} [[b]]The bot is back online![[/b]]\n\nTap the «{upd}» button to start {Y}\n\n{Z} Thank you for your patience {Z}",
        "go": "🔄 Refresh",
    },
    "fr": {
        "msg": "{W}RASEEDKOM:{W}\n{H} [[b]]Le bot est en cours de mise à jour[[/b]] {S}\n\nBienvenue sur RASEEDKOM !\nNous travaillons sur une nouvelle mise à jour pour vous offrir une meilleure expérience et plus de produits.\n\n{T} La mise à jour ne sera pas longue, le bot sera de retour très bientôt, si Dieu le veut.\n\n{B} Appuyez sur « Me prévenir au démarrage » et vous recevrez une notification dès le retour du bot.\n\n{F} Merci pour votre patience et votre confiance {R}",
        "notify": "🔔 Me prévenir au démarrage", "channel": "📢 Canal officiel", "support": "💬 Assistance",
        "ok": "✅ C'est noté ! Nous vous préviendrons dès le retour du bot.", "already": "✅ Vous êtes déjà inscrit, nous vous préviendrons au retour du bot.",
        "back": "{X} [[b]]Le bot est de retour ![[/b]]\n\nAppuyez sur le bouton «{upd}» pour commencer {Y}\n\n{Z} Merci pour votre patience {Z}",
        "go": "🔄 Actualiser",
    },
}

def _maint_tx(lang):
    return MAINT_TEXTS.get(lang) or MAINT_TEXTS["ar"]

def _maint_markup(lang):
    tx = _maint_tx(lang)
    mk = InlineKeyboardMarkup(row_width=1)
    b1 = InlineKeyboardButton(text=tx["notify"], callback_data="mnt_notify")
    b1.icon_dyn = MAINT_EMO["B"]
    mk.add(b1)
    b2 = InlineKeyboardButton(text=tx["channel"], url=CHANNEL_LINK)
    b2.icon_dyn = ICON_MENU_CHANNEL
    mk.add(b2)
    b3 = InlineKeyboardButton(text=tx["support"], url=MY_PRIVATE_CHAT_LINK)
    b3.icon_dyn = ICON_SUPPORT
    mk.add(b3)
    return mk

MAINT_EMO = {"W": "5447644880824181073", "H": "5197371802136892976", "S": "5440621591387980068",
             "T": "5454415424319931791", "B": "5458603043203327669", "F": "5217712513847676489",
             "R": "5300779290181262152",
             "X": "5226928895189598791", "Y": "5453957774079706024", "Z": "5447183459602669338"}
MAINT_ICON_REFRESH = "6136212667624331858"
MAINT_EMO_FALLBACK = {"W": "⚠️", "H": "🔨", "S": "🔜", "T": "⏳", "B": "🔔", "F": "🙂", "R": "🔥", "X": "✅", "Y": "👇", "Z": "🔻"}

def _maint_build(text, custom=True):
    """يحوّل {W}.. إلى إيموجي مخصص (entities) و [[b]]..[[/b]] إلى خط عريض."""
    plain, ents, bold_start = "", [], None
    pos = 0
    for m in re.finditer(r"\{([WHSTBFRXYZ])\}|\[\[(/?)b\]\]", text):
        plain += text[pos:m.start()]
        pos = m.end()
        if m.group(1):
            k = m.group(1)
            if custom:
                ents.append(telebot.types.MessageEntity("custom_emoji", _u16(plain), 1, custom_emoji_id=MAINT_EMO[k]))
                plain += "⭐"
            else:
                plain += MAINT_EMO_FALLBACK[k]
        elif m.group(2):
            if bold_start is not None:
                ents.append(telebot.types.MessageEntity("bold", bold_start, _u16(plain) - bold_start))
                bold_start = None
        else:
            bold_start = _u16(plain)
    plain += text[pos:]
    return plain, ents

def _maint_alert_text(lang):
    plain, _ = _maint_build(_maint_tx(lang)["msg"], custom=False)
    lines = [x for x in plain.split("\n") if x.strip()]
    return (lines[1] if len(lines) > 1 else lines[0])[:190]

import json as _json
MAINT_SEEN = "rk:maint:seen"      # كل من ظهرت له رسالة التحديث (يصله إشعار العودة)
MAINT_MSGS = "rk:maint:m:"        # رسائل التحديث لكل زبون (لحذفها عند العودة)
_maint_msgs_mem = {}
_maint_seen_mem = set()

def _maint_get_msgs(uid):
    uid = str(uid)
    if uid in _maint_msgs_mem:
        return list(_maint_msgs_mem[uid])
    try:
        raw = kv_get(MAINT_MSGS + uid)
        return list(_json.loads(raw)) if raw else []
    except Exception:
        return []

def _maint_track(uid, chat_id, mid):
    uid = str(uid)
    lst = _maint_get_msgs(uid)
    if [chat_id, mid] not in lst:
        lst.append([chat_id, mid])
    lst = lst[-5:]
    _maint_msgs_mem[uid] = lst
    try:
        kv_set(MAINT_MSGS + uid, _json.dumps(lst))
    except Exception:
        pass
    if uid not in _maint_seen_mem:
        _maint_seen_mem.add(uid)
        try:
            _sadd(MAINT_SEEN, uid)
        except Exception:
            pass

def _maint_clear_msgs(uid, keep=None):
    """يحذف رسائل التحديث السابقة لهذا الزبون (ما عدا keep=[chat,mid])."""
    uid = str(uid)
    for c, m in _maint_get_msgs(uid):
        if keep and [c, m] == list(keep):
            continue
        try:
            bot.delete_message(c, m)
        except Exception:
            pass
    _maint_msgs_mem.pop(uid, None)
    try:
        kv_del(MAINT_MSGS + uid)
    except Exception:
        pass

def _maint_send_new(chat_id, lang):
    tx = _maint_tx(lang)
    mk = _maint_markup(lang)
    if not _icons_off():
        try:
            plain, ents = _maint_build(tx["msg"], custom=True)
            if len(plain) <= 1000:
                return bot.send_photo(chat_id, UNIFIED_IMAGE_URL, caption=plain, caption_entities=ents, reply_markup=mk)
            return bot.send_message(chat_id, plain, entities=ents, reply_markup=mk)
        except Exception as e:
            print(f"maintenance custom-emoji failed: {e}")
    plain, ents = _maint_build(tx["msg"], custom=False)
    ents = [x for x in ents if x.type == "bold"]
    try:
        if len(plain) <= 1000:
            return bot.send_photo(chat_id, UNIFIED_IMAGE_URL, caption=plain, caption_entities=ents, reply_markup=mk)
    except Exception as e:
        print(f"maintenance photo failed: {e}")
    try:
        return bot.send_message(chat_id, plain, entities=ents, reply_markup=mk)
    except Exception as e:
        print(f"maintenance message failed: {e}")
    return None

def send_maintenance(chat_id, lang):
    _maint_clear_msgs(chat_id)      # لا نترك رسائل تحديث قديمة متراكمة
    msg = _maint_send_new(chat_id, lang)
    if msg is not None:
        _maint_track(chat_id, chat_id, msg.message_id)

def _maint_edit_into(call, lang):
    """يحوّل القائمة المفتوحة عند الزبون نفسها إلى رسالة التحديث (تختفي القائمة)."""
    m = call.message
    ics = not _icons_off()
    plain, ents = _maint_build(_maint_tx(lang)["msg"], custom=ics)
    if not ics:
        ents = [x for x in ents if x.type == "bold"]
    mk = _maint_markup(lang)
    try:
        if getattr(m, "photo", None):
            bot.edit_message_caption(caption=plain, chat_id=m.chat.id, message_id=m.message_id,
                                     caption_entities=ents, reply_markup=mk)
        else:
            bot.edit_message_text(plain, m.chat.id, m.message_id, entities=ents, reply_markup=mk)
        _maint_clear_msgs(call.from_user.id, keep=[m.chat.id, m.message_id])
        _maint_track(call.from_user.id, m.chat.id, m.message_id)
        return
    except Exception as e:
        if "not modified" in str(e):
            _maint_track(call.from_user.id, m.chat.id, m.message_id)
            return
        print(f"maint edit failed: {e}")
    try:
        bot.delete_message(m.chat.id, m.message_id)
    except Exception:
        pass
    send_maintenance(m.chat.id, lang)

_send_main_menu_pre_maint = send_main_menu

def send_main_menu(chat_id, lang):
    if _maint_on() and str(chat_id) != str(ADMIN_CHAT_ID):
        return send_maintenance(chat_id, lang)
    return _send_main_menu_pre_maint(chat_id, lang)

_maint_last = {}

def _maint_blocked_user(user):
    return bool(user) and str(user.id) != str(ADMIN_CHAT_ID) and _maint_on()

_MAINT_PASS_CMDS = ("/start", "/language", "/lang", "/update", "/refresh")

def _maint_msg_filter(m):
    try:
        if m.chat.type != "private" or not _maint_blocked_user(m.from_user):
            return False
        txt = (m.text or "").strip()
        if txt.split(" ")[0].split("@")[0].lower() in _MAINT_PASS_CMDS:
            return False
        if txt in KB_UPDATE_TEXTS or txt in KB_LANG_TEXTS:
            return False
        return True
    except Exception:
        return False

@bot.message_handler(func=_maint_msg_filter, content_types=["text", "photo", "video", "document", "sticker", "voice", "audio", "contact", "location"])
def maint_block_message(message):
    uid = str(message.from_user.id)
    now = time.time()
    if now - _maint_last.get(uid, 0) < 20:
        return
    _maint_last[uid] = now
    if uid in user_lang:
        send_maintenance(message.chat.id, get_lang(uid))
    elif gate_ok(message.chat.id, message.from_user.id):
        send_language_menu(message.chat.id)

bot.message_handlers.insert(0, bot.message_handlers.pop())

_MAINT_PASS_CB = ("gate_verify", "change_lang", "mnt_notify", "mn_refresh")

def _maint_cb_filter(c):
    try:
        if not _maint_blocked_user(c.from_user):
            return False
        d = c.data or ""
        if d in _MAINT_PASS_CB or d.startswith("lang_"):
            return False
        return True
    except Exception:
        return False

@bot.callback_query_handler(func=_maint_cb_filter)
def maint_block_callback(call):
    lang = get_lang(call.from_user.id) if str(call.from_user.id) in user_lang else "ar"
    try:
        bot.answer_callback_query(call.id, _maint_alert_text(lang))
    except Exception:
        pass
    try:
        _maint_edit_into(call, lang)
    except Exception as e:
        print(f"maint edit error: {e}")

bot.callback_query_handlers.insert(0, bot.callback_query_handlers.pop())

# ---- أزرار رسائل قديمة (أُرسلت قبل نهاية آخر تحديث): لا نفتح القائمة القديمة، بل نرسل قائمة جديدة ----
STALE_TEXTS = {
    "ar": "✨ تم تحديث البوت! أرسلنا لك القائمة الجديدة، اضغط «المنتجات» من الأسفل.",
    "en": "✨ The bot was updated! We sent you the new menu, tap «Products» below.",
    "fr": "✨ Le bot a été mis à jour ! Nouveau menu envoyé, appuyez sur « Produits » en bas.",
}

def _stale_cb_filter(c):
    try:
        if not c.from_user or str(c.from_user.id) == str(ADMIN_CHAT_ID):
            return False
        m = c.message
        if not m or getattr(m.chat, "type", "") != "private":
            return False
        d = c.data or ""
        if d in _MAINT_PASS_CB or d.startswith("lang_") or d == "noop":
            return False
        end = _maint_end_ts()
        if not end or _maint_on():
            return False
        return int(getattr(m, "date", 0) or 0) < end
    except Exception:
        return False

@bot.callback_query_handler(func=_stale_cb_filter)
def stale_callback(call):
    uid = str(call.from_user.id)
    lang = get_lang(uid) if uid in user_lang else "ar"
    try:
        bot.answer_callback_query(call.id, STALE_TEXTS.get(lang, STALE_TEXTS["ar"]), show_alert=True)
    except Exception:
        pass
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    except Exception:
        pass
    try:
        send_main_menu(call.message.chat.id, lang)
    except Exception as e:
        print(f"stale menu error: {e}")

bot.callback_query_handlers.insert(0, bot.callback_query_handlers.pop())

@bot.callback_query_handler(func=lambda c: c.data == "mnt_notify")
def maint_notify_cb(call):
    uid = str(call.from_user.id)
    lang = get_lang(uid) if uid in user_lang else "ar"
    tx = _maint_tx(lang)
    try:
        was = uid in _smembers(MAINT_SUBS)
        if not was:
            _sadd(MAINT_SUBS, uid)
        bot.answer_callback_query(call.id, tx["already" if was else "ok"], show_alert=True)
        if not was:
            try:
                total = len(_smembers(MAINT_SUBS))
                u = call.from_user
                nm = html.escape(((u.first_name or "") + " " + (u.last_name or "")).strip() or "—")
                un = f" @{u.username}" if getattr(u, "username", None) else ""
                bot.send_message(ADMIN_CHAT_ID,
                    f"🔔 <b>زبون ضغط «أعلمني عند البدء»</b>\n👤 {nm}{un} (ID: <code>{uid}</code>)\n\n📊 المنتظرون الآن: <b>{total}</b>",
                    parse_mode="HTML")
            except Exception as e:
                print(f"maint admin notify failed: {e}")
    except Exception as e:
        print(f"maint notify error: {e}")

def _maint_broadcast_back():
    try:
        targets = set(map(str, _smembers(MAINT_SUBS))) | set(map(str, _smembers(MAINT_SEEN)))
    except Exception:
        targets = set()
    targets |= set(_maint_seen_mem)
    if not targets:
        return 0

    def _run():
        sent = 0
        for uid in targets:
            try:
                _maint_clear_msgs(uid)     # تختفي رسالة التحديث
                lang = get_lang(uid) if str(uid) in user_lang else "ar"
                tx = _maint_tx(lang)
                txt = tx["back"].replace("{upd}", re.sub(r"^[^\w]+", "", t(lang, "kb_update")).strip() or t(lang, "kb_update"))
                try:    # يثبّت زر «تحديث» في الأسفل (لوحة المفاتيح تبقى بعد حذف الرسالة)
                    kbm = bot.send_message(int(uid), "🔄", reply_markup=build_reply_keyboard(lang))
                    bot.delete_message(int(uid), kbm.message_id)
                except Exception:
                    pass
                mk_back = InlineKeyboardMarkup()
                bgo = InlineKeyboardButton(text=tx["go"], callback_data="mn_refresh")
                bgo.icon_dyn = MAINT_ICON_REFRESH
                mk_back.add(bgo)
                sent_ok = False
                if not _icons_off():
                    try:
                        pl, en = _maint_build(txt, custom=True)
                        bot.send_message(int(uid), pl, entities=en, reply_markup=mk_back)
                        sent_ok = True
                    except Exception as e:
                        print(f"back custom-emoji failed: {e}")
                if not sent_ok:
                    pl, en = _maint_build(txt, custom=False)
                    bot.send_message(int(uid), pl, entities=[x for x in en if x.type == "bold"], reply_markup=mk_back)
                sent += 1
            except Exception:
                pass
            time.sleep(0.06)
        for k in (MAINT_SUBS, MAINT_SEEN):
            try:
                kv_del(k)
            except Exception:
                pass
        _maint_seen_mem.clear()
        _maint_msgs_mem.clear()
        monitor_send(f"🔔 <b>أُرسل إشعار عودة البوت</b> لـ {sent} زبون")

    threading.Thread(target=_run, daemon=True).start()
    return len(targets)

@bot.message_handler(commands=["maint", "maintenance"])
def maint_command(message):
    if not is_admin_msg(message):
        return
    parts = (message.text or "").split()
    if len(parts) > 1 and parts[1].lower() in ("on", "off"):
        on = parts[1].lower() == "on"
        was = _maint_on()
        _maint_set(on)
        extra = ""
        if was and not on:
            extra = f"\n🔔 إشعار العودة أُرسل لـ {_maint_broadcast_back()} زبون."
        bot.reply_to(message, f"🛠️ وضع التحديث: {'✅ شغّال' if on else '⛔ مطفأ'}" + extra)
        return
    bot.reply_to(message, f"🛠️ وضع التحديث: {'✅ شغّال' if _maint_on() else '⛔ مطفأ'}\nالمشتركون في الإشعار: {len(_smembers(MAINT_SUBS))} | شاهدوا رسالة التحديث: {len(_smembers(MAINT_SEEN))}\n/maint on | off")
'''
patch(r"""# ========== استقبال رقم العملية من الزبون (يجب أن يبقى بعد باقي معالجات النصوص) ==========""",
      NEW_BLOCK + "\n" + r"""# ========== استقبال رقم العملية من الزبون (يجب أن يبقى بعد باقي معالجات النصوص) ==========""", "insert_block")

# 14) تشغيل حلقة التأكيد التلقائي
patch(r"""monitor_send("🟢 <b>البوت اشتغل</b>", key="boot", cooldown=120)""",
      r"""threading.Thread(target=order_autoconfirm_loop, daemon=True).start()
monitor_send("🟢 <b>البوت اشتغل</b>", key="boot", cooldown=120)""", "start_autoconfirm")


# ===== ربط API المورّد (Vente) =====
patch(r"""    # منتجات يدوية (A/B): تسجيل الطلب + جمع البيانات / إشعار الأدمن
    if pid in MANUAL_IDS:
        _fulfill_manual(chat_id, uid, lang, claim, canon, retry, mark, failed)
        return
""", r"""    # منتجات يدوية (A/B): تسجيل الطلب + جمع البيانات / إشعار الأدمن
    if pid in MANUAL_IDS:
        _fulfill_manual(chat_id, uid, lang, claim, canon, retry, mark, failed)
        return

    # منتجات المورّد (Vente) + Gemini عند نفاد مخزونك
    if _vt_is_pid(pid):
        _fulfill_vente(chat_id, uid, lang, claim, canon, retry, mark, failed)
        return
    if pid == GEMINI_ID and _gem_use_vente(claim):
        _fulfill_vente(chat_id, uid, lang, claim, canon, retry, mark, failed, vid=_gem_vid() or claim.get("vt"))
        return
""", "vente_fulfill_branch")
patch(r"""        if pid == GEMINI_ID:
            out = gemini_stock() < int(str(label).lstrip("x") or 1)""",
      r"""        if _vt_is_pid(pid):
            out = _vt_stock(pid) < _vt_qty(label)
        elif pid == GEMINI_ID:
            out = gemini_stock() < int(str(label).lstrip("x") or 1)""", "vente_wpay_stock")
patch(r"""def handle_product_view(call):
    product_id = call.data.replace("buy_", "")
""", r"""def handle_product_view(call):
    product_id = call.data.replace("buy_", "")
    if product_id in OWN_ALWAYS_HIDDEN:
        # منتجك الخاص المحذوف: يمنع الوصول إليه من أزرار/روابط قديمة
        try:
            bot.answer_callback_query(call.id, "❌ هذا المنتج لم يعد متوفراً • No longer available • Produit indisponible", show_alert=True)
        except Exception:
            pass
        return
    if _vt_is_pid(product_id):
        _vt_view(call, product_id)
        return
""", "vente_product_view")
patch(r"""    gift_markup.add(_gb)
""",
      r"""    gift_markup.add(_gb)
    _psn_amount_icons(gift_markup)
    _gift_amount_post(gift_markup, product_id)
""", "psn_amount_icons")
patch(r"""threading.Thread(target=order_autoconfirm_loop, daemon=True).start()
monitor_send("🟢 <b>البوت اشتغل</b>", key="boot", cooldown=120)""",
      r"""threading.Thread(target=order_autoconfirm_loop, daemon=True).start()
if VENTE_KEY:
    threading.Thread(target=vt_refresh_loop, daemon=True).start()
monitor_send("🟢 <b>البوت اشتغل</b>", key="boot", cooldown=120)""", "vente_start")

if _errors:
    sys.exit("❌ فشل تطبيق التعديلات (هل bot_base.py هو الكود القديم نفسه؟):\n" + "\n".join(_errors))

patch(r"""print("Bot is running...")""",
      r"""# قسم «تعلّم كيف تشتري»: ملف منفصل learn.py (إن غاب أو فشل يشتغل البوت عادي بدونه)
for _fn in ("learn.py", "reviews.py", "pimages.py", "rateprompt.py", "webstore.py", "qtyflow.py"):
    try:
        _lp = os.path.join(os.path.dirname(os.path.abspath(BASE_FILE)), _fn)
        if os.path.exists(_lp):
            exec(compile(open(_lp, encoding="utf-8").read(), _lp, "exec"), globals())
        else:
            print(f"{_fn} not found - section disabled")
    except Exception as _le:
        print(f"{_fn} failed to load: {_le}")
print("Bot is running...")""", "load_learn")

# اتصال تليجرام أكثر تحمّلاً: استعلام قصير + تجديد الجلسة (حل Read timed out على Render)
patch(r"""bot.infinity_polling()""",
      r"""_poll_kw = {}
try:
    import inspect as _insp
    from telebot import apihelper as _ah
    for _an, _av in (("CONNECT_TIMEOUT", 10), ("SESSION_TIME_TO_LIVE", 60)):
        try:
            setattr(_ah, _an, _av)
        except Exception:
            pass
    _psig = _insp.signature(bot.infinity_polling).parameters
    if "timeout" in _psig:
        _poll_kw["timeout"] = 10
    if "long_polling_timeout" in _psig:
        _poll_kw["long_polling_timeout"] = 5
except Exception as _pe:
    print(f"polling tune skipped: {_pe}")
print(f"polling options: {_poll_kw}")
bot.infinity_polling(**_poll_kw)""", "tune_polling")

if _errors:
    sys.exit("❌ فشل تطبيق التعديلات (هل bot_base.py هو الكود القديم نفسه؟):\n" + "\n".join(_errors))

exec(compile(src, BASE_FILE, "exec"), globals())
