# -*- coding: utf-8 -*-
# ============================================================
# learn.py — قسم «تعلّم كيف تشتري»  (معزول تماماً عن الشراء الحقيقي)
#
# • يُحمَّل من main.py داخل try/except: إن غاب الملف أو فيه خطأ يشتغل البوت عادي.
# • كل الأزرار تبدأ بـ dm_ وكل الحالة في الذاكرة (_lm_state)، ولا يلمس أي شيء حقيقي:
#   لا فواتير، لا مخزون، لا محفظة، لا كوينز، لا مورّد، لا أدمن (إلا إشعار دخول واحد يومياً).
# • المنتج المُسلَّم في النهاية نص عشوائي مكتوب هنا، ليس له علاقة بأي منتج حقيقي.
# • أمر الأدمن: /learn on | off
# ============================================================

import random, string, time, re, html, threading

LM_ICON = "5192825506239616944"        # أيقونة الزر الأزرق
LM_KEY = "rk:learn:on"                 # "0" = متوقف  (الافتراضي: يعمل)
LM_WAIT = "rk:learn:subs"              # من ضغط «أعلمني عند البدء»
LM_STATE_TTL = 20 * 60                 # مدة بقاء حالة التعلّم في الذاكرة
LM_PRODUCTS = {"a": "2.00", "b": "5.00"}   # سعر المنتجين التجريبيين ($)

_lm_state = {}          # uid -> {"step", "k", "oid", "da", "ts"}
_lm_ntf_mem = {}
_lm_cache = {"t": 0.0, "v": True}

