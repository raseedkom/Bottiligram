# -*- coding: utf-8 -*-
# rateprompt.py — طلب تقييم من الزبون بعد تسليم المنتج («⭐ قيّم تجربتك»).
# - نجوم فقط (1-5)، بدون تعليق ولا اسم؛ يُحفظ الحرف الأول من اسم حسابه فقط (A***).
# - تقييم واحد لكل طلب. يدخل نفس قائمة reviews.py فتتحدث النجوم في المتجر المصغّر تلقائياً.
# - لا يلمس الشراء ولا التسليم: يلتفّ حول record_purchase / order_save ويرسل الطلب بعد دقيقة ونصف.
# - أدمن: زر «🧪 جرّب طلب التقييم» (يرسل لك نفس رسالة الزبون ولا يحفظ شيئاً) وزر تشغيل/إطفاء.
# أسماء مستعملة من main.py: bot, ADMIN_CHAT_ID, InlineKeyboardButton, InlineKeyboardMarkup, kv_get, kv_set,
#   get_lang, MANUAL_IDS, record_purchase, order_save, _learn_admin_btn, _rv_load, _rv_save (reviews.py)

import json as _rp_json
import time as _rp_time
import html as _rp_html
import hashlib as _rp_hash
import threading as _rp_threading

RP_ON_KEY = "rk:rq:on"             # "0" = مطفأ
RP_DELAY = 90                      # ثانية بعد التسليم
RP_TTL = 30 * 24 * 3600
_rp_lock = _rp_threading.Lock()

_RP_TX = {
    "ar": {"ask": "⭐ <b>قيّم تجربتك</b>\n\nشكراً لثقتك 🙏\nكيف كانت تجربتك مع:\n📦 <b>{p}</b>\n\nاضغط على عدد النجوم (من 5):",
           "later": "✖️ لاحقاً", "thanks": "✅ شكراً على تقييمك!\n{s}\n📦 {p}",
           "dup": "سبق وقيّمت هذا الطلب ✅", "gone": "انتهت صلاحية هذا الطلب."},
    "en": {"ask": "⭐ <b>Rate your experience</b>\n\nThank you for your trust 🙏\nHow was your experience with:\n📦 <b>{p}</b>\n\nTap the number of stars (out of 5):",
           "later": "✖️ Later", "thanks": "✅ Thanks for your rating!\n{s}\n📦 {p}",
           "dup": "You already rated this order ✅", "gone": "This request has expired."},
    "fr": {"ask": "⭐ <b>Évaluez votre expérience</b>\n\nMerci pour votre confiance 🙏\nComment s'est passée votre expérience avec :\n📦 <b>{p}</b>\n\nAppuyez sur le nombre d'étoiles (sur 5) :",
           "later": "✖️ Plus tard", "thanks": "✅ Merci pour votre avis !\n{s}\n📦 {p}",
           "dup": "Vous avez déjà noté cette commande ✅", "gone": "Cette demande a expiré."},
}


def _rp_tx(lang):
    return _RP_TX.get(lang) or _RP_TX["ar"]


def _rp_on():
    try:
        return str(kv_get(RP_ON_KEY)) != "0"
    except Exception:
        return True


def _rp_tok(key):
    return _rp_hash.sha1(str(key).encode()).hexdigest()[:10]


def _rp_get(tok):
    try:
        raw = kv_get("rk:rq:t:" + tok)
        return _rp_json.loads(raw) if raw else None
    except Exception:
        return None


def _rp_put(tok, rec):
    kv_set("rk:rq:t:" + tok, _rp_json.dumps(rec, ensure_ascii=False), ex=RP_TTL)


def _rp_send(uid, pk, pname, key, test=False):
    """يرسل رسالة طلب التقييم الآن."""
    try:
        tok = _rp_tok(key)
        if not test:
            if not kv_set("rk:rq:s:" + tok, "1", ex=RP_TTL, nx=True):
                return False                      # أُرسل سابقاً لهذا الطلب
        try:
            lang = get_lang(uid)
        except Exception:
            lang = "ar"
        tx = _rp_tx(lang)
        _rp_put(tok, {"uid": int(uid), "pk": pk, "pname": pname, "test": bool(test), "done": False})
        mk = InlineKeyboardMarkup()
        mk.row(*[InlineKeyboardButton(text=f"{n}⭐", callback_data=f"rqs_{tok}_{n}") for n in range(1, 6)])
        mk.add(InlineKeyboardButton(text=tx["later"], callback_data=f"rqx_{tok}"))
        bot.send_message(int(uid), tx["ask"].format(p=_rp_html.escape(str(pname))), parse_mode="HTML", reply_markup=mk)
        return True
    except Exception as e:
        print(f"rate prompt send failed: {e}")
        return False


