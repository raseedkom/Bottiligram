# -*- coding: utf-8 -*-
# qtyflow.py — (1) شاشة الكمية: [1] [2] [3] خضراء + «مخصص» زرقاء (الزبون يكتب العدد) + رجوع،
#                  بسقف المخزون، لمنتجات المورّد وGemini وبطاقات الهدايا. الإجمالي يظهر في الفاتورة كالمعتاد.
#              (2) تحت رسالة التسليم التلقائي: 📥 تنزيل ملف TXT + شراء + فتح المتجر المصغّر + المحفظة/حسابي/طلباتي.
# لا يلمس الدفع ولا التسليم: يعيد استعمال نفس معالجات الكميات والفواتير الموجودة (vq_ / gq_ / gqt_).
# أسماء مستعملة من main.py: bot, telebot, InlineKeyboardMarkup, InlineKeyboardButton, t, tr, wt, get_lang,
#   find_product, notify_admin, register_user, send_card, sync_stock, GEMINI_ID, GEMINI_TEXTS, VT_TEXTS, _VT_PRODS,
#   _vt_back_cb, _vt_warranty, gemini_stock, gemini_unit_price, GIFT_VARIANTS, _gift_stock, handle_vente_qty,
#   handle_gemini_qty, handle_gift_qty, order_log_auto, _oid_from, order_get, send_main_menu, kv_get, kv_set,
#   ADMIN_CHAT_ID, mt, _maint_blocked_user, send_maintenance, user_lang

import io as _qf_io
import re as _qf_re
import html as _qf_html
import time as _qf_time
import types as _qf_types
from decimal import Decimal as _QD

QF_HARD_MAX = 50          # سقف أمان لأي طلب كمية
QF_UNKNOWN_MAX = 10       # عند عدم معرفة المخزون (بعض بطاقات الهدايا)
QF_STATE_TTL = 300        # 5 دقائق لانتظار العدد المكتوب
QF_TXT_KEY = "rk:qf:txt"  # "0" = إيقاف أزرار التسليم

# رفع سقف الكميات في المعالجات الأصلية (هي تتحقق من المخزون بنفسها)
try:
    VENTE_MAX_QTY = QF_HARD_MAX
    GIFT_MAX_QTY = QF_HARD_MAX
    GEMINI_MAX_QTY = QF_HARD_MAX
    GEMINI_QTYS = tuple(range(1, QF_HARD_MAX + 1))
except Exception as _e:
    print(f"qtyflow caps failed: {_e}")

_qf_state = {}            # uid -> {"ref","ts","card","prompt"}

_QF_TX = {
    "ar": {"custom": "مخصص", "ask": "🔢 <b>الكمية</b>\n\n✏️ أرسل عدد العناصر التي تريد شراءها:\n💰 سعر الوحدة: <b>${u}</b>\n📦 المخزون المتاح: <b>{m}</b>",
           "bad": "⚠️ أرسل رقماً صحيحاً بين 1 و{m}.", "gone": "انتهت الجلسة، أعد اختيار المنتج.",
           "qty": "🔢 اختر الكمية:\n📦 {p}\n💰 سعر الوحدة: ${u}\n📦 المتاح: {m}"},
    "en": {"custom": "Custom", "ask": "🔢 <b>Quantity</b>\n\n✏️ Send the number of items you want to buy:\n💰 Unit price: <b>${u}</b>\n📦 Available stock: <b>{m}</b>",
           "bad": "⚠️ Send a whole number between 1 and {m}.", "gone": "Session expired, please pick the product again.",
           "qty": "🔢 Choose the quantity:\n📦 {p}\n💰 Unit price: ${u}\n📦 Available: {m}"},
    "fr": {"custom": "Personnalisé", "ask": "🔢 <b>Quantité</b>\n\n✏️ Envoyez le nombre d'articles à acheter :\n💰 Prix unitaire : <b>${u}</b>\n📦 Stock disponible : <b>{m}</b>",
           "bad": "⚠️ Envoyez un nombre entier entre 1 et {m}.", "gone": "Session expirée, choisissez à nouveau le produit.",
           "qty": "🔢 Choisissez la quantité :\n📦 {p}\n💰 Prix unitaire : ${u}\n📦 Disponible : {m}"},
}
_QF_BTN = {
    "ar": {"txt": "📥 تنزيل ملف TXT", "shop": "🛒 شراء", "store": "🛍️ فتح المتجر", "wal": "💰 المحفظة", "prof": "👤 حسابي", "hist": "🧾 طلباتي", "file": "📁 الطلب"},
    "en": {"txt": "📥 Download TXT file", "shop": "🛒 Buy", "store": "🛍️ Open store", "wal": "💰 Wallet", "prof": "👤 Profile", "hist": "🧾 Orders", "file": "📁 Order"},
    "fr": {"txt": "📥 Télécharger le fichier TXT", "shop": "🛒 Acheter", "store": "🛍️ Ouvrir la boutique", "wal": "💰 Portefeuille", "prof": "👤 Profil", "hist": "🧾 Commandes", "file": "📁 Commande"},
}


