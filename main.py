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
      r"""    markup.add(InlineKeyboardButton(text="📦 الطلبات المعلقة", callback_data="adm_pend"))
    markup.add(InlineKeyboardButton(text=f"💳 الدفعات المعلقة ({_pp_count()})", callback_data="ap_l"))
    markup.add(InlineKeyboardButton(text="💳 شحن محفظة زبون", callback_data="ap_wt"))
    markup.add(InlineKeyboardButton(text="✏️ تعديل وصف منتج", callback_data="ap_dp"))
    markup.add(InlineKeyboardButton(text="⚙️ طرق الدفع", callback_data="ap_pm"))
    markup.add(InlineKeyboardButton(text="💲 المخزون / الأسعار", callback_data="adm_prices"))
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
    order_log_auto(uid, claim.get("product_name"), claim.get("price"), canon, "\n".join(links))""", "log_gemini")
patch(r"""            record_purchase(uid, pid, claim.get("product_name"), claim.get("price"), canon, via=claim.get("via", "binance"))""",
      r"""            record_purchase(uid, pid, claim.get("product_name"), claim.get("price"), canon, via=claim.get("via", "binance"))
            order_log_auto(uid, claim.get("product_name"), claim.get("price"), canon, "\n".join(codes))""", "log_fazer")


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
    "chatgpt_plus_1m", "chatgpt_k12_edu", "office365_1y", "elevenlabs_3m",
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
        "buy_hint": "💳 اضغط «اشتري الآن» لإنشاء فاتورة الدفع عبر Binance Pay.",
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
        "input_saved": "✅ تم تأكيد بياناتك. طلبك قيد التنفيذ وسنُعلمك هنا فور اكتماله.",
        "queued": "ℹ️ سنطلب منك بيانات هذا الطلب بعد إنهاء الطلب الحالي.",
        "executed": "✅ <b>تم تنفيذ / تفعيل طلبك بنجاح!</b>\n\n📦 {product}\n\nإذا واجهت أي مشكلة تواصل مع الدعم 👇",
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
        "buy_hint": "💳 Tap «Buy now» to create a Binance Pay invoice.",
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
        "input_saved": "✅ Details confirmed. Your order is being fulfilled and we will notify you here once done.",
        "queued": "ℹ️ We'll ask for this order's details after you finish the current one.",
        "executed": "✅ <b>Your order has been fulfilled / activated!</b>\n\n📦 {product}\n\nIf you have any problem, contact support 👇",
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
        "buy_hint": "💳 Appuyez sur « Acheter maintenant » pour créer une facture Binance Pay.",
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
        "input_saved": "✅ Informations confirmées. Votre commande est en cours et nous vous préviendrons ici dès qu'elle sera terminée.",
        "queued": "ℹ️ Nous vous demanderons les informations de cette commande après la commande en cours.",
        "executed": "✅ <b>Votre commande a été exécutée / activée !</b>\n\n📦 {product}\n\nEn cas de problème, contactez l'assistance 👇",
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
    _manual_stock_dec(pid)
    _sadd(ORDSET_KEY, oid)
    spname = html.escape(pname)
    if was_out:
        alert_admin(f"⚠️ <b>بيع بينما المخزون 0</b>\n📦 {spname}\n👤 <code>{uid}</code>")
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
        _edit_cb(call, mt(lang, "input_saved"))
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
    try:
        sent = bot.send_message(
            uid, mt(lang, "delivery").format(product=html.escape(o["product_name"]), body=body),
            parse_mode="HTML", reply_markup=mk, disable_web_page_preview=True,
        )
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