def _rp_schedule(uid, pk, pname, key):
    try:
        if not _rp_on() or not pk or not pname:
            return
        t = _rp_threading.Timer(RP_DELAY, _rp_send, args=(uid, pk, pname, key))
        t.daemon = True
        t.start()
    except Exception as e:
        print(f"rate prompt schedule failed: {e}")


# ---------------- الالتفاف حول نقاط التسليم ----------------
_rp_orig_record = record_purchase


def record_purchase(uid, pid, pname, amount, canon, via="binance"):
    r = _rp_orig_record(uid, pid, pname, amount, canon, via=via)
    try:
        if pid and via != "manual_nr" and pid not in MANUAL_IDS:      # التسليم فوري (تلقائي / مورّد / Gemini / هدايا)
            _rp_schedule(uid, str(pid), pname, "rec:" + str(canon))
    except Exception as e:
        print(f"rate prompt hook (record) failed: {e}")
    return r


_rp_orig_order_save = order_save


def order_save(o):
    r = _rp_orig_order_save(o)
    try:
        if (o.get("status") in ("delivered_wait", "done") and o.get("product_id") not in (None, "", "auto")
                and o.get("product_id") in MANUAL_IDS):                # منتجات يدوية: عند تسليمها فعلاً
            _rp_schedule(o.get("user_id"), str(o["product_id"]), o.get("product_name"), "ord:" + str(o.get("oid")))
    except Exception as e:
        print(f"rate prompt hook (order) failed: {e}")
    return r


# ---------------- ضغطات الزبون ----------------
def _rp_stars(n):
    return "⭐" * n + "☆" * (5 - n)


def _rp_letter(user):
    for ch in (getattr(user, "first_name", "") or ""):
        if ch.isalnum():
            return ch.upper()
    return ""


def _rp_notify_admin(u, rec, n):
    """يصل الأدمن إشعار بكل تقييم: النجوم + الاسم الكامل + المعرّف + رابط المحادثة."""
    try:
        full = " ".join(x for x in [getattr(u, "first_name", "") or "", getattr(u, "last_name", "") or ""] if x).strip() or "—"
        un = getattr(u, "username", None)
        uid = int(u.id)
        lines = [
            "🧪 <b>تجربة تقييم</b> (لم يُحفظ)" if rec.get("test") else "⭐ <b>تقييم جديد</b>",
            "",
            f"📦 {_rp_html.escape(str(rec.get('pname')))}",
            f"{_rp_stars(n)}  ({n}/5)",
            "",
            f"👤 {_rp_html.escape(full)}",
            f"🔗 @{_rp_html.escape(un)}" if un else "🔗 (بدون username)",
            f"🆔 <code>{uid}</code>",
            f'💬 <a href="tg://user?id={uid}">فتح محادثة الزبون</a>',
        ]
        bot.send_message(int(ADMIN_CHAT_ID), "\n".join(lines), parse_mode="HTML", disable_web_page_preview=True)
    except Exception as e:
        print(f"rate prompt admin notify failed: {e}")


