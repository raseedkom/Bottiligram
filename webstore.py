# -*- coding: utf-8 -*-
# webstore.py — المتجر المصغّر (Telegram Mini App): كل المنتجات بصورها ونجومها، بحث وفرز وكل اللغات.
# يُحمَّل من main.py داخل try/except: إن غاب الملف أو فشل يشتغل البوت عادياً.
# الأمان:
#  - لا يشتري شيئاً من الصفحة نفسها: الضغط على «اشترِ» يفتح نفس مسار الشراء داخل البوت (نفس الأزرار).
#  - يتحقق من هوية الزبون بتوقيع تيليجرام (initData) قبل أي ضغط، ويقبل فقط أزرار المنتجات المعروضة.
#  - لا يلمس التسليم ولا المحافظ ولا المورّد، ويقرأ فقط ما يعرضه المتجر أصلاً.
# أسماء مستعملة من main.py: app, bot, TOKEN, telebot, generate_store_keyboard, generate_gift_keyboard (إن وُجد),
#   find_product, tr, get_lang, STORE_GROUPS, _group_range, _vt_find_cell, _vt_price_txt, SUPPORTED_LANGS,
#   _maint_blocked_user, prof_get, wallet_avail_c, _money, kv_get, kv_set, ADMIN_CHAT_ID,
#   pi_get (من pimages.py إن وُجد)، _rv_load (من reviews.py إن وُجد)

import os as _ws_os
import io as _ws_io
import json as _ws_json_mod
import time as _ws_time
import hmac as _ws_hmac
import hashlib as _ws_hashlib
import threading as _ws_threading
import types as _ws_types
import urllib.parse as _ws_urlparse
import requests as _ws_requests
from flask import Flask as _WSFlask, request as _ws_rq, jsonify as _ws_jsonify, Response as _WSResp, redirect as _ws_redirect

WS_CACHE_TTL = 25
WS_AUTH_MAX_AGE = 24 * 3600
WS_PRESS_GAP = 2.0
WS_MENU_KEY = "rk:ws:menu"          # "0" = زر القائمة الافتراضي، غير ذلك = Web Store

_ws_cache = {}                       # lang -> (ts, items)
_ws_lock = _ws_threading.Lock()
_ws_last_press = {}
_ws_img_cache = {}                   # pk -> (fid, bytes, mime)
_ws_rv_cache = {"t": 0.0, "agg": {}}


def _ws_base_url():
    base = (_ws_os.environ.get("WEBAPP_URL") or _ws_os.environ.get("RENDER_EXTERNAL_URL")
            or "https://bottiligram-1eu.onrender.com").rstrip("/")
    return base + "/store"


# ---------------- التحقق من هوية تيليجرام ----------------
def _ws_verify(init_data):
    try:
        if not init_data:
            return None
        parsed = dict(_ws_urlparse.parse_qsl(init_data, keep_blank_values=True))
        got = parsed.pop("hash", None)
        if not got:
            return None
        check = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))
        secret = _ws_hmac.new(b"WebAppData", TOKEN.encode(), _ws_hashlib.sha256).digest()
        calc = _ws_hmac.new(secret, check.encode(), _ws_hashlib.sha256).hexdigest()
        if not _ws_hmac.compare_digest(calc, got):
            return None
        if _ws_time.time() - int(parsed.get("auth_date", "0") or 0) > WS_AUTH_MAX_AGE:
            return None
        user = _ws_json_mod.loads(parsed.get("user", "{}"))
        if not user.get("id"):
            return None
        return user
    except Exception:
        return None


# ---------------- جمع المنتجات من نفس أزرار المتجر ----------------
def _ws_num(txt):
    try:
        s = str(txt).replace("$", "").split("-")[0].replace("+", "").strip()
        return float(s)
    except Exception:
        return 0.0


def _ws_has_admin_img(pk):
    try:
        return pi_get(pk)
    except NameError:
        return None
    except Exception:
        return None


