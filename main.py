# -*- coding: utf-8 -*-
# ============================================================
# main.py  — ملف التحديث الوحيد
# يقرأ الكود القديم من bot_base.py (هو نفسه main.py القديم بعد إعادة تسميته)
# ويطبّق عليه التعديلات: طلبات يدوية A/B + محفظة + جرس التوفر + سجل الطلبات.
# ============================================================
import os, sys

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
      r"""    if claim.get("status") in ("delivered", "manual"):""", "wallet_ok")

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
        "bad_username": "❌ اسم مستخدم غير صالح (3-15 حرفاً، يبدأ بحرف، أحرف/أرقام/. _ - فقط). أعد الإرسال.",
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
        "bad_username": "❌ Invalid username (3-15 chars, starts with a letter, letters/digits/. _ - only). Send it again.",
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
        "bad_username": "❌ Nom d'utilisateur invalide (3-15 caractères, commence par une lettre, lettres/chiffres/. _ - uniquement). Renvoyez-le.",
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
        pid, idx = call.data[5:].rsplit("_", 1)
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
    try:
        _, act, oid = call.data.split("_", 2)
    except ValueError:
        bot.answer_callback_query(call.id)
        return
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
    parts = call.data.split("_", 2)
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