LM_T = {
    "ar": {
        "btn": "📚 تعلّم كيف تشتري",
        "tag": "🎓 <b>وضع التعلّم</b> — مثال فقط، لا يوجد دفع حقيقي ولا منتج حقيقي",
        "home": "📚 <b>تعلّم كيف تشتري</b>\n\n{tag}\n\n<b>الخطوة 1/4:</b> اختر أحد المنتجين التجريبيين:",
        "pname": {"a": "منتج تجريبي A (مثال)", "b": "منتج تجريبي B (مثال)"},
        "pdesc": "هذا منتج للتعلّم فقط. لا يوجد شيء حقيقي ولن يُخصم منك أي مبلغ.",
        "prod": "{tag}\n\n<b>الخطوة 2/4:</b> هذه صفحة المنتج، فيها الاسم والسعر والوصف.\n\n✅ اخترت: <b>{name}</b>\n💰 السعر: <b>${price}</b>\n📦 المتوفر: <b>♾️</b>\n\n❞ الوصف:\n{desc}\n\n👇 اضغط «اشتري الآن» لتنتقل إلى اختيار طريقة الدفع.",
        "pick": "{tag}\n\n<b>الخطوة 3/4:</b> اختر طريقة الدفع (كما في الشراء الحقيقي).\n\n",
        "step4": "{tag}\n\n<b>الخطوة 4/4 — {method}:</b>\n\n",
        "bn_demo": "🎯 <b>للمثال:</b> بعد الدفع تحصل على رقم عملية (Order ID). هذا هو رقم المثال، انسخه بالزر أدناه ثم أرسله هنا في الشات:\n<code>{oid}</code>",
        "copy_oid": "📋 نسخ رقم العملية (للمثال)",
        "now_photo": "👉 <b>للتعلّم:</b> أرسل الآن أي صورة عشوائية من عندك (مثال).",
        "now_fx": "👉 <b>للتعلّم:</b> أرسل الآن رسالة بهذا الشكل بالمبلغ الظاهر أعلاه والوقت (مثال).",
        "after": "هنا يتحقق البوت فوراً لأنه مثال، وفي الشراء الحقيقي يصلك المنتج بعد التحقق 🎓",
        "fx_hint": "✉️ ابعث رسالة بهذا الشكل (المبلغ والوقت):\n<code>فليكسي\nالمبلغ : {da}Da\nالوقت : 12:33</code>",
        "fx_amt": "❌ المبلغ غير مطابق. المطلوب: <b>{da} DA</b>.\nأعد إرسال الرسالة بالمبلغ الصحيح.",
        "ok": "✅ <b>تم تأكيد الدفع!</b> (مثال)\n\n🎁 هذا هو <b>المنتج التجريبي</b> (ليس حقيقياً):\n<code>{code}</code>\n\n🎓 هكذا يصلك منتجك الحقيقي بعد التحقق من دفعتك.\n\n💡 تذكّر في الشراء الحقيقي:\n• ادفع المبلغ المطلوب بالضبط\n• اكتب الرسالة أو أرسل الصورة كما رأيت هنا\n• إن واجهت مشكلة تواصل مع الدعم\n\n🎉 أنت الآن جاهز للشراء الحقيقي!",
        "stopped": "📚 <b>تعلّم كيف تشتري</b>\n\n⛔ هذا القسم متوقف حالياً.\n\nاضغط «أعلمني عند البدء» وسيصلك إشعار فور عودته.",
        "nt_btn": "🔔 أعلمني عند البدء",
        "nt_ok": "✅ تم تسجيلك! سنخبرك فور عودة القسم.",
        "nt_already": "✅ أنت مسجّل مسبقاً، سنخبرك فور عودته.",
        "back_on": "🎓 <b>عاد قسم «تعلّم كيف تشتري»!</b>\n\nاضغط الزر أدناه للبدء.",
        "busy": "⚠️ لديك عملية شراء حقيقية قيد الإنجاز. أنهِها أو ألغِها أولاً، ثم عد إلى «تعلّم كيف تشتري».",
        "end": "❌ إنهاء التعلّم",
        "again": "🔁 أعد التعلّم",
        "real": "🛍️ ابدأ الشراء الحقيقي",
    },
    "en": {
        "btn": "📚 Learn how to buy",
        "tag": "🎓 <b>Learning mode</b> — example only, no real payment and no real product",
        "home": "📚 <b>Learn how to buy</b>\n\n{tag}\n\n<b>Step 1/4:</b> Choose one of the two demo products:",
        "pname": {"a": "Demo product A (example)", "b": "Demo product B (example)"},
        "pdesc": "This product is for learning only. Nothing is real and you will not be charged.",
        "prod": "{tag}\n\n<b>Step 2/4:</b> This is the product page, with the name, price and description.\n\n✅ You chose: <b>{name}</b>\n💰 Price: <b>${price}</b>\n📦 Available: <b>♾️</b>\n\n❞ Description:\n{desc}\n\n👇 Tap «Buy now» to move on to choosing the payment method.",
        "pick": "{tag}\n\n<b>Step 3/4:</b> Choose the payment method (just like a real purchase).\n\n",
        "step4": "{tag}\n\n<b>Step 4/4 — {method}:</b>\n\n",
        "bn_demo": "🎯 <b>For the example:</b> after paying you get a transaction number (Order ID). Here is the example number, copy it with the button below, then send it here in the chat:\n<code>{oid}</code>",
        "copy_oid": "📋 Copy order ID (example)",
        "now_photo": "👉 <b>For learning:</b> now send any random picture from your phone (example).",
        "now_fx": "👉 <b>For learning:</b> now send a message in this format with the amount shown above and the time (example).",
        "after": "Here the bot verifies instantly because it is an example; in a real purchase you receive the product after verification 🎓",
        "fx_hint": "✉️ Send a message in this format (amount and time):\n<code>Flexy\nAmount : {da}Da\nTime : 12:33</code>",
        "fx_amt": "❌ The amount does not match. Required: <b>{da} DA</b>.\nPlease resend the message with the correct amount.",
        "ok": "✅ <b>Payment confirmed!</b> (example)\n\n🎁 Here is the <b>demo product</b> (not real):\n<code>{code}</code>\n\n🎓 This is how your real product reaches you after your payment is verified.\n\n💡 Remember for a real purchase:\n• Pay the exact amount requested\n• Write the message or send the picture exactly as you saw here\n• If you have a problem, contact support\n\n🎉 You are now ready for a real purchase!",
        "stopped": "📚 <b>Learn how to buy</b>\n\n⛔ This section is currently stopped.\n\nTap «Notify me when it starts» and you will get a message as soon as it is back.",
        "nt_btn": "🔔 Notify me when it starts",
        "nt_ok": "✅ Done! We'll let you know as soon as it is back.",
        "nt_already": "✅ You're already subscribed, we'll notify you when it is back.",
        "back_on": "🎓 <b>«Learn how to buy» is back!</b>\n\nTap the button below to start.",
        "busy": "⚠️ You have a real purchase in progress. Finish or cancel it first, then come back to «Learn how to buy».",
        "end": "❌ End learning",
        "again": "🔁 Try again",
        "real": "🛍️ Start a real purchase",
    },
    "fr": {
        "btn": "📚 Apprendre à acheter",
        "tag": "🎓 <b>Mode apprentissage</b> — exemple uniquement, aucun paiement réel ni produit réel",
        "home": "📚 <b>Apprendre à acheter</b>\n\n{tag}\n\n<b>Étape 1/4 :</b> Choisissez l'un des deux produits de démonstration :",
        "pname": {"a": "Produit démo A (exemple)", "b": "Produit démo B (exemple)"},
        "pdesc": "Ce produit sert uniquement à apprendre. Rien n'est réel et rien ne sera débité.",
        "prod": "{tag}\n\n<b>Étape 2/4 :</b> Voici la page du produit, avec le nom, le prix et la description.\n\n✅ Vous avez choisi : <b>{name}</b>\n💰 Prix : <b>${price}</b>\n📦 Disponible : <b>♾️</b>\n\n❞ Description :\n{desc}\n\n👇 Appuyez sur « Acheter maintenant » pour passer au choix du mode de paiement.",
        "pick": "{tag}\n\n<b>Étape 3/4 :</b> Choisissez le mode de paiement (comme pour un vrai achat).\n\n",
        "step4": "{tag}\n\n<b>Étape 4/4 — {method} :</b>\n\n",
        "bn_demo": "🎯 <b>Pour l'exemple :</b> après le paiement vous recevez un numéro de transaction (Order ID). Voici le numéro d'exemple, copiez-le avec le bouton ci-dessous puis envoyez-le ici dans le chat :\n<code>{oid}</code>",
        "copy_oid": "📋 Copier l'ID de commande (exemple)",
        "now_photo": "👉 <b>Pour apprendre :</b> envoyez maintenant n'importe quelle image au hasard (exemple).",
        "now_fx": "👉 <b>Pour apprendre :</b> envoyez maintenant un message sous cette forme avec le montant ci-dessus et l'heure (exemple).",
        "after": "Ici le bot vérifie instantanément car c'est un exemple ; pour un vrai achat vous recevez le produit après vérification 🎓",
        "fx_hint": "✉️ Envoyez un message sous cette forme (montant et heure) :\n<code>Flexy\nMontant : {da}Da\nHeure : 12:33</code>",
        "fx_amt": "❌ Le montant ne correspond pas. Montant requis : <b>{da} DA</b>.\nRenvoyez le message avec le bon montant.",
        "ok": "✅ <b>Paiement confirmé !</b> (exemple)\n\n🎁 Voici le <b>produit de démonstration</b> (non réel) :\n<code>{code}</code>\n\n🎓 C'est ainsi que votre vrai produit vous parvient après vérification du paiement.\n\n💡 À retenir pour un vrai achat :\n• Payez exactement le montant demandé\n• Écrivez le message ou envoyez l'image comme vous l'avez vu ici\n• En cas de problème, contactez le support\n\n🎉 Vous êtes prêt pour un vrai achat !",
        "stopped": "📚 <b>Apprendre à acheter</b>\n\n⛔ Cette section est actuellement arrêtée.\n\nAppuyez sur « Me prévenir au démarrage » pour être averti dès son retour.",
        "nt_btn": "🔔 Me prévenir au démarrage",
        "nt_ok": "✅ Enregistré ! Nous vous préviendrons dès son retour.",
        "nt_already": "✅ Vous êtes déjà inscrit, nous vous préviendrons dès son retour.",
        "back_on": "🎓 <b>La section « Apprendre à acheter » est de retour !</b>\n\nAppuyez sur le bouton ci-dessous pour commencer.",
        "busy": "⚠️ Vous avez un vrai achat en cours. Terminez-le ou annulez-le d'abord, puis revenez à « Apprendre à acheter ».",
        "end": "❌ Terminer l'apprentissage",
        "again": "🔁 Recommencer",
        "real": "🛍️ Commencer un vrai achat",
    },
}