def _qf_tx(lang):
    return _QF_TX.get(lang) or _QF_TX["ar"]


def _qf_bt(lang):
    return _QF_BTN.get(lang) or _QF_BTN["ar"]


def _qf_money(x):
    return str(_QD(str(x)).quantize(_QD("0.01")))


# ---------------- معلومات المنتج من المرجع ----------------
def _qf_info(ref):
    """يرجع (maxq, unit_price_str, handler, data_fmt, name) أو None. data_fmt فيه {q}."""
    kind = ref[0]
    if kind == "v":
        vid = int(ref[1:])
        p = _VT_PRODS.get("vt" + str(vid))
        if not p:
            return None
        maxq = min(int(p["stock"]), QF_HARD_MAX)
        return maxq, _qf_money(p["price"].lstrip("$")), handle_vente_qty, f"vq_{vid}_" + "{q}", p.get("name", "")
    if kind == "g":
        product = find_product(GEMINI_ID)
        maxq = min(int(gemini_stock()), QF_HARD_MAX)
        return maxq, _qf_money(gemini_unit_price()), handle_gemini_qty, "gq_{q}", (product or {}).get("name", "Gemini")
    if kind == "f":
        _, pid, idx = ref.split(":")
        label, price = GIFT_VARIANTS[pid][int(idx)]
        st = _gift_stock(pid, label)
        maxq = QF_UNKNOWN_MAX if st is None else min(int(st), QF_HARD_MAX)
        product = find_product(pid) or {}
        return maxq, _qf_money(price), handle_gift_qty, f"gqt_{pid}_{idx}_" + "{q}", f"{product.get('name', '')} — {label}"
    return None


def _qf_markup(lang, ref, maxq, back_cb):
    mk = InlineKeyboardMarkup(row_width=3)
    row = []
    for q in range(1, min(3, maxq) + 1):
        b = InlineKeyboardButton(text=str(q), callback_data=f"qfq|{ref}|{q}")
        b.style = "success"
        row.append(b)
    if row:
        mk.row(*row)
    if maxq > 3:
        c = InlineKeyboardButton(text=_qf_tx(lang)["custom"], callback_data=f"qfc|{ref}")
        c.style = "primary"
        mk.add(c)
    mk.add(InlineKeyboardButton(text=t(lang, "back"), callback_data=back_cb))
    return mk


# ---------------- المورّد: صفحة المنتج ----------------
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
    if stock > 0:
        mk = _qf_markup(lang, f"v{p['vid']}", min(stock, QF_HARD_MAX), _vt_back_cb(p))
        bottom = gt["choose_qty"]
    else:
        mk = InlineKeyboardMarkup(row_width=1)
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


# ---------------- Gemini: صفحة المنتج ----------------
def _qf_gemini_select(call):
    product = find_product(GEMINI_ID)
    lang = get_lang(call.from_user.id)
    gt = GEMINI_TEXTS.get(lang, GEMINI_TEXTS["ar"])
    if call.message.chat.type == "private":
        register_user(call.from_user.id)
    notify_admin(call.from_user, product, lang)
    sync_stock()
    stock = product["stock"]
    if stock > 0:
        markup = _qf_markup(lang, "g", min(int(stock), QF_HARD_MAX), "back_to_main")
        bottom = gt["choose_qty"]
    else:
        markup = InlineKeyboardMarkup(row_width=1)
        bottom = gt["out_of_stock"]
        markup.add(InlineKeyboardButton(text=t(lang, "notify_me"), callback_data=f"notify_{GEMINI_ID}"))
        markup.add(InlineKeyboardButton(text=t(lang, "back"), callback_data="back_to_main"))
    caption = (
        f"{t(lang, 'chosen')} *{tr(product, 'name', lang)}*\n"
        f"{t(lang, 'price')} *{product['price']}*\n"
        f"{t(lang, 'available')} *{stock}*\n\n"
        f"{t(lang, 'description')}\n{tr(product, 'description', lang)}\n\n"
        f"{bottom}"
    )
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    send_card(call.message.chat.id, product, caption, markup)
    bot.answer_callback_query(call.id)