def _rp_cb(call):
    d = call.data or ""
    try:
        if d.startswith("rqx_"):
            tok = d[4:]
            rec = _rp_get(tok)
            if rec and int(rec["uid"]) == int(call.from_user.id):
                try:
                    bot.delete_message(call.message.chat.id, call.message.message_id)
                except Exception:
                    pass
            bot.answer_callback_query(call.id)
            return
        _, tok, n = d.split("_")
        n = int(n)
        if not 1 <= n <= 5:
            raise ValueError
        rec = _rp_get(tok)
        lang = get_lang(call.from_user.id)
        tx = _rp_tx(lang)
        if not rec or int(rec["uid"]) != int(call.from_user.id):
            bot.answer_callback_query(call.id, tx["gone"], show_alert=True)
            return
        with _rp_lock:
            rec = _rp_get(tok) or rec
            if rec.get("done"):
                bot.answer_callback_query(call.id, tx["dup"], show_alert=True)
                return
            if not rec.get("test"):
                items = _rv_load()
                items.append({"id": str(int(_rp_time.time() * 1000)), "pk": rec["pk"], "pname": rec["pname"],
                              "stars": n, "name": _rp_letter(call.from_user), "ts": int(_rp_time.time()),
                              "src": "customer"})
                _rv_save(items)
            rec["done"] = True
            _rp_put(tok, rec)
        _rp_notify_admin(call.from_user, rec, n)
        msg = tx["thanks"].format(s=_rp_stars(n), p=_rp_html.escape(str(rec["pname"])))
        if rec.get("test"):
            msg += "\n\n🧪 تجربة فقط — لم يُحفظ شيء."
        try:
            bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, parse_mode="HTML")
        except Exception:
            bot.send_message(call.message.chat.id, msg, parse_mode="HTML")
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"rate prompt callback failed: {e}")
        try:
            bot.answer_callback_query(call.id)
        except Exception:
            pass


bot.callback_query_handler(func=lambda c: (c.data or "").startswith(("rqs_", "rqx_")))(_rp_cb)
bot.callback_query_handlers.insert(0, bot.callback_query_handlers.pop())


# ---------------- أدمن: تجربة + تشغيل/إطفاء ----------------
def _rp_is_admin(uid):
    return str(uid) == str(ADMIN_CHAT_ID)


def _rp_admin_cb(call):
    try:
        if not _rp_is_admin(call.from_user.id):
            bot.answer_callback_query(call.id)
            return
        if call.data == "rq_test":
            ok = _rp_send(call.from_user.id, "test_product", "Netflix Premium (تجربة)",
                          f"test:{_rp_time.time()}", test=True)
            bot.answer_callback_query(call.id, "📨 أُرسلت لك رسالة الزبون" if ok else "⚠️ تعذّر الإرسال")
        elif call.data == "rq_tog":
            kv_set(RP_ON_KEY, "0" if _rp_on() else "1")
            bot.answer_callback_query(call.id, "✅ مفعّل" if _rp_on() else "⛔ مطفأ", show_alert=True)
            try:
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                              reply_markup=_rp_admin_kb())
            except Exception:
                pass
        elif call.data == "rq_home":
            bot.answer_callback_query(call.id)
            txt = ("⭐ <b>طلب تقييم الزبون</b>\n\nيُرسل للزبون بعد تسليم طلبه بدقيقة ونصف: نجوم فقط، "
                   "ويدخل مع تقييماتك الحقيقية في المتجر المصغّر.\n\n"
                   f"الحالة: {'✅ مفعّل' if _rp_on() else '⛔ مطفأ'}")
            try:
                bot.edit_message_text(txt, call.message.chat.id, call.message.message_id,
                                      parse_mode="HTML", reply_markup=_rp_admin_kb())
            except Exception:
                bot.send_message(call.message.chat.id, txt, parse_mode="HTML", reply_markup=_rp_admin_kb())
    except Exception as e:
        print(f"rate prompt admin failed: {e}")


def _rp_admin_kb():
    mk = InlineKeyboardMarkup()
    mk.add(InlineKeyboardButton(text="🧪 جرّب طلب التقييم (يصلك أنت)", callback_data="rq_test"))
    mk.add(InlineKeyboardButton(text=("⛔ إطفاء الطلب" if _rp_on() else "✅ تشغيل الطلب"), callback_data="rq_tog"))
    mk.add(InlineKeyboardButton(text="🔙 رجوع", callback_data="adm_home"))
    return mk


bot.callback_query_handler(func=lambda c: c.data in ("rq_test", "rq_tog", "rq_home"))(_rp_admin_cb)
bot.callback_query_handlers.insert(0, bot.callback_query_handlers.pop())

_rp_prev_admin_btn = _learn_admin_btn


def _learn_admin_btn(markup):
    try:
        _rp_prev_admin_btn(markup)
    except Exception as e:
        print(f"learn admin button failed: {e}")
    markup.add(InlineKeyboardButton(text="🧪 طلب تقييم الزبون", callback_data="rq_home"))


print("rateprompt.py loaded ✅")