LM_METHOD_NAME = {"bn": "Binance", "bd": "Baridimob", "fx": "Flixy", "rd": "RedotPay"}
LM_FAKE = {"bn": "123456789", "bd": "00799999000000000000", "fx": "0600000000", "rd": "000000000"}


def _lm_tx(lang):
    return LM_T.get(lang) or LM_T["ar"]


def _lm_name(lang, k):
    return _lm_tx(lang)["pname"].get(k, "?")


# ---------- التشغيل / الإيقاف ----------
def _lm_on():
    now = time.time()
    if now - _lm_cache["t"] < 3:
        return _lm_cache["v"]
    try:
        v = str(kv_get(LM_KEY)) != "0"
    except Exception:
        v = _lm_cache["v"]
    _lm_cache.update(t=now, v=v)
    return v


def _lm_set(on):
    kv_set(LM_KEY, "1" if on else "0")
    _lm_cache.update(t=time.time(), v=bool(on))
    if not on:
        _lm_state.clear()


# ---------- حالة المستخدم (ذاكرة فقط) ----------
def _lm_get(uid):
    st = _lm_state.get(uid)
    if not st:
        return None
    if time.time() - st["ts"] > LM_STATE_TTL:
        _lm_state.pop(uid, None)
        return None
    return st


def _lm_real_busy(uid):
    """الشراء الحقيقي له الأولوية دائماً: أي فاتورة/دفع حقيقي جارٍ يلغي التعلّم."""
    try:
        if get_pending_invoice_id(uid) is not None:
            return True
    except Exception:
        return True
    try:
        if _pp_active(uid):
            return True
    except Exception:
        return True
    return False


