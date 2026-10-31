# -*- coding: utf-8 -*-
# reviews.py — تقييمات الزبائن (الأدمن يضيف آراء حقيقية قالها زبائنه فعلاً)
# يُحمَّل من main.py داخل try/except: إن غاب الملف أو فشل يشتغل البوت عادياً.
# لا يلمس الشراء ولا التسليم ولا المحافظ ولا المورّد. خزّنت التقييمات في Redis فقط.
# أسماء مستعملة من main.py: bot, ADMIN_CHAT_ID, InlineKeyboardButton, InlineKeyboardMarkup,
#   kv_get, kv_set, products, _VT_PRODS, _learn_admin_btn

import json as _rv_json
import time as _rv_time
import html as _rv_html

RV_KEY = "rk:rev:all"          # قائمة JSON بكل التقييمات
RV_STATE_TTL = 900             # 15 دقيقة لحالة الإدخال
RV_SHOW_LAST = 8

_rv_state = {}                 # uid -> {"step":..., "ts":..., ...}


# ---------------- تخزين ----------------
def _rv_load():
    raw = kv_get(RV_KEY)
    if not raw:
        return []
    try:
        data = _rv_json.loads(raw)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _rv_save(items):
    kv_set(RV_KEY, _rv_json.dumps(items, ensure_ascii=False))


def rv_stats(pkey):
    """(المتوسط، العدد) لمنتج بمفتاحه. للاستعمال لاحقاً في الـMini App."""
    items = [r for r in _rv_load() if r.get("pk") == pkey]
    if not items:
        return (0.0, 0)
    return (round(sum(int(r.get("stars", 0)) for r in items) / len(items), 2), len(items))


def rv_list(pkey, limit=20):
    items = [r for r in _rv_load() if r.get("pk") == pkey]
    return sorted(items, key=lambda r: r.get("ts", 0), reverse=True)[:limit]


# ---------------- مساعدات ----------------
def _rv_is_admin_id(uid):
    return str(uid) == str(ADMIN_CHAT_ID)


def _rv_esc(s):
    return _rv_html.escape(str(s or ""), quote=False)


def _rv_who(letter):
    """الخصوصية: يُعرض الحرف الأول فقط (A***) أو «زبون»."""
    l = (letter or "").strip()[:1]
    return (_rv_esc(l.upper()) + "***") if l else "زبون"


def _rv_stars(n):
    n = max(0, min(5, int(n or 0)))
    return "⭐" * n + "☆" * (5 - n)


def _rv_get_state(uid):
    st = _rv_state.get(uid)
    if not st:
        return None
    if _rv_time.time() - st.get("ts", 0) > RV_STATE_TTL:
        _rv_state.pop(uid, None)
        return None
    return st


def _rv_set_state(uid, **kw):
    st = _rv_state.get(uid) or {}
    st.update(kw)
    st["ts"] = _rv_time.time()
    _rv_state[uid] = st
    return st


def _rv_clear(uid):
    _rv_state.pop(uid, None)


def _rv_show(chat_id, msg_id, text, markup):
    """يعدّل الرسالة إن أمكن وإلا يرسل جديدة."""
    if msg_id:
        try:
            bot.edit_message_text(text, chat_id, msg_id, parse_mode="HTML", reply_markup=markup)
            return
        except Exception as e:
            if "not modified" in str(e).lower():
                return
    try:
        bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)
    except Exception as e:
        print(f"reviews show failed: {e}")


def _rv_kb(*rows):
    mk = InlineKeyboardMarkup()
    for r in rows:
        mk.row(*[InlineKeyboardButton(text=t_, callback_data=cb) for (t_, cb) in r])
    return mk


# ---------------- بحث المنتجات ----------------
def _rv_candidates():
    """كل المنتجات المعروفة: (مفتاح, اسم). منتجاتك الخاصة + منتجات المورّد."""
    out = []
    seen = set()
    try:
        for p in products:
            if p.get("type") == "separator":
                continue
            pid = str(p.get("id", ""))
            nm = str(p.get("name", "")).strip()
            if pid and nm and pid not in seen:
                seen.add(pid)
                out.append((pid, nm))
    except Exception as e:
        print(f"reviews own products failed: {e}")
    try:
        for pid, p in list(_VT_PRODS.items()):
            nm = str(p.get("name", "")).strip()
            if nm and str(pid) not in seen:
                seen.add(str(pid))
                out.append((str(pid), nm))
    except Exception as e:
        print(f"reviews supplier products failed: {e}")
    return out