def _ws_img_for(pks):
    """رابط الصورة: صورة الأدمن أولاً (file_id عبر وسيط الخادم أو رابط)، ثم صورة المنتج نفسها."""
    for pk in pks:
        ref = _ws_has_admin_img(pk)
        if ref:
            if str(ref).startswith("http"):
                return str(ref)
            return "/store/img/" + _ws_urlparse.quote(str(pk), safe="")
    for pk in pks:
        try:
            p = find_product(pk)
        except Exception:
            p = None
        img = (p or {}).get("image")
        if img and str(img).startswith("http"):
            try:
                if str(img) == str(UNIFIED_IMAGE_URL):
                    continue
            except Exception:
                pass
            return str(img)
    return None


def _ws_agg_reviews():
    now = _ws_time.time()
    if now - _ws_rv_cache["t"] < 30:
        return _ws_rv_cache["agg"]
    agg = {}
    try:
        for r in _rv_load():
            a = agg.setdefault(r.get("pk"), [0, 0])
            a[0] += int(r.get("stars", 0))
            a[1] += 1
    except NameError:
        agg = {}
    except Exception:
        agg = _ws_rv_cache["agg"]
    _ws_rv_cache["agg"] = agg
    _ws_rv_cache["t"] = now
    return agg


def _ws_rating(pks):
    agg = _ws_agg_reviews()
    s = n = 0
    for pk in pks:
        a = agg.get(pk)
        if a:
            s += a[0]
            n += a[1]
    if not n:
        return None, 0
    return round(s / n, 1), n


def _ws_stock_n(v):
    if v == "♾️":
        return -1
    try:
        return int(v)
    except Exception:
        return 0


def _ws_item_from_cb(cb, lang, page):
    oos = cb.startswith("oos_")
    # مجموعة منتجات المورّد
    key = None
    if cb.startswith("vgrp_"):
        key = cb[5:]
    elif cb.startswith("oos_vg_"):
        key = cb[7:]
    if key is not None:
        cell = _vt_find_cell(key)
        if not cell:
            return None
        _k, title, its = cell
        ins = [p for p in its if p["stock"] > 0] or its
        stock = sum(p["stock"] for p in its)
        price = _vt_price_txt(ins)
        pks = [p["id"] for p in its]
        return {"cb": cb, "name": title, "icon": its[0].get("icon", ""), "price": price, "pnum": _ws_num(price),
                "stock": stock, "oos": oos or stock <= 0, "sec": page, "pks": pks}
    # مجموعة منتجاتك
    gid = None
    if cb == "oos_netflix" or cb == "grp_netflix":
        gid = "netflix"
    elif cb.startswith("grp_"):
        gid = cb[4:]
    elif cb.startswith("oos_grp_"):
        gid = cb[8:]
    if gid is not None:
        g = STORE_GROUPS.get(gid)
        if not g:
            return None
        lo, hi, stock = _group_range(gid)
        price = lo if lo == hi else f"{lo} - {hi}"
        sn = _ws_stock_n(stock)
        return {"cb": cb, "name": g["name"], "icon": g.get("icon", ""), "price": price, "pnum": _ws_num(lo),
                "stock": sn, "oos": oos or sn == 0, "sec": page, "pks": list(g["members"])}
    # منتج مفرد
    pid = None
    if cb.startswith("buy_"):
        pid = cb[4:]
    elif cb.startswith("oos_"):
        pid = cb[4:]
    if pid:
        p = find_product(pid)
        if not p or p.get("type") == "separator":
            return None
        sn = _ws_stock_n(p.get("stock"))
        return {"cb": cb, "name": tr(p, "name", lang), "icon": p.get("icon", ""), "price": p.get("price", ""),
                "pnum": _ws_num(p.get("price", "0")), "stock": sn, "oos": oos or sn == 0, "sec": page, "pks": [pid]}
    return None