def _lm_kb_texts():
    out = set()
    for nm in ("KB_START_TEXTS", "KB_PRODUCTS_TEXTS", "KB_SUPPORT_TEXTS", "KB_LANG_TEXTS", "KB_UPDATE_TEXTS"):
        try:
            out |= set(globals().get(nm) or ())
        except Exception:
            pass
    return out


# ---------- أدوات العرض ----------
def _lm_show(call, text, mk):
    m = call.message
    chat_id = m.chat.id
    if getattr(m, "content_type", "text") == "text":
        try:
            bot.edit_message_text(text, chat_id, m.message_id, parse_mode="HTML",
                                  reply_markup=mk, disable_web_page_preview=True)
            return
        except Exception as e:
            if "not modified" in str(e).lower():
                return
    else:
        try:
            bot.delete_message(chat_id, m.message_id)
        except Exception:
            pass
    bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=mk, disable_web_page_preview=True)


def _lm_btn(text, cb, style=None, icon=None):
    b = InlineKeyboardButton(text=text, callback_data=cb)
    if style:
        b.style = style
    if icon:
        b.icon_dyn = icon
    return b


def _lm_copy_btn(label, value, cb):
    try:
        if CopyTextButton is not None:
            return InlineKeyboardButton(text=label, copy_text=CopyTextButton(text=value))
    except Exception:
        pass
    return InlineKeyboardButton(text=label, callback_data=cb)


def _lm_new_oid():
    return str(random.randint(10 ** 17, 10 ** 18 - 1))


def _lm_new_code():
    al = string.ascii_uppercase + string.digits
    return "DEMO-" + "-".join("".join(random.choice(al) for _ in range(4)) for _ in range(3))


def _lm_notify_admin(user):
    """إشعار واحد لكل زبون في اليوم (بتوقيت الجزائر) عند دخوله «تعلّم كيف تشتري»."""
    uid = str(user.id)
    day = time.strftime("%Y%m%d", time.gmtime(time.time() + 3600))
    try:
        first = bool(kv_set(f"rk:learn:ntf:{uid}:{day}", "1", ex=90000, nx=True))
    except Exception:
        first = _lm_ntf_mem.get(uid) != day
    _lm_ntf_mem[uid] = day
    if not first:
        return

    def _do():
        try:
            nm = html.escape(((user.first_name or "") + " " + (user.last_name or "")).strip() or "—")
            un = f" @{user.username}" if getattr(user, "username", None) else ""
            bot.send_message(ADMIN_CHAT_ID,
                             f"🎓 <b>زبون دخل «تعلّم كيف تشتري»</b>\n👤 {nm}{un} (ID: <code>{uid}</code>)",
                             parse_mode="HTML")
        except Exception as e:
            print(f"learn admin notify failed: {e}")

    threading.Thread(target=_do, daemon=True).start()


# ---------- الشاشات ----------
def _lm_home(call, lang):
    tx = _lm_tx(lang)
    mk = InlineKeyboardMarkup(row_width=1)
    for k, price in LM_PRODUCTS.items():
        mk.add(_lm_btn(f"🎁 {_lm_name(lang, k)} | ${price}", f"dm_p_{k}", style="success"))
    mk.add(_lm_btn(t(lang, "back"), "dm_end"))
    _lm_show(call, tx["home"].format(tag=tx["tag"]), mk)