_qf_old_gem = handle_gemini_select
handle_gemini_select = _qf_gemini_select
for _h in bot.callback_query_handlers:
    if _h.get("function") is _qf_old_gem:
        _h["function"] = _qf_gemini_select


# ---------------- بطاقات الهدايا: شاشة الكمية بعد اختيار القيمة ----------------
def _gift_ask_qty(call, product, pid, idx, label, price, lang):
    stock = _gift_stock(pid, label)
    maxq = QF_UNKNOWN_MAX if stock is None else min(int(stock), QF_HARD_MAX)
    if maxq <= 1:
        return False                      # كمية واحدة فقط: المسار القديم مباشرة
    mk = _qf_markup(lang, f"f:{pid}:{idx}", maxq, f"buy_{pid}")
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    bot.send_message(
        call.message.chat.id,
        _qf_tx(lang)["qty"].format(p=f"{tr(product, 'name', lang)} — {label}", u=_qf_money(price), m=maxq),
        reply_markup=mk,
    )
    bot.answer_callback_query(call.id)
    return True


# ---------------- ضغط 1/2/3 ----------------
def _qf_maint(call):
    """وضع التحديث: نفس منع المتجر لغير الأدمن."""
    try:
        if _maint_blocked_user(call.from_user):
            bot.answer_callback_query(call.id)
            send_maintenance(call.message.chat.id, get_lang(call.from_user.id))
            return True
    except Exception:
        pass
    return False


def _qf_cb_q(call):
    if _qf_maint(call):
        return
    try:
        _, ref, q = call.data.split("|")
        info = _qf_info(ref)
        if not info:
            raise ValueError("no info")
        handler, fmt = info[2], info[3]
        call.data = fmt.format(q=int(q))
        handler(call)
    except Exception as e:
        print(f"qtyflow qty press failed: {e}")
        try:
            bot.answer_callback_query(call.id)
        except Exception:
            pass


# ---------------- مخصص: طلب كتابة العدد ----------------
def _qf_cb_custom(call):
    if _qf_maint(call):
        return
    uid = call.from_user.id
    lang = get_lang(uid)
    tx = _qf_tx(lang)
    try:
        ref = call.data.split("|")[1]
        info = _qf_info(ref)
        if not info or info[0] < 1:
            bot.answer_callback_query(call.id)
            return
        maxq, unit = info[0], info[1]
        mk = InlineKeyboardMarkup()
        mk.add(InlineKeyboardButton(text=t(lang, "back"), callback_data="qfb"))
        sent = bot.send_message(call.message.chat.id, tx["ask"].format(u=unit, m=maxq), parse_mode="HTML", reply_markup=mk)
        _qf_state[uid] = {"ref": ref, "ts": _qf_time.time(),
                          "card": (call.message.chat.id, call.message.message_id),
                          "prompt": (sent.chat.id, sent.message_id)}
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"qtyflow custom failed: {e}")
        try:
            bot.answer_callback_query(call.id)
        except Exception:
            pass


def _qf_cb_back(call):
    st = _qf_state.pop(call.from_user.id, None)
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    bot.answer_callback_query(call.id)


def _qf_clear_filter(call):
    """أي ضغطة أخرى تلغي انتظار العدد (باش ما يلتقط أرقاماً أخرى مثل رقم العملية)."""
    try:
        if not (call.data or "").startswith("qf"):
            _qf_state.pop(call.from_user.id, None)
    except Exception:
        pass
    return False