def _ws_collect(lang):
    items, seen = [], set()
    pages = [("subs", generate_store_keyboard)]
    try:
        pages.append(("gifts", generate_gift_keyboard))
    except NameError:
        pass
    for page, gen in pages:
        try:
            mk = gen(lang)
        except Exception as e:
            print(f"webstore collect {page} failed: {e}")
            continue
        for row in mk.keyboard:
            for b in row:
                cb = getattr(b, "callback_data", "") or ""
                if cb in seen:
                    continue
                try:
                    it = _ws_item_from_cb(cb, lang, page)
                except Exception as e:
                    print(f"webstore item {cb} failed: {e}")
                    it = None
                if it:
                    seen.add(cb)
                    items.append(it)
    out = []
    for it in items:
        pks = it.pop("pks")
        avg, n = _ws_rating(pks)
        it["img"] = _ws_img_for(pks)
        it["rating"] = avg
        it["rn"] = n
        it["name"] = str(it["name"]).replace("‎", "").strip()
        out.append(it)
    return out


def _ws_items(lang):
    now = _ws_time.time()
    with _ws_lock:
        c = _ws_cache.get(lang)
        if c and now - c[0] < WS_CACHE_TTL:
            return c[1]
    items = _ws_collect(lang)
    with _ws_lock:
        _ws_cache[lang] = (now, items)
    return items


# ---------------- الخادم (تطبيق Flask مستقل يُدمَج في التطبيق الأصلي دون المساس به) ----------------
_ws_app = _WSFlask("webstore")


@_ws_app.route("/store")
def ws_page():
    r = _WSResp(_WS_HTML, mimetype="text/html")
    r.headers["Cache-Control"] = "no-store"
    return r


@_ws_app.route("/store/api/list", methods=["POST"])
def ws_api_list():
    data = _ws_rq.get_json(silent=True) or {}
    user = _ws_verify(data.get("initData", ""))
    lang = "ar"
    if user:
        lang = get_lang(user["id"])
    else:
        q = str(data.get("lang") or "ar")
        lang = q if q in SUPPORTED_LANGS else "ar"
    maint = False
    bal = None
    if user:
        try:
            maint = bool(_maint_blocked_user(_ws_types.SimpleNamespace(id=user["id"])))
        except Exception:
            maint = False
        try:
            bal = "$" + _money(wallet_avail_c(prof_get(user["id"])))
        except Exception:
            bal = None
    items = [] if maint else _ws_items(lang)
    return _ws_jsonify({"ok": True, "auth": bool(user), "lang": lang, "maint": maint, "balance": bal, "items": items})


def _ws_make_user(u):
    try:
        return telebot.types.User(id=int(u["id"]), is_bot=False, first_name=u.get("first_name") or "",
                                  last_name=u.get("last_name"), username=u.get("username"),
                                  language_code=u.get("language_code"))
    except Exception:
        return _ws_types.SimpleNamespace(id=int(u["id"]), is_bot=False, first_name=u.get("first_name") or "",
                                         last_name=u.get("last_name"), username=u.get("username"),
                                         language_code=u.get("language_code"), full_name=u.get("first_name") or "")


def _ws_do_press(u, cb):
    uid = int(u["id"])
    try:
        ph = bot.send_message(uid, "⏳")
        call = _ws_types.SimpleNamespace(id="qb", data=cb, from_user=_ws_make_user(u), message=ph,
                                         chat_instance="webstore", inline_message_id=None)
        for h in list(bot.callback_query_handlers):
            try:
                ok = bot._test_message_handler(h, call)
            except Exception:
                f = (h.get("filters") or {}).get("func")
                ok = (f is None) or bool(f(call))
            if ok:
                h["function"](call)
                break
    except Exception as e:
        print(f"webstore press failed: {e}")