def _admin_panel_extra(call, op):
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
        if o.get("status") == "pending" and o.get("cat") == "B":
            mk.add(InlineKeyboardButton(text="📤 إرسال بيانات الطلب للزبون", callback_data=f"ord_d_{oid}"))
        if o.get("status") == "pending" and o.get("cat") == "A":
            mk.add(InlineKeyboardButton(text="✅ تم التنفيذ", callback_data=f"ord_x_{oid}"))
        mk.add(InlineKeyboardButton(text="⬅️ القائمة", callback_data="ord_l_0"))
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
    if act == "x":
        ok, msg = mark_executed(oid)
        bot.answer_callback_query(call.id, "✅" if ok else "❌")
        bot.send_message(chat_id, msg)
        show_pending_orders(chat_id, msg_id)
        return
    bot.answer_callback_query(call.id)

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
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=support_markup(lang))
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
            bot.edit_message_reply_markup(o["chat_id"], o["message_id"], reply_markup=support_markup(get_lang(o["user_id"])))
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
    "gemini_18m", "capcut_1m",
    ("duolingo_12m", "duolingo_link_12m"),
    ("netflix_full", "netflix_profile"),
    ("prime_video_ultra_6m", "amazon_prime_6m"),
    "grp:claude_api",
    ("chatgpt_plus_1m", "chatgpt_k12_edu"),
    ("office365_1y", "elevenlabs_3m"),
    "nordvpn_3m", "n8n_starter_12m",
    "grp:snapchat",
    "canva_edu_500", "canva_edu_5000", "freefire_diamonds",
    "sep:sep_gift_cards", "apple_gift_tr", "apple_gift_in", "apple_gift_fr",
]