def _qf_norm_digits(s):
    return str(s).translate(str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")).strip()


def _qf_msg_filter(m):
    try:
        st = _qf_state.get(m.from_user.id)
        if not st or m.chat.type != "private":
            return False
        if _qf_time.time() - st["ts"] > QF_STATE_TTL:
            _qf_state.pop(m.from_user.id, None)
            return False
        txt = _qf_norm_digits(m.text or "")
        if _qf_re.fullmatch(r"\d{1,4}", txt):
            return True
        _qf_state.pop(m.from_user.id, None)          # أي نص آخر/أمر يلغي الانتظار ويمر لباقي البوت
        return False
    except Exception:
        return False


def _qf_msg(m):
    uid = m.from_user.id
    lang = get_lang(uid)
    tx = _qf_tx(lang)
    st = _qf_state.get(uid)
    if not st:
        return
    try:
        if _maint_blocked_user(m.from_user):
            _qf_state.pop(uid, None)
            send_maintenance(m.chat.id, lang)
            return
        n = int(_qf_norm_digits(m.text))
        info = _qf_info(st["ref"])
        if not info:
            _qf_state.pop(uid, None)
            bot.send_message(m.chat.id, tx["gone"])
            return
        maxq, handler, fmt = info[0], info[2], info[3]
        if n < 1 or n > maxq:
            bot.send_message(m.chat.id, tx["bad"].format(m=maxq))
            return
        _qf_state.pop(uid, None)
        for cid, mid in (st.get("card"), st.get("prompt")):
            try:
                bot.delete_message(cid, mid)
            except Exception:
                pass
        ph = bot.send_message(m.chat.id, "⏳")
        call = _qf_types.SimpleNamespace(id="qb", data=fmt.format(q=n), from_user=m.from_user, message=ph,
                                         chat_instance="qty", inline_message_id=None)
        handler(call)
    except Exception as e:
        print(f"qtyflow typed qty failed: {e}")


# ---------------- أزرار تحت رسالة التسليم ----------------
_qf_last = {}                                  # chat_id -> (message_id, ts, text, markup)
_qf_orig_send = bot.send_message


def _qf_send_tracked(*a, **k):
    res = _qf_orig_send(*a, **k)
    try:
        cid = a[0] if a else k.get("chat_id")
        text = a[1] if len(a) > 1 else k.get("text")
        if res is not None and getattr(res, "message_id", None):
            if len(_qf_last) > 3000:
                _qf_last.clear()
            _qf_last[str(cid)] = (res.message_id, _qf_time.time(), str(text or ""), k.get("reply_markup"))
    except Exception:
        pass
    return res


bot.send_message = _qf_send_tracked


def _qf_txt_on():
    try:
        return str(kv_get(QF_TXT_KEY)) != "0"
    except Exception:
        return True


def _qf_delivery_markup(lang, oid, old):
    """أزرار تحت رسالة التسليم: TXT + نفس قائمة /start (بدون زر الإحالة) + فتح المتجر المصغّر."""
    bt = _qf_bt(lang)
    mk = InlineKeyboardMarkup()
    try:
        if isinstance(old, InlineKeyboardMarkup):
            for row in old.keyboard:
                mk.row(*row)
    except Exception:
        pass
    mk.add(InlineKeyboardButton(text=bt["txt"], callback_data=f"qtx_{oid}"))
    shop = InlineKeyboardButton(text=bt["shop"], callback_data="qgo|shop")
    shop.style = "success"
    mk.add(shop)
    try:
        url = globals()["_ws_base_url"]()
        mk.add(InlineKeyboardButton(text=bt["store"], web_app=telebot.types.WebAppInfo(url=url)))
    except Exception:
        pass
    mk.add(InlineKeyboardButton(text=bt["wal"], callback_data="qgo|pf_wallet"))
    try:
        game = InlineKeyboardButton(text=smt(lang, "game"), callback_data="qgo|sm_game")
        game.style = "danger"
        mk.add(game)
    except Exception as e:
        print(f"qtyflow game btn failed: {e}")
    mk.row(InlineKeyboardButton(text=bt["prof"], callback_data="qgo|pf_profile"),
           InlineKeyboardButton(text=bt["hist"], callback_data="qgo|pf_hist"))
    try:
        mk.add(InlineKeyboardButton(text=smt(lang, "api"), callback_data="qgo|sm_api"))
        mk.row(InlineKeyboardButton(text=t(lang, "kb_support"), url=MY_PRIVATE_CHAT_LINK),
               InlineKeyboardButton(text=smt(lang, "channel"), url=CHANNEL_LINK))
        mk.add(InlineKeyboardButton(text=t(lang, "change_lang"), callback_data="qgo|change_lang"))
    except Exception as e:
        print(f"qtyflow extra btns failed: {e}")
    return mk


def _qf_attach(uid, canon, delivery):
    if not _qf_txt_on():
        return
    rec = _qf_last.get(str(uid))
    if not rec or _qf_time.time() - rec[1] > 120:
        return
    plain = _qf_html.unescape(rec[2])
    lines = [l.strip() for l in str(delivery).split("\n") if l.strip()]
    if not lines or not any(l[:30] in plain for l in lines):
        return                                   # آخر رسالة ليست رسالة التسليم
    try:
        lang = get_lang(uid)
    except Exception:
        lang = "ar"
    mk = _qf_delivery_markup(lang, _oid_from(canon), rec[3])
    bot.edit_message_reply_markup(chat_id=int(uid), message_id=rec[0], reply_markup=mk)


_qf_orig_ola = order_log_auto


def order_log_auto(uid, pname, price, canon, delivery):
    r = _qf_orig_ola(uid, pname, price, canon, delivery)
    try:
        _qf_attach(uid, canon, delivery)
    except Exception as e:
        print(f"qtyflow delivery buttons failed: {e}")
    return r


_qf_txt_gap = {}


def _qf_cb_txt(call):
    uid = call.from_user.id
    try:
        oid = call.data[4:]
        o = order_get(oid)
        if not o or (str(o.get("user_id")) != str(uid) and str(uid) != str(ADMIN_CHAT_ID)):
            bot.answer_callback_query(call.id)
            return
        now = _qf_time.time()
        if now - _qf_txt_gap.get(uid, 0) < 3:
            bot.answer_callback_query(call.id)
            return
        _qf_txt_gap[uid] = now
        body = str(o.get("delivery") or "").strip()
        lines = [l for l in body.split("\n") if l.strip()]
        if lines and all(len(l.split()) == 1 for l in lines):
            body = "\n\n".join(l.strip() for l in lines)       # عناصر مفردة: سطر فارغ بين كل واحد
        name = _qf_re.sub(r"[^\w\-]+", "_", str(o.get("product_name") or "order")).strip("_")[:40] or "order"
        f = _qf_io.BytesIO(body.encode("utf-8"))
        f.name = f"{name}_order-{oid}.txt"
        lang = get_lang(uid)
        bot.send_document(call.message.chat.id, f,
                          caption=f"{_qf_bt(lang)['file']} #{oid}\n{o.get('product_name') or ''}")
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"qtyflow txt failed: {e}")
        try:
            bot.answer_callback_query(call.id)
        except Exception:
            pass


