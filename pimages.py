# -*- coding: utf-8 -*-
# pimages.py — صور المنتجات (الأدمن يضيف صورة لأي منتج: صورة تُرسلها أو رابط)
# يُحمَّل من main.py داخل try/except: إن غاب الملف أو فشل يشتغل البوت عادياً.
# - تُخزَّن الصور في Redis فقط (file_id أو رابط) ولا يُلمس الشراء/التسليم/المحافظ/المورّد.
# - صفحة المنتج في البوت تستعمل الصورة المضافة بدل الصورة الافتراضية (عبر send_card).
# أسماء مستعملة من main.py: bot, ADMIN_CHAT_ID, InlineKeyboardButton, InlineKeyboardMarkup,
#   kv_get, kv_set, products, _VT_PRODS, send_card, _learn_admin_btn

import json as _pi_json
import time as _pi_time
import html as _pi_html

PI_KEY = "rk:img:map"          # {pk: {"fid":..., "url":..., "name":...}}
PI_STATE_TTL = 900
PI_CACHE_TTL = 30

_pi_state = {}
_pi_cache = {"t": 0.0, "map": {}}


# ---------------- تخزين ----------------
def _pi_load(force=False):
    if not force and _pi_time.time() - _pi_cache["t"] < PI_CACHE_TTL:
        return _pi_cache["map"]
    raw = kv_get(PI_KEY)
    try:
        data = _pi_json.loads(raw) if raw else {}
        if not isinstance(data, dict):
            data = {}
    except Exception:
        data = {}
    _pi_cache["map"] = data
    _pi_cache["t"] = _pi_time.time()
    return data


def _pi_save(data):
    kv_set(PI_KEY, _pi_json.dumps(data, ensure_ascii=False))
    _pi_cache["map"] = data
    _pi_cache["t"] = _pi_time.time()


def pi_get(pk):
    """الصورة المحفوظة لمنتج (file_id أو رابط) أو None. للاستعمال لاحقاً في الـMini App."""
    try:
        e = _pi_load().get(str(pk))
    except Exception:
        return None
    if not e:
        return None
    return e.get("fid") or e.get("url")


# ---------------- مساعدات ----------------
def _pi_is_admin_id(uid):
    return str(uid) == str(ADMIN_CHAT_ID)


def _pi_esc(s):
    return _pi_html.escape(str(s or ""), quote=False)


def _pi_get_state(uid):
    st = _pi_state.get(uid)
    if not st:
        return None
    if _pi_time.time() - st.get("ts", 0) > PI_STATE_TTL:
        _pi_state.pop(uid, None)
        return None
    return st


def _pi_set_state(uid, **kw):
    st = _pi_state.get(uid) or {}
    st.update(kw)
    st["ts"] = _pi_time.time()
    _pi_state[uid] = st
    return st


def _pi_clear(uid):
    _pi_state.pop(uid, None)


def _pi_show(chat_id, msg_id, text, markup):
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
        print(f"pimages show failed: {e}")


def _pi_kb(*rows):
    mk = InlineKeyboardMarkup()
    for r in rows:
        mk.row(*[InlineKeyboardButton(text=t_, callback_data=cb) for (t_, cb) in r])
    return mk


def _pi_candidates():
    out, seen = [], set()
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
        print(f"pimages own products failed: {e}")
    try:
        for pid, p in list(_VT_PRODS.items()):
            nm = str(p.get("name", "")).strip()
            if nm and str(pid) not in seen:
                seen.add(str(pid))
                out.append((str(pid), nm))
    except Exception as e:
        print(f"pimages supplier products failed: {e}")
    return out


def _pi_search(query, limit=8):
    toks = [w for w in str(query).lower().split() if w]
    if not toks:
        return []
    res = []
    for pk, nm in _pi_candidates():
        if all(w in nm.lower() for w in toks):
            res.append((pk, nm))
        if len(res) >= limit:
            break
    return res


def _pi_free_key(name):
    base = "".join(ch if ch.isalnum() else "_" for ch in name.lower()).strip("_")
    return "free_" + (base[:40] or "x")


# ---------------- الشاشات ----------------
def _pi_home(chat_id, msg_id=None):
    try:
        n = len(_pi_load(force=True))
    except Exception:
        n = "?"
    text = (
        "🖼️ <b>صور المنتجات</b>\n\n"
        f"عدد المنتجات التي لها صورة مضافة: <b>{n}</b>\n\n"
        "اختر منتجاً وأرسل له صورة (أو رابط صورة). تظهر الصورة في صفحة المنتج داخل البوت، "
        "وستُستعمل لاحقاً في المتجر المصغّر."
    )
    mk = _pi_kb(
        [("➕ إضافة / تغيير صورة", "pi_add")],
        [("📋 المنتجات التي لها صور", "pi_list")],
        [("🔙 رجوع", "adm_home")],
    )
    _pi_show(chat_id, msg_id, text, mk)