def _rv_search(query, limit=8):
    toks = [w for w in str(query).lower().split() if w]
    if not toks:
        return []
    res = []
    for pk, nm in _rv_candidates():
        low = nm.lower()
        if all(w in low for w in toks):
            res.append((pk, nm))
        if len(res) >= limit:
            break
    return res


def _rv_free_key(name):
    base = "".join(ch if ch.isalnum() else "_" for ch in name.lower()).strip("_")
    return "free_" + (base[:40] or "x")


# ---------------- الشاشات ----------------
def _rv_home(chat_id, msg_id=None):
    try:
        items = _rv_load()
    except Exception:
        items = None
    if items is None:
        total = "?"
    else:
        total = len(items)
    text = (
        "⭐ <b>تقييمات الزبائن</b>\n\n"
        f"عدد التقييمات المسجّلة: <b>{total}</b>\n\n"
        "هنا تضيف <b>تقييمات حقيقية</b> أعطاها زبائنك فعلاً (منتج + نجوم + أول حرف من اسمه للخصوصية).\n"
        "⚠️ أضف فقط ما قاله الزبون حقاً وبعدد النجوم الذي أعطاه."
    )
    mk = _rv_kb(
        [("➕ إضافة تقييم", "rv_add")],
        [("📋 التقييمات الحالية", "rv_list")],
        [("🔙 رجوع", "adm_home")],
    )
    _rv_show(chat_id, msg_id, text, mk)


def _rv_list_screen(chat_id, msg_id=None):
    try:
        items = _rv_load()
    except Exception:
        _rv_show(chat_id, msg_id, "⚠️ تعذّر قراءة التقييمات الآن (مشكلة تخزين). جرّب بعد قليل.", _rv_kb([("🔙 رجوع", "rv_home")]))
        return
    if not items:
        _rv_show(chat_id, msg_id, "لا توجد تقييمات بعد.\nاضغط «إضافة تقييم» لتبدأ.", _rv_kb([("➕ إضافة تقييم", "rv_add")], [("🔙 رجوع", "rv_home")]))
        return
    agg = {}
    for r in items:
        a = agg.setdefault(r.get("pk"), {"name": r.get("pname", "؟"), "sum": 0, "n": 0})
        a["sum"] += int(r.get("stars", 0))
        a["n"] += 1
    lines = ["📊 <b>ملخص المنتجات</b>"]
    for pk, a in sorted(agg.items(), key=lambda kv: -kv[1]["n"]):
        lines.append(f"• {_rv_esc(a['name'])}: <b>{a['sum'] / a['n']:.1f}</b>/5 ({a['n']})")
    last = sorted(items, key=lambda r: r.get("ts", 0), reverse=True)[:RV_SHOW_LAST]
    lines.append("\n🕘 <b>آخر التقييمات</b>")
    rows = []
    for r in last:
        lines.append(f"{_rv_stars(r.get('stars'))} — {_rv_esc(r.get('pname', ''))} — {_rv_who(r.get('name'))}")
        rows.append([(f"🗑 حذف: {str(r.get('pname', ''))[:18]} ({r.get('stars')}⭐)", f"rv_del_{r.get('id')}")])
    rows.append([("🔙 رجوع", "rv_home")])
    _rv_show(chat_id, msg_id, "\n".join(lines), _rv_kb(*rows))


def _rv_ask_product(chat_id, msg_id=None):
    text = (
        "➕ <b>إضافة تقييم حقيقي</b>\n\n"
        "1️⃣ اكتب <b>جزءاً من اسم المنتج</b> (مثال: <code>chatgpt</code> أو <code>apple</code> أو <code>canva</code>)."
    )
    _rv_show(chat_id, msg_id, text, _rv_kb([("❌ إلغاء", "rv_home")]))


def _rv_ask_stars(chat_id, msg_id, pname):
    text = f"✅ المنتج: <b>{_rv_esc(pname)}</b>\n\n2️⃣ كم نجمة أعطى الزبون؟"
    mk = _rv_kb(
        [(f"{i}⭐", f"rv_st_{i}") for i in (1, 2, 3, 4, 5)],
        [("❌ إلغاء", "rv_home")],
    )
    _rv_show(chat_id, msg_id, text, mk)