def _qf_cb_txt_demo(call):
    """زر TXT في رسالة «تعلّم كيف تشتري»: يرسل ملفاً تجريبياً بالكود المعروض (لا علاقة له بأي طلب حقيقي)."""
    try:
        code = call.data[4:]
        if not _qf_re.fullmatch(r"DEMO(-[A-Z0-9]{4}){3}", code):
            bot.answer_callback_query(call.id)
            return
        f = _qf_io.BytesIO((code + "\n").encode("utf-8"))
        f.name = "demo_order.txt"
        bot.send_document(call.message.chat.id, f, caption="📁 DEMO (مثال)")
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"qtyflow demo txt failed: {e}")
        try:
            bot.answer_callback_query(call.id)
        except Exception:
            pass


def _qf_cb_go(call):
    """أزرار جنب التسليم: تفتح قوائم البوت في رسالة جديدة دون المساس برسالة التسليم."""
    uid = call.from_user.id
    if _qf_maint(call):
        return
    try:
        target = call.data.split("|")[1]
        bot.answer_callback_query(call.id)
        lang = get_lang(uid)
        if target == "shop":
            send_main_menu(call.message.chat.id, lang)
            return
        if target == "change_lang":
            send_language_menu(call.message.chat.id)
            return
        if target not in ("pf_wallet", "pf_profile", "pf_hist", "sm_game", "sm_api"):
            return
        ph = bot.send_message(call.message.chat.id, "⏳")
        fake = _qf_types.SimpleNamespace(id="qb", data=target, from_user=call.from_user, message=ph,
                                         chat_instance="qgo", inline_message_id=None)
        for h in list(bot.callback_query_handlers):
            try:
                ok = bot._test_message_handler(h, fake)
            except Exception:
                f = (h.get("filters") or {}).get("func")
                ok = (f is None) or bool(f(fake))
            if ok:
                h["function"](fake)
                break
    except Exception as e:
        print(f"qtyflow go failed: {e}")