def _pi_list_screen(chat_id, msg_id=None):
    try:
        data = _pi_load(force=True)
    except Exception:
        _pi_show(chat_id, msg_id, "⚠️ تعذّر قراءة الصور الآن (مشكلة تخزين).", _pi_kb([("🔙 رجوع", "pi_home")]))
        return
    if not data:
        _pi_show(chat_id, msg_id, "لا توجد صور مضافة بعد.", _pi_kb([("➕ إضافة صورة", "pi_add")], [("🔙 رجوع", "pi_home")]))
        return
    lines = ["📋 <b>المنتجات التي لها صور</b>\n"]
    rows = []
    for i, (pk, e) in enumerate(sorted(data.items(), key=lambda kv: str(kv[1].get("name", "")))):
        kind = "📷" if e.get("fid") else "🔗"
        lines.append(f"{kind} {_pi_esc(e.get('name', pk))}")
        if i < 20:
            rows.append([(f"🗑 {str(e.get('name', pk))[:30]}", f"pi_del_{pk[:40]}")])
    rows.append([("🔙 رجوع", "pi_home")])
    _pi_show(chat_id, msg_id, "\n".join(lines), _pi_kb(*rows))


# ---------------- رسائل الأدمن ----------------
def _pi_msg_filter(m):
    try:
        if not _pi_is_admin_id(m.chat.id):
            return False
        ct = getattr(m, "content_type", "text")
        txt = (getattr(m, "text", None) or "")
        if ct == "text" and txt.startswith("/"):
            _pi_clear(m.chat.id)
            return False
        st = _pi_get_state(m.chat.id)
        if not st:
            return False
        if st.get("step") == "q":
            return ct == "text"
        if st.get("step") == "img":
            return ct in ("text", "photo", "document")
        return False
    except Exception:
        return False


def _pi_try_preview(chat_id, ref, caption):
    """يرسل المعاينة؛ إن فشلت فالصورة/الرابط غير صالح."""
    try:
        bot.send_photo(chat_id, ref, caption=caption)
        return True
    except Exception as e:
        print(f"pimages preview failed: {e}")
        return False


def pi_input(m):
    uid = m.chat.id
    st = _pi_get_state(uid)
    if not st:
        return
    mid = st.get("mid")
    step = st.get("step")
    ct = getattr(m, "content_type", "text")
    if step == "q":
        txt = (m.text or "").strip()
        try:
            bot.delete_message(uid, m.message_id)
        except Exception:
            pass
        cands = _pi_search(txt)
        rows = [[(nm[:40], f"pi_pk_{i}")] for i, (pk, nm) in enumerate(cands)]
        rows.append([(f"➕ استعمل «{txt[:25]}» كاسم منتج", "pi_pk_free")])
        rows.append([("❌ إلغاء", "pi_home")])
        _pi_set_state(uid, step="pick", cands=cands, free=txt[:60])
        head = "اختر المنتج:" if cands else "لم أجد منتجاً بهذا الاسم. يمكنك استعماله كاسم منتج (لن يظهر في صفحة البوت، فقط في المتجر المصغّر):"
        _pi_show(uid, mid, f"1️⃣ {head}", _pi_kb(*rows))
        return
    if step == "img":
        ref = None
        kind = None
        if ct == "photo":
            ref = m.photo[-1].file_id
            kind = "fid"
        elif ct == "document":
            doc = getattr(m, "document", None)
            mime = (getattr(doc, "mime_type", "") or "")
            if doc and mime.startswith("image/"):
                ref = doc.file_id
                kind = "fid"
        elif ct == "text":
            txt = (m.text or "").strip()
            if txt.lower().startswith("https://") and " " not in txt:
                ref = txt
                kind = "url"
        if not ref:
            bot.send_message(uid, "⚠️ أرسل <b>صورة</b> (كصورة عادية) أو <b>رابطاً</b> يبدأ بـ https://", parse_mode="HTML")
            return
        name = st.get("pname") or "منتج"
        if not _pi_try_preview(uid, ref, f"🖼️ معاينة: {name}"):
            bot.send_message(uid, "⚠️ لم أستطع استعمال هذه الصورة/الرابط. جرّب صورة أخرى أو رابطاً مباشراً للصورة.", parse_mode="HTML")
            return
        try:
            data = dict(_pi_load(force=True))
            data[st["pk"]] = {kind: ref, "name": name}
            _pi_save(data)
        except Exception as e:
            print(f"pimages save failed: {e}")
            bot.send_message(uid, "⚠️ تعذّر الحفظ (مشكلة تخزين). جرّب بعد قليل.")
            return
        _pi_clear(uid)
        bot.send_message(
            uid, f"✅ تم حفظ صورة <b>{_pi_esc(name)}</b>.", parse_mode="HTML",
            reply_markup=_pi_kb([("➕ صورة أخرى", "pi_add")], [("📋 القائمة", "pi_list")], [("🔙 رجوع", "pi_home")]),
        )