@_ws_app.route("/store/api/press", methods=["POST"])
def ws_api_press():
    data = _ws_rq.get_json(silent=True) or {}
    user = _ws_verify(data.get("initData", ""))
    if not user:
        return _ws_jsonify({"ok": False, "err": "auth"}), 401
    cb = str(data.get("cb") or "")
    lang = get_lang(user["id"])
    allowed = {it["cb"] for it in _ws_items(lang)} | {"pf_wallet"}
    if cb not in allowed:
        return _ws_jsonify({"ok": False, "err": "bad"}), 400
    now = _ws_time.time()
    last = _ws_last_press.get(user["id"], 0)
    if now - last < WS_PRESS_GAP:
        return _ws_jsonify({"ok": False, "err": "slow"}), 429
    _ws_last_press[user["id"]] = now
    _ws_threading.Thread(target=_ws_do_press, args=(user, cb), daemon=True).start()
    return _ws_jsonify({"ok": True})


@_ws_app.route("/store/img/<path:pk>")
def ws_img(pk):
    pk = _ws_urlparse.unquote(pk)
    try:
        ref = pi_get(pk)
    except Exception:
        ref = None
    if not ref:
        return ("", 404)
    if str(ref).startswith("http"):
        return _ws_redirect(str(ref), code=302)
    c = _ws_img_cache.get(pk)
    if c and c[0] == ref:
        data, mime = c[1], c[2]
    else:
        try:
            f = bot.get_file(ref)
            r = _ws_requests.get(f"https://api.telegram.org/file/bot{TOKEN}/{f.file_path}", timeout=20)
            r.raise_for_status()
            data = r.content
            low = str(f.file_path).lower()
            mime = "image/png" if low.endswith(".png") else ("image/webp" if low.endswith(".webp") else "image/jpeg")
        except Exception as e:
            print(f"webstore image fetch failed: {e}")
            return ("", 502)
        if len(_ws_img_cache) > 60:
            _ws_img_cache.pop(next(iter(_ws_img_cache)), None)
        _ws_img_cache[pk] = (ref, data, mime)
    resp = _WSResp(data, mimetype=mime)
    resp.headers["Cache-Control"] = "public, max-age=3600"
    return resp


# ---------------- ربط المسارات بالتطبيق الأصلي (دون إضافة routes بعد بدء الخادم) ----------------
_ws_orig_wsgi = app.wsgi_app


def _ws_wsgi(environ, start_response):
    if str(environ.get("PATH_INFO", "")).startswith("/store"):
        return _ws_app(environ, start_response)
    return _ws_orig_wsgi(environ, start_response)


app.wsgi_app = _ws_wsgi


# ---------------- زر «Web Store» بجانب خانة الكتابة ----------------
def _ws_menu_on():
    """True = الزر لكل الزبائن (الإطلاق). الافتراضي: مطفأ → الزر للأدمن فقط في الكيبورد السفلي."""
    try:
        return str(kv_get(WS_MENU_KEY)) == "1"
    except Exception:
        return False


def _ws_apply_menu():
    for _ in range(4):
        try:
            if _ws_menu_on():
                bot.set_chat_menu_button(menu_button=telebot.types.MenuButtonWebApp(
                    "🛍️ Web Store", telebot.types.WebAppInfo(url=_ws_base_url())))
            else:
                bot.set_chat_menu_button(menu_button=telebot.types.MenuButtonCommands())
            print("webstore menu button set ✅")
            return
        except Exception as e:
            print(f"webstore menu button failed: {e}")
            _ws_time.sleep(6)


def ws_command(message):
    try:
        if str(message.chat.id) != str(ADMIN_CHAT_ID):
            return
        parts = (message.text or "").split()
        arg = parts[1].lower() if len(parts) > 1 else ""
        if arg not in ("on", "off"):
            bot.send_message(message.chat.id,
                             f"🛍️ المتجر المصغّر: {'✅ ظاهر للجميع' if _ws_menu_on() else '🔒 للأدمن فقط'}\n\n"
                             "/webmenu on — يظهر زر Web Store لكل الزبائن (الإطلاق)\n/webmenu off — للأدمن فقط (زر في الكيبورد السفلي)\n\n"
                             f"🔗 {_ws_base_url()}")
            return
        kv_set(WS_MENU_KEY, "1" if arg == "on" else "0")
        _ws_apply_menu()
        bot.send_message(message.chat.id, "✅ Web Store ظاهر الآن لكل الزبائن" if arg == "on" else "🔒 Web Store للأدمن فقط (اضغط «تحديث» ليظهر الزر في الكيبورد)")
    except Exception as e:
        print(f"webmenu command failed: {e}")