# ---------------- تسجيل المعالجات (بأولوية) ----------------
bot.callback_query_handler(func=lambda c: (c.data or "").startswith("qfq|"))(_qf_cb_q)
bot.callback_query_handler(func=lambda c: (c.data or "").startswith("qfc|"))(_qf_cb_custom)
bot.callback_query_handler(func=lambda c: c.data == "qfb")(_qf_cb_back)
bot.callback_query_handler(func=lambda c: (c.data or "").startswith("qtx_"))(_qf_cb_txt)
bot.callback_query_handler(func=lambda c: (c.data or "").startswith("qgo|"))(_qf_cb_go)
bot.callback_query_handler(func=lambda c: (c.data or "").startswith("qtd_"))(_qf_cb_txt_demo)
for _i in range(6):
    bot.callback_query_handlers.insert(0, bot.callback_query_handlers.pop())
bot.callback_query_handler(func=_qf_clear_filter)(lambda c: None)
bot.callback_query_handlers.insert(0, bot.callback_query_handlers.pop())

bot.message_handler(func=_qf_msg_filter)(_qf_msg)
bot.message_handlers.insert(0, bot.message_handlers.pop())


def _qf_txtbtn_cmd(m):
    try:
        if str(m.chat.id) != str(ADMIN_CHAT_ID):
            return
        parts = (m.text or "").split()
        arg = parts[1].lower() if len(parts) > 1 else ""
        if arg in ("on", "off"):
            kv_set(QF_TXT_KEY, "1" if arg == "on" else "0")
        bot.send_message(m.chat.id, f"📥 أزرار تحت رسالة التسليم (TXT + المتجر): {'✅ مفعّلة' if _qf_txt_on() else '⛔ مطفأة'}\n\n/txtbtn on — تشغيل\n/txtbtn off — إطفاء")
    except Exception as e:
        print(f"txtbtn command failed: {e}")


bot.message_handler(commands=["txtbtn"])(_qf_txtbtn_cmd)
bot.message_handlers.insert(0, bot.message_handlers.pop())


# ---------------- أدمن: /retry_now — إعادة محاولة الطلبات المدفوعة العالقة فوراً ----------------
def _qf_do_retry(chat_id):
    canons = list(pend_list())
    if not canons:
        bot.send_message(chat_id, "✅ لا توجد طلبات مدفوعة عالقة. (ما هو عالق ينتظر رصيد المورّد يظهر هنا)")
        return
    lines = [f"🔁 <b>طلبات مدفوعة عالقة: {len(canons)}</b>\n"]
    for c in canons[:15]:
        try:
            cl = kv_get_json(f"rk:tx:{c}") or {}
        except Exception:
            cl = {}
        lines.append(f"• {_qf_html.escape(str(cl.get('product_name', '?')))} | <code>{cl.get('user_id', '?')}</code> | <code>{_qf_html.escape(c[:14])}</code>")
    lines.append("\n⏳ جارٍ إعادة المحاولة الآن، وتصلك رسائل النجاح أو الفشل.")
    bot.send_message(chat_id, "\n".join(lines), parse_mode="HTML")
    _qf_threading.Thread(target=retry_pending_orders, daemon=True).start()


def _qf_retry_cmd(m):
    try:
        if str(m.chat.id) == str(ADMIN_CHAT_ID):
            _qf_do_retry(m.chat.id)
    except Exception as e:
        print(f"retry_now failed: {e}")


def _qf_retry_cb(call):
    try:
        if str(call.from_user.id) != str(ADMIN_CHAT_ID):
            bot.answer_callback_query(call.id)
            return
        bot.answer_callback_query(call.id, "🔁")
        _qf_do_retry(call.message.chat.id)
    except Exception as e:
        print(f"retry button failed: {e}")


import threading as _qf_threading
bot.message_handler(commands=["retry_now"])(_qf_retry_cmd)
bot.message_handlers.insert(0, bot.message_handlers.pop())
bot.callback_query_handler(func=lambda c: c.data == "qf_retry")(_qf_retry_cb)
bot.callback_query_handlers.insert(0, bot.callback_query_handlers.pop())

_qf_prev_admin_btn = _learn_admin_btn


def _learn_admin_btn(markup):
    try:
        _qf_prev_admin_btn(markup)
    except Exception as e:
        print(f"learn admin button failed: {e}")
    try:
        n = len(list(pend_list()))
    except Exception:
        n = 0
    markup.add(InlineKeyboardButton(text=f"🔁 إعادة محاولة الطلبات العالقة ({n})", callback_data="qf_retry"))


print("qtyflow.py loaded ✅")