# ---------------- الأزرار ----------------
def _pi_cb_filter(call):
    try:
        return (call.data or "").startswith("pi_") and _pi_is_admin_id(call.from_user.id)
    except Exception:
        return False


def pi_callback(call):
    uid = call.from_user.id
    cid = call.message.chat.id
    mid = call.message.message_id
    d = call.data or ""
    try:
        if d == "pi_home":
            _pi_clear(uid)
            _pi_home(cid, mid)
        elif d == "pi_list":
            _pi_clear(uid)
            _pi_list_screen(cid, mid)
        elif d == "pi_add":
            _pi_set_state(uid, step="q", mid=mid)
            _pi_show(cid, mid,
                     "➕ <b>إضافة صورة لمنتج</b>\n\n1️⃣ اكتب <b>جزءاً من اسم المنتج</b> (مثال: <code>chatgpt</code> أو <code>capcut</code>).",
                     _pi_kb([("❌ إلغاء", "pi_home")]))
        elif d.startswith("pi_pk_"):
            st = _pi_get_state(uid)
            if not st or st.get("step") != "pick":
                bot.answer_callback_query(call.id, "انتهت الجلسة، ابدأ من جديد.", show_alert=True)
                return
            if d == "pi_pk_free":
                nm = st.get("free") or "منتج"
                pk = _pi_free_key(nm)
            else:
                pk, nm = st["cands"][int(d.split("_")[-1])]
            _pi_set_state(uid, step="img", pk=pk, pname=nm, mid=mid)
            _pi_show(cid, mid,
                     f"✅ المنتج: <b>{_pi_esc(nm)}</b>\n\n2️⃣ أرسل الآن <b>الصورة</b> (كصورة عادية) أو <b>رابط</b> صورة يبدأ بـ https://",
                     _pi_kb([("❌ إلغاء", "pi_home")]))
        elif d.startswith("pi_del_"):
            pk = d[len("pi_del_"):]
            try:
                data = dict(_pi_load(force=True))
                key = next((k for k in data if k[:40] == pk), None)
                if key:
                    data.pop(key, None)
                    _pi_save(data)
            except Exception as e:
                print(f"pimages delete failed: {e}")
                bot.answer_callback_query(call.id, "⚠️ تعذّر الحذف الآن.", show_alert=True)
                return
            bot.answer_callback_query(call.id, "🗑 تم الحذف")
            _pi_list_screen(cid, mid)
            return
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"pimages callback error: {e}")
        try:
            bot.answer_callback_query(call.id, "⚠️ حدث خطأ، جرّب مرة أخرى.", show_alert=True)
        except Exception:
            pass


def _pi_clear_filter(call):
    try:
        if not (call.data or "").startswith("pi_") and _pi_is_admin_id(call.from_user.id):
            _pi_clear(call.from_user.id)
    except Exception:
        pass
    return False


# ---------------- التسجيل بأولوية أعلى ----------------
bot.message_handler(func=_pi_msg_filter, content_types=["text", "photo", "document"])(pi_input)
bot.message_handlers.insert(0, bot.message_handlers.pop())

bot.callback_query_handler(func=_pi_cb_filter)(pi_callback)
bot.callback_query_handlers.insert(0, bot.callback_query_handlers.pop())

bot.callback_query_handler(func=_pi_clear_filter)(lambda call: None)
bot.callback_query_handlers.insert(0, bot.callback_query_handlers.pop())


# ---------------- استعمال الصورة المضافة في صفحة المنتج داخل البوت ----------------
_pi_send_card_orig = send_card


def send_card(chat_id, product, caption, markup):
    try:
        ref = pi_get(product.get("id")) if isinstance(product, dict) else None
        if ref:
            product = dict(product)
            product["image"] = ref
    except Exception as e:
        print(f"pimages override skipped: {e}")
    return _pi_send_card_orig(chat_id, product, caption, markup)


# ---------------- زر لوحة الأدمن (يُضاف بعد الأزرار السابقة) ----------------
_pi_prev_admin_btn = _learn_admin_btn


def _learn_admin_btn(markup):
    try:
        _pi_prev_admin_btn(markup)
    except Exception as e:
        print(f"previous admin button failed: {e}")
    markup.add(InlineKeyboardButton(text="🖼️ صور المنتجات", callback_data="pi_home"))


print("pimages.py loaded ✅")