# مجموعات: زر واحد طويل يفتح صفحة فيها أزرار المنتجات
STORE_GROUPS = {
    "claude_api": {"name": "Claude API", "icon": "🧠", "members": ["claude_100_30d", "claude_10m_1d"]},
    "snapchat": {"name": "Snapchat Plus+", "icon": "👻", "members": ["snapchat_3m", "snapchat_6m", "snapchat_12m"]},
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
        text=f"{item['icon']} {tr(item, 'name', lang)} | {item['price']} | {stock_display}",
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

def generate_store_keyboard(lang):
    sync_stock()
    markup = InlineKeyboardMarkup(row_width=2)
    shown = set()
    group_members = {m for g in STORE_GROUPS.values() for m in g["members"]}

    for slot in STORE_SLOTS:
        if isinstance(slot, tuple):
            items = [find_product(pid) for pid in slot]
            items = [i for i in items if i]
            shown.update(i["id"] for i in items)
            if len(items) == 2:
                markup.row(_pair_button(items[0], lang), _pair_button(items[1], lang))
            elif items:
                markup.add(_slot_button(items[0], lang))
        elif slot.startswith("grp:"):
            gid = slot[4:]
            g = STORE_GROUPS.get(gid)
            if not g:
                continue
            lo, hi, stock = _group_range(gid)
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
            if item:
                shown.add(item["id"])
                markup.add(_slot_button(item, lang))

    # أي منتج يضيفه الأدمن لاحقاً ولم يوضع في الترتيب يظهر في الآخر
    for item in products:
        if item.get("type") == "separator" or item["id"] in shown or item["id"] in group_members:
            continue
        markup.add(_slot_button(item, lang))

    markup.add(InlineKeyboardButton(text=t(lang, "change_lang"), callback_data="change_lang"))
    markup.row(
        InlineKeyboardButton(text=wt(lang, "btn_profile"), callback_data="pf_profile"),
        InlineKeyboardButton(text=wt(lang, "btn_history"), callback_data="pf_hist"),
    )
    markup.add(InlineKeyboardButton(text=wt(lang, "btn_wallet"), callback_data="pf_wallet"))
    return markup

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
            mk.add(_slot_button(item, lang))
    mk.add(InlineKeyboardButton(text=t(lang, "back"), callback_data="back_to_main"))
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
from decimal import ROUND_CEILING

SEP = chr(95)
BARIDI_RIP = "00799999002013573542"
FLEXY_NUMBER = "0699177640"
PM_DEFAULT_RATE = {"bd": Decimal("260"), "fx": Decimal("317.20")}
PM_ICON = {"bd": "🏦", "fx": "📱"}
PM_NAME = {
    "bd": {"ar": "بريدي موب", "en": "Baridimob", "fr": "Baridimob"},
    "fx": {"ar": "Flixy", "en": "Flixy", "fr": "Flixy"},
}

PM_TEXTS = {
    "ar": {
        "pick_buy": "🛒 <b>طلب جديد</b>\n\n📦 {product}\n💵 المجموع: <b>{amount}$</b>\n\n💳 اختر طريقة الدفع:",
        "pick_topup": "➕ <b>شحن المحفظة</b>\n\n💳 اختر طريقة الدفع:",
        "btn_wallet": "💼 المحفظة (${bal})",
        "btn_binance": "الدفع عبر Binance",
        "btn_bd": "بريدي موب",
        "btn_fx": "Flixy +22%",
        "soon": "🔄 جاري التحديث، ستتوفر هذه الطريقة قريباً",
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
        "proof_hint_fx": "✉️ ابعث رسالة الفليكسي بالشكل المطلوب (فليكسي، المبلغ، الوقت) أو لقطة شاشة.",
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
        "proof_hint_fx": "✉️ Send the Flexy message in the required format (Flexy, amount, time) or a screenshot.",
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
        "proof_hint_fx": "✉️ Envoyez le message Flexy au format demandé (Flexy, montant, heure) ou une capture d'écran.",
        "busy": "ℹ️ Vous avez déjà un paiement en cours de vérification. Attendez sa confirmation avant d'en démarrer un nouveau.",
        "approved": "✅ <b>Votre portefeuille a été rechargé avec succès !</b>\n\n💵 +{amount}$\n💼 Solde disponible : <b>${avail}</b>\n\n🛍️ Vous pouvez maintenant choisir votre produit et payer avec le portefeuille.",
        "rejected": "❌ <b>Paiement incorrect</b>\n\nNous n'avons pas pu vérifier votre paiement. Si vous pensez qu'il s'agit d'une erreur, contactez l'assistance.",
    },
}

def pmt(lang, key):
    return PM_TEXTS.get(lang, PM_TEXTS["ar"])[key]

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
_mem_pmw = {"bd": set(), "fx": set()}

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

def _create_pp(uid, m, kind, what, usd):
    usd = f"{Decimal(str(usd)):.2f}"
    req = {
        "id": uuid.uuid4().hex[:8], "uid": uid, "m": m, "kind": kind, "what": what,
        "usd": usd, "da": pm_da(usd, m), "rate": str(pm_rate(m)),
        "status": "awaiting", "ts": int(time.time()),
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
    mk.add(InlineKeyboardButton(text="RedotPay", callback_data=ids["soon"]))
    mk.add(InlineKeyboardButton(text="Bybit", callback_data=ids["soon"]))

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
        "fx": f"pm_fx_{invoice_id}", "soon": f"pm_soon_{invoice_id}",
    })
    mk.add(InlineKeyboardButton(text=t(lang, "cancel"), callback_data=f"cancel_{invoice_id}"))
    return mk

def topup_method_picker(call, lang):
    mk = InlineKeyboardMarkup(row_width=1)
    _pm_method_rows(lang, mk, {"bn": "pm_tbn", "bd": "pm_tbd", "fx": "pm_tfx", "soon": "pm_tsoon"})
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

def _pm_soon_screen(call, lang, back_cb):
    mk = InlineKeyboardMarkup(row_width=1)
    mk.add(InlineKeyboardButton(text=t(lang, "back"), callback_data=back_cb))
    _pf_show(call, pmt(lang, "soon"), mk)