def _lm_product(call, lang, k):
    tx = _lm_tx(lang)
    mk = InlineKeyboardMarkup(row_width=1)
    mk.add(_lm_btn(mt(lang, "buy_btn"), f"dm_b_{k}", icon=ICON_BUY))
    mk.add(_lm_btn(t(lang, "back"), "dm_home"))
    _lm_show(call, tx["prod"].format(tag=tx["tag"], name=_lm_name(lang, k), price=LM_PRODUCTS[k],
                                     desc=tx["pdesc"]), mk)


def _lm_picker(call, lang, k):
    tx = _lm_tx(lang)
    mk = InlineKeyboardMarkup(row_width=1)
    mk.add(_lm_btn(pmt(lang, "btn_binance"), f"dm_m_bn_{k}"))
    mk.add(_lm_btn(pmt(lang, "btn_bd"), f"dm_m_bd_{k}"))
    mk.add(_lm_btn(pmt(lang, "btn_fx"), f"dm_m_fx_{k}"))
    mk.add(_lm_btn("RedotPay", f"dm_m_rd_{k}"))
    mk.add(_lm_btn(t(lang, "back"), f"dm_p_{k}"))
    mk.add(_lm_btn(tx["end"], "dm_end"))
    text = tx["pick"].format(tag=tx["tag"]) + pmt(lang, "pick_buy").format(
        product=html.escape(_lm_name(lang, k)), amount=LM_PRODUCTS[k])
    _lm_show(call, text, mk)


def _lm_inject(body, hint, after_text):
    """يضع سطر التلميح قبل الخطوة 3 (أو قبل نص الخاتمة إن لم توجد خطوة 3)."""
    marker = "3️⃣ " + after_text
    i = body.find(marker)
    if i < 0:
        i = body.rfind(after_text)
    if i < 0:
        return body + "\n\n" + hint
    sep = "\n" if marker in body else "\n\n"
    return body[:i] + hint + sep + body[i:]


def _lm_method(call, lang, m, k):
    uid = call.from_user.id
    tx = _lm_tx(lang)
    price = LM_PRODUCTS[k]
    name = html.escape(_lm_name(lang, k))
    head = tx["step4"].format(tag=tx["tag"], method=LM_METHOD_NAME[m])
    mk = InlineKeyboardMarkup(row_width=1)
    st = {"k": k, "ts": time.time(), "m": m}

    if m == "bn":
        st.update(step="bn", oid=_lm_new_oid())
        body = (
            f"<b>{t(lang, 'invoice_title')}</b>\n\n"
            f"📦 {name}\n"
            f"{t(lang, 'invoice_amount')} <b>{price} USDT</b>\n\n"
            f"💳 <b>Binance Pay ID:</b>\n<code>{LM_FAKE['bn']}</code>\n\n"
            f"{t(lang, 'invoice_steps')}\n\n"
            f"{tx['bn_demo'].format(oid=st['oid'])}"
        )
        mk.add(_lm_copy_btn(tx["copy_oid"], st["oid"], "dm_cp_oid"))
    elif m == "fx":
        da = pm_da(price, "fx")
        st.update(step="fx", da=da)
        body = pmt(lang, "pay_fx").format(
            what=name, usd=price, rate=_fmt_rate(pm_rate("fx")), da=da,
            dest=LM_FAKE["fx"], after=tx["after"])
        body = _lm_inject(body, tx["now_fx"], tx["after"])
        mk.add(_lm_copy_btn(pmt(lang, "copy_fx"), LM_FAKE["fx"], "dm_cp_dest"))
    elif m == "bd":
        st.update(step="photo")
        body = pmt(lang, "pay_bd").format(
            what=name, usd=price, rate=_fmt_rate(pm_rate("bd")), da=pm_da(price, "bd"),
            dest=LM_FAKE["bd"], after=tx["after"])
        body = _lm_inject(body, tx["now_photo"], tx["after"])
        mk.add(_lm_copy_btn(pmt(lang, "copy_bd"), LM_FAKE["bd"], "dm_cp_dest"))
    else:  # rd
        st.update(step="photo")
        body = pmt(lang, "pay_rd").format(what=name, usd=price, dest=LM_FAKE["rd"], after=tx["after"])
        body = _lm_inject(body, tx["now_photo"], tx["after"])
        mk.add(_lm_copy_btn(pmt(lang, "copy_rd"), LM_FAKE["rd"], "dm_cp_dest"))

    st["dest"] = LM_FAKE[m]
    _lm_state[uid] = st
    mk.add(_lm_btn(t(lang, "back"), f"dm_b_{k}"))      # رجوع خطوة واحدة: إلى طرق الدفع
    mk.add(_lm_btn(tx["end"], "dm_end"))                # الخروج من التعلّم
    _lm_show(call, head + body, mk)