def _rv_ask_name(chat_id, msg_id=None):
    text = (
        "3️⃣ اكتب <b>أول حرف من اسم حساب الزبون</b> (حرف واحد فقط، للخصوصية)،\n"
        "أو اضغط «مجهول» ليظهر «زبون».\n"
        "🔒 لا تكتب اسمه كاملاً ولا معرّفه ولا رقمه."
    )
    _rv_show(chat_id, msg_id, text, _rv_kb([("👤 مجهول", "rv_skip_n")], [("❌ إلغاء", "rv_home")]))


def _rv_confirm(chat_id, msg_id, st):
    text = (
        "🔎 <b>راجع التقييم قبل الحفظ</b>\n\n"
        f"📦 المنتج: <b>{_rv_esc(st.get('pname'))}</b>\n"
        f"{_rv_stars(st.get('stars'))}\n"
        f"👤 {_rv_who(st.get('name'))}\n\n"
        "⚠️ تأكد أنه تقييم حقيقي لزبون فعلي."
    )
    mk = _rv_kb([("✅ حفظ", "rv_save"), ("❌ إلغاء", "rv_home")])
    _rv_show(chat_id, msg_id, text, mk)


# ---------------- معالجة الرسائل (نصوص الأدمن أثناء الإدخال) ----------------
def _rv_msg_filter(m):
    try:
        if getattr(m, "content_type", "text") != "text":
            return False
        if not _rv_is_admin_id(m.chat.id):
            return False
        txt = (m.text or "")
        if txt.startswith("/"):
            _rv_clear(m.chat.id)      # أي أمر يلغي الإدخال
            return False
        st = _rv_get_state(m.chat.id)
        return bool(st and st.get("step") in ("q", "n"))
    except Exception:
        return False


def rv_input(m):
    uid = m.chat.id
    st = _rv_get_state(uid)
    if not st:
        return
    txt = (m.text or "").strip()
    try:
        bot.delete_message(uid, m.message_id)
    except Exception:
        pass
    mid = st.get("mid")
    step = st.get("step")
    if step == "q":
        res = _rv_search(txt)
        cands = [(pk, nm) for pk, nm in res]
        rows = [[(f"{nm[:40]}", f"rv_pk_{i}")] for i, (pk, nm) in enumerate(cands)]
        rows.append([(f"➕ استعمل «{txt[:25]}» كاسم منتج", "rv_pk_free")])
        rows.append([("❌ إلغاء", "rv_home")])
        _rv_set_state(uid, step="pick", cands=cands, free=txt[:60])
        head = "اختر المنتج:" if cands else "لم أجد منتجاً بهذا الاسم. يمكنك استعماله كاسم منتج:"
        _rv_show(uid, mid, f"1️⃣ {head}", _rv_kb(*rows))
        return
    if step == "n":
        st = _rv_set_state(uid, name=txt[:1], step="confirm")
        _rv_confirm(uid, mid, st)
        return


# ---------------- معالجة الأزرار ----------------
def _rv_cb_filter(call):
    try:
        d = call.data or ""
        return d.startswith("rv_") and _rv_is_admin_id(call.from_user.id)
    except Exception:
        return False