def _pm_pay_text(lang, req):
    m = req["m"]
    dest = BARIDI_RIP if m == "bd" else FLEXY_NUMBER
    after = pmt(lang, "after_buy" if req["kind"] == "buy" else "after_topup")
    return pmt(lang, "pay_" + m).format(
        what=html.escape(req["what"]), usd=req["usd"], rate=_fmt_rate(req["rate"]),
        da=req["da"], dest=dest, after=after,
    ), dest

def _pm_pay_markup(lang, req, dest):
    mk = InlineKeyboardMarkup(row_width=1)
    mk.add(_pm_copy_button(lang, req["m"], dest))
    mk.add(InlineKeyboardButton(text=t(lang, "cancel"), callback_data=f"pmx_{req['id']}"))
    return mk

def _pm_show_pay(call, lang, req):
    text, dest = _pm_pay_text(lang, req)
    _pf_show(call, text, _pm_pay_markup(lang, req, dest))

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
        bot.answer_callback_query(call.id, BARIDI_RIP if arg == "bd" else FLEXY_NUMBER, show_alert=True)
        return

    if cmd == "nt":
        if arg in PM_NAME:
            pmw_add(arg, uid)
            bot.answer_callback_query(call.id, pmt(lang, "nt_ok").format(method=PM_NAME[arg][lang]), show_alert=True)
            monitor_send(
                f"🔔 <b>زبون طلب إعلامه بتوفر {PM_NAME[arg]['ar']}</b>\n\n👤 {_user_link(uid)}\n"
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
        _pm_soon_screen(call, lang, "pf_top" if arg == "t" else f"pm_back_{arg}")
        bot.answer_callback_query(call.id)
        return

    if cmd == "bn":
        inv = _pm_inv(call, arg, lang)
        if inv:
            product = find_product(inv["product_id"])
            _pf_show(call, _bn_invoice_text(lang, inv, product), _bn_invoice_markup(lang, arg, False))
            bot.answer_callback_query(call.id)
        return

    if cmd in ("bd", "fx"):
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
            req = _create_pp(uid, cmd, "buy", inv["product_name"], inv["price_usdt"])
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
        _pm_soon_screen(call, lang, "pf_top")
        bot.answer_callback_query(call.id)
        return

    if cmd in ("tbd", "tfx"):
        m = cmd[1:]
        if not pm_enabled(m):
            _pm_full_screen(call, lang, m, "pf_top")
            bot.answer_callback_query(call.id)
            return
        mk = InlineKeyboardMarkup(row_width=2)
        mk.row(*[
            InlineKeyboardButton(text=f"{a}$ = {pm_da(a, m)} DA", callback_data=f"pm_ta_{m}_{a}")
            for a in TOPUP_AMOUNTS
        ])
        mk.add(InlineKeyboardButton(text=wt(lang, "btn_topup_other"), callback_data=f"pm_to_{m}"))
        mk.add(InlineKeyboardButton(text=t(lang, "back"), callback_data="pf_top"))
        _pf_show(call, pmt(lang, "topup_amounts").format(method=PM_NAME[m][lang], rate=_fmt_rate(pm_rate(m))), mk)
        bot.answer_callback_query(call.id)
        return

    if cmd == "to":
        if arg not in PM_NAME:
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
            if m not in PM_NAME or amount not in [Decimal(a) for a in TOPUP_AMOUNTS]:
                raise ValueError("bad")
        except Exception:
            bot.answer_callback_query(call.id)
            return
        _pm_topup_request(call, None, uid, lang, m, amount)
        return

    bot.answer_callback_query(call.id)

def _pm_topup_request(call, chat_id, uid, lang, m, amount):
    """ينشئ طلب شحن (بريدي موب/Flixy) ويعرض التعليمات. call أو chat_id."""
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
        f"📦 {html.escape(req['what'])}\n💵 ${req['usd']} = {req['da']} DA\n🆔 #{req['id']}\n\n"
        f"ادخل /admin ← 💳 الدفعات المعلقة للتأكد."
    )
    alert_admin(txt)
    monitor_send(txt)

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
        req["file_id"] = message.photo[-1].file_id
    else:
        txt = (message.text or "").strip()
        if req["m"] == "bd" or not re.search(r"\d", txt):
            bot.send_message(message.chat.id, pmt(lang, "proof_hint_" + req["m"]), parse_mode="HTML")
            return True
        req["text"] = txt[:500]
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
        f"📦 {html.escape(req['what'])}\n💵 ${req['usd']} = <b>{req['da']} DA</b> (1$ = {_fmt_rate(req['rate'])})\n"
        f"🕒 {_fmt_date(req.get('sub_ts', 0))}"
    )
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
        if p.get("type") == "separator":
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
    for m in ("bd", "fx"):
        on = pm_enabled(m)
        lines.append(
            f"{PM_ICON[m]} <b>{PM_NAME[m]['ar']}</b>: {'✅ مفعّلة' if on else '⛔ موقوفة'} | "
            f"1$ = {_fmt_rate(pm_rate(m))} DA | ⏳ {len(pmw_list(m))} ينتظرون"
        )
        mk.row(
            InlineKeyboardButton(text=f"✅ تفعيل {PM_NAME[m]['ar']}", callback_data=f"ap_on_{m}"),
            InlineKeyboardButton(text=f"⛔ إيقاف {PM_NAME[m]['ar']}", callback_data=f"ap_off_{m}"),
        )
        mk.add(InlineKeyboardButton(text=f"💱 سعر صرف {PM_NAME[m]['ar']}", callback_data=f"ap_rt_{m}"))
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
                bot.send_message(int(u), pmt(lang, "avail").format(method=PM_NAME[m][lang]),
                                 parse_mode="HTML", reply_markup=mk)
                sent += 1
            except Exception as e:
                print(f"pm waiter notify failed: {e}")
            time.sleep(0.05)
        monitor_send(f"🔔 <b>أُعلم {sent} زبون بتوفر {PM_NAME[m]['ar']}</b>")

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
        mk.add(InlineKeyboardButton(text=f"✅ {req['usd']}$ (مبلغ الطلب)", callback_data=f"ap_amt_{arg}_{req['usd']}"))
        mk.add(InlineKeyboardButton(text="❌ إلغاء", callback_data="ap_l"))
        bot.send_message(
            chat_id,
            f"💵 أرسل المبلغ بالدولار لإضافته إلى محفظة الزبون <code>{req['uid']}</code>\n(مثال: <code>5</code>)",
            parse_mode="HTML", reply_markup=mk,
        )
    elif cmd == "amt":
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
        amount = _parse_price(text)
        if amount is None:
            bot.reply_to(message, "❌ مبلغ غير صالح. أرسل مثلاً: 5")
            return
        _ap_wait.pop(aid, None)
        ok, msg = _ap_approve(st["rid"], amount)
        bot.send_message(message.chat.id, msg, parse_mode="HTML")
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

'''
patch(r"""# ========== استقبال رقم العملية من الزبون (يجب أن يبقى بعد باقي معالجات النصوص) ==========""",
      NEW_BLOCK + "\n" + r"""# ========== استقبال رقم العملية من الزبون (يجب أن يبقى بعد باقي معالجات النصوص) ==========""", "insert_block")

# 14) تشغيل حلقة التأكيد التلقائي
patch(r"""monitor_send("🟢 <b>البوت اشتغل</b>", key="boot", cooldown=120)""",
      r"""threading.Thread(target=order_autoconfirm_loop, daemon=True).start()
monitor_send("🟢 <b>البوت اشتغل</b>", key="boot", cooldown=120)""", "start_autoconfirm")

if _errors:
    sys.exit("❌ فشل تطبيق التعديلات (هل bot_base.py هو الكود القديم نفسه؟):\n" + "\n".join(_errors))

exec(compile(src, BASE_FILE, "exec"), globals())