def _lm_success(chat_id, uid, lang):
    _lm_state.pop(uid, None)
    tx = _lm_tx(lang)
    mk = InlineKeyboardMarkup(row_width=1)
    mk.add(_lm_btn(tx["again"], "dm_home", style="primary", icon=LM_ICON))
    mk.add(_lm_btn(tx["real"], "dm_end"))
    bot.send_message(chat_id, tx["ok"].format(code=_lm_new_code()), parse_mode="HTML", reply_markup=mk)


def _lm_stopped(call, lang):
    tx = _lm_tx(lang)
    mk = InlineKeyboardMarkup(row_width=1)
    mk.add(_lm_btn(tx["nt_btn"], "dm_nt", icon=ICON_BELL))
    mk.add(_lm_btn(t(lang, "back"), "dm_end"))
    _lm_show(call, tx["stopped"], mk)


# ---------- فحص رسالة الفليكسي ----------
_AR_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def _lm_parse_fx(text):
    s = (text or "").translate(_AR_DIGITS)
    amt = None
    m = re.search(r"(?:المبلغ|montant|amount)\s*[:：]?\s*(\d[\d\s]*)", s, re.I)
    if m:
        try:
            amt = int(re.sub(r"\s+", "", m.group(1)))
        except Exception:
            amt = None
    tm = re.search(r"\b\d{1,2}\s*[:hH]\s*\d{2}\b", s)
    return amt, bool(tm)


# ---------- معالجات الرسائل (نص / صورة) ----------
def _lm_msg_filter(m):
    try:
        if not m.from_user or m.chat.type != "private":
            return False
        uid = m.from_user.id
        st = _lm_get(uid)
        if not st:
            return False
        if not _lm_on():
            _lm_state.pop(uid, None)
            return False
        if _maint_blocked_user(m.from_user):
            return False
        if _lm_real_busy(uid):
            _lm_state.pop(uid, None)
            return False
        ct = m.content_type
        if ct == "text":
            tx = (m.text or "").strip()
            if not tx:
                return False
            if tx.startswith("/") or tx in _lm_kb_texts():
                _lm_state.pop(uid, None)
                return False
            return True
        if ct == "photo":
            return True
        if ct == "document":
            return str(getattr(m.document, "mime_type", "") or "").startswith("image/")
        return False
    except Exception:
        return False


def lm_input(message):
    uid = message.from_user.id
    cid = message.chat.id
    lang = get_lang(uid)
    tx = _lm_tx(lang)
    st = _lm_get(uid)
    if not st:
        return
    step = st["step"]
    is_text = message.content_type == "text"
    body = (message.text or "").strip() if is_text else ""

    if step == "bn":
        if not is_text or not re.fullmatch(r"[A-Za-z0-9_\-]{8,64}", body):
            bot.send_message(cid, t(lang, "send_id_hint"))
            return
        bot.send_message(cid, t(lang, "verifying"))
        time.sleep(1.2)
        if body != st["oid"]:
            bot.send_message(cid, t(lang, "not_found"))     # نفس رد البوت على معرّف خاطئ
            return
        _lm_success(cid, uid, lang)
        return

    if step == "fx":
        if not is_text:
            bot.send_message(cid, tx["fx_hint"].format(da=st["da"]), parse_mode="HTML")
            return
        amt, has_time = _lm_parse_fx(body)
        if amt is None or not has_time:
            bot.send_message(cid, tx["fx_hint"].format(da=st["da"]), parse_mode="HTML")
            return
        bot.send_message(cid, t(lang, "verifying"))
        time.sleep(1.2)
        if amt != st["da"]:
            bot.send_message(cid, tx["fx_amt"].format(da=st["da"]), parse_mode="HTML")
            return
        _lm_success(cid, uid, lang)
        return

    if step == "photo":
        if is_text:
            bot.send_message(cid, pmt(lang, "proof_hint_bd"), parse_mode="HTML")
            return
        bot.send_message(cid, t(lang, "verifying"))
        time.sleep(1.2)
        _lm_success(cid, uid, lang)