# زر Web Store في الكيبورد السفلي للأدمن فقط (مكان مستقل، ولا يمس زر قائمة الأوامر)
try:
    _ws_orig_persist = send_persistent_menu

    def send_persistent_menu(chat_id, lang):
        try:
            if str(chat_id) == str(ADMIN_CHAT_ID):
                kb = build_reply_keyboard(lang)
                kb.row(telebot.types.KeyboardButton("🛍️ Web Store", web_app=telebot.types.WebAppInfo(url=_ws_base_url())))
                bot.send_message(chat_id, t(lang, "menu_hint"), reply_markup=kb)
                return
        except Exception as e:
            print(f"webstore admin keyboard failed: {e}")
        return _ws_orig_persist(chat_id, lang)
except NameError:
    pass


bot.message_handler(commands=["webmenu"])(ws_command)
bot.message_handlers.insert(0, bot.message_handlers.pop())

_ws_threading.Thread(target=_ws_apply_menu, daemon=True).start()


# ---------------- واجهة الصفحة ----------------
_WS_HTML = r'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>RASEEDKOM Store</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
:root{--bg:#0e1621;--card:#17212b;--card2:#1e2c3a;--txt:#e9eef5;--mut:#8b9bb0;--acc:#3b82f6;--ok:#22c55e;--bad:#ef4444;--star:#fbbf24;--line:#243447}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{margin:0;background:var(--bg);color:var(--txt);font-family:system-ui,-apple-system,"Segoe UI",Roboto,Tahoma,sans-serif}
body{padding:0 14px 28px;min-height:100vh}
.top{position:sticky;top:0;z-index:5;background:var(--bg);padding:12px 0 8px}
.hdr{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:10px}
.brand{display:flex;align-items:center;gap:10px;min-width:0}
.logo{width:42px;height:42px;border-radius:12px;background:linear-gradient(135deg,#6366f1,#8b5cf6);display:grid;place-items:center;font-size:22px;flex:none}
.brand b{display:block;font-size:17px}
.brand span{font-size:12px;color:var(--mut)}
.wallet{display:flex;gap:6px;flex:none}
.pill{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:8px 12px;font-weight:700;font-size:14px;color:var(--ok);cursor:pointer;white-space:nowrap}
.pill.btn{background:var(--acc);color:#fff;border-color:var(--acc)}
.search{position:relative}
.search input{width:100%;background:var(--card);border:1px solid var(--line);color:var(--txt);border-radius:14px;padding:13px 40px;font-size:15px;outline:none}
.search input:focus{border-color:var(--acc)}
.search i{position:absolute;top:50%;transform:translateY(-50%);inset-inline-start:14px;font-style:normal;opacity:.6}
.chips{display:flex;gap:8px;overflow-x:auto;padding:12px 0 4px;scrollbar-width:none}
.chips::-webkit-scrollbar{display:none}
.chip{flex:none;background:var(--card);border:1px solid var(--line);color:var(--txt);border-radius:999px;padding:9px 16px;font-size:14px;cursor:pointer}
.chip.on{background:var(--acc);border-color:var(--acc);color:#fff}
.bar{display:flex;gap:8px;align-items:center;padding:6px 0}
.bar select{flex:1;background:var(--card);border:1px solid var(--line);color:var(--txt);border-radius:12px;padding:10px;font-size:14px}
.bar label{display:flex;align-items:center;gap:6px;font-size:13px;color:var(--mut);white-space:nowrap}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:8px}
@media(min-width:620px){.grid{grid-template-columns:repeat(3,1fr)}}
.card{background:var(--card);border:1px solid var(--line);border-radius:18px;overflow:hidden;display:flex;flex-direction:column;cursor:pointer;transition:transform .12s}
.card:active{transform:scale(.98)}
.card.out{opacity:.62}
.img{position:relative;aspect-ratio:16/10;background:linear-gradient(135deg,#1b2a3b,#233649);display:grid;place-items:center;overflow:hidden}
.img img{width:100%;height:100%;object-fit:cover;display:block}
.img .emo{font-size:46px}
.badge{position:absolute;top:8px;inset-inline-end:8px;font-size:11px;font-weight:700;border-radius:999px;padding:4px 9px;background:rgba(15,25,36,.85);border:1px solid;backdrop-filter:blur(4px)}
.badge.ok{color:var(--ok);border-color:#1f6b3d}
.badge.no{color:var(--bad);border-color:#7a2a2a}
.info{padding:10px 12px 12px;display:flex;flex-direction:column;gap:6px;flex:1}
.name{font-weight:700;font-size:14px;line-height:1.35;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;min-height:2.7em}
.rate{font-size:12px;color:var(--mut);display:flex;align-items:center;gap:4px}
.rate b{color:var(--star)}
.rate .new{background:#1f3a5f;color:#9cc4ff;border-radius:6px;padding:2px 7px;font-size:11px;font-weight:600}
.row{display:flex;align-items:center;justify-content:space-between;margin-top:auto;gap:8px}
.price{font-weight:800;font-size:16px}
.add{width:36px;height:36px;border-radius:11px;background:var(--acc);color:#fff;border:0;font-size:22px;line-height:1;cursor:pointer;flex:none}
.card.out .add{background:#2b3a4b;color:#7d8da1}
.empty,.note{text-align:center;color:var(--mut);padding:40px 10px;font-size:15px}
.toast{position:fixed;bottom:22px;left:50%;transform:translateX(-50%);background:#0b1220;border:1px solid var(--line);color:var(--txt);padding:11px 18px;border-radius:12px;font-size:14px;opacity:0;pointer-events:none;transition:.2s;z-index:20}
.toast.show{opacity:1}
.skel{height:200px;border-radius:18px;background:linear-gradient(90deg,var(--card),var(--card2),var(--card));background-size:200% 100%;animation:sk 1.2s infinite}
@keyframes sk{to{background-position:-200% 0}}
</style>
</head>
<body>
<div class="top">
  <div class="hdr">
    <div class="brand"><div class="logo">🛍️</div><div><b>RASEEDKOM</b><span id="sub"></span></div></div>
    <div class="wallet"><div class="pill" id="bal" style="display:none"></div><div class="pill btn" id="walletBtn"></div></div>
  </div>
  <div class="search"><i>🔎</i><input id="q" type="search" autocomplete="off"></div>
  <div class="chips" id="chips"></div>
  <div class="bar"><select id="sort"></select><label><input type="checkbox" id="stockOnly"><span id="stockLbl"></span></label></div>
</div>
<div class="grid" id="grid"></div>
<div class="toast" id="toast"></div>
<script>
const TG = window.Telegram && Telegram.WebApp;
if (TG) { try { TG.ready(); TG.expand(); } catch(e){} }
const I18N = {
 ar:{sub:"متجر رقمي · تسليم فوري",search:"ابحث عن منتج أو اشتراك...",all:"الكل",subs:"اشتراكات",gifts:"بطاقات الهدايا",
     s_def:"الترتيب الافتراضي",s_pa:"السعر: الأقل أولاً",s_pd:"السعر: الأعلى أولاً",s_nm:"الاسم",s_rt:"الأعلى تقييماً",
     only:"المتوفر فقط",instock:"متوفر",out:"نفد",inf:"متوفر",new:"جديد",wallet:"المحفظة",empty:"لا توجد نتائج",
     opening:"جارٍ فتح المنتج في البوت...",maint:"المتجر قيد التحديث حالياً، عد بعد قليل 🛠️",noauth:"افتح المتجر من داخل البوت لتتمكن من الشراء.",
     err:"تعذر التحميل، حاول مجدداً",slow:"لحظة... حاول بعد ثانيتين",fail:"تعذّر فتح المنتج"},
 fr:{sub:"Boutique numérique · livraison instantanée",search:"Rechercher un produit...",all:"Tout",subs:"Abonnements",gifts:"Cartes cadeaux",
     s_def:"Ordre par défaut",s_pa:"Prix croissant",s_pd:"Prix décroissant",s_nm:"Nom",s_rt:"Mieux notés",
     only:"En stock",instock:"En stock",out:"Épuisé",inf:"Disponible",new:"Nouveau",wallet:"Portefeuille",empty:"Aucun résultat",
     opening:"Ouverture du produit dans le bot...",maint:"Boutique en maintenance, revenez bientôt 🛠️",noauth:"Ouvrez la boutique depuis le bot pour acheter.",
     err:"Chargement impossible, réessayez",slow:"Un instant... réessayez dans 2 secondes",fail:"Impossible d'ouvrir le produit"},
 en:{sub:"Digital store · instant delivery",search:"Search products...",all:"All",subs:"Subscriptions",gifts:"Gift cards",
     s_def:"Default order",s_pa:"Price: low to high",s_pd:"Price: high to low",s_nm:"Name",s_rt:"Top rated",
     only:"In stock only",instock:"In Stock",out:"Sold Out",inf:"Available",new:"New",wallet:"Wallet",empty:"No results",
     opening:"Opening the product in the bot...",maint:"Store under maintenance, please come back soon 🛠️",noauth:"Open the store from inside the bot to buy.",
     err:"Couldn't load, please retry",slow:"One moment... try again in 2 seconds",fail:"Couldn't open the product"}
};
let L = "ar", T = I18N.ar, ITEMS = [], AUTH = false, CAT = "all";
const $ = id => document.getElementById(id);
function toast(m){const t=$("toast");t.textContent=m;t.classList.add("show");clearTimeout(toast._t);toast._t=setTimeout(()=>t.classList.remove("show"),2200)}
function applyLang(l){
  L = I18N[l] ? l : "ar"; T = I18N[L];
  document.documentElement.lang = L; document.documentElement.dir = L==="ar" ? "rtl" : "ltr";
  $("sub").textContent = T.sub; $("q").placeholder = T.search; $("walletBtn").textContent = "💳 " + T.wallet;
  $("stockLbl").textContent = T.only;
  const s = $("sort"); const cur = s.value || "def";
  s.innerHTML = [["def",T.s_def],["pa",T.s_pa],["pd",T.s_pd],["nm",T.s_nm],["rt",T.s_rt]].map(o=>`<option value="${o[0]}">${o[1]}</option>`).join("");
  s.value = cur;
  const ch = [["all",T.all],["subs",T.subs],["gifts",T.gifts]];
  $("chips").innerHTML = ch.map(c=>`<div class="chip ${CAT===c[0]?"on":""}" data-c="${c[0]}">${c[1]}</div>`).join("");
  $("chips").querySelectorAll(".chip").forEach(e=>e.onclick=()=>{CAT=e.dataset.c;applyLang(L);render()});
}
function stars(it){
  if(it.rating==null) return `<span class="new">🆕 ${T.new}</span>`;
  return `<b>★</b> ${it.rating.toFixed(1)} <span>(${it.rn})</span>`;
}
function render(){
  const q = $("q").value.trim().toLowerCase(), so = $("sort").value, only = $("stockOnly").checked;
  let list = ITEMS.filter(it => (CAT==="all"||it.sec===CAT) && (!q || it.name.toLowerCase().includes(q)) && (!only || !it.oos));
  const idx = new Map(ITEMS.map((x,i)=>[x.cb,i]));
  if(so==="pa") list.sort((a,b)=>a.pnum-b.pnum);
  else if(so==="pd") list.sort((a,b)=>b.pnum-a.pnum);
  else if(so==="nm") list.sort((a,b)=>a.name.localeCompare(b.name));
  else if(so==="rt") list.sort((a,b)=>(b.rating||0)-(a.rating||0)||b.rn-a.rn);
  else list.sort((a,b)=>idx.get(a.cb)-idx.get(b.cb));
  const g = $("grid");
  if(!list.length){ g.innerHTML = `<div class="empty" style="grid-column:1/-1">${T.empty}</div>`; return; }
  g.innerHTML = "";
  list.forEach(it=>{
    const c = document.createElement("div"); c.className = "card" + (it.oos?" out":"");
    const img = document.createElement("div"); img.className = "img";
    if(it.img){
      const im = new Image(); im.loading = "lazy"; im.alt = ""; im.src = it.img;
      im.onerror = ()=>{ im.remove(); const e=document.createElement("div"); e.className="emo"; e.textContent=it.icon||"📦"; img.prepend(e); };
      img.appendChild(im);
    } else { const e=document.createElement("div"); e.className="emo"; e.textContent=it.icon||"📦"; img.appendChild(e); }
    const b = document.createElement("div"); b.className = "badge " + (it.oos?"no":"ok");
    b.textContent = it.oos ? ("● "+T.out) : (it.stock<0 ? ("● "+T.inf) : ("● "+T.instock+" ("+it.stock+")"));
    img.appendChild(b);
    const info = document.createElement("div"); info.className = "info";
    const nm = document.createElement("div"); nm.className = "name"; nm.textContent = it.name;
    const rt = document.createElement("div"); rt.className = "rate"; rt.innerHTML = stars(it);
    const row = document.createElement("div"); row.className = "row";
    const pr = document.createElement("div"); pr.className = "price"; pr.textContent = it.price;
    const ad = document.createElement("button"); ad.className = "add"; ad.textContent = "+";
    row.append(pr, ad); info.append(nm, rt, row); c.append(img, info);
    c.onclick = ()=>press(it.cb);
    g.appendChild(c);
  });
}
async function api(path, body){
  const r = await fetch(path,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(Object.assign({initData:TG?TG.initData:""},body||{}))});
  let j = {}; try{ j = await r.json(); }catch(e){}
  return {status:r.status, j};
}
let busy = false;
async function press(cb){
  if(!AUTH){ toast(T.noauth); return; }
  if(busy) return; busy = true;
  try{
    const {status,j} = await api("/store/api/press",{cb});
    if(status===200 && j.ok){ toast(T.opening); try{TG.HapticFeedback.impactOccurred("light")}catch(e){} setTimeout(()=>{ try{TG.close()}catch(e){} },450); }
    else if(status===429){ toast(T.slow); }
    else toast(T.fail);
  }catch(e){ toast(T.fail); }
  setTimeout(()=>busy=false,900);
}
async function load(){
  $("grid").innerHTML = '<div class="skel"></div><div class="skel"></div><div class="skel"></div><div class="skel"></div>';
  try{
    const {j} = await api("/store/api/list",{lang:(TG&&TG.initDataUnsafe&&TG.initDataUnsafe.user&&TG.initDataUnsafe.user.language_code)||"ar"});
    if(!j.ok) throw 0;
    AUTH = !!j.auth; applyLang(j.lang);
    if(j.balance){ $("bal").style.display=""; $("bal").textContent = j.balance; }
    if(j.maint){ $("grid").innerHTML = `<div class="note" style="grid-column:1/-1">${T.maint}</div>`; return; }
    ITEMS = j.items || []; render();
    if(!AUTH) toast(T.noauth);
  }catch(e){ applyLang("ar"); $("grid").innerHTML = `<div class="note" style="grid-column:1/-1">${T.err}</div>`; }
}
$("q").addEventListener("input", render);
$("sort").addEventListener("change", render);
$("stockOnly").addEventListener("change", render);
$("walletBtn").onclick = ()=>press("pf_wallet");
$("bal").onclick = ()=>press("pf_wallet");
if(TG){ try{ TG.setHeaderColor(getComputedStyle(document.documentElement).getPropertyValue("--bg").trim()||"#0e1621"); }catch(e){} }
applyLang("ar"); load();
</script>
</body>
</html>
'''

print("webstore.py loaded ✅")