def rv_callback(call):
    uid = call.from_user.id
    cid = call.message.chat.id
    mid = call.message.message_id
    d = call.data or ""
    try:
        if d == "rv_home":
            _rv_clear(uid)
            _rv_home(cid, mid)
        elif d == "rv_list":
            _rv_clear(uid)
            _rv_list_screen(cid, mid)
        elif d == "rv_add":
            _rv_set_state(uid, step="q", mid=mid)
            _rv_ask_product(cid, mid)
        elif d.startswith("rv_pk_"):
            st = _rv_get_state(uid)
            if not st or st.get("step") != "pick":
                bot.answer_callback_query(call.id, "انتهت الجلسة، ابدأ من جديد.", show_alert=True)
                return
            if d == "rv_pk_free":
                nm = st.get("free") or "منتج"
                pk = _rv_free_key(nm)
            else:
                i = int(d.split("_")[-1])
                pk, nm = st["cands"][i]
            _rv_set_state(uid, step="stars", pk=pk, pname=nm, mid=mid)
            _rv_ask_stars(cid, mid, nm)
        elif d.startswith("rv_st_"):
            st = _rv_get_state(uid)
            if not st or st.get("step") != "stars":
                bot.answer_callback_query(call.id, "انتهت الجلسة، ابدأ من جديد.", show_alert=True)
                return
            n = max(1, min(5, int(d.split("_")[-1])))
            _rv_set_state(uid, stars=n, step="n", mid=mid)
            _rv_ask_name(cid, mid)
        elif d == "rv_skip_n":
            st = _rv_get_state(uid)
            if not st:
                bot.answer_callback_query(call.id, "انتهت الجلسة، ابدأ من جديد.", show_alert=True)
                return
            st = _rv_set_state(uid, name="", step="confirm", mid=mid)
            _rv_confirm(cid, mid, st)
        elif d == "rv_save":
            st = _rv_get_state(uid)
            if not st or st.get("step") != "confirm":
                bot.answer_callback_query(call.id, "انتهت الجلسة، ابدأ من جديد.", show_alert=True)
                return
            try:
                items = _rv_load()
                items.append({
                    "id": str(int(_rv_time.time() * 1000)),
                    "pk": st.get("pk"),
                    "pname": st.get("pname"),
                    "stars": int(st.get("stars")),
                    "name": st.get("name") or "",
                    "ts": int(_rv_time.time()),
                    "src": "admin",
                })
                _rv_save(items)
            except Exception as e:
                print(f"reviews save failed: {e}")
                bot.answer_callback_query(call.id, "⚠️ تعذّر الحفظ (مشكلة تخزين). جرّب بعد قليل.", show_alert=True)
                return
            _rv_clear(uid)
            bot.answer_callback_query(call.id, "✅ تم حفظ التقييم")
            _rv_show(cid, mid, "✅ تم حفظ التقييم.", _rv_kb([("➕ إضافة آخر", "rv_add")], [("📋 التقييمات", "rv_list")], [("🔙 رجوع", "rv_home")]))
            return
        elif d.startswith("rv_del_"):
            rid = d[len("rv_del_"):]
            try:
                items = _rv_load()
                new = [r for r in items if str(r.get("id")) != rid]
                if len(new) != len(items):
                    _rv_save(new)
            except Exception as e:
                print(f"reviews delete failed: {e}")
                bot.answer_callback_query(call.id, "⚠️ تعذّر الحذف الآن.", show_alert=True)
                return
            bot.answer_callback_query(call.id, "🗑 تم الحذف")
            _rv_list_screen(cid, mid)
            return
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"reviews callback error: {e}")
        try:
            bot.answer_callback_query(call.id, "⚠️ حدث خطأ، جرّب مرة أخرى.", show_alert=True)
        except Exception:
            pass


def _rv_clear_filter(call):
    """أي زر آخر في لوحة الأدمن يلغي حالة الإدخال. لا يعالج شيئاً (يرجع False)."""
    try:
        if not (call.data or "").startswith("rv_") and _rv_is_admin_id(call.from_user.id):
            _rv_clear(call.from_user.id)
    except Exception:
        pass
    return False


# ---------------- التسجيل بأولوية أعلى ----------------
bot.message_handler(func=_rv_msg_filter, content_types=["text"])(rv_input)
bot.message_handlers.insert(0, bot.message_handlers.pop())

bot.callback_query_handler(func=_rv_cb_filter)(rv_callback)
bot.callback_query_handlers.insert(0, bot.callback_query_handlers.pop())

bot.callback_query_handler(func=_rv_clear_filter)(lambda call: None)
bot.callback_query_handlers.insert(0, bot.callback_query_handlers.pop())


# ---------------- زر لوحة الأدمن (يُضاف بعد زر learn إن وُجد) ----------------
_rv_prev_admin_btn = _learn_admin_btn


def _learn_admin_btn(markup):
    try:
        _rv_prev_admin_btn(markup)
    except Exception as e:
        print(f"learn admin button failed: {e}")
    markup.add(InlineKeyboardButton(text="⭐ تقييمات الزبائن", callback_data="rv_home"))


def _rv_cmd(m):
    try:
        if not _rv_is_admin_id(m.chat.id):
            return
        _rv_clear(m.chat.id)
        _rv_home(m.chat.id)
    except Exception as e:
        print(f"reviews command failed: {e}")


bot.message_handler(commands=["reviews", "addreview"])(_rv_cmd)
bot.message_handlers.insert(0, bot.message_handlers.pop())

print("reviews.py loaded ✅")