# ---------- معالج الأزرار dm_ ----------
def _lm_cb_filter(c):
    try:
        if not (c.data or "").startswith("dm_"):
            return False
        if _maint_blocked_user(c.from_user):
            return False      # وضع التحديث يتولى الأمر
        return True
    except Exception:
        return False


def lm_callback(call):
    uid = call.from_user.id
    lang = get_lang(uid)
    tx = _lm_tx(lang)
    d = call.data or ""
    try:
        if d == "dm_adm":      # زر لوحة الأدمن: تشغيل/إيقاف القسم
            if str(uid) != str(ADMIN_CHAT_ID):
                bot.answer_callback_query(call.id)
                return
            was = _lm_on()
            waiting = 0
            try:
                waiting = len(_smembers(LM_WAIT))
            except Exception:
                pass
            if was:
                _lm_set(False)
            else:
                _lm_set(True)
                _lm_broadcast_back()
            try:
                rm = call.message.reply_markup
                for row in rm.keyboard:
                    for b in row:
                        if getattr(b, "callback_data", None) == "dm_adm":
                            b.text = _lm_admin_label()
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=rm)
            except Exception as e:
                print(f"learn admin label update failed: {e}")
            bot.answer_callback_query(
                call.id,
                ("⛔ تم إيقاف «تعلّم كيف تشتري». من يضغط الزر يجد رسالة التوقف مع «أعلمني عند البدء»." if was
                 else f"✅ تم تشغيل «تعلّم كيف تشتري». أُرسل إشعار العودة لـ {waiting} زبون."),
                show_alert=True)
            return

        if d == "dm_end":
            _lm_state.pop(uid, None)
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except Exception:
                pass
            bot.answer_callback_query(call.id)
            send_main_menu(call.message.chat.id, lang)
            return

        if d == "dm_nt":
            try:
                was = str(uid) in {str(x) for x in _smembers(LM_WAIT)}
                if not was:
                    _sadd(LM_WAIT, str(uid))
            except Exception:
                was = False
            bot.answer_callback_query(call.id, tx["nt_already" if was else "nt_ok"], show_alert=True)
            if not was:
                try:
                    total = len(_smembers(LM_WAIT))
                    u = call.from_user
                    nm = html.escape(((u.first_name or "") + " " + (u.last_name or "")).strip() or "—")
                    un = f" @{u.username}" if getattr(u, "username", None) else ""
                    bot.send_message(ADMIN_CHAT_ID,
                                     f"🔔 <b>زبون ضغط «أعلمني عند البدء» (قسم التعلّم)</b>\n👤 {nm}{un} (ID: <code>{uid}</code>)\n\n📊 المنتظرون الآن: <b>{total}</b>",
                                     parse_mode="HTML")
                except Exception as e:
                    print(f"learn nt admin notify failed: {e}")
            return

        if not _lm_on():
            _lm_state.pop(uid, None)
            bot.answer_callback_query(call.id)
            _lm_stopped(call, lang)
            return

        if d == "dm_home":
            if _lm_real_busy(uid):
                _lm_state.pop(uid, None)
                bot.answer_callback_query(call.id, tx["busy"], show_alert=True)
                return
            _lm_state.pop(uid, None)
            bot.answer_callback_query(call.id)
            _lm_notify_admin(call.from_user)
            _lm_home(call, lang)
            return

        if d.startswith("dm_cp_"):
            st = _lm_get(uid)
            val = ""
            if st:
                val = st.get("oid") if d == "dm_cp_oid" else st.get("dest", "")
            bot.answer_callback_query(call.id, str(val or ""), show_alert=True)
            return

        if _lm_real_busy(uid):
            _lm_state.pop(uid, None)
            bot.answer_callback_query(call.id, tx["busy"], show_alert=True)
            return

        if d.startswith("dm_p_") and d[5:] in LM_PRODUCTS:
            _lm_state.pop(uid, None)
            bot.answer_callback_query(call.id)
            _lm_product(call, lang, d[5:])
            return

        if d.startswith("dm_b_") and d[5:] in LM_PRODUCTS:
            _lm_state.pop(uid, None)
            bot.answer_callback_query(call.id)
            _lm_picker(call, lang, d[5:])
            return

        if d.startswith("dm_m_"):
            parts = d.split("_")        # dm, m, <method>, <k>
            if len(parts) == 4 and parts[2] in LM_METHOD_NAME and parts[3] in LM_PRODUCTS:
                bot.answer_callback_query(call.id)
                _lm_method(call, lang, parts[2], parts[3])
                return

        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"learn callback error: {e}")
        try:
            bot.answer_callback_query(call.id)
        except Exception:
            pass


def _lm_clear_filter(c):
    """يمر على كل الأزرار: أي زر ليس dm_ (شراء حقيقي مثلاً) ينهي حالة التعلّم. لا يعالج شيئاً."""
    try:
        if c.from_user and not (c.data or "").startswith("dm_"):
            _lm_state.pop(c.from_user.id, None)
    except Exception:
        pass
    return False


def lm_noop(call):
    pass


# ---------- أمر الأدمن ----------
def lm_command(message):
    if not is_admin_msg(message):
        return
    parts = (message.text or "").split()
    arg = parts[1].lower() if len(parts) > 1 else ""
    if arg == "off":
        _lm_set(False)
    elif arg == "on":
        was_off = not _lm_on()
        _lm_set(True)
        if was_off:
            _lm_broadcast_back()
    try:
        waiting = len(_smembers(LM_WAIT))
    except Exception:
        waiting = 0
    bot.reply_to(message,
                 "🎓 قسم «تعلّم كيف تشتري»: " + ("✅ شغّال" if _lm_on() else "⛔ متوقف")
                 + f"\n👥 بانتظار «أعلمني عند البدء»: {waiting}\n/learn on | off")


def _lm_broadcast_back():
    try:
        targets = [str(x) for x in _smembers(LM_WAIT)]
    except Exception:
        targets = []
    if not targets:
        return

    def _run():
        sent = 0
        for uid in targets:
            try:
                lang = get_lang(uid)
                tx = _lm_tx(lang)
                mk = InlineKeyboardMarkup(row_width=1)
                mk.add(_lm_btn(tx["btn"], "dm_home", style="primary", icon=LM_ICON))
                bot.send_message(int(uid), tx["back_on"], parse_mode="HTML", reply_markup=mk)
                sent += 1
            except Exception:
                pass
            time.sleep(0.06)
        try:
            kv_del(LM_WAIT)
        except Exception:
            pass
        try:
            bot.send_message(ADMIN_CHAT_ID, f"🔔 أُرسل إشعار عودة «تعلّم كيف تشتري» لـ {sent} زبون", parse_mode="HTML")
        except Exception:
            pass

    threading.Thread(target=_run, daemon=True).start()


# ---------- التسجيل (بأولوية أعلى من معالجات الشراء الحقيقي) ----------
bot.message_handler(func=_lm_msg_filter, content_types=["text", "photo", "document"])(lm_input)
bot.message_handlers.insert(0, bot.message_handlers.pop())

bot.message_handler(commands=["learn"])(lm_command)

bot.callback_query_handler(func=_lm_cb_filter)(lm_callback)
bot.callback_query_handlers.insert(0, bot.callback_query_handlers.pop())

bot.callback_query_handler(func=_lm_clear_filter)(lm_noop)
bot.callback_query_handlers.insert(0, bot.callback_query_handlers.pop())

# ---------- زر القائمة الرئيسية (أزرق، تحت «من سيفوز؟») — آخر خطوة: لا يظهر الزر إلا بعد نجاح كل ما قبله ----------
_lm_gsk_orig = generate_store_keyboard


def _lm_gsk_with_button(lang):
    mk = _lm_gsk_orig(lang)
    try:
        if sum(len(r) for r in mk.keyboard) < 100:
            b = InlineKeyboardButton(text=_lm_tx(lang)["btn"], callback_data="dm_home")
            b.style = "primary"
            b.icon_dyn = LM_ICON
            mk.add(b)
    except Exception as e:
        print(f"learn menu button failed: {e}")
    return mk


generate_store_keyboard = _lm_gsk_with_button


def _lm_admin_label():
    return "🎓 تعلّم كيف تشتري: " + ("✅ شغّال (اضغط للإيقاف)" if _lm_on() else "⛔ متوقف (اضغط للتشغيل)")


def _lm_admin_btn(markup):
    markup.add(InlineKeyboardButton(text=_lm_admin_label(), callback_data="dm_adm"))


_learn_admin_btn = _lm_admin_btn      # يظهر الزر في لوحة الأدمن (يستدعيه main.py)

print("learn.py loaded ✅")
