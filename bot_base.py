from flask import Flask
import threading
import uuid

app = Flask('')

@app.route('/')
def home():
    return "I'm alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

threading.Thread(target=run).start()

import os
import re
import json
import html
import time
import hmac
import hashlib
import requests
import telebot
from decimal import Decimal, InvalidOperation
from urllib.parse import urlencode
from telebot.apihelper import ApiTelegramException
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

try:
    from telebot.types import BotCommand, BotCommandScopeChat
except ImportError:
    BotCommand = BotCommandScopeChat = None

try:
    from telebot.types import CopyTextButton  # زر النسخ الحقيقي (نسخة حديثة من المكتبة)
except ImportError:
    CopyTextButton = None

TOKEN = os.environ["BOT_TOKEN"]
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID", "8491461365")
bot = telebot.TeleBot(TOKEN)

# ========== بوت المراقبة (إشعارات مهمة فقط) ==========
MONITOR_BOT_TOKEN = os.environ.get("MONITOR_BOT_TOKEN", "")
MONITOR_CHAT_ID = os.environ.get("MONITOR_CHAT_ID", ADMIN_CHAT_ID)

BROADCAST_CHAT_ID = os.environ.get("BROADCAST_CHAT_ID", ADMIN_CHAT_ID)
BROADCAST_INTERVAL_SECONDS = int(os.environ.get("BROADCAST_INTERVAL_SECONDS", 1200))
USER_BROADCAST_INTERVAL_SECONDS = int(os.environ.get("USER_BROADCAST_INTERVAL_SECONDS", 7200))
USER_BROADCAST_ENABLED = os.environ.get("USER_BROADCAST_ENABLED", "1") == "1"
BOT_LINK = "https://t.me/RASEEDKOM_store_bot"
UNIFIED_IMAGE_URL = "https://i.postimg.cc/MpN8H2jq/IMG-3158"
MY_PRIVATE_CHAT_LINK = "https://t.me/Raseedkom"
CHANNEL_LINK = "https://t.me/+riEDwvUvQdxmMzU0"

SUPPORTED_LANGS = ("ar", "en", "fr")

# ========== بطاقات الهداية: القيم والأسعار ==========
GIFT_VARIANTS = {
    "apple_gift_tr": [
        ("10 TRY", "1.00"), ("50 TRY", "1.35"), ("100 TRY", "2.50"),
        ("150 TRY", "3.60"), ("200 TRY", "5.00"), ("250 TRY", "5.70"),
    ],
    "apple_gift_in": [
        ("100 INR", "1.40"), ("200 INR", "2.45"), ("250 INR", "3.05"),
        ("500 INR", "6.15"), ("1000 INR", "12.00"), ("1500 INR", "28.10"),
    ],
    "apple_gift_fr": [
        ("2 EUR", "2.45"), ("10 EUR", "12.00"), ("20 EUR", "23.65"),
        ("50 EUR", "59.00"), ("75 EUR", "89.00"), ("100 EUR", "116.22"),
    ],
}

def clean_gift_description(text):
    """يحذف قائمة أسعار القيم من وصف بطاقات الهداية (يبقى الوصف فقط)."""
    lines = [
        l for l in text.split("\n")
        if not ("Apple Gift Card" in l and "▶" in l) and not l.strip().startswith("🎁")
    ]
    out = "\n".join(lines)
    while "\n\n\n" in out:
        out = out.replace("\n\n\n", "\n\n")
    return out.strip()

# ========== إعدادات الدفع التلقائي ==========
BINANCE_PAY_ID = os.environ.get("BINANCE_PAY_ID", "878309128")  # معرف حسابك في Binance Pay
BINANCE_API_KEY = os.environ.get("BINANCE_API_KEY", "")
BINANCE_SECRET_KEY = os.environ.get("BINANCE_SECRET_KEY", "")
BINANCE_BASE_URL = os.environ.get("BINANCE_BASE_URL", "https://api.binance.com")
ACCEPTED_CURRENCIES = {"USDT"}

FAZER_API_KEY = os.environ.get("FAZER_API_KEY", "")
FAZER_BASE_URL = "https://api.fzr.cards/api/v2"
FAZER_CACHE_SECONDS = 900  # كاش الكتالوج: 15 دقيقة

INVOICE_TTL = 20 * 60        # صلاحية الفاتورة (20 دقيقة)
INVOICE_GRACE = 10 * 60      # مهلة إضافية لمن دفع في آخر لحظة
MAX_ATTEMPTS = 8             # أقصى عدد محاولات إرسال رقم عملية خلال 10 دقائق

# إذا لم يطابق البحث التلقائي بطاقة معينة، اكتب الربط هنا يدوياً
# (استعمل الأمر /fazer_catalog لمعرفة الأرقام). مثال:
# ("apple_gift_tr", "100 TRY"): {"category_id": "xxx", "card_id": "yyy"},
FAZER_MANUAL_MAP = {
}

# ========== Gemini: دفع وتسليم تلقائي (الروابط في Upstash) ==========
GEMINI_ID = "gemini_18m"
GEMINI_LINKS_KEY = "rk:gemini:links"   # قائمة الروابط في Upstash
GEMINI_UNIT_PRICE = Decimal("1.80")    # سعر الرابط الواحد
GEMINI_QTYS = (1, 2)                   # الأعداد المتاحة

GEMINI_TEXTS = {
    "ar": {
        "choose_qty": "🛒 اختر العدد الذي تريد شراءه",
        "out_of_stock": "❌ هذا المنتج نفد من المخزون حالياً.",
        "out": "❌ هذا المنتج نفد من المخزون حالياً.",
        "qty_left": "❌ المتوفر حالياً {n} فقط، اختر عدداً أقل.",
        "delivered": "✅ تم تأكيد الدفع!\n\n📧 إليك حسابك:\n—————————————\n\n{links}\n\n🛡️ الضمان: 0 يوم\n📌 احتفظ بهذه المعلومات في مكان آمن\n\n🙏 شكراً لشرائك!",
    },
    "en": {
        "choose_qty": "🛒 Choose the quantity you want to buy",
        "out_of_stock": "❌ This product is currently out of stock.",
        "out": "❌ This product is currently out of stock.",
        "qty_left": "❌ Only {n} available right now, choose a lower quantity.",
        "delivered": "✅ Payment confirmed!\n\n📧 Here is your account:\n—————————————\n\n{links}\n\n🛡️ Warranty: 0 days\n📌 Keep this information in a safe place\n\n🙏 Thank you for your purchase!",
    },
    "fr": {
        "choose_qty": "🛒 Choisissez la quantité à acheter",
        "out_of_stock": "❌ Ce produit est actuellement en rupture de stock.",
        "out": "❌ Ce produit est actuellement en rupture de stock.",
        "qty_left": "❌ Seulement {n} disponible(s) pour le moment, choisissez une quantité plus petite.",
        "delivered": "✅ Paiement confirmé !\n\n📧 Voici votre compte :\n—————————————\n\n{links}\n\n🛡️ Garantie : 0 jour\n📌 Conservez ces informations en lieu sûr\n\n🙏 Merci pour votre achat !",
    },
}

WALLET_PCT = 5         # مكافأة المحفظة على الشراء المدفوع مباشرة بـ Binance (وعلى /addpurchase)
GIFT_REWARD_PCT = 2    # مكافأة بطاقات الهداية
TOPUP_PID = "__topup__"            # معرّف فاتورة شحن المحفظة
TOPUP_AMOUNTS = (1, 5, 10, 20)     # أزرار الشحن السريع
TOPUP_MIN = Decimal("0.5")
TOPUP_MAX = Decimal("500")

WALLET_TEXTS = {
    "ar": {
        "btn_profile": "👤 الملف الشخصي",
        "btn_history": "🧾 سجل المشتريات",
        "btn_wallet": "💼 المحفظة",
        "btn_topup": "➕ شحن المحفظة",
        "btn_topup_other": "✏️ مبلغ آخر",
        "unavailable": "⚠️ الخدمة غير متاحة حالياً، حاول لاحقاً.",
        "profile": "👤 <b>ملفك الشخصي</b>\n\n🆔 المعرّف: <code>{id}</code>\n📛 الاسم: {name}\n📅 تاريخ الانضمام: {joined}\n🛒 إجمالي المشتريات: {buys}\n💵 إجمالي الإنفاق: ${spent}",
        "history": "🧾 <b>سجل المشتريات</b>\n\n{lines}\n\n✅ المكتملة: {done}\n❌ الملغاة: {canc}\n📊 نسبة النجاح: {pct}%",
        "by_product": "📦 المشتريات حسب المنتج:",
        "history_empty": "— لا توجد مشتريات بعد —",
        "wallet": "💼 <b>المحفظة</b>\n\n🎁 المكافآت: ${rewards}\n💳 الرصيد المشحون: ${topup}\n➖ المستخدم: ${used}\n✅ <b>الرصيد المتاح: ${avail}</b>\n\n🎁 مكافأة {pct}% على كل شراء مدفوع مباشرة بـ Binance ({gift_pct}% لبطاقات الهداية). الشحن والدفع من المحفظة لا يعطيان مكافأة.",
        "wallet_note": "ℹ️ لما يوصل رصيدك لقيمة منتج حاب تستبدل بيه، تواصل معانا في خانة الدعم (تسليم يدوي).",
        "topup_pick": "➕ <b>شحن المحفظة</b>\n\nاختر المبلغ الذي تريد شحنه (USDT):",
        "topup_other_prompt": "✏️ أرسل المبلغ الذي تريد شحنه بالدولار (من {min} إلى {max}).\nمثال: <code>7.5</code>",
        "topup_bad": "❌ مبلغ غير صالح. أرسل رقماً بين {min} و {max}.",
        "topup_name": "💳 شحن المحفظة",
        "topup_steps": "1️⃣ افتح Binance ← Pay ← إرسال\n2️⃣ ضع المعرف أعلاه وأرسل المبلغ بعملة <b>USDT</b>\n3️⃣ بعد الدفع انسخ <b>رقم العملية (Order ID)</b> وأرسله هنا في الشات\n\n✅ يُضاف المبلغ المدفوع فعلياً إلى محفظتك بعد التحقق (بدون مكافأة).",
        "topup_edit_done": "✅ <b>تم شحن المحفظة</b>\n\n💵 {amount} USDT",
        "topup_credited": "✅ تم شحن محفظتك بمبلغ <b>{amount}$</b>.\n💼 الرصيد المتاح: <b>${avail}</b>",
        "partial": "✅ تم استلام <b>{paid} USDT</b> من أصل {need} USDT.\n\n💳 أكمل المبلغ الباقي <b>{rest}$</b> وابعث رقم العملية الجديد باش نسلّمك منتجك.",
        "already_counted": "ℹ️ رقم العملية هذا محسوب مسبقاً.\n💳 المبلغ المتبقي: <b>{rest}$</b> — ابعث رقم عملية جديد.",
        "converted": "⌛ انتهت الفاتورة ولم يكتمل الدفع.\n💼 تمت إضافة <b>{amount}$</b> إلى محفظتك (بدون مكافأة). تقدر تشحن الباقي وتشتري من المحفظة.",
        "wpay_btn": "💼 ادفع من المحفظة",
        "wpay_done": "✅ <b>تم الدفع من المحفظة</b>\n\n📦 {product}\n💵 {amount} USDT",
        "wpay_fail": "⚠️ تعذر تسليم طلبك الآن، تم إرجاع <b>{amount}$</b> إلى محفظتك. حاول لاحقاً أو تواصل مع الدعم.",
        "wpay_short": "❌ رصيد المحفظة غير كافٍ.",
        "wpay_expired": "⌛ انتهت صلاحية هذه الفاتورة.",
        "wpay_mixed": "⚠️ دفعت جزءاً من هذه الفاتورة عبر Binance، أكمل الباقي عبر Binance (لا يمكن الدفع المختلط).",
        "wpay_busy": "⏳ حاول مرة أخرى بعد لحظة.",
        "wpay_out": "❌ هذا المنتج غير متوفر حالياً.",
    },
    "en": {
        "btn_profile": "👤 My profile",
        "btn_history": "🧾 Purchase history",
        "btn_wallet": "💼 Wallet",
        "btn_topup": "➕ Top up wallet",
        "btn_topup_other": "✏️ Other amount",
        "unavailable": "⚠️ Service unavailable right now, try again later.",
        "profile": "👤 <b>Your profile</b>\n\n🆔 ID: <code>{id}</code>\n📛 Name: {name}\n📅 Joined: {joined}\n🛒 Total purchases: {buys}\n💵 Total spent: ${spent}",
        "history": "🧾 <b>Purchase history</b>\n\n{lines}\n\n✅ Completed: {done}\n❌ Cancelled: {canc}\n📊 Success rate: {pct}%",
        "by_product": "📦 Purchases by product:",
        "history_empty": "— No purchases yet —",
        "wallet": "💼 <b>Wallet</b>\n\n🎁 Rewards: ${rewards}\n💳 Topped-up balance: ${topup}\n➖ Used: ${used}\n✅ <b>Available balance: ${avail}</b>\n\n🎁 {pct}% reward on every purchase paid directly with Binance ({gift_pct}% for gift cards). Top-ups and wallet payments earn no reward.",
        "wallet_note": "ℹ️ When your balance reaches the value of a product you want to exchange it for, contact us in the support section (manual delivery).",
        "topup_pick": "➕ <b>Top up wallet</b>\n\nChoose the amount to add (USDT):",
        "topup_other_prompt": "✏️ Send the amount you want to add in dollars ({min} to {max}).\nExample: <code>7.5</code>",
        "topup_bad": "❌ Invalid amount. Send a number between {min} and {max}.",
        "topup_name": "💳 Wallet top-up",
        "topup_steps": "1️⃣ Open Binance → Pay → Send\n2️⃣ Enter the ID above and send the amount in <b>USDT</b>\n3️⃣ After paying, copy the <b>Order ID</b> and send it here in the chat\n\n✅ The amount actually paid is added to your wallet after verification (no reward).",
        "topup_edit_done": "✅ <b>Wallet topped up</b>\n\n💵 {amount} USDT",
        "topup_credited": "✅ Your wallet was topped up with <b>{amount}$</b>.\n💼 Available balance: <b>${avail}</b>",
        "partial": "✅ Received <b>{paid} USDT</b> out of {need} USDT.\n\n💳 Pay the remaining <b>{rest}$</b> and send the new Order ID so we can deliver your product.",
        "already_counted": "ℹ️ This Order ID was already counted.\n💳 Remaining amount: <b>{rest}$</b> — send a new Order ID.",
        "converted": "⌛ The invoice expired and the payment was not completed.\n💼 <b>{amount}$</b> was added to your wallet (no reward). You can top up the rest and buy from the wallet.",
        "wpay_btn": "💼 Pay from wallet",
        "wpay_done": "✅ <b>Paid from wallet</b>\n\n📦 {product}\n💵 {amount} USDT",
        "wpay_fail": "⚠️ We couldn't deliver your order right now, <b>{amount}$</b> was refunded to your wallet. Try again later or contact support.",
        "wpay_short": "❌ Not enough wallet balance.",
        "wpay_expired": "⌛ This invoice has expired.",
        "wpay_mixed": "⚠️ You already paid part of this invoice with Binance, pay the rest with Binance (mixed payment isn't possible).",
        "wpay_busy": "⏳ Please try again in a moment.",
        "wpay_out": "❌ This product is currently unavailable.",
    },
    "fr": {
        "btn_profile": "👤 Mon profil",
        "btn_history": "🧾 Historique d'achats",
        "btn_wallet": "💼 Portefeuille",
        "btn_topup": "➕ Recharger le portefeuille",
        "btn_topup_other": "✏️ Autre montant",
        "unavailable": "⚠️ Service indisponible pour le moment, réessayez plus tard.",
        "profile": "👤 <b>Votre profil</b>\n\n🆔 ID : <code>{id}</code>\n📛 Nom : {name}\n📅 Inscription : {joined}\n🛒 Total des achats : {buys}\n💵 Total dépensé : ${spent}",
        "history": "🧾 <b>Historique d'achats</b>\n\n{lines}\n\n✅ Terminées : {done}\n❌ Annulées : {canc}\n📊 Taux de réussite : {pct}%",
        "by_product": "📦 Achats par produit :",
        "history_empty": "— Aucun achat pour le moment —",
        "wallet": "💼 <b>Portefeuille</b>\n\n🎁 Récompenses : ${rewards}\n💳 Solde rechargé : ${topup}\n➖ Utilisé : ${used}\n✅ <b>Solde disponible : ${avail}</b>\n\n🎁 {pct}% de récompense sur chaque achat payé directement avec Binance ({gift_pct}% pour les cartes cadeaux). Les recharges et paiements par portefeuille ne donnent pas de récompense.",
        "wallet_note": "ℹ️ Quand votre solde atteint la valeur d'un produit que vous voulez échanger, contactez-nous dans la section assistance (livraison manuelle).",
        "topup_pick": "➕ <b>Recharger le portefeuille</b>\n\nChoisissez le montant à ajouter (USDT) :",
        "topup_other_prompt": "✏️ Envoyez le montant à ajouter en dollars ({min} à {max}).\nExemple : <code>7.5</code>",
        "topup_bad": "❌ Montant invalide. Envoyez un nombre entre {min} et {max}.",
        "topup_name": "💳 Recharge du portefeuille",
        "topup_steps": "1️⃣ Ouvrez Binance → Pay → Envoyer\n2️⃣ Entrez l'ID ci-dessus et envoyez le montant en <b>USDT</b>\n3️⃣ Après le paiement, copiez le <b>numéro de commande (Order ID)</b> et envoyez-le ici dans le chat\n\n✅ Le montant réellement payé est ajouté à votre portefeuille après vérification (sans récompense).",
        "topup_edit_done": "✅ <b>Portefeuille rechargé</b>\n\n💵 {amount} USDT",
        "topup_credited": "✅ Votre portefeuille a été rechargé de <b>{amount}$</b>.\n💼 Solde disponible : <b>${avail}</b>",
        "partial": "✅ Reçu <b>{paid} USDT</b> sur {need} USDT.\n\n💳 Payez le reste <b>{rest}$</b> et envoyez le nouveau numéro de commande pour recevoir votre produit.",
        "already_counted": "ℹ️ Ce numéro de commande est déjà comptabilisé.\n💳 Montant restant : <b>{rest}$</b> — envoyez un nouveau numéro.",
        "converted": "⌛ La facture a expiré et le paiement n'a pas été complété.\n💼 <b>{amount}$</b> ont été ajoutés à votre portefeuille (sans récompense). Vous pouvez recharger le reste et acheter avec le portefeuille.",
        "wpay_btn": "💼 Payer avec le portefeuille",
        "wpay_done": "✅ <b>Payé avec le portefeuille</b>\n\n📦 {product}\n💵 {amount} USDT",
        "wpay_fail": "⚠️ Impossible de livrer votre commande pour le moment, <b>{amount}$</b> ont été remboursés dans votre portefeuille. Réessayez plus tard ou contactez l'assistance.",
        "wpay_short": "❌ Solde du portefeuille insuffisant.",
        "wpay_expired": "⌛ Cette facture a expiré.",
        "wpay_mixed": "⚠️ Vous avez déjà payé une partie de cette facture avec Binance, payez le reste avec Binance (paiement mixte impossible).",
        "wpay_busy": "⏳ Réessayez dans un instant.",
        "wpay_out": "❌ Ce produit est actuellement indisponible.",
    },
}

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
        "cmd_update": "🔄 تحديث",
        "support_msg": "💬 للدعم والطلبات، تواصل معي مباشرة في الخاص 👇",
        "support_btn": "💬 تواصل مع الدعم",
        "buy_hint": "🛒 لإتمام الطلب والشراء، اضغط على زر 'اطلب الآن 🛒' لتتوجه مباشرة للخاص.",
        "choose_card": "🛒 لإتمام الطلب اختر بطاقتك",
        "thanks": "🤍 شكرا على ثقتكم 🤍",
        "out_of_stock": "❌ هذا المنتج نفد من المخزون حالياً.\n🛒 للاستفسار أو الطلب المسبق، اضغط على 'اطلب الآن'.",
        "kb_start": "🚀 ابدأ",
        "kb_products": "🛍️ المنتجات",
        "kb_support": "💬 الدعم",
        "kb_lang": "🌐 اللغة",
        "kb_update": "🔄 تحديث",
        "menu_hint": "⬇️ القائمة:",
        "start_guide": "🎉 !مرحباً بك 🎉\n\n🎯 :دليل سريع كيف تستعمل البوت\n\n1. اختر المنتج الذي تريده\n2. اضغط على \"🛒 اطلب الآن\"\n3. أكمل الدفع\n4. بعد الدفع، أرسل رقم الطلب للتحقق\n5. يتم ارسال طلبك ✅\n\n🎯 عدم فهم طريقة الاستخدام؟ تواصل معنا 👇",
        "pay_binance": "💳 ادفع عبر Binance Pay",
        "invoice_title": "🧾 فاتورة الدفع",
        "invoice_id": "معرف الدفع:",
        "invoice_amount": "المبلغ:",
        "invoice_expire": "الانتهاء خلال 20 دقيقة ⏱️",
        "copy_id": "📋 نسخ معرف الدفع",
        "cancel": "❌ إلغاء",
        "invoice_steps": "1️⃣ افتح Binance ← Pay ← إرسال\n2️⃣ ضع المعرف أعلاه وأرسل المبلغ بعملة <b>USDT</b>\n3️⃣ بعد الدفع انسخ <b>رقم العملية (Order ID)</b> وأرسله هنا في الشات\n\n✅ يصلك الكود تلقائياً بعد التحقق",
        "send_id_hint": "⚠️ أرسل رقم العملية (Order ID) فقط، بدون مسافات أو كلمات إضافية.",
        "verifying": "⏳ جاري التحقق من الدفع...",
        "not_found": "❌ لم أجد هذه العملية بعد. تأكد أنك دفعت إلى المعرف الصحيح، وانتظر دقيقة ثم أعد إرسال الرقم.",
        "underpaid": "❌ المبلغ المدفوع ({paid} USDT) أقل من المطلوب ({need} USDT). تواصل مع الدعم.",
        "bad_currency": "❌ يجب أن يكون الدفع بعملة USDT. تواصل مع الدعم.",
        "old_tx": "❌ هذه العملية قديمة (قبل إنشاء الفاتورة). أنشئ فاتورة جديدة وادفع من جديد.",
        "used": "⚠️ رقم العملية هذا مستعمل من قبل.",
        "expired": "⌛ انتهت صلاحية الفاتورة. اختر المنتج من جديد، وإذا كنت قد دفعت فتواصل مع الدعم مع رقم العملية.",
        "processing": "✅ تم استلام دفعك. طلبك قيد المعالجة، وسيصلك الكود تلقائياً هنا بمجرد توفره (لا تحتاج لفعل أي شيء).",
        "delivered": "✅ تم الدفع بنجاح!\n\n📦 {product}\n💵 {amount} USDT\n\n🎁 الكود:\n{codes}\n\n🛡️ الضمان: ساعة واحدة من وقت الشراء.",
        "too_many": "⛔ محاولات كثيرة. انتظر 10 دقائق أو تواصل مع الدعم.",
        "temp_error": "⚠️ خطأ مؤقت، أعد المحاولة بعد قليل.",
        "no_binance": "⚠️ التحقق التلقائي غير متاح حالياً، تواصل مع الدعم برقم العملية.",
        "out_variant": "❌ هذه القيمة نفدت حالياً، اختر قيمة أخرى.",
        "cancelled": "تم إلغاء الفاتورة.",
        "inv_expired_edit": "⌛ <b>فاتورة منتهية</b>\n\n📦 {product}\n💵 {amount} USDT\n\n❌ تم إلغاء هذه الفاتورة تلقائياً بعد {ttl} دقيقة.",
        "inv_expired_notice": "⌛ انتهت مدة الفاتورة ({ttl} دقيقة) وتم إلغاؤها تلقائياً.\n\n⚠️ لا تدفع إليها بعد الآن.\n✅ إذا كنت قد دفعت قبل انتهائها، أرسل رقم العملية (Order ID) هنا خلال {grace} دقائق.\n🛍️ وإلا اضغط على الزر بالأسفل لإنشاء طلب جديد.",
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
        "cmd_update": "🔄 Refresh",
        "support_msg": "💬 For support and orders, contact me directly in private 👇",
        "support_btn": "💬 Contact support",
        "buy_hint": "🛒 To complete your order, tap 'Order now 🛒' to go directly to the private chat.",
        "choose_card": "🛒 To complete your order, choose your card",
        "thanks": "🤍 Thank you for your trust 🤍",
        "out_of_stock": "❌ This product is currently out of stock.\n🛒 For questions or pre-orders, tap 'Order now'.",
        "kb_start": "🚀 Start",
        "kb_products": "🛍️ Products",
        "kb_support": "💬 Support",
        "kb_lang": "🌐 Language",
        "kb_update": "🔄 Refresh",
        "menu_hint": "⬇️ Menu:",
        "start_guide": "🎉 Welcome! 🎉\n\n🎯 Quick guide on how to use the bot:\n\n1. Choose the product you want\n2. Tap \"🛒 Order now\"\n3. Complete the payment\n4. After payment, send the order number for verification\n5. Your order will be sent to you ✅\n\n🎯 Don't understand how to use it? Contact us 👇",
        "pay_binance": "💳 Pay with Binance Pay",
        "invoice_title": "🧾 Payment Invoice",
        "invoice_id": "Payment ID:",
        "invoice_amount": "Amount:",
        "invoice_expire": "Expires in 20 minutes ⏱️",
        "copy_id": "📋 Copy Payment ID",
        "cancel": "❌ Cancel",
        "invoice_steps": "1️⃣ Open Binance → Pay → Send\n2️⃣ Enter the ID above and send the amount in <b>USDT</b>\n3️⃣ After paying, copy the <b>Order ID</b> and send it here in the chat\n\n✅ You receive the code automatically after verification",
        "send_id_hint": "⚠️ Send only the Order ID, with no spaces or extra words.",
        "verifying": "⏳ Verifying your payment...",
        "not_found": "❌ I can't find this transaction yet. Make sure you paid to the correct ID, wait a minute, then resend the number.",
        "underpaid": "❌ The amount paid ({paid} USDT) is lower than required ({need} USDT). Contact support.",
        "bad_currency": "❌ Payment must be made in USDT. Contact support.",
        "old_tx": "❌ This transaction is older than the invoice. Create a new invoice and pay again.",
        "used": "⚠️ This order number has already been used.",
        "expired": "⌛ The invoice has expired. Choose the product again, and if you already paid, contact support with your order number.",
        "processing": "✅ Your payment was received. Your order is being processed and the code will be sent to you here automatically as soon as it is available (no action needed).",
        "delivered": "✅ Payment successful!\n\n📦 {product}\n💵 {amount} USDT\n\n🎁 Code:\n{codes}\n\n🛡️ Warranty: one hour from the time of purchase.",
        "too_many": "⛔ Too many attempts. Wait 10 minutes or contact support.",
        "temp_error": "⚠️ Temporary error, please try again shortly.",
        "no_binance": "⚠️ Automatic verification is unavailable right now, contact support with your order number.",
        "out_variant": "❌ This amount is currently out of stock, choose another one.",
        "cancelled": "Invoice cancelled.",
        "inv_expired_edit": "⌛ <b>Invoice expired</b>\n\n📦 {product}\n💵 {amount} USDT\n\n❌ This invoice was automatically cancelled after {ttl} minutes.",
        "inv_expired_notice": "⌛ The invoice time ({ttl} minutes) is over and it was cancelled automatically.\n\n⚠️ Do not pay it anymore.\n✅ If you paid before it expired, send the Order ID here within {grace} minutes.\n🛍️ Otherwise tap the button below to create a new order.",
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
        "cmd_update": "🔄 Actualiser",
        "support_msg": "💬 Pour l'assistance et les commandes, contactez-moi directement en privé 👇",
        "support_btn": "💬 Contacter l'assistance",
        "buy_hint": "🛒 Pour finaliser votre commande, appuyez sur « Commander maintenant 🛒 » pour aller directement en privé.",
        "choose_card": "🛒 Pour finaliser votre commande, choisissez votre carte",
        "thanks": "🤍 Merci de votre confiance 🤍",
        "out_of_stock": "❌ Ce produit est actuellement en rupture de stock.\n🛒 Pour toute question ou précommande, appuyez sur « Commander maintenant ».",
        "kb_start": "🚀 Commencer",
        "kb_products": "🛍️ Produits",
        "kb_support": "💬 Assistance",
        "kb_lang": "🌐 Langue",
        "kb_update": "🔄 Actualiser",
        "menu_hint": "⬇️ Menu :",
        "start_guide": "🎉 Bienvenue ! 🎉\n\n🎯 Guide rapide pour utiliser le bot :\n\n1. Choisissez le produit que vous voulez\n2. Appuyez sur « 🛒 Commander maintenant »\n3. Terminez le paiement\n4. Après le paiement, envoyez le numéro de commande pour vérification\n5. Votre commande vous sera envoyée ✅\n\n🎯 Vous ne comprenez pas comment l'utiliser ? Contactez-nous 👇",
        "pay_binance": "💳 Payer avec Binance Pay",
        "invoice_title": "🧾 Facture de paiement",
        "invoice_id": "ID de paiement :",
        "invoice_amount": "Montant :",
        "invoice_expire": "Expire dans 20 minutes ⏱️",
        "copy_id": "📋 Copier l'ID de paiement",
        "cancel": "❌ Annuler",
        "invoice_steps": "1️⃣ Ouvrez Binance → Pay → Envoyer\n2️⃣ Entrez l'ID ci-dessus et envoyez le montant en <b>USDT</b>\n3️⃣ Après le paiement, copiez le <b>numéro de commande (Order ID)</b> et envoyez-le ici dans le chat\n\n✅ Vous recevez le code automatiquement après vérification",
        "send_id_hint": "⚠️ Envoyez uniquement le numéro de commande (Order ID), sans espaces ni mots en plus.",
        "verifying": "⏳ Vérification du paiement en cours...",
        "not_found": "❌ Je ne trouve pas encore cette transaction. Vérifiez que vous avez payé au bon ID, attendez une minute puis renvoyez le numéro.",
        "underpaid": "❌ Le montant payé ({paid} USDT) est inférieur au montant demandé ({need} USDT). Contactez l'assistance.",
        "bad_currency": "❌ Le paiement doit être fait en USDT. Contactez l'assistance.",
        "old_tx": "❌ Cette transaction est antérieure à la facture. Créez une nouvelle facture et payez à nouveau.",
        "used": "⚠️ Ce numéro de commande a déjà été utilisé.",
        "expired": "⌛ La facture a expiré. Choisissez à nouveau le produit, et si vous avez déjà payé, contactez l'assistance avec votre numéro de commande.",
        "processing": "✅ Votre paiement a été reçu. Votre commande est en cours de traitement et le code vous sera envoyé ici automatiquement dès qu'il sera disponible (aucune action nécessaire).",
        "delivered": "✅ Paiement réussi !\n\n📦 {product}\n💵 {amount} USDT\n\n🎁 Code :\n{codes}\n\n🛡️ Garantie : une heure à partir de l'achat.",
        "too_many": "⛔ Trop de tentatives. Attendez 10 minutes ou contactez l'assistance.",
        "temp_error": "⚠️ Erreur temporaire, réessayez dans un instant.",
        "no_binance": "⚠️ La vérification automatique est indisponible pour le moment, contactez l'assistance avec votre numéro de commande.",
        "out_variant": "❌ Cette valeur est actuellement en rupture de stock, choisissez-en une autre.",
        "cancelled": "Facture annulée.",
        "inv_expired_edit": "⌛ <b>Facture expirée</b>\n\n📦 {product}\n💵 {amount} USDT\n\n❌ Cette facture a été annulée automatiquement après {ttl} minutes.",
        "inv_expired_notice": "⌛ Le délai de la facture ({ttl} minutes) est écoulé et elle a été annulée automatiquement.\n\n⚠️ Ne la payez plus.\n✅ Si vous avez payé avant son expiration, envoyez le numéro de commande (Order ID) ici dans les {grace} minutes.\n🛍️ Sinon, appuyez sur le bouton ci-dessous pour créer une nouvelle commande.",
    },
}

TRANSLATIONS = {
    "sep_gift_cards": {
        "en": {"text": "⬇️ Gift Cards ⬇️"},
        "fr": {"text": "⬇️ Cartes cadeaux ⬇️"}
    },
    "gemini_18m": {
        "en": {"description": "🤖 Gemini AI Pro 18 months [NW]\n⭐️ Gemini AI Pro for 18 months\n✦ 🚫 Activation without a card\n✦ ⏩ 5 TB of Google One cloud storage\n✦ 🚀 No VPN needed.\n\n✨ Extra features:\n- 1050 free credits on Google Flow and images\n- 3 free videos on Gemini every day for the whole subscription (18 months)\n- Activation is done on your own Gmail through an activation link only\n\nI tested it myself, so there is no replacement\n🫶 12-hour warranty."},
        "fr": {"description": "🤖 Gemini AI Pro 18 mois [NW]\n⭐️ Gemini AI Pro pour 18 mois\n✦ 🚫 Activation sans carte bancaire\n✦ ⏩ 5 To de stockage cloud Google One\n✦ 🚀 Aucun VPN nécessaire.\n\n✨ Avantages supplémentaires :\n- 1050 crédits gratuits sur Google Flow et images\n- 3 vidéos gratuites sur Gemini chaque jour pendant toute la durée de l'abonnement (18 mois)\n- L'activation se fait sur votre propre Gmail via un lien d'activation uniquement\n\nJe l'ai testé moi-même, donc il n'y a pas de remplacement\n🫶 Garantie de 12 heures."}
    },
    "capcut_1m": {
        "en": {"name": "CapCut Pro (private account - full month)", "description": "🔥 CapCut Pro subscription (private account - full month) 🎬\n\n⚡️ Sold: 89\n⏳ Duration: 30 days (a full month).\n🛡️ Warranty: full warranty for the entire subscription period (30 days).\n\nGet your account and start editing professionally with no limits!\n\n✨ Features:\n- AI tools: smart trimming, auto-generated captions, and professional tracking.\n- Full Pro library: trending fonts, music, effects, and unlimited ready-made templates.\n- Top-quality export: 4K resolution and 60 frames per second (60 FPS).\n- No watermark and no ads.\n\n⚙️ Account details:\n👤 Type: a brand-new private account (email + password) just for your projects.\n💻 Supported devices: Android, iOS, Windows, Mac, and directly on the website.\n⚡ Delivery: instant and automatic, 24/7."},
        "fr": {"name": "CapCut Pro (compte privé - mois complet)", "description": "🔥 Abonnement CapCut Pro (compte privé - mois complet) 🎬\n\n⚡️ Vendus : 89\n⏳ Durée : 30 jours (un mois complet).\n🛡️ Garantie : garantie complète pendant toute la durée de l'abonnement (30 jours).\n\nRécupérez votre compte et commencez à monter professionnellement sans limites !\n\n✨ Fonctionnalités :\n- Outils d'IA : découpage intelligent, génération automatique de sous-titres (Auto-captions), et suivi professionnel.\n- Bibliothèque Pro complète : polices tendance, musique, effets et modèles prêts à l'emploi illimités.\n- Export en qualité maximale : résolution 4K et 60 images par seconde (60 FPS).\n- Sans filigrane et sans publicité.\n\n⚙️ Détails du compte :\n👤 Type : compte privé entièrement nouveau (e-mail + mot de passe) réservé à vos projets.\n💻 Appareils compatibles : Android, iOS, Windows, Mac et directement sur le site.\n⚡ Livraison : instantanée et automatique, 24h/24 et 7j/7."}
    },
    "duolingo_12m": {
        "en": {"description": "🦉 Super Duolingo 12 months (official account upgrade)\n- Full warranty\n- Use Duolingo Super with all advanced features\n- Learn languages without ads"},
        "fr": {"description": "🦉 Super Duolingo 12 mois (mise à niveau officielle du compte)\n- Garantie complète\n- Utilisez Duolingo Super avec toutes les fonctionnalités avancées\n- Apprenez les langues sans publicité"}
    },
    "duolingo_link_12m": {
        "en": {"name": "Duolingo Super 1 year (link) + 1 month warranty", "description": "⭐ Link to get a Duolingo Super offer for one year with a 1-month warranty\n\n📊 Sales: 103 accounts\n\n🔗 Link to get a Duolingo Super offer for one year with a 1-month warranty\n\n❇️ A smooth, effective and unlimited experience for learning foreign languages.\n❇️ When you buy the offer, it is applied directly to the main account you currently use.\n❇️ Method: a link to claim the offer.\n❇️ Subscription duration: one year.\n⚙️ Warranty: one month.\n⛓️‍💥 Please use the link right after payment.\n❇️ No payment card needed: just open the link the bot sends you and get the offer"},
        "fr": {"name": "Duolingo Super 1 an (lien) + garantie 1 mois", "description": "⭐ Lien pour obtenir l'offre Duolingo Super pendant un an avec une garantie d'un mois\n\n📊 Ventes : 103 comptes\n\n🔗 Lien pour obtenir l'offre Duolingo Super pendant un an avec une garantie d'un mois\n\n❇️ Une expérience fluide, efficace et illimitée pour apprendre les langues étrangères.\n❇️ Lors de l'achat, l'offre est appliquée directement sur le compte principal que vous utilisez actuellement.\n❇️ Méthode : un lien pour obtenir l'offre.\n❇️ Durée de l'abonnement : un an.\n⚙️ Garantie : un mois.\n⛓️‍💥 Veuillez utiliser le lien juste après le paiement.\n❇️ Aucune carte bancaire nécessaire : ouvrez simplement le lien envoyé par le bot et obtenez l'offre"}
    },
    "netflix_full": {
        "en": {"name": "Netflix 2 months full account (5 profiles)", "description": "📦 Netflix Premium accounts - 2 months\n\n✅ Netflix Premium accounts\n✅ Login with email and password\n✅ 1-month warranty\n🔵 Cheapest price — 10$ means 5$ for a full account 😍\n✅ High-quality streaming\n✅ Up to 5 profiles and 4 devices\n✅ Works on mobile, laptop, tablet and smart TV\n✅ Support available 12/24 hours\n📊 Sold: 432 accounts"},
        "fr": {"name": "Netflix 2 mois compte complet (5 profils)", "description": "📦 Comptes Netflix Premium - 2 mois\n\n✅ Comptes Netflix Premium\n✅ Connexion par e-mail et mot de passe\n✅ Garantie d'un mois\n🔵 Prix le plus bas — 10$ soit 5$ le compte complet 😍\n✅ Streaming haute qualité\n✅ Jusqu'à 5 profils et 4 appareils\n✅ Fonctionne sur mobile, ordinateur portable, tablette et Smart TV\n✅ Support disponible 12/24 heures\n📊 Vendus : 432 comptes"}
    },
    "netflix_profile": {
        "en": {"name": "Netflix 2 months single profile", "description": "📦 Netflix Premium accounts - 2 months\n\n✅ Netflix Premium accounts\n❌ Do not change the name or the password, otherwise you will be removed from the account with no warranty\n✅ Login with email and password\n🔵 Cheapest price — 2.30$\n✅ High-quality streaming\n✅ One profile on one account\n✅ Works on mobile, laptop, tablet and smart TV\n✅ Support available when needed\n📊 Sold: 216 accounts"},
        "fr": {"name": "Netflix 2 mois un seul profil", "description": "📦 Comptes Netflix Premium - 2 mois\n\n✅ Comptes Netflix Premium\n❌ Interdiction de changer le nom ou le mot de passe, sinon vous serez exclu du compte sans garantie\n✅ Connexion par e-mail et mot de passe\n🔵 Prix le plus bas — 2,30$\n✅ Streaming haute qualité\n✅ Un profil sur un compte\n✅ Fonctionne sur mobile, ordinateur portable, tablette et Smart TV\n✅ Support disponible en cas de besoin\n📊 Vendus : 216 comptes"}
    },
    "nordvpn_3m": {
        "en": {"description": "🛡️ NordVPN - 3 months\n\n- Premium access to NordVPN for 3 months on up to 10 devices at the same time.\n\nActivation steps in detail:\n➡️ Activation link: https://my.nordaccount.com/activate\n- Enter your code here\n➡️ Enter your email address\n➡️ Enter the verification code received in your email\n➡️ On the payment page, scroll down and click Skip\n\nDone! Just log in with your email on any device.\n\n📊 Sold: 390 accounts"},
        "fr": {"description": "🛡️ NordVPN - 3 mois\n\n- Accès premium à NordVPN pendant 3 mois sur jusqu'à 10 appareils simultanément.\n\nÉtapes d'activation détaillées :\n➡️ Lien d'activation : https://my.nordaccount.com/activate\n- Saisissez votre code ici\n➡️ Saisissez votre adresse e-mail\n➡️ Saisissez le code de vérification reçu par e-mail\n➡️ Sur la page de paiement, faites défiler vers le bas et cliquez sur Skip (Passer)\n\nC'est fait ! Connectez-vous simplement avec votre e-mail sur n'importe quel appareil.\n\n📊 Vendus : 390 comptes"}
    },
    "n8n_starter_12m": {
        "en": {"description": "⚡ N8N Starter 12m\n\n- Duration: 12 months\n- Official voucher code\n- 🚫 No warranty after the code is activated on your account\n\n⚠️ Please note that the code must be redeemed within 7 days of purchase. Codes not used within this period may expire and are no longer eligible for support or replacement.\n\n📊 Sold: 4 accounts"},
        "fr": {"description": "⚡ N8N Starter 12m\n\n- Durée : 12 mois\n- Code coupon officiel\n- 🚫 Aucune garantie après l'activation du code sur votre compte\n\n⚠️ Veuillez noter que le code doit être utilisé dans les 7 jours suivant l'achat. Les codes non utilisés durant cette période peuvent expirer et ne sont plus éligibles au support ni au remplacement.\n\n📊 Vendus : 4 comptes"}
    },
    "snapchat_3m": {
        "en": {"description": "👻 Snapchat Plus+ 3M FW available\n\n- Warranty: 90 days\n- Stock: manual activation accounts\n- Sold: 354 accounts\n\n❞ Description:\nActivate Snapchat+ and give your account a real Premium experience with exclusive features:\n\nNo password needed, only your username (ID)\n✅ Storage solution (depending on your plan)\n🎨 Amazing themes\n👑 A new and unique account look\n⚡ Fast and safe activation\n\n👌Activation method: send me only your Username in private and get fast activation 💨"},
        "fr": {"description": "👻 Snapchat Plus+ 3M FW disponible\n\n- Garantie : 90 jours\n- Stock : comptes à activation manuelle\n- Vendus : 354 comptes\n\n❞ Description :\nActivez Snapchat+ et offrez à votre compte une vraie expérience Premium avec des fonctionnalités exclusives :\n\nAucun mot de passe nécessaire, uniquement votre nom d'utilisateur (ID)\n✅ Solution de stockage (selon votre forfait)\n🎨 Thèmes magnifiques\n👑 Un look de compte nouveau et unique\n⚡ Activation rapide et sécurisée\n\n👌Méthode d'activation : envoyez-moi uniquement votre Username en privé pour une activation rapide 💨"}
    },
    "snapchat_6m": {
        "en": {"description": "👻 Snapchat Plus+ 6M FW available\n\n- Warranty: 180 days\n- Stock: manual activation accounts\n- Sold: 354 accounts\n\n❞ Description:\nActivate Snapchat+ and give your account a real Premium experience with exclusive features:\n\nNo password needed, only your account ID\nAndroid + iPhone\n✅ Storage solution (depending on your plan)\n🎨 Amazing themes\n👑 A new and unique account look\n⚡ Fast and safe activation\n\n👌Activation method: send me only your Username in private and get fast activation 💨"},
        "fr": {"description": "👻 Snapchat Plus+ 6M FW disponible\n\n- Garantie : 180 jours\n- Stock : comptes à activation manuelle\n- Vendus : 354 comptes\n\n❞ Description :\nActivez Snapchat+ et offrez à votre compte une vraie expérience Premium avec des fonctionnalités exclusives :\n\nAucun mot de passe nécessaire, uniquement l'ID de votre compte\nAndroid + iPhone\n✅ Solution de stockage (selon votre forfait)\n🎨 Thèmes magnifiques\n👑 Un look de compte nouveau et unique\n⚡ Activation rapide et sécurisée\n\n👌Méthode d'activation : envoyez-moi uniquement votre Username en privé pour une activation rapide 💨"}
    },
    "snapchat_12m": {
        "en": {"description": "👻 Snapchat Plus+ 12M FW available\n\n- Warranty: for the whole subscription period\n- Stock: manual activation accounts\n- Sold: 231 accounts\n\n❞ Description:\nActivate Snapchat+ and give your account a real Premium experience with exclusive features: for a full year\n\nNo password needed, only your account ID\nAndroid + iPhone\n✅ Storage solution (depending on your plan)\n🎨 Amazing themes\n👑 A new and unique account look\n⚡ Fast and safe activation\n\n👌Activation method: send me only your Username in private and get fast activation 💨"},
        "fr": {"description": "👻 Snapchat Plus+ 12M FW disponible\n\n- Garantie : pendant toute la durée de l'abonnement\n- Stock : comptes à activation manuelle\n- Vendus : 231 comptes\n\n❞ Description :\nActivez Snapchat+ et offrez à votre compte une vraie expérience Premium avec des fonctionnalités exclusives : pour une année complète\n\nAucun mot de passe nécessaire, uniquement l'ID de votre compte\nAndroid + iPhone\n✅ Solution de stockage (selon votre forfait)\n🎨 Thèmes magnifiques\n👑 Un look de compte nouveau et unique\n⚡ Activation rapide et sécurisée\n\n👌Méthode d'activation : envoyez-moi uniquement votre Username en privé pour une activation rapide 💨"}
    },
    "canva_edu_500": {
        "en": {"name": "Canva Edu Pro — 500 seats", "description": "🎨 Canva Edu Pro — 500 seats\n\n🔥 Canva Education account/dashboard for students and teachers\nEnjoy Canva's education benefits and Pro tools to create professional designs easily.\n\n✨ What do you get?\n- 🎓 Access to Canva education benefits.\n- 💎 Canva Pro tools and many professional features.\n- 📚 Ready-made education templates.\n- 🎨 Design presentations, posts, videos and educational files.\n- 🤖 AI tools such as Magic Write.\n\n📦 Capacity: 500 seats\n💰 Price: only 10$\n⚠️ Important: no warranty on this product.\n\n🚀 Suitable for students, teachers, designers and business owners"},
        "fr": {"name": "Canva Edu Pro — 500 places", "description": "🎨 Canva Edu Pro — 500 places\n\n🔥 Compte/tableau de bord Canva Éducation pour les étudiants et les enseignants\nProfitez des avantages éducatifs de Canva et des outils Pro pour créer facilement des designs professionnels.\n\n✨ Ce que vous obtenez :\n- 🎓 Accès aux avantages éducatifs de Canva.\n- 💎 Les outils Canva Pro et de nombreuses fonctionnalités professionnelles.\n- 📚 Modèles éducatifs prêts à l'emploi.\n- 🎨 Création de présentations, publications, vidéos et documents éducatifs.\n- 🤖 Outils d'IA comme Magic Write.\n\n📦 Capacité : 500 places\n💰 Prix : seulement 10$\n⚠️ Important : produit sans garantie.\n\n🚀 Idéal pour les étudiants, enseignants, designers et porteurs de projets"}
    },
    "canva_edu_5000": {
        "en": {"name": "Canva Education Premium subscription | 3 years on your personal account", "description": "✨ Canva Education Premium subscription | 3 years on your personal account ✨\n\n❇️ Sold: 34150\n\nDesign professionally with no limits, with full access to the huge design library:\n⏳ Duration: 3 full years with instant activation and continuous technical support 🛠️\n💎 Features: open access to millions of templates, photos, videos and premium fonts 🖼️🎬\n💻 Compatibility: works smoothly on computer (PC / Mac) and phones (Android / iOS) 📱\n🔒 Security & privacy: activation is done via an official invite link or code — we never ask for your password 🔑🚫\n\n📥 Quick activation steps:\n1️⃣ Confirm your order 🛒\n2️⃣ Send your account email in the chat ✉️\n3️⃣ Accept the invite, congrats — it's activated instantly 🎉"},
        "fr": {"name": "Abonnement Canva Education Premium | 3 ans sur votre compte personnel", "description": "✨ Abonnement Canva Education Premium | 3 ans sur votre compte personnel ✨\n\n❇️ Vendus : 34150\n\nCréez des designs professionnels sans limites, avec un accès complet à l'immense bibliothèque de création :\n⏳ Durée : 3 années complètes avec activation instantanée et support technique continu 🛠️\n💎 Fonctionnalités : accès ouvert à des millions de modèles, photos, vidéos et polices premium 🖼️🎬\n💻 Compatibilité : fonctionne parfaitement sur ordinateur (PC / Mac) et téléphones (Android / iOS) 📱\n🔒 Sécurité et confidentialité : l'activation se fait via un lien d'invitation officiel ou un code — nous ne demandons jamais votre mot de passe 🔑🚫\n\n📥 Étapes d'activation rapide :\n1️⃣ Confirmez votre commande 🛒\n2️⃣ Envoyez l'e-mail de votre compte dans la conversation ✉️\n3️⃣ Acceptez l'invitation, félicitations — activation instantanée 🎉"}
    },
    "freefire_diamonds": {
        "en": {"description": "🔥 Free Fire Diamonds 💎 top-up in the fastest and easiest way! 🔥\n\nNeed to top up your account's diamonds? 💎\nWith our service you can top up Free Fire Diamonds with the ID only ✅\n\n🔒 No password or any account information needed\n⚡️ The top-up is fast, in just one minute after payment is completed and the ID is sent.\n\n💎 Package prices without bonus diamonds:\n\n110💎 ▶️ 1.45$\n\n231💎 ▶️ 2.20$\n\n583💎 ▶️ 5.05$\n\n1188💎 ▶️ 10.10$\n\n2420💎 ▶️ 19.50$\n\n📩 How to order:\n1️⃣ Contact us\n2️⃣ Choose the package that suits you\n3️⃣ Make the payment\n4️⃣ Send us only your account ID\n5️⃣ The diamonds are added to your account ⚡️\n\n🛡️ Warranty available ✅\n🚀 Fast execution\n🔐 We don't ask for any sensitive account information\n\n💎 Order your top-up now and enjoy the game! 🎮🔥"},
        "fr": {"description": "🔥 Recharge Free Fire Diamonds 💎 de la manière la plus rapide et la plus simple ! 🔥\n\nBesoin de recharger les diamants de votre compte ? 💎\nRechargez Free Fire Diamonds avec l'ID uniquement ✅\n\n🔒 Aucun mot de passe ni information de compte requis\n⚡️ Recharge en une minute après le paiement et l'envoi de l'ID.\n\n💎 Prix des packs sans diamants bonus :\n\n110💎 ▶️ 1.45$\n\n231💎 ▶️ 2.20$\n\n583💎 ▶️ 5.05$\n\n1188💎 ▶️ 10.10$\n\n2420💎 ▶️ 19.50$\n\n📩 Comment commander :\n1️⃣ Contactez-nous\n2️⃣ Choisissez le pack qui vous convient\n3️⃣ Effectuez le paiement\n4️⃣ Envoyez-nous uniquement l'ID de votre compte\n5️⃣ Les diamants sont ajoutés à votre compte ⚡️\n\n🛡️ Garantie disponible ✅\n🚀 Exécution rapide\n🔐 Aucune information sensible demandée\n\n💎 Commandez votre recharge maintenant et profitez du jeu ! 🎮🔥"}
    },
    "apple_gift_tr": {
        "en": {"name": "Apple Gift Card 🇹🇷 Turkish", "description": "🍎 Apple Gift Card 🇹🇷 — Turkey\n\nFor the Turkish App Store 📱\n💳 After payment you receive the activation code immediately.\n\n🛡️ Warranty: one hour from the time of purchase.\n(We have never had any problem with the codes.)"},
        "fr": {"name": "Apple Gift Card 🇹🇷 Turque", "description": "🍎 Apple Gift Card 🇹🇷 — Turquie\n\nDestinée à l'App Store turc 📱\n💳 Après le paiement, vous recevez immédiatement le code d'activation.\n\n🛡️ Garantie : une heure à partir de l'achat.\n(Nous n'avons jamais eu de problème avec les codes.)"}
    },
    "apple_gift_in": {
        "en": {"name": "Apple Gift Card 🇮🇳 Indian", "description": "🍎 Apple Gift Card 🇮🇳 — India\n\nCards for the Indian App Store 📱\n💳 After payment you receive the activation code immediately.\n\n🛡️ Warranty: one hour from the time of purchase.\n(We have never had any problem with the codes.)"},
        "fr": {"name": "Apple Gift Card 🇮🇳 Indienne", "description": "🍎 Apple Gift Card 🇮🇳 — Inde\n\nCartes destinées à l'App Store indien 📱\n💳 Après le paiement, vous recevez immédiatement le code d'activation.\n\n🛡️ Garantie : une heure à partir de l'achat.\n(Nous n'avons jamais eu de problème avec les codes.)"}
    },
    "apple_gift_fr": {
        "en": {"name": "Apple Gift Card 🇫🇷 French", "description": "🍎 Apple Gift Card 🇫🇷 — France\n\nCards for the French App Store 📱\n💳 After payment you receive the activation code immediately.\n\n🛡️ Warranty: one hour from the time of purchase.\n(We have never had any problem with the codes.)"},
        "fr": {"name": "Apple Gift Card 🇫🇷 Française", "description": "🍎 Apple Gift Card 🇫🇷 — France\n\nCartes destinées à l'App Store français 📱\n💳 Après le paiement, vous recevez immédiatement le code d'activation.\n\n🛡️ Garantie : une heure à partir de l'achat.\n(Nous n'avons jamais eu de problème avec les codes.)"}
    },
}

products = [
    {
        "id": "gemini_18m",
        "name": "Gemini 18 months",
        "price": "$1.80",
        "stock": 0,  # يُحدَّث تلقائياً من Upstash (عدد الروابط)
        "icon": "⚡",
        "image": "https://i.postimg.cc/52zRxRM3/IMG-3570.jpg",
        "description": "🤖 جيمني إي آي برو 18 شهراً [NW]\n⭐️ جيمني إي آي برو لمدة 18 شهراً\n✦ 🚫 تفعيل بدون بطاقة\n✦ ⏩ مساحة تخزين سحابي 5 تيرابايت على جوجل ون\n✦ 🚀 لا حاجة لشبكة افتراضية (VPN).\n\n✨ مميزات إضافية:\n- رصيد 1050 كريدي على Google Flow والصور مجاناً\n- عمل 3 فيديوهات مجاناً على Gemini كل يوم طيلة مدة الاشتراك (18 شهر)\n- طريقة التفعيل تكون على جيمايل خاص بك عن طريق رابط تفعيل فقط\n\nلقد اختبارته بنفسي لذلك لا يوجد استبدال\n🫶 ضمان لمدة 12 ساعة.",
    },
    {
        "id": "capcut_1m",
        "name": "CapCut Pro (حساب خاص - شهر كامل)",
        "price": "$2.20",
        "stock": 16,
        "icon": "🎬",
        "image": "https://i.postimg.cc/DzpSgryL/IMG-3143.jpg",
        "description": "🔥 اشتراك كاب كات برو | CapCut Pro (حساب خاص - شهر كامل) 🎬\n\n⚡️ المباع: 89\n⏳ المدة: 30 يوم (شهر كامل).\n🛡️ الضمان: ضمان كامل طوال فترة الاشتراك (30 يوم).\n\nاستلم حسابك وابدأ المونتاج باحترافية بدون قيود!\n\n✨ المميزات:\n- أدوات الذكاء الاصطناعي (AI): قص ذكي، توليد التسميات التلقائية (Auto-captions)، وتتبع احترافي.\n- مكتبة برو كاملة: خطوط ترند، موسيقى، مؤثرات، وقوالب جاهزة غير محدودة.\n- تصدير بأعلى جودة: دقة 4K و 60 إطار في الثانية (60 FPS).\n- بدون علامة مائية وبدون إعلانات.\n\n⚙️ تفاصيل الحساب:\n👤 النوع: حساب خاص وجديد بالكامل (إيميل + باسوورد) لمشاريعك فقط.\n💻 الأجهزة المدعومة: Android, iOS, Windows, Mac والموقع مباشرة.\n⚡ التسليم: فوري وتلقائي 24/7.",
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
        "price": "$10.00",
        "stock": 1,
        "icon": "🍿",
        "image": "https://i.postimg.cc/zDM5d4D3/IMG-3568.jpg",
        "description": "📦 حسابات نتفليكس بريميوم - شهرين\n\n✅ حسابات نتفليكس بريميوم\n✅ تسجيل الدخول بالبريد الإلكتروني وكلمة المرور\n✅ ضمان لمدة شهر الأول\n🔵 أرخص سعر — 10$ يعني 5$ حساب كامل 😍\n✅ يدعم البث بجودة عالية\n✅ يمكن استخدام ما يصل إلى 5 ملفات شخصية و4 أجهزة\n✅ يعمل على الهاتف المحمول، الكمبيوتر المحمول، التابلت والتلفزيون الذكي\n✅ الدعم متاح 12/24 ساعة\n📊 المباعة: 432 حسابات",
    },
    {
        "id": "netflix_profile",
        "name": "Netflix شهرين بروفيل واحد",
        "price": "$2.30",
        "stock": 36,
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
        "name": "اشتراك Canva Education المميز | 3 سنوات على حسابك الشخصي",
        "price": "$1.20",
        "stock": 500,
        "icon": "🎨",
        "image": "https://i.postimg.cc/sxq1rsZR/IMG-3373.jpg",
        "description": "✨ اشتراك CNVA Education المميز | 3 سنوات على حسابك الشخصي ✨\n\n❇️ المباع: 34150\n\nصمّم باحترافية وبدون حدود مع وصول كامل لمكتبة التصميم الضخمة:\n⏳ المدة: 3 سنوات كاملة مع تفعيل فوري ودعم فني متواصل 🛠️\n💎 المميزات: وصول مفتوح لملايين القوالب، الصور، الفيديوهات، والخطوط المميزة (Premium) 🖼️🎬\n💻 التوافق: يعمل بسلاسة على الكمبيوتر (PC / Mac) والهواتف (Android / iOS) 📱\n🔒 الأمان والخصوصية: التفعيل يتم عبر رابط دعوة رسمي أو رمز — لا نطلب كلمة المرور أبداً 🔑🚫\n\n📥 خطوات التفعيل السريع:\n1️⃣ أكّد طلبك 🛒\n2️⃣ أرسل إيميل حسابك في المحادثة ✉️\n3️⃣ اقبل الدعوة ومبروك عليك التفعيل فوراً 🎉",
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
        "description": "🍎 Apple Gift Card 🇹🇷 — تركية\n\nمخصّصة لمتجر App Store التركي 📱\n💳 عند الدفع يصلك كود التفعيل مباشرة.\n\n🛡️ الضمان: ساعة واحدة من وقت الشراء.\n(لم يسبق أن واجهتنا أي مشكلة مع الأكواد.)",
    },
    {
        "id": "apple_gift_in",
        "name": "Apple Gift Card 🇮🇳 هندية",
        "price": "$1.40 - $28.10",
        "stock": "♾️",
        "icon": "🍎",
        "description": "🍎 Apple Gift Card 🇮🇳 — هندية\n\nبطاقات مخصّصة لمتجر App Store الهند 📱\n💳 عند الدفع يصلك كود التفعيل مباشرة.\n\n🛡️ الضمان: ساعة واحدة من وقت الشراء.\n(لم يسبق أن واجهتنا أي مشكلة مع الأكواد.)",
    },
    {
        "id": "apple_gift_fr",
        "name": "Apple Gift Card 🇫🇷 فرنسية",
        "price": "$2.45 - $116.22",
        "stock": "♾️",
        "icon": "🍎",
        "description": "🍎 Apple Gift Card 🇫🇷 — فرنسا\n\nبطاقات مخصّصة لمتجر App Store الفرنسي 📱\n💳 عند الدفع يصلك كود التفعيل مباشرة.\n\n🛡️ الضمان: ساعة واحدة من وقت الشراء.\n(لم يسبق أن واجهتنا أي مشكلة مع الأكواد.)",
    },
]

# ========== التحكم في الأسعار من تيليغرام (الأدمن فقط) ==========
PRICES_KEY = "rk:prices"  # hash في Upstash: product_id -> السعر
BASE_PRICES = {p["id"]: p["price"] for p in products if p.get("type") != "separator"}
STOCK_KEY = "rk:stock"  # hash في Upstash: product_id -> الكمية (رقم أو "inf" لـ ♾️)
BASE_STOCK = {p["id"]: p["stock"] for p in products if p.get("type") != "separator"}

LANG_FILE = "user_lang.json"
LANG_KEY = "user_lang"
USERS_KEY = "all_users"

db = None
if os.environ.get("UPSTASH_REDIS_REST_URL") and os.environ.get("UPSTASH_REDIS_REST_TOKEN"):
    try:
        from upstash_redis import Redis
        db = Redis.from_env()
        print("Upstash Redis connected.")
    except Exception as e:
        print(f"Upstash unavailable, using local file only: {e}")
        db = None

def _load_lang_file():
    try:
        with open(LANG_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_langs():
    try:
        with open(LANG_FILE, "w", encoding="utf-8") as f:
            json.dump(user_lang, f)
    except Exception as e:
        print(f"Could not save languages: {e}")

def load_langs():
    langs = _load_lang_file()
    if db:
        try:
            remote = {str(k): v for k, v in (db.hgetall(LANG_KEY) or {}).items()}
            merged = {**langs, **remote}
            missing = {k: v for k, v in merged.items() if k not in remote}
            if missing:
                db.hset(LANG_KEY, values=missing)
            return merged
        except Exception as e:
            print(f"Could not load langs from Upstash: {e}")
    return langs

user_lang = load_langs()

def load_users():
    users = set(user_lang.keys())
    if db:
        try:
            remote = {str(u) for u in (db.smembers(USERS_KEY) or [])}
            missing = users - remote
            if missing:
                db.sadd(USERS_KEY, *missing)
            users |= remote
        except Exception as e:
            print(f"Could not load users from Upstash: {e}")
    return users

known_users = load_users()

def save_lang(user_id, lang):
    uid = str(user_id)
    user_lang[uid] = lang
    if db:
        try:
            db.hset(LANG_KEY, uid, lang)
        except Exception as e:
            print(f"Could not save lang to Upstash: {e}")
    save_langs()

def register_user(user_id):
    uid = str(user_id)
    if uid in known_users:
        return
    known_users.add(uid)
    if db:
        try:
            db.sadd(USERS_KEY, uid)
        except Exception as e:
            print(f"Could not register user: {e}")

def remove_user(user_id):
    uid = str(user_id)
    known_users.discard(uid)
    if db:
        try:
            db.srem(USERS_KEY, uid)
        except Exception as e:
            print(f"Could not remove user: {e}")

def db_get_int(key, default=0):
    if db:
        try:
            value = db.get(key)
            return int(value) if value is not None else default
        except Exception as e:
            print(f"db_get_int error: {e}")
    return default

def db_set(key, value):
    if db:
        try:
            db.set(key, value)
        except Exception as e:
            print(f"db_set error: {e}")

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

# ============================================================
# ========== تخزين الفواتير والعمليات (Redis + ذاكرة) ==========
# ============================================================
class StorageError(Exception):
    pass

_mem = {}
_mem_lock = threading.Lock()

def _mem_get(key):
    with _mem_lock:
        item = _mem.get(key)
        if not item:
            return None
        value, exp = item
        if exp and exp < time.time():
            _mem.pop(key, None)
            return None
        return value

def kv_get(key):
    if db:
        try:
            return db.get(key)
        except Exception as e:
            print(f"kv_get error: {e}")
            raise StorageError(str(e))
    return _mem_get(key)

def kv_set(key, value, ex=None, nx=False):
    """يرجع True إذا تم الحفظ، False إذا nx وكان المفتاح موجوداً."""
    if db:
        try:
            return bool(db.set(key, value, ex=ex, nx=nx))
        except Exception as e:
            print(f"kv_set error: {e}")
            raise StorageError(str(e))
    with _mem_lock:
        if nx:
            item = _mem.get(key)
            if item and (not item[1] or item[1] >= time.time()):
                return False
        _mem[key] = (value, time.time() + ex if ex else None)
        return True

def kv_del(key):
    if db:
        try:
            db.delete(key)
            return
        except Exception as e:
            print(f"kv_del error: {e}")
            raise StorageError(str(e))
    with _mem_lock:
        _mem.pop(key, None)

def kv_incr_window(key, window):
    if db:
        try:
            n = int(db.incr(key))
            if n == 1:
                db.expire(key, window)
            return n
        except Exception as e:
            print(f"kv_incr error: {e}")
            raise StorageError(str(e))
    cur = _mem_get(key)
    n = int(cur) + 1 if cur else 1
    with _mem_lock:
        old = _mem.get(key)
        exp = old[1] if (old and old[1] and old[1] >= time.time()) else time.time() + window
        _mem[key] = (n, exp)
    return n

def kv_get_json(key):
    v = kv_get(key)
    if v is None:
        return None
    if isinstance(v, (dict, list)):
        return v
    try:
        return json.loads(v)
    except Exception:
        return None

_mem_pend = set()

def pend_add(canon):
    """قائمة الطلبات المدفوعة التي لم تُسلَّم بعد (لإعادة المحاولة تلقائياً)."""
    if db:
        try:
            db.sadd("rk:pendset", canon)
            return
        except Exception as e:
            print(f"pend_add error: {e}")
            return
    _mem_pend.add(canon)

def pend_remove(canon):
    if db:
        try:
            db.srem("rk:pendset", canon)
            return
        except Exception as e:
            print(f"pend_remove error: {e}")
            return
    _mem_pend.discard(canon)

def pend_list():
    if db:
        try:
            return [str(x) for x in (db.smembers("rk:pendset") or [])]
        except Exception as e:
            print(f"pend_list error: {e}")
            return []
    return list(_mem_pend)

def _user_link(uid):
    return f'<a href="tg://user?id={uid}">{uid}</a>'

def monitor_send(text, key=None, cooldown=0):
    """يرسل إشعاراً لبوت المراقبة. key+cooldown (ثواني) لمنع تكرار نفس التنبيه."""
    if not MONITOR_BOT_TOKEN:
        return
    if key and cooldown:
        try:
            if not kv_set(f"rk:mon:{key}", "1", ex=cooldown, nx=True):
                return
        except StorageError:
            pass

    def _do():
        try:
            r = requests.post(
                f"https://api.telegram.org/bot{MONITOR_BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": MONITOR_CHAT_ID,
                    "text": text[:3900],
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True,
                },
                timeout=15,
            )
            if r.status_code != 200:
                print(f"monitor_send http {r.status_code}: {r.text[:200]}")
        except Exception as e:
            print(f"monitor_send failed: {e}")

    threading.Thread(target=_do, daemon=True).start()

def create_invoice(user_id, product_id, label, price_usdt, product_name):
    """ينشئ فاتورة جديدة ويربطها بالزبون، يرجع invoice_id."""
    invoice_id = uuid.uuid4().hex[:10]
    data = {
        "user_id": user_id,
        "product_id": product_id,
        "label": label,
        "product_name": product_name,
        "price_usdt": price_usdt,
        "created_at": time.time(),
    }
    ttl = INVOICE_TTL + INVOICE_GRACE + 600
    kv_set(f"rk:inv:{invoice_id}", json.dumps(data), ex=ttl)
    kv_set(f"rk:pend:{user_id}", invoice_id, ex=ttl)
    inv_live_add(invoice_id)  # لتراقبها حلقة الانتهاء التلقائي
    return invoice_id

# ---------- مراقبة انتهاء الفواتير (إلغاء تلقائي بعد 20 دقيقة) ----------
_mem_live = set()

def inv_live_add(inv_id):
    if db:
        try:
            db.sadd("rk:invlive", inv_id)
            return
        except Exception as e:
            print(f"inv_live_add error: {e}")
    _mem_live.add(inv_id)

def inv_live_remove(inv_id):
    _mem_live.discard(inv_id)
    if db:
        try:
            db.srem("rk:invlive", inv_id)
        except Exception as e:
            print(f"inv_live_remove error: {e}")

def inv_live_list():
    ids = set(_mem_live)
    if db:
        try:
            ids |= {str(x) for x in (db.smembers("rk:invlive") or [])}
        except Exception as e:
            print(f"inv_live_list error: {e}")
    return list(ids)

def attach_invoice_msg(inv_id, sent):
    """يحفظ رقم رسالة الفاتورة لنعدلها عند الانتهاء."""
    try:
        inv = get_invoice(inv_id)
        if not inv:
            return
        inv["chat_id"] = sent.chat.id
        inv["message_id"] = sent.message_id
        remaining = int(INVOICE_TTL + INVOICE_GRACE + 600 - (time.time() - inv["created_at"]))
        kv_set(f"rk:inv:{inv_id}", json.dumps(inv), ex=max(60, remaining))
    except Exception as e:
        print(f"attach_invoice_msg error: {e}")

def get_invoice(invoice_id):
    return kv_get_json(f"rk:inv:{invoice_id}")

def get_pending_invoice_id(user_id):
    try:
        v = kv_get(f"rk:pend:{user_id}")
    except StorageError:
        return None
    return str(v) if v else None

def clear_pending(user_id):
    try:
        kv_del(f"rk:pend:{user_id}")
    except StorageError:
        pass

# ============================================================
# ========== Gemini: المخزون والتسليم من Upstash ==========
# ============================================================
def gemini_stock():
    """المخزون = عدد الروابط في Upstash."""
    if not db:
        return 0
    try:
        return int(db.llen(GEMINI_LINKS_KEY) or 0)
    except Exception as e:
        print(f"gemini_stock error: {e}")
        monitor_send(f"🚨 <b>مشكل في الاتصال بـ Upstash</b>\n<code>{html.escape(str(e))[:300]}</code>",
                     key="upstash_err", cooldown=1800)
        return 0

_PRICE_RE = re.compile(r"\$\d+(\.\d+)?")

def editable_products():
    """المنتجات ذات السعر الواحد فقط (بدون النطاقات مثل بطاقات الهداية وFree Fire)."""
    return [
        p for p in products
        if p.get("type") != "separator"
        and p["id"] not in GIFT_VARIANTS
        and _PRICE_RE.fullmatch(BASE_PRICES.get(p["id"], ""))
    ]

def stock_editable_products():
    """المنتجات ذات المخزون اليدوي (بدون Gemini لأن مخزونه من Upstash، وبدون بطاقات الهداية لأنها من FAZER)."""
    return [
        p for p in products
        if p.get("type") != "separator"
        and p["id"] != GEMINI_ID
        and p["id"] not in GIFT_VARIANTS
    ]

def sync_prices():
    """يقرأ الأسعار والكميات من Upstash ويطبقها على قائمة products (أو يرجع الأصلي إذا حُذف التعديل)."""
    if not db:
        return
    try:
        data = {str(k): str(v) for k, v in (db.hgetall(PRICES_KEY) or {}).items()}
    except Exception as e:
        print(f"sync_prices error: {e}")
        return
    for p in editable_products():
        if p["id"] in data:
            try:
                p["price"] = f"${Decimal(data[p['id']]):.2f}"
            except InvalidOperation:
                pass
        else:
            p["price"] = BASE_PRICES[p["id"]]

    try:
        sdata = {str(k): str(v) for k, v in (db.hgetall(STOCK_KEY) or {}).items()}
    except Exception as e:
        print(f"sync_stock overrides error: {e}")
        return
    for p in stock_editable_products():
        raw = sdata.get(p["id"])
        if raw is None:
            p["stock"] = BASE_STOCK[p["id"]]
        elif raw == "inf":
            p["stock"] = "♾️"
        else:
            try:
                p["stock"] = max(0, int(raw))
            except ValueError:
                p["stock"] = BASE_STOCK[p["id"]]

def gemini_unit_price():
    sync_prices()
    p = find_product(GEMINI_ID)
    try:
        return Decimal(p["price"].lstrip("$"))
    except Exception:
        return GEMINI_UNIT_PRICE

def sync_stock():
    sync_prices()
    p = find_product(GEMINI_ID)
    if p:
        p["stock"] = gemini_stock()

def _fulfill_gemini(chat_id, uid, lang, claim, canon, retry, mark, failed):
    """يسحب الروابط من Upstash ويسلّمها. آمن ضد التسليم المزدوج."""
    pname = html.escape(claim.get("product_name") or "Gemini")
    try:
        n = int(str(claim.get("label", "x1")).lstrip("x"))
    except ValueError:
        n = 1
    out_key = f"rk:gem:out:{canon}"

    try:
        links = kv_get_json(out_key)
    except StorageError:
        failed(f"⚠️ <b>خطأ تخزين أثناء تسليم Gemini</b>\n👤 <code>{uid}</code>\n🧾 <code>{html.escape(canon)}</code>")
        return

    if not links:
        if not db:
            failed("⚠️ <b>Upstash غير متصل، لا يمكن تسليم Gemini</b>")
            return
        try:
            got = db.lpop(GEMINI_LINKS_KEY, n)
        except Exception as e:
            failed(f"⚠️ <b>فشل قراءة روابط Gemini</b>\n{html.escape(str(e))[:300]}")
            return
        if got is None:
            got = []
        elif isinstance(got, str):
            got = [got]
        got = [str(x) for x in got]

        if len(got) < n:
            if got:
                try:
                    db.lpush(GEMINI_LINKS_KEY, *reversed(got))  # أرجعها
                except Exception as e:
                    print(f"gemini push back error: {e}")
                    alert_admin("⚠️ تعذر إرجاع الروابط:\n" + "\n".join(html.escape(x) for x in got))
            failed(
                f"⚠️ <b>دفع مقبول لكن مخزون Gemini غير كافٍ</b>\n\n"
                f"📦 {pname}\n👤 ID: <code>{uid}</code>\n💵 {claim.get('paid')} USDT\n"
                f"🧾 <code>{html.escape(canon)}</code>\n\n"
                f"أضف روابط من Upstash CLI:\n<code>RPUSH {GEMINI_LINKS_KEY} \"link\"</code>\n"
                f"والبوت يسلّم تلقائياً خلال دقائق."
            )
            return
        links = got
        try:
            kv_set(out_key, json.dumps(links), ex=30 * 86400)
        except StorageError:
            alert_admin(f"⚠️ تعذر حفظ نسخة التسليم. الروابط للزبون <code>{uid}</code>:\n"
                        + "\n".join(html.escape(x) for x in links))

    links_txt = "\n\n".join(f"🔑 {html.escape(l)}" for l in links)
    text = GEMINI_TEXTS.get(lang, GEMINI_TEXTS["ar"])["delivered"].format(links=links_txt)
    try:
        bot.send_message(chat_id, text, parse_mode="HTML", disable_web_page_preview=True)
    except Exception as e:
        print(f"gemini deliver failed: {e}")
        monitor_send(f"⚠️ <b>تعذر إرسال رابط Gemini للزبون</b> {_user_link(uid)}\nالروابط وصلتك في البوت الرئيسي.")
        alert_admin(f"⚠️ <b>تعذر إرسال روابط Gemini للزبون</b> <code>{uid}</code>\n"
                    f"🧾 <code>{html.escape(canon)}</code>\n" + "\n".join(html.escape(x) for x in links))
    mark("delivered")
    clear_pending(uid)
    record_purchase(uid, GEMINI_ID, claim.get("product_name"), claim.get("price"), canon, via=claim.get("via", "binance"))

    left = gemini_stock()
    alert_admin(
        ("✅ <b>بيع Gemini تلقائي (بعد إعادة المحاولة)</b>" if retry else "✅ <b>بيع Gemini تلقائي</b>")
        + f"\n📦 {pname}\n👤 <code>{uid}</code>\n💵 مدفوع: {claim.get('paid')} USDT\n"
        f"📉 المخزون المتبقي: {left}" + (" ⚠️ اقترب من النفاد!" if left <= 2 else "")
    )
    monitor_send(
        f"✅ <b>شراء جديد</b>\n\n📦 {pname}\n👤 {_user_link(uid)}\n"
        f"💵 {claim.get('paid')} USDT\n📉 المخزون المتبقي: {left}"
    )
    if left <= 0:
        monitor_send(
            "📭 <b>مخزون Gemini نفد!</b>\nزيد روابط في Upstash:\n"
            f"<code>RPUSH {GEMINI_LINKS_KEY} \"link\"</code>",
            key="gem_empty", cooldown=3600,
        )
    elif left <= 2:
        monitor_send(f"⚠️ <b>مخزون Gemini قارب النفاد</b>: {left} فقط", key="gem_low", cooldown=3600)

# ============================================================
# ========== Binance Pay: التحقق من الدفع ==========
# ============================================================
class BinanceError(Exception):
    pass

def binance_pay_history(start_ms, end_ms, limit=100):
    if not BINANCE_API_KEY or not BINANCE_SECRET_KEY:
        raise BinanceError("missing_keys")
    params = {
        "startTimestamp": int(start_ms),
        "endTimestamp": int(end_ms),
        "limit": limit,
        "timestamp": int(time.time() * 1000),
        "recvWindow": 10000,
    }
    query = urlencode(params)
    sig = hmac.new(BINANCE_SECRET_KEY.encode(), query.encode(), hashlib.sha256).hexdigest()
    url = f"{BINANCE_BASE_URL}/sapi/v1/pay/transactions?{query}&signature={sig}"
    try:
        r = requests.get(url, headers={"X-MBX-APIKEY": BINANCE_API_KEY}, timeout=20)
    except Exception as e:
        raise BinanceError(f"network: {e}")
    try:
        data = r.json()
    except Exception:
        raise BinanceError(f"http {r.status_code}: {r.text[:200]}")
    if r.status_code != 200 or str(data.get("code")) not in ("000000", "0") or data.get("success") is False:
        raise BinanceError(f"http {r.status_code}: {str(data)[:300]}")
    return data.get("data") or []

def _to_decimal(v):
    try:
        return Decimal(str(v))
    except (InvalidOperation, ValueError):
        return Decimal(0)

def find_binance_payment(order_id, invoice_created_at):
    """يبحث عن عملية واردة برقمها. يرجع (status, tx)."""
    now_ms = int(time.time() * 1000)
    start_ms = int(invoice_created_at * 1000) - 15 * 60 * 1000
    txs = binance_pay_history(start_ms, now_ms + 60_000)
    oid = order_id.strip()
    for tx in txs:
        ids = [str(tx.get(k)) for k in ("transactionId", "orderId", "prepayId") if tx.get(k)]
        if not ids:
            continue
        match = oid in ids or (len(oid) >= 10 and any(i.endswith(oid) for i in ids))
        if not match:
            continue
        amount = _to_decimal(tx.get("amount"))
        currency = str(tx.get("currency") or "").upper()
        info = {
            "tx_id": str(tx.get("transactionId") or ids[0]),
            "amount": amount,
            "currency": currency,
            "time": int(tx.get("transactionTime") or 0),
        }
        if amount <= 0:
            return "not_found", None  # عملية صادرة وليست واردة
        if currency not in ACCEPTED_CURRENCIES:
            return "bad_currency", info
        if info["time"] and info["time"] < int(invoice_created_at * 1000) - 120_000:
            return "old", info
        return "ok", info
    return "not_found", None

# ============================================================
# ========== FAZER: الكتالوج والشراء ==========
# ============================================================
class FazerError(Exception):
    pass

_catalog = {"ts": 0, "cats": None}
_catalog_lock = threading.Lock()

def _fazer_headers(extra=None):
    h = {
        "X-API-Key": FAZER_API_KEY,
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "RaseedkomBot/1.0",
    }
    if extra:
        h.update(extra)
    return h

def _fazer_get(path, params=None):
    if not FAZER_API_KEY:
        raise FazerError("missing FAZER_API_KEY")
    try:
        r = requests.get(FAZER_BASE_URL + path, headers=_fazer_headers(), params=params, timeout=20)
    except Exception as e:
        raise FazerError(f"network: {e}")
    try:
        data = r.json()
    except Exception:
        raise FazerError(f"http {r.status_code}: {r.text[:200]}")
    if r.status_code != 200 or not data.get("ok"):
        raise FazerError(f"http {r.status_code}: {str(data)[:300]}")
    return data

def _fazer_fetch_catalog():
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
    apple = [c for c in cats if re.search(r"apple|itunes", f"{c.get('name','')} {c.get('note','')}", re.I)]
    result = []
    for c in apple:
        d = _fazer_get("/giftcards/cards", {"category_id": c.get("category_id")})
        result.append({
            "category_id": str(c.get("category_id")),
            "name": c.get("name") or "",
            "note": c.get("note") or "",
            "offers": d.get("offers") or [],
        })
    return result

def fazer_load_catalog(force=False, allow_fetch=True):
    fresh = _catalog["cats"] is not None and time.time() - _catalog["ts"] < FAZER_CACHE_SECONDS
    if fresh and not force:
        return _catalog["cats"]
    if not allow_fetch:
        return _catalog["cats"]
    with _catalog_lock:
        fresh = _catalog["cats"] is not None and time.time() - _catalog["ts"] < FAZER_CACHE_SECONDS
        if fresh and not force:
            return _catalog["cats"]
        cats = _fazer_fetch_catalog()
        _catalog["cats"] = cats
        _catalog["ts"] = time.time()
        return cats

COUNTRY_RE = {
    "apple_gift_tr": re.compile(r"turk|türk|🇹🇷|\btr\b|\btry\b", re.I),
    "apple_gift_in": re.compile(r"india|🇮🇳|\binr\b", re.I),
    "apple_gift_fr": re.compile(r"france|french|🇫🇷|\bfr\b", re.I),
}

def _norm_name(s):
    s = str(s or "")
    s = re.sub(r"(?<=\d)[,\s](?=\d{3}(?!\d))", "", s)   # 1,500 -> 1500
    s = re.sub(r"(\d)\.0+(?!\d)", r"\1", s)              # 50.00 -> 50
    return s

def fazer_match(product_id, label, cats):
    """يرجع (mapping, reason). reason: no_catalog / no_offer / ambiguous / manual."""
    if not cats:
        return None, "no_catalog"
    num = label.split()[0]
    country = COUNTRY_RE.get(product_id)
    manual = FAZER_MANUAL_MAP.get((product_id, label))
    if manual:
        for c in cats:
            if c["category_id"] != str(manual["category_id"]):
                continue
            for o in c["offers"]:
                if str(o.get("card_id")) == str(manual["card_id"]):
                    return _mapping(c, o), "manual"
        return {"category_id": str(manual["category_id"]), "card_id": str(manual["card_id"]),
                "price_usd": None, "stock": None, "name": label}, "manual"
    num_re = re.compile(rf"(?<![\d.]){re.escape(num)}(?!\d|\.\d)")
    found = []
    for c in cats:
        cat_ok = bool(country and country.search(f"{c['name']} {c['note']}"))
        for o in c["offers"]:
            name = _norm_name(o.get("name"))
            offer_ok = bool(country and country.search(name))
            if (cat_ok or offer_ok) and num_re.search(name):
                found.append((c, o))
    uniq = {(c["category_id"], str(o.get("card_id"))): (c, o) for c, o in found}
    if not uniq:
        return None, "no_offer"
    if len(uniq) > 1:
        return None, "ambiguous"
    c, o = next(iter(uniq.values()))
    return _mapping(c, o), "auto"

def _mapping(c, o):
    return {
        "category_id": c["category_id"],
        "card_id": str(o.get("card_id")),
        "price_usd": o.get("price_usd"),
        "stock": o.get("stock"),
        "name": o.get("name") or "",
    }

def fazer_resolve(product_id, label, allow_fetch=True):
    cats = fazer_load_catalog(allow_fetch=allow_fetch)
    mapping, _ = fazer_match(product_id, label, cats)
    return mapping

def fazer_order(category_id, card_id, idem_key):
    if not FAZER_API_KEY:
        raise FazerError("missing FAZER_API_KEY")
    try:
        r = requests.post(
            FAZER_BASE_URL + "/giftcards/order",
            headers=_fazer_headers({"Idempotency-Key": idem_key[:250]}),
            json={"category_id": category_id, "card_id": card_id, "quantity": 1},
            timeout=45,
        )
    except Exception as e:
        raise FazerError(f"network: {e}")
    try:
        data = r.json()
    except Exception:
        raise FazerError(f"http {r.status_code}: {r.text[:200]}")
    return r.status_code, data

def extract_codes(order):
    cards = None
    if isinstance(order, dict):
        for k in ("cards", "codes", "items"):
            if order.get(k):
                cards = order[k]
                break
    out = []

    def add(c):
        if isinstance(c, str):
            if c.strip():
                out.append(c.strip())
        elif isinstance(c, dict):
            for k in ("code", "pin", "key", "value", "serial", "redeem_code", "card"):
                if c.get(k):
                    out.append(str(c[k]))
                    return
            vals = [str(v) for v in c.values() if isinstance(v, (str, int)) and str(v) != ""]
            if vals:
                out.append(" | ".join(vals))
        elif c is not None:
            out.append(str(c))

    if isinstance(cards, list):
        for c in cards:
            add(c)
    elif cards:
        add(cards)
    return out

# ============================================================
# ========== مساعدات الإشعارات ==========
# ============================================================
def alert_admin(text):
    try:
        bot.send_message(ADMIN_CHAT_ID, text[:3900], parse_mode="HTML")
    except Exception as e:
        print(f"alert_admin failed: {e}")

def send_long(chat_id, text):
    for i in range(0, len(text), 3800):
        bot.send_message(chat_id, text[i:i + 3800])

def is_admin_msg(message):
    return str(message.chat.id) == str(ADMIN_CHAT_ID)

def support_markup(lang):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text=t(lang, "support_btn"), url=MY_PRIVATE_CHAT_LINK))
    return markup

# ============================================================
# ========== معالجة الدفع والتسليم ==========
# ============================================================
def fulfill_order(chat_id, uid, lang, claim, canon, retry=False):
    """يشتري من FAZER ويسلّم الكود. retry=True: إعادة محاولة تلقائية صامتة عند الفشل."""
    lock_key = f"rk:lock:{canon}"
    try:
        if not kv_set(lock_key, "1", ex=90, nx=True):
            if not retry:
                bot.send_message(chat_id, t(lang, "processing"))
            return
    except StorageError:
        if not retry:
            bot.send_message(chat_id, t(lang, "temp_error"))
        return
    try:
        _fulfill_locked(chat_id, uid, lang, claim, canon, retry)
    finally:
        try:
            kv_del(lock_key)
        except StorageError:
            pass

def _fulfill_locked(chat_id, uid, lang, claim, canon, retry):
    pid, label = claim["product_id"], claim["label"]
    price = _to_decimal(claim.get("price"))
    pname = html.escape(claim.get("product_name") or f"{pid} {label}")
    was_pending = claim.get("status") == "paid_pending"

    def mark(status):
        claim["status"] = status
        try:
            kv_set(f"rk:tx:{canon}", json.dumps(claim))
        except StorageError:
            pass
        if status == "paid_pending":
            pend_add(canon)
        else:
            pend_remove(canon)

    def failed(admin_text):
        """فشل مؤقت: نحفظ الطلب، وننبه الأدمن والزبون مرة واحدة فقط (ليس في كل إعادة محاولة)."""
        first_time = claim.get("status") != "paid_pending"
        mark("paid_pending")
        if not retry and first_time:
            alert_admin(admin_text)
            monitor_send("⏳ <b>طلب معلّق</b>\n\n" + admin_text)
        if not retry and claim.get("via") != "wallet":
            bot.send_message(chat_id, t(lang, "processing"), reply_markup=support_markup(lang))

    # Gemini: تسليم من Upstash (بدون FAZER)
    if pid == GEMINI_ID:
        _fulfill_gemini(chat_id, uid, lang, claim, canon, retry, mark, failed)
        return

    try:
        mapping = fazer_resolve(pid, label, allow_fetch=True)
    except FazerError as e:
        mapping = None
        print(f"fazer_resolve error: {e}")

    if not mapping:
        failed(
            f"⚠️ <b>دفع مقبول لكن لم أجد البطاقة في FAZER</b>\n\n"
            f"📦 {pname}\n👤 ID: <code>{uid}</code>\n"
            f"💵 {claim.get('paid')} USDT\n🧾 Binance: <code>{html.escape(canon)}</code>\n\n"
            f"استعمل /fazer_check. البوت سيعيد المحاولة تلقائياً كل بضع دقائق."
        )
        return

    cost = _to_decimal(mapping.get("price_usd")) if mapping.get("price_usd") is not None else None
    n = int(claim.get("idem_n", 0))
    idem_key = f"rk-{canon}" if n == 0 else f"rk-{canon}-{n}"
    try:
        status, data = fazer_order(mapping["category_id"], mapping["card_id"], idem_key)
    except FazerError as e:
        failed(
            f"⚠️ <b>فشل الاتصال بـ FAZER أثناء الشراء</b>\n\n📦 {pname}\n👤 <code>{uid}</code>\n"
            f"🧾 <code>{html.escape(canon)}</code>\n{html.escape(str(e))[:300]}\n\n"
            f"البوت سيعيد المحاولة تلقائياً."
        )
        return

    if status == 200 and isinstance(data, dict) and data.get("ok"):
        codes = extract_codes(data.get("order"))
        if codes:
            codes_html = "\n".join(f"<code>{html.escape(c)}</code>" for c in codes)
            text = t(lang, "delivered").format(
                product=pname, amount=html.escape(str(claim.get("paid"))), codes=codes_html
            )
            delivered_ok = True
            try:
                bot.send_message(chat_id, text, parse_mode="HTML")
            except Exception as e:
                delivered_ok = False
                alert_admin(
                    f"⚠️ <b>تعذر إرسال الكود للزبون</b> <code>{uid}</code>\n"
                    f"🧾 <code>{html.escape(canon)}</code>\n" + codes_html
                )
                print(f"deliver failed: {e}")
                monitor_send(f"⚠️ <b>تعذر إرسال الكود للزبون</b> {_user_link(uid)}\nالكود وصلك في البوت الرئيسي.")
            mark("delivered")
            clear_pending(uid)
            record_purchase(uid, pid, claim.get("product_name"), claim.get("price"), canon, via=claim.get("via", "binance"))

            # رسالة الشكر: تُرسل مرة واحدة فقط، بعد تسليم الكود فعلياً، ولا تؤثر على التسليم
            if delivered_ok:
                try:
                    bot.send_message(chat_id, t(lang, "thanks"))
                except Exception as e:
                    print(f"thanks message failed: {e}")

            margin = ""
            if cost is not None and price:
                diff = price - cost
                margin = f"\n💹 الربح التقريبي: {diff:.2f}$" + (" ⚠️ خسارة!" if diff < 0 else "")
            alert_admin(
                ("✅ <b>بيع تلقائي (بعد إعادة المحاولة)</b>" if retry or was_pending
                 else "✅ <b>بيع تلقائي</b>")
                + f"\n📦 {pname}\n👤 <code>{uid}</code>\n"
                f"💵 مدفوع: {claim.get('paid')} USDT"
                + (f" | تكلفة FAZER: {cost}$" if cost is not None else "") + margin
            )
            monitor_send(
                f"✅ <b>شراء جديد</b>\n\n📦 {pname}\n👤 {_user_link(uid)}\n"
                f"💵 {claim.get('paid')} USDT" + margin
            )
            return
        # الطلب مقبول لكن بلا أكواد بعد (نفس المفتاح يرجع نفس الطلب لاحقاً)
        failed(
            f"⚠️ <b>طلب FAZER بلا أكواد بعد</b>\n📦 {pname}\n👤 <code>{uid}</code>\n"
            f"🧾 <code>{html.escape(canon)}</code>\n"
            f"{html.escape(json.dumps(data.get('order'), ensure_ascii=False)[:1200])}"
        )
        return

    # فشل الشراء (رصيد ناقص، مخزون، حظر...)
    err = ""
    if isinstance(data, dict):
        err = f"{data.get('code', '')} {data.get('error', '')}"
    try:
        raw_err = json.dumps(data, ensure_ascii=False)[:500]
    except Exception:
        raw_err = str(data)[:500]
    if status == 402 or re.search(r"balance|insufficient|funds|credit|رصيد", f"{err} {raw_err}", re.I):
        monitor_send(
            "🚨 <b>رصيد FAZER خالص أو غير كافٍ!</b>\n\n"
            "اشحن الحساب، والبوت يكمل الطلبات المعلقة وحدو.\n"
            f"<code>{html.escape(err.strip())[:200]}</code>",
            key="fazer_balance", cooldown=1800,
        )
    # رفض واضح (4xx) = لم يُنشأ طلب، فنستعمل مفتاحاً جديداً في المحاولة القادمة
    if status in (400, 402, 403, 404, 422):
        claim["idem_n"] = n + 1
    failed(
        f"🚨 <b>فشل شراء FAZER</b> (HTTP {status})\n📦 {pname}\n👤 <code>{uid}</code>\n"
        f"🧾 <code>{html.escape(canon)}</code>\n{html.escape(err)[:300]}\n\n"
        f"إذا كان السبب الرصيد: اشحن حسابك، والبوت يكمل الطلب ويرسل الكود للزبون تلقائياً خلال دقائق."
    )

def retry_pending_orders():
    for canon in pend_list():
        try:
            claim = kv_get_json(f"rk:tx:{canon}")
        except StorageError:
            return
        if not claim or claim.get("status") == "delivered":
            pend_remove(canon)
            continue
        if time.time() - float(claim.get("ts", time.time())) > 3 * 86400:
            pend_remove(canon)
            alert_admin(f"⌛ توقفت إعادة المحاولة (مرت 3 أيام) للعملية <code>{html.escape(canon)}</code> — الزبون <code>{claim.get('user_id')}</code>. سلّم يدوياً.")
            monitor_send(f"⌛ <b>توقفت إعادة المحاولة (3 أيام)</b>\n🧾 <code>{html.escape(canon)}</code>\n👤 {_user_link(claim.get('user_id'))}\nسلّم يدوياً.")
            continue
        uid = claim["user_id"]
        try:
            fulfill_order(uid, uid, get_lang(uid), claim, canon, retry=True)
        except Exception as e:
            print(f"retry error for {canon}: {e}")
        time.sleep(2)

def pending_retry_loop():
    time.sleep(60)
    while True:
        try:
            if FAZER_API_KEY or db:
                retry_pending_orders()
        except Exception as e:
            print(f"pending_retry_loop error: {e}")
        time.sleep(180)

def process_order_id(message, order_id):
    uid = message.from_user.id
    chat_id = message.chat.id
    lang = get_lang(uid)

    try:
        inv_id = get_pending_invoice_id(uid)
        invoice = get_invoice(inv_id) if inv_id else None
    except StorageError:
        bot.send_message(chat_id, t(lang, "temp_error"))
        return
    if not invoice:
        bot.send_message(chat_id, t(lang, "expired"), reply_markup=support_markup(lang))
        return

    if time.time() - invoice["created_at"] > INVOICE_TTL + INVOICE_GRACE:
        clear_pending(uid)
        alert_admin(
            f"⌛ زبون <code>{uid}</code> أرسل رقم عملية بعد انتهاء الفاتورة\n"
            f"📦 {html.escape(invoice['product_name'])}\n🧾 <code>{html.escape(order_id)}</code>"
        )
        monitor_send(
            f"⌛ <b>زبون أرسل رقم عملية بعد انتهاء الفاتورة</b>\n\n"
            f"📦 {html.escape(invoice['product_name'])}\n👤 {_user_link(uid)}\n🧾 <code>{html.escape(order_id)}</code>"
        )
        bot.send_message(chat_id, t(lang, "expired"), reply_markup=support_markup(lang))
        return

    try:
        if kv_incr_window(f"rk:att:{uid}", 600) > MAX_ATTEMPTS:
            bot.send_message(chat_id, t(lang, "too_many"), reply_markup=support_markup(lang))
            return
    except StorageError:
        bot.send_message(chat_id, t(lang, "temp_error"))
        return

    bot.send_message(chat_id, t(lang, "verifying"))

    try:
        status, tx = find_binance_payment(order_id, invoice["created_at"])
    except BinanceError as e:
        print(f"binance error: {e}")
        alert_admin(f"🚨 <b>خطأ Binance أثناء التحقق</b>\n<code>{html.escape(str(e))[:400]}</code>")
        monitor_send(f"🚨 <b>خطأ Binance أثناء التحقق</b>\n<code>{html.escape(str(e))[:300]}</code>",
                     key="binance_err", cooldown=900)
        bot.send_message(chat_id, t(lang, "no_binance"), reply_markup=support_markup(lang))
        return

    if status == "not_found":
        bot.send_message(chat_id, t(lang, "not_found"))
        return
    if status == "bad_currency":
        bot.send_message(chat_id, t(lang, "bad_currency"), reply_markup=support_markup(lang))
        return
    if status == "old":
        bot.send_message(chat_id, t(lang, "old_tx"))
        return

    _settle_payment(chat_id, uid, lang, inv_id, invoice, tx)

def _settle_payment(chat_id, uid, lang, inv_id, invoice, tx):
    """يطبّق الدفعة على الفاتورة: شحن محفظة، أو دفعة ناقصة تُجمع، أو دفعة مكتملة تُسلَّم."""
    need = _to_decimal(invoice["price_usdt"])
    canon = tx["tx_id"]
    amount = tx["amount"]
    is_topup = invoice["product_id"] == TOPUP_PID

    try:
        existing = kv_get_json(f"rk:tx:{canon}")
        if existing:  # طلب مكتمل سابق: إعادة محاولة تسليم لنفس الزبون فقط
            if is_topup or str(existing.get("user_id")) != str(uid):
                bot.send_message(chat_id, t(lang, "used"))
                return
            if existing.get("status") == "delivered":
                clear_pending(uid)
                bot.send_message(chat_id, t(lang, "used"), reply_markup=support_markup(lang))
                return
            fulfill_order(chat_id, uid, lang, existing, canon)
            return
        owner = kv_get(f"rk:txu:{canon}")  # عملية سُجلت سابقاً كدفعة جزئية/شحن
        if owner is not None:
            if is_topup or str(owner) != str(inv_id) or kv_get(f"rk:invpaid:{inv_id}") is not None:
                bot.send_message(chat_id, t(lang, "used"))
                return
            acc = kv_get_json(f"rk:invp:{inv_id}") or {}
            rest = max(Decimal(0), need - _to_decimal(acc.get("sum", 0)))
            bot.send_message(chat_id, wt(lang, "already_counted").format(rest=f"{rest:.2f}"), parse_mode="HTML")
            return
    except StorageError:
        bot.send_message(chat_id, t(lang, "temp_error"))
        return

    if is_topup:
        _handle_topup_tx(chat_id, uid, lang, inv_id, invoice, tx)
        return

    if not db and amount < need:  # بدون Upstash لا يمكن جمع الدفعات
        bot.send_message(
            chat_id,
            t(lang, "underpaid").format(paid=amount.normalize(), need=need),
            reply_markup=support_markup(lang),
        )
        return

    if not _ilock(inv_id):
        bot.send_message(chat_id, t(lang, "temp_error"))
        return
    claim = None
    try:
        if kv_get(f"rk:invpaid:{inv_id}") is not None:
            bot.send_message(chat_id, t(lang, "used"))
            return
        if kv_get(f"rk:invconv:{inv_id}") is not None:  # تحولت دفعاتها للمحفظة
            bot.send_message(chat_id, t(lang, "expired"), reply_markup=support_markup(lang))
            return
        acc = kv_get_json(f"rk:invp:{inv_id}") or {}
        txs = dict(acc.get("txs") or {})
        total = _to_decimal(acc.get("sum", 0)) + amount

        if total < need:  # دفعة ناقصة: نسجلها ونجمعها مع التالية
            if not kv_set(f"rk:txu:{canon}", str(inv_id), nx=True):
                bot.send_message(chat_id, t(lang, "used"))
                return
            txs[canon] = str(amount)
            acc.update({
                "uid": uid, "pname": invoice["product_name"], "pid": invoice["product_id"],
                "need": str(need), "txs": txs, "sum": str(total),
                "exp": invoice["created_at"] + INVOICE_TTL + INVOICE_GRACE,
            })
            kv_set(f"rk:invp:{inv_id}", json.dumps(acc), ex=3 * 86400)
            part_add(inv_id)
            bot.send_message(
                chat_id,
                wt(lang, "partial").format(paid=f"{total:.2f}", need=f"{need:.2f}", rest=f"{need - total:.2f}"),
                parse_mode="HTML",
            )
            return

        claim = {
            "user_id": uid,
            "invoice_id": inv_id,
            "product_id": invoice["product_id"],
            "label": invoice["label"],
            "product_name": invoice["product_name"],
            "price": invoice["price_usdt"],
            "paid": format(total.normalize(), "f"),
            "txs": list(txs.keys()) + [canon],
            "via": "binance",
            "status": "claimed",
            "ts": int(time.time()),
        }
        if not kv_set(f"rk:tx:{canon}", json.dumps(claim), nx=True):
            bot.send_message(chat_id, t(lang, "used"))
            return
        if not kv_set(f"rk:invpaid:{inv_id}", canon, nx=True):
            kv_del(f"rk:tx:{canon}")
            bot.send_message(chat_id, t(lang, "used"))
            return
        kv_del(f"rk:invp:{inv_id}")
        part_remove(inv_id)
    except StorageError:
        bot.send_message(chat_id, t(lang, "temp_error"))
        return
    finally:
        _iunlock(inv_id)

    fulfill_order(chat_id, uid, lang, claim, canon)

# ============================================================
# ========== أوامر الأدمن للتشخيص ==========
# ============================================================
@bot.message_handler(commands=["binance_test"])
def binance_test_command(message):
    if not is_admin_msg(message):
        return
    try:
        now = int(time.time() * 1000)
        txs = binance_pay_history(now - 3 * 24 * 3600 * 1000, now)
    except BinanceError as e:
        bot.reply_to(message, f"❌ Binance: {str(e)[:500]}")
        return
    if not txs:
        bot.reply_to(message, "✅ الاتصال بـ Binance يعمل، لكن لا توجد عمليات في آخر 3 أيام.")
        return
    lines = ["✅ الاتصال بـ Binance يعمل. آخر العمليات:"]
    for tx in txs[:8]:
        ts = time.strftime("%m-%d %H:%M", time.gmtime(int(tx.get("transactionTime") or 0) / 1000))
        lines.append(
            f"• {tx.get('orderType', '?')} | {tx.get('amount')} {tx.get('currency')} | {ts} UTC\n"
            f"  transactionId: {tx.get('transactionId')}"
        )
    send_long(message.chat.id, "\n".join(lines))

@bot.message_handler(commands=["fazer_check"])
def fazer_check_command(message):
    if not is_admin_msg(message):
        return
    try:
        cats = fazer_load_catalog(force=True)
    except FazerError as e:
        bot.reply_to(message, f"❌ FAZER: {str(e)[:500]}")
        return
    lines = [f"✅ كتالوج Apple: {len(cats)} قسم"]
    for pid, variants in GIFT_VARIANTS.items():
        lines.append(f"\n— {pid}")
        for label, price in variants:
            m, reason = fazer_match(pid, label, cats)
            if m:
                lines.append(f"✅ {label} → {m['card_id']} | تكلفة {m['price_usd']}$ | بيع {price}$ | مخزون {m['stock']}")
            else:
                lines.append(f"❌ {label} → {reason}")
    send_long(message.chat.id, "\n".join(lines))

@bot.message_handler(commands=["fazer_catalog"])
def fazer_catalog_command(message):
    if not is_admin_msg(message):
        return
    parts = (message.text or "").split(maxsplit=1)
    try:
        cats = fazer_load_catalog(force=True)
    except FazerError as e:
        bot.reply_to(message, f"❌ FAZER: {str(e)[:500]}")
        return
    if len(parts) == 2:
        cid = parts[1].strip()
        for c in cats:
            if c["category_id"] == cid:
                lines = [f"{c['name']} ({cid})"]
                for o in c["offers"]:
                    lines.append(f"{o.get('card_id')} | {o.get('name')} | {o.get('price_usd')}$ | stock {o.get('stock')}")
                send_long(message.chat.id, "\n".join(lines))
                return
        bot.reply_to(message, "قسم غير موجود.")
        return
    lines = ["أقسام Apple (استعمل /fazer_catalog <category_id> لرؤية العروض):"]
    for c in cats:
        lines.append(f"{c['category_id']} | {c['name']} | {len(c['offers'])} عرض")
    send_long(message.chat.id, "\n".join(lines))

def set_user_commands(chat_id, lang):
    if BotCommand is None:
        return
    try:
        cmds = [
            BotCommand("update", t(lang, "cmd_update")),
            BotCommand("language", t(lang, "cmd_language")),
            BotCommand("support", t(lang, "cmd_support")),
        ]
        if str(chat_id) == str(ADMIN_CHAT_ID):
            cmds.append(BotCommand("prices", "💲 التحكم في الأسعار"))
            cmds.append(BotCommand("admin", "🛠️ لوحة الأدمن (المحافظ)"))
        bot.set_my_commands(cmds, scope=BotCommandScopeChat(chat_id))
    except Exception as e:
        print(f"Could not set commands: {e}")

def set_default_commands():
    if BotCommand is None:
        return
    try:
        bot.set_my_commands(
            [
                BotCommand("update", "🔄 تحديث / Refresh / Actualiser"),
                BotCommand("language", "🌐 اللغة / Language / Langue"),
                BotCommand("support", "💬 الدعم / Support"),
            ]
        )
    except Exception as e:
        print(f"Could not set default commands: {e}")

def find_product(product_id):
    return next((p for p in products if p["id"] == product_id), None)

def generate_store_keyboard(lang):
    sync_stock()
    markup = InlineKeyboardMarkup(row_width=2)
    for item in products:
        if item.get("type") == "separator":
            markup.add(InlineKeyboardButton(text=tr(item, "text", lang), callback_data="noop"))
            continue
        stock_display = item["stock"] if item["stock"] == "♾️" else f"📦 {item['stock']}"
        button_text = f"{item['icon']} {tr(item, 'name', lang)} | {item['price']} | {stock_display}"
        markup.add(InlineKeyboardButton(text=button_text, callback_data=f"buy_{item['id']}"))
    markup.add(InlineKeyboardButton(text=t(lang, "change_lang"), callback_data="change_lang"))
    markup.row(
        InlineKeyboardButton(text=wt(lang, "btn_profile"), callback_data="pf_profile"),
        InlineKeyboardButton(text=wt(lang, "btn_history"), callback_data="pf_hist"),
    )
    markup.add(InlineKeyboardButton(text=wt(lang, "btn_wallet"), callback_data="pf_wallet"))
    return markup

def build_reply_keyboard(lang):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton(t(lang, "kb_start")), KeyboardButton(t(lang, "kb_products")))
    markup.row(KeyboardButton(t(lang, "kb_support")), KeyboardButton(t(lang, "kb_lang")))
    markup.row(KeyboardButton(t(lang, "kb_update")))
    return markup

def send_persistent_menu(chat_id, lang):
    bot.send_message(chat_id, t(lang, "menu_hint"), reply_markup=build_reply_keyboard(lang))

KB_START_TEXTS = {TEXTS[l]["kb_start"] for l in SUPPORTED_LANGS}
KB_PRODUCTS_TEXTS = {TEXTS[l]["kb_products"] for l in SUPPORTED_LANGS}
KB_SUPPORT_TEXTS = {TEXTS[l]["kb_support"] for l in SUPPORTED_LANGS}
KB_LANG_TEXTS = {TEXTS[l]["kb_lang"] for l in SUPPORTED_LANGS}
KB_UPDATE_TEXTS = {TEXTS[l]["kb_update"] for l in SUPPORTED_LANGS}

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

def send_card(chat_id, product, caption, markup):
    """يرسل بطاقة بالصورة ثم النص."""
    for photo in (product.get("image"), UNIFIED_IMAGE_URL):
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
                return
            except Exception:
                continue
    bot.send_message(chat_id, caption.replace("*", ""), reply_markup=markup)

@bot.message_handler(commands=["start"])
def send_welcome(message):
    register_user(message.from_user.id)
    ensure_profile(message.from_user.id, message.from_user.first_name)
    uid = str(message.from_user.id)
    if uid in user_lang:
        lang = get_lang(uid)
        set_user_commands(message.chat.id, lang)
        send_persistent_menu(message.chat.id, lang)
        send_main_menu(message.chat.id, lang)
    else:
        send_language_menu(message.chat.id)

def refresh_for_user(chat_id, user_id):
    register_user(user_id)
    ensure_profile(user_id)
    uid = str(user_id)
    if uid in user_lang:
        lang = get_lang(uid)
        set_user_commands(chat_id, lang)
        send_persistent_menu(chat_id, lang)
        send_main_menu(chat_id, lang)
    else:
        send_language_menu(chat_id)

@bot.message_handler(commands=["update", "refresh"])
def update_command(message):
    refresh_for_user(message.chat.id, message.from_user.id)

@bot.message_handler(commands=["language", "lang"])
def choose_language(message):
    register_user(message.from_user.id)
    send_language_menu(message.chat.id)

@bot.message_handler(commands=["support"])
def support_command(message):
    register_user(message.from_user.id)
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

def notify_admin_interest(user, product, lang):
    try:
        username = f"@{user.username}" if user.username else user.first_name
        text = (
            f"🔔 <b>زبون طلب أن يُعلَم عند توفر منتج نفد من المخزون</b>\n\n"
            f"👤 الزبون: {html.escape(username)} (ID: <code>{user.id}</code>)\n"
            f"📦 المنتج: <b>{html.escape(product['name'])}</b>\n"
            f"💰 السعر: <b>{html.escape(product['price'])}</b>\n"
            f"🌐 اللغة: {lang}"
        )
        bot.send_message(ADMIN_CHAT_ID, text, parse_mode="HTML")
    except Exception as e:
        print(f"Error sending admin interest notification: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def handle_set_lang(call):
    lang = call.data.replace("lang_", "")
    if lang not in SUPPORTED_LANGS:
        bot.answer_callback_query(call.id)
        return
    save_lang(call.from_user.id, lang)
    register_user(call.from_user.id)
    ensure_profile(call.from_user.id, call.from_user.first_name)
    set_user_commands(call.message.chat.id, lang)
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    send_persistent_menu(call.message.chat.id, lang)
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

@bot.message_handler(func=lambda m: m.text in KB_START_TEXTS)
def handle_kb_start(message):
    register_user(message.from_user.id)
    lang = get_lang(message.from_user.id)
    bot.send_message(message.chat.id, t(lang, "start_guide"))

@bot.message_handler(func=lambda m: m.text in KB_PRODUCTS_TEXTS)
def handle_kb_products(message):
    register_user(message.from_user.id)
    lang = get_lang(message.from_user.id)
    send_main_menu(message.chat.id, lang)

@bot.message_handler(func=lambda m: m.text in KB_SUPPORT_TEXTS)
def handle_kb_support(message):
    support_command(message)

@bot.message_handler(func=lambda m: m.text in KB_LANG_TEXTS)
def handle_kb_lang(message):
    register_user(message.from_user.id)
    send_language_menu(message.chat.id)

@bot.message_handler(func=lambda m: m.text in KB_UPDATE_TEXTS)
def handle_kb_update(message):
    refresh_for_user(message.chat.id, message.from_user.id)

# ========== بطاقات الهداية: صفحة المنتج (الوصف + أزرار القيم) ==========
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_") and find_product(call.data[4:]) and find_product(call.data[4:]).get("id") in GIFT_VARIANTS)
def handle_gift_card_select(call):
    product_id = call.data.replace("buy_", "")
    selected_product = find_product(product_id)
    if not selected_product or product_id not in GIFT_VARIANTS:
        bot.answer_callback_query(call.id)
        return

    lang = get_lang(call.from_user.id)
    if call.message.chat.type == "private":
        register_user(call.from_user.id)

    # إشعار الأدمن بأن الزبون اختار بطاقة هداية
    notify_admin(call.from_user, selected_product, lang)

    # أزرار القيم (زر لكل قيمة) + رجوع
    gift_markup = InlineKeyboardMarkup(row_width=1)
    for i, (label, price) in enumerate(GIFT_VARIANTS[product_id]):
        gift_markup.add(InlineKeyboardButton(
            text=f"{selected_product['icon']} {label} | ${price}",
            callback_data=f"var_{product_id}_{i}",
        ))
    gift_markup.add(InlineKeyboardButton(text=t(lang, "back"), callback_data="back_to_main"))

    # نفس شكل صفحة المنتج: اخترت + السعر + المتوفر + الوصف (بدون أسعار القيم) + سطر التوجيه
    caption = (
        f"{t(lang, 'chosen')} *{tr(selected_product, 'name', lang)}*\n"
        f"{t(lang, 'price')} *{selected_product['price']}*\n"
        f"{t(lang, 'available')} *♾️*\n\n"
        f"{t(lang, 'description')}\n"
        f"{clean_gift_description(tr(selected_product, 'description', lang))}\n\n"
        f"{t(lang, 'choose_card')}"
    )
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    send_card(call.message.chat.id, selected_product, caption, gift_markup)
    bot.answer_callback_query(call.id)

# ========== اختيار قيمة بطاقة الهداية ← شاشة الدفع مباشرة ==========
def build_invoice_text(lang, invoice, product):
    return (
        f"<b>{t(lang, 'invoice_title')}</b>\n\n"
        f"📦 {html.escape(tr(product, 'name', lang))} — {html.escape(invoice['label'])}\n"
        f"{t(lang, 'invoice_amount')} <b>{html.escape(str(invoice['price_usdt']))} USDT</b>\n\n"
        f"💳 <b>Binance Pay ID:</b>\n<code>{html.escape(BINANCE_PAY_ID)}</code>\n\n"
        f"{t(lang, 'invoice_steps')}\n\n"
        f"⏱️ {t(lang, 'invoice_expire')}"
    )

def build_invoice_markup(lang, invoice_id, wallet=False):
    markup = InlineKeyboardMarkup()
    if wallet:
        markup.add(InlineKeyboardButton(text=wt(lang, "wpay_btn"), callback_data=f"wpay_{invoice_id}"))
    btn = None
    if CopyTextButton is not None:
        try:
            btn = InlineKeyboardButton(text=t(lang, "copy_id"), copy_text=CopyTextButton(text=BINANCE_PAY_ID))
        except Exception:
            btn = None
    if btn is None:
        btn = InlineKeyboardButton(text=t(lang, "copy_id"), callback_data=f"copy_id_{invoice_id}")
    markup.add(btn)
    markup.add(InlineKeyboardButton(text=t(lang, "cancel"), callback_data=f"cancel_{invoice_id}"))
    return markup

@bot.callback_query_handler(func=lambda call: call.data.startswith("var_"))
def handle_gift_variant(call):
    try:
        product_id, idx = call.data[4:].rsplit("_", 1)
        product = find_product(product_id)
        label, price = GIFT_VARIANTS[product_id][int(idx)]
    except Exception:
        bot.answer_callback_query(call.id)
        return

    lang = get_lang(call.from_user.id)
    if call.message.chat.type == "private":
        register_user(call.from_user.id)

    # تحقق سريع من المخزون (من الكاش فقط، بدون انتظار)
    try:
        mapping = fazer_resolve(product_id, label, allow_fetch=False)
        if mapping and mapping.get("stock") is not None and int(mapping["stock"]) <= 0:
            monitor_send(f"📦 <b>نفدت قيمة في FAZER</b>\n{html.escape(product['name'])} — {html.escape(label)}",
                         key=f"fz_out_{product_id}_{label}", cooldown=3600)
            bot.answer_callback_query(call.id, t(lang, "out_variant"), show_alert=True)
            return
    except Exception:
        pass

    # إشعار الأدمن بالقيمة المختارة
    notify_admin(call.from_user, {"name": f"{product['name']} — {label}", "price": f"${price}"}, lang)

    try:
        invoice_id = create_invoice(call.from_user.id, product_id, label, price, f"{product['name']} — {label}")
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
        reply_markup=build_invoice_markup(lang, invoice_id, _wallet_covers(call.from_user.id, invoice.get("price_usdt"))),
    )
    attach_invoice_msg(invoice_id, sent)
    bot.answer_callback_query(call.id)

# ========== زر النسخ (احتياطي للنسخ القديمة من المكتبة) ==========
@bot.callback_query_handler(func=lambda call: call.data.startswith("copy_id_"))
def handle_copy_id(call):
    bot.answer_callback_query(call.id, f"💳 {BINANCE_PAY_ID}", show_alert=True)

# ========== إلغاء الفاتورة ==========
@bot.callback_query_handler(func=lambda call: call.data.startswith("cancel_"))
def handle_cancel_invoice(call):
    lang = get_lang(call.from_user.id)
    try:
        _inv_id = get_pending_invoice_id(call.from_user.id)
        _inv = get_invoice(_inv_id) if _inv_id else None
    except StorageError:
        _inv = None
    if _inv:
        monitor_send(
            f"❌ <b>إلغاء فاتورة</b>\n\n📦 {html.escape(_inv['product_name'])}\n"
            f"💵 {html.escape(str(_inv['price_usdt']))} USDT\n👤 {_user_link(call.from_user.id)}"
        )
    _cancel_id = call.data.replace("cancel_", "", 1)
    inv_live_remove(_cancel_id)  # ألغاها الزبون بنفسه: لا إشعار انتهاء
    try:
        _cinv = get_invoice(_cancel_id)
    except StorageError:
        _cinv = None
    if _cinv and _cinv.get("product_id") != TOPUP_PID:
        convert_partial(_cancel_id)  # إن كانت فيها دفعات جزئية تتحول لمحفظته
        record_cancel(call.from_user.id, _cancel_id)
    clear_pending(call.from_user.id)
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    send_main_menu(call.message.chat.id, lang)
    bot.answer_callback_query(call.id, t(lang, "cancelled"))

# ========== Gemini: صفحة المنتج (الوصف + أزرار العدد 1 و 2) ==========
@bot.callback_query_handler(func=lambda call: call.data == f"buy_{GEMINI_ID}")
def handle_gemini_select(call):
    product = find_product(GEMINI_ID)
    lang = get_lang(call.from_user.id)
    gt = GEMINI_TEXTS.get(lang, GEMINI_TEXTS["ar"])
    if call.message.chat.type == "private":
        register_user(call.from_user.id)

    notify_admin(call.from_user, product, lang)
    sync_stock()
    stock = product["stock"]

    markup = InlineKeyboardMarkup(row_width=3)
    if stock > 0:
        markup.row(*[
            InlineKeyboardButton(text=str(q), callback_data=f"gq_{q}")
            for q in GEMINI_QTYS if q <= stock
        ])
        bottom = gt["choose_qty"]
    else:
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

@bot.callback_query_handler(func=lambda call: call.data.startswith("gq_"))
def handle_gemini_qty(call):
    lang = get_lang(call.from_user.id)
    gt = GEMINI_TEXTS.get(lang, GEMINI_TEXTS["ar"])
    try:
        qty = int(call.data[3:])
    except ValueError:
        bot.answer_callback_query(call.id)
        return
    if qty not in GEMINI_QTYS:
        bot.answer_callback_query(call.id)
        return

    stock = gemini_stock()
    if stock < qty:
        msg = gt["out"] if stock <= 0 else gt["qty_left"].format(n=stock)
        bot.answer_callback_query(call.id, msg, show_alert=True)
        return

    product = find_product(GEMINI_ID)
    price = str((gemini_unit_price() * qty).quantize(Decimal("0.01")))
    label = f"x{qty}"
    full_name = f"{product['name']} — {label}"

    notify_admin(call.from_user, {"name": full_name, "price": f"${price}"}, lang)
    try:
        invoice_id = create_invoice(call.from_user.id, GEMINI_ID, label, price, full_name)
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
        reply_markup=build_invoice_markup(lang, invoice_id, _wallet_covers(call.from_user.id, invoice.get("price_usdt"))),
    )
    attach_invoice_msg(invoice_id, sent)
    bot.answer_callback_query(call.id)

# ========== منتجات عادية (ليست بطاقات هداية) ==========
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_") and find_product(call.data[4:]) and find_product(call.data[4:]).get("id") not in GIFT_VARIANTS)
def handle_product_view(call):
    product_id = call.data.replace("buy_", "")
    selected_product = find_product(product_id)
    if not selected_product:
        bot.answer_callback_query(call.id)
        return
    sync_prices()

    lang = get_lang(call.from_user.id)
    if call.message.chat.type == "private":
        register_user(call.from_user.id)

    notify_admin(call.from_user, selected_product, lang)

    markup = InlineKeyboardMarkup()
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
    send_card(call.message.chat.id, selected_product, caption, markup)
    bot.answer_callback_query(call.id)

@bot.message_handler(content_types=["photo"])
def get_photo_file_id(message):
    if str(message.chat.id) != str(ADMIN_CHAT_ID):
        return
    file_id = message.photo[-1].file_id
    bot.reply_to(message, f"file_id:\n<code>{file_id}</code>", parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data == "noop")
def handle_noop(call):
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "back_to_main")
def handle_back(call):
    clear_pending(call.from_user.id)
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    send_main_menu(call.message.chat.id, get_lang(call.from_user.id))
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("notify_"))
def handle_notify(call):
    product_id = call.data.replace("notify_", "")
    product = find_product(product_id)
    lang = get_lang(call.from_user.id)
    if product:
        notify_admin_interest(call.from_user, product, lang)
    bot.answer_callback_query(
        call.id,
        text=t(lang, "notify_ok"),
        show_alert=True,
    )

# ============================================================
# ========== لوحة التحكم في الأسعار (الأدمن فقط) ==========
# ============================================================
PRICE_STEPS = ("-1", "-0.5", "+0.5", "+1")
STOCK_STEPS = ("-5", "-1", "+1", "+5")
_price_wait = {}  # admin_id -> ("price" | "stock", product_id) (ينتظر رقماً يدوياً)

def _fmt_stock(v):
    return "♾️" if v == "♾️" else str(v)

def _parse_stock(text):
    s = text.strip().replace("،", "")
    if s in ("inf", "∞", "♾️", "♾"):
        return "inf"
    if not s.isdigit():
        return None
    v = int(s)
    return v if 0 <= v <= 100000 else None

def _save_stock(pid, value):
    """value: رقم أو "inf". يحفظ في Upstash ويحدّث الذاكرة."""
    if not db:
        return False
    db.hset(STOCK_KEY, pid, str(value))
    p = find_product(pid)
    if p:
        p["stock"] = "♾️" if value == "inf" else int(value)
    return True

def _stock_changed(pid, old, new):
    p = find_product(pid)
    monitor_send(
        f"📦 <b>تغيير كمية</b>\n\n📦 {html.escape(p['name'])}\n"
        f"{html.escape(_fmt_stock(old))} ➜ <b>{html.escape(_fmt_stock(new))}</b>"
    )

def _is_admin_user(user_id):
    return str(user_id) == str(ADMIN_CHAT_ID)

def _cur_price(p):
    return Decimal(p["price"].lstrip("$"))

def _parse_price(text):
    try:
        v = Decimal(text.strip().replace("$", "").replace(",", ".").replace("،", "."))
    except InvalidOperation:
        return None
    if v <= 0 or v > 1000:
        return None
    return v.quantize(Decimal("0.01"))

def _save_price(pid, value):
    """يحفظ في Upstash (يقرأه بوت المتجر فوراً) ويحدّث الذاكرة."""
    if not db:
        return False
    db.hset(PRICES_KEY, pid, str(value))
    p = find_product(pid)
    if p:
        p["price"] = f"${value:.2f}"
    return True

def _pr_show(chat_id, msg_id, text, markup):
    try:
        if msg_id:
            bot.edit_message_text(text, chat_id, msg_id, parse_mode="HTML", reply_markup=markup)
            return
    except Exception as e:
        if "not modified" in str(e).lower():
            return
    bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)

def show_price_list(chat_id, msg_id=None):
    sync_stock()
    markup = InlineKeyboardMarkup(row_width=1)
    price_ids = {p["id"] for p in editable_products()}
    stock_ids = {p["id"] for p in stock_editable_products()}
    for p in products:
        if p.get("type") == "separator" or p["id"] not in (price_ids | stock_ids):
            continue
        markup.add(InlineKeyboardButton(
            text=f"{p['icon']} {p['name']} | {p['price']} | 📦 {_fmt_stock(p['stock'])}",
            callback_data=f"pr_sel_{p['id']}",
        ))
    text = "💲 <b>التحكم في الأسعار والكميات</b>\nاختر المنتج:"
    if not db:
        text += "\n\n⚠️ Upstash غير متصل: التعديل لن يُحفظ."
    _pr_show(chat_id, msg_id, text, markup)

def show_price_panel(chat_id, msg_id, pid):
    sync_prices()
    p = find_product(pid)
    if not p:
        return show_price_list(chat_id, msg_id)
    markup = InlineKeyboardMarkup()
    text = f"{p['icon']} <b>{html.escape(p['name'])}</b>\n"

    if pid in {x["id"] for x in editable_products()}:
        markup.row(*[
            InlineKeyboardButton(text=f"{s}$", callback_data=f"pr_adj_{pid}_{s}")
            for s in PRICE_STEPS
        ])
        markup.add(InlineKeyboardButton(text="✏️ إدخال سعر يدوياً", callback_data=f"pr_man_{pid}"))
        markup.add(InlineKeyboardButton(text="♻️ رجوع للسعر الأصلي", callback_data=f"pr_rst_{pid}"))
        text += (
            f"\n💰 السعر الحالي: <b>{html.escape(p['price'])}</b>\n"
            f"📌 السعر الأصلي: {html.escape(BASE_PRICES[pid])}\n"
        )

    if pid in {x["id"] for x in stock_editable_products()}:
        markup.row(*[
            InlineKeyboardButton(text=f"{s} 📦", callback_data=f"pr_stk_{pid}_{s}")
            for s in STOCK_STEPS
        ])
        markup.row(
            InlineKeyboardButton(text="✏️ إدخال كمية", callback_data=f"pr_sman_{pid}"),
            InlineKeyboardButton(text="♾️ لانهائي", callback_data=f"pr_sinf_{pid}"),
        )
        markup.add(InlineKeyboardButton(text="♻️ رجوع للكمية الأصلية", callback_data=f"pr_srst_{pid}"))
        text += (
            f"\n📦 الكمية الحالية: <b>{html.escape(_fmt_stock(p['stock']))}</b>\n"
            f"📌 الكمية الأصلية: {html.escape(_fmt_stock(BASE_STOCK[pid]))}\n"
        )

    markup.add(InlineKeyboardButton(text="⬅️ القائمة", callback_data="pr_list"))
    _pr_show(chat_id, msg_id, text, markup)

def _price_changed(pid, old, new):
    p = find_product(pid)
    monitor_send(
        f"💲 <b>تغيير سعر</b>\n\n📦 {html.escape(p['name'])}\n"
        f"{old} ➜ <b>${new:.2f}</b>"
    )

@bot.message_handler(commands=["settings", "prices"])
def prices_command(message):
    if not is_admin_msg(message):
        return  # يتجاهل غير الأدمن بصمت
    _price_wait.pop(message.from_user.id, None)
    _adm_wait.pop(message.from_user.id, None)
    show_price_list(message.chat.id)

@bot.callback_query_handler(func=lambda c: c.data.startswith("pr_"))
def handle_price_callbacks(call):
    if not _is_admin_user(call.from_user.id):
        bot.answer_callback_query(call.id)
        return
    chat_id, msg_id, data = call.message.chat.id, call.message.message_id, call.data
    _price_wait.pop(call.from_user.id, None)
    _adm_wait.pop(call.from_user.id, None)

    if data == "pr_list":
        show_price_list(chat_id, msg_id)
        bot.answer_callback_query(call.id)
        return

    if data.startswith("pr_sel_"):
        show_price_panel(chat_id, msg_id, data[7:])
        bot.answer_callback_query(call.id)
        return

    if data.startswith("pr_man_"):
        pid = data[7:]
        _price_wait[call.from_user.id] = ("price", pid)
        p = find_product(pid)
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(text="❌ إلغاء", callback_data=f"pr_sel_{pid}"))
        _pr_show(chat_id, msg_id,
                 f"✏️ أرسل السعر الجديد لـ <b>{html.escape(p['name'])}</b>\nمثال: <code>2.5</code>",
                 markup)
        bot.answer_callback_query(call.id)
        return

    if data.startswith("pr_sman_"):
        pid = data[8:]
        p = find_product(pid)
        if not p or pid not in {x["id"] for x in stock_editable_products()}:
            bot.answer_callback_query(call.id)
            return
        _price_wait[call.from_user.id] = ("stock", pid)
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(text="❌ إلغاء", callback_data=f"pr_sel_{pid}"))
        _pr_show(chat_id, msg_id,
                 f"✏️ أرسل الكمية الجديدة لـ <b>{html.escape(p['name'])}</b>\n"
                 f"مثال: <code>25</code> (أو <code>inf</code> للانهائي)",
                 markup)
        bot.answer_callback_query(call.id)
        return

    if data.startswith("pr_sinf_") or data.startswith("pr_srst_") or data.startswith("pr_stk_"):
        if not db:
            bot.answer_callback_query(call.id, "⚠️ Upstash غير متصل", show_alert=True)
            return
        try:
            if data.startswith("pr_stk_"):
                pid, step = data[7:].rsplit("_", 1)
            else:
                pid, step = data[8:], None
            p = find_product(pid)
            if not p or pid not in {x["id"] for x in stock_editable_products()}:
                bot.answer_callback_query(call.id)
                return
            sync_prices()
            old = p["stock"]
            if data.startswith("pr_stk_"):
                base = 0 if old == "♾️" else int(old)
                new = max(0, min(100000, base + int(step)))
                _save_stock(pid, new)
            elif data.startswith("pr_sinf_"):
                new = "♾️"
                _save_stock(pid, "inf")
            else:
                db.hdel(STOCK_KEY, pid)
                p["stock"] = BASE_STOCK[pid]
                new = p["stock"]
        except Exception as e:
            bot.answer_callback_query(call.id, f"خطأ: {str(e)[:150]}", show_alert=True)
            return
        if new != old:
            _stock_changed(pid, old, new)
        show_price_panel(chat_id, msg_id, pid)
        bot.answer_callback_query(call.id, f"📦 {_fmt_stock(new)}")
        return

    if data.startswith("pr_rst_"):
        pid = data[7:]
        p = find_product(pid)
        if not p or not db:
            bot.answer_callback_query(call.id, "⚠️ Upstash غير متصل", show_alert=True)
            return
        old = p["price"]
        try:
            db.hdel(PRICES_KEY, pid)
        except Exception as e:
            bot.answer_callback_query(call.id, f"خطأ: {str(e)[:150]}", show_alert=True)
            return
        p["price"] = BASE_PRICES[pid]
        _price_changed(pid, old, _cur_price(p))
        show_price_panel(chat_id, msg_id, pid)
        bot.answer_callback_query(call.id, "♻️ تمت الاستعادة")
        return

    if data.startswith("pr_adj_"):
        try:
            pid, step = data[7:].rsplit("_", 1)
            p = find_product(pid)
            sync_prices()
            old = p["price"]
            new = (_cur_price(p) + Decimal(step)).quantize(Decimal("0.01"))
        except Exception:
            bot.answer_callback_query(call.id)
            return
        if new <= 0:
            bot.answer_callback_query(call.id, "❌ السعر لا يمكن أن يكون 0 أو أقل", show_alert=True)
            return
        try:
            ok = _save_price(pid, new)
        except Exception as e:
            bot.answer_callback_query(call.id, f"خطأ: {str(e)[:150]}", show_alert=True)
            return
        if not ok:
            bot.answer_callback_query(call.id, "⚠️ Upstash غير متصل", show_alert=True)
            return
        _price_changed(pid, old, new)
        show_price_panel(chat_id, msg_id, pid)
        bot.answer_callback_query(call.id, f"✅ ${new:.2f}")
        return

    bot.answer_callback_query(call.id)

def _awaiting_price(m):
    return (
        bool(m.text) and not m.text.startswith("/")
        and m.chat.type == "private" and _is_admin_user(m.from_user.id)
        and m.from_user.id in _price_wait
    )

@bot.message_handler(func=_awaiting_price, content_types=["text"])
def handle_manual_price(message):
    kind, pid = _price_wait.get(message.from_user.id)

    if kind == "stock":
        sval = _parse_stock(message.text)
        if sval is None:
            bot.reply_to(message, "❌ كمية غير صالحة. أرسل رقماً مثل: 25 (أو inf)")
            return
        p = find_product(pid)
        old = p["stock"]
        try:
            ok = _save_stock(pid, sval)
        except Exception as e:
            bot.reply_to(message, f"❌ خطأ في الحفظ: {str(e)[:200]}")
            return
        if not ok:
            bot.reply_to(message, "⚠️ Upstash غير متصل، لم تُحفظ الكمية.")
            return
        _price_wait.pop(message.from_user.id, None)
        _stock_changed(pid, old, p["stock"])
        show_price_panel(message.chat.id, None, pid)
        return

    value = _parse_price(message.text)
    if value is None:
        bot.reply_to(message, "❌ رقم غير صالح. أرسل مثلاً: 2.5")
        return
    p = find_product(pid)
    old = p["price"]
    try:
        ok = _save_price(pid, value)
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ في الحفظ: {str(e)[:200]}")
        return
    if not ok:
        bot.reply_to(message, "⚠️ Upstash غير متصل، لم يُحفظ السعر.")
        return
    _price_wait.pop(message.from_user.id, None)
    _price_changed(pid, old, value)
    show_price_panel(message.chat.id, None, pid)

# ============================================================
# ========== الملف الشخصي + سجل المشتريات + المحفظة ==========
# ============================================================
def wt(lang, key):
    return WALLET_TEXTS.get(lang, WALLET_TEXTS["ar"])[key]

def _money(cents):
    return f"{Decimal(int(cents)) / 100:.2f}"

def wallet_avail_c(p):
    """الرصيد المتاح = المكافآت + المشحون − المستبدل (يدوي) − المصروف في الشراء من المحفظة."""
    return max(0, p["reward_c"] + p["topup_c"] - p["redeemed_c"] - p["wspent_c"])

def _prof_key(uid):
    return f"rk:prof:{uid}"

def ensure_profile(uid, name=None):
    """ينشئ تاريخ الانضمام (مرة واحدة فقط) ويحدّث الاسم."""
    if not db:
        return
    try:
        k = _prof_key(uid)
        db.hsetnx(k, "joined", str(int(time.time())))
        if name:
            db.hset(k, "name", str(name)[:100])
    except Exception as e:
        print(f"ensure_profile error: {e}")

def prof_get(uid):
    h = {str(k): str(v) for k, v in (db.hgetall(_prof_key(uid)) or {}).items()}

    def _i(key):
        try:
            return int(float(h.get(key, 0) or 0))
        except ValueError:
            return 0

    # حسابات قديمة (قبل فصل المكافآت): المكافأة = 5% من الإنفاق
    reward = _i("reward_c") if "reward_c" in h else _i("spent_c") * WALLET_PCT // 100
    return {
        "name": h.get("name", ""), "joined": _i("joined"), "buys": _i("buys"),
        "spent_c": _i("spent_c"), "redeemed_c": _i("redeemed_c"), "cancelled": _i("cancelled"),
        "reward_c": reward, "topup_c": _i("topup_c"), "wspent_c": _i("wspent_c"),
    }

def _ensure_reward_field(uid):
    """يرحّل المكافأة القديمة (5% من الإنفاق) إلى حقل مستقل قبل أول زيادة جديدة."""
    k = _prof_key(uid)
    h = {str(a): str(b) for a, b in (db.hgetall(k) or {}).items()}
    if "reward_c" not in h:
        try:
            legacy = int(float(h.get("spent_c", 0) or 0)) * WALLET_PCT // 100
        except ValueError:
            legacy = 0
        db.hsetnx(k, "reward_c", str(legacy))

def wallet_credit(uid, cents, kind, note=""):
    """يضيف رصيداً مشحوناً (شحن أو دفعة ناقصة محوّلة). بدون مكافأة."""
    ensure_profile(uid)
    _ensure_reward_field(uid)
    db.hincrby(_prof_key(uid), "topup_c", int(cents))
    wlog_add(uid, kind, cents, note)

def ubuy_get(uid):
    out = {}
    for k, v in (db.hgetall(f"rk:ubuy:{uid}") or {}).items():
        try:
            out[str(k)] = int(float(v))
        except ValueError:
            pass
    return out

def wlog_add(uid, kind, cents, note=""):
    key = f"rk:wlog:{uid}"
    db.lpush(key, json.dumps({"k": kind, "c": int(cents), "n": note or "", "t": int(time.time())}, ensure_ascii=False))
    db.ltrim(key, 0, 49)

def wlog_list(uid, n=5):
    rows = []
    for raw in (db.lrange(f"rk:wlog:{uid}", 0, n - 1) or []):
        try:
            rows.append(raw if isinstance(raw, dict) else json.loads(raw))
        except Exception:
            pass
    return rows

def record_purchase(uid, pid, pname, amount, canon, via="binance"):
    """يسجل شراءً مكتملاً. آمن ضد التكرار (إعادة المحاولة لا تسجل مرتين).
    via: binance/manual = مكافأة (2% بطاقات الهداية، 5% الباقي) | wallet = بدون مكافأة."""
    if not db:
        return
    guard = f"rk:rec:{canon}"
    try:
        if not kv_set(guard, "1", nx=True):
            return
        cents = int((Decimal(str(amount)) * 100).to_integral_value())
        ensure_profile(uid)
        _ensure_reward_field(uid)
        k = _prof_key(uid)
        reward_c = 0
        if via in ("binance", "manual"):
            pct = GIFT_REWARD_PCT if pid in GIFT_VARIANTS else WALLET_PCT
            reward_c = cents * pct // 100
        db.hincrby(k, "buys", 1)
        db.hincrby(k, "spent_c", cents)
        if reward_c:
            db.hincrby(k, "reward_c", reward_c)
        db.hincrby(f"rk:ubuy:{uid}", f"p:{pid}" if pid else f"m:{pname}", 1)
        wlog_add(uid, "buy", cents, pname)
        if reward_c:
            wlog_add(uid, "reward", reward_c, pname)
    except Exception as e:
        print(f"record_purchase error: {e}")
        try:
            kv_del(guard)
        except Exception:
            pass

def record_cancel(uid, inv_id):
    """يحسب فاتورة ملغاة/منتهية مرة واحدة فقط."""
    if not db:
        return
    try:
        if not kv_set(f"rk:cnt:{inv_id}", "1", ex=7 * 86400, nx=True):
            return
        ensure_profile(uid)
        db.hincrby(_prof_key(uid), "cancelled", 1)
    except Exception as e:
        print(f"record_cancel error: {e}")

def _fmt_date(ts):
    return time.strftime("%d %b %Y, %H:%M", time.gmtime(ts)) if ts else "—"

def _success_pct(done, canc):
    """نسبة وحدة: المكتملة ترفعها والملغاة تخفضها."""
    tot = done + canc
    return round(done * 100 / tot) if tot > 0 else 0

def _pf_markup(lang, screen, wallet_label=None):
    m = InlineKeyboardMarkup()
    if screen == "profile":
        m.row(
            InlineKeyboardButton(text=wt(lang, "btn_history"), callback_data="pf_hist"),
            InlineKeyboardButton(text=wt(lang, "btn_wallet"), callback_data="pf_wallet"),
        )
    elif screen == "hist":
        m.add(InlineKeyboardButton(text=wallet_label or wt(lang, "btn_wallet"), callback_data="pf_wallet"))
        m.add(InlineKeyboardButton(text=wt(lang, "btn_profile"), callback_data="pf_profile"))
    elif screen == "topup":
        m.row(*[
            InlineKeyboardButton(text=f"{a}$", callback_data=f"pf_topa_{a}")
            for a in TOPUP_AMOUNTS
        ])
        m.add(InlineKeyboardButton(text=wt(lang, "btn_topup_other"), callback_data="pf_topo"))
        m.add(InlineKeyboardButton(text=wt(lang, "btn_wallet"), callback_data="pf_wallet"))
    else:
        m.add(InlineKeyboardButton(text=wt(lang, "btn_topup"), callback_data="pf_top"))
        m.add(InlineKeyboardButton(text=t(lang, "support_btn"), url=MY_PRIVATE_CHAT_LINK))
        m.add(InlineKeyboardButton(text=wt(lang, "btn_history"), callback_data="pf_hist"))
    m.add(InlineKeyboardButton(text=t(lang, "back"), callback_data="pf_back"))
    return m

def _pf_show(call, text, markup):
    chat_id = call.message.chat.id
    if call.message.content_type == "text":
        try:
            bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="HTML", reply_markup=markup)
            return
        except Exception as e:
            if "not modified" in str(e).lower():
                return
    bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)

def _history_lines(lang, uid):
    items = sorted(ubuy_get(uid).items(), key=lambda kv: -kv[1])
    if not items:
        return wt(lang, "history_empty")
    lines = [wt(lang, "by_product")]
    for field, n in items:
        kind, _, val = field.partition(":")
        if kind == "p" and find_product(val):
            name = tr(find_product(val), "name", lang)
        else:
            name = val
        lines.append(f"• {html.escape(name)}: {n}")
    return "\n".join(lines)

@bot.callback_query_handler(func=lambda c: c.data.startswith("pf_"))
def handle_profile_callbacks(call):
    uid = call.from_user.id
    lang = get_lang(uid)
    data = call.data

    if data == "pf_back":  # لا يمسح فاتورة الدفع المفتوحة
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        send_main_menu(call.message.chat.id, lang)
        bot.answer_callback_query(call.id)
        return

    if not db:
        bot.answer_callback_query(call.id, wt(lang, "unavailable"), show_alert=True)
        return
    register_user(uid)
    ensure_profile(uid, call.from_user.first_name)
    if data != "pf_topo":
        _topup_wait.pop(uid, None)

    # ---- شحن المحفظة ----
    if data == "pf_top":
        _pf_show(call, wt(lang, "topup_pick"), _pf_markup(lang, "topup"))
        bot.answer_callback_query(call.id)
        return
    if data.startswith("pf_topa_"):
        try:
            amount = Decimal(data[len("pf_topa_"):])
        except InvalidOperation:
            bot.answer_callback_query(call.id)
            return
        if amount not in [Decimal(a) for a in TOPUP_AMOUNTS]:
            bot.answer_callback_query(call.id)
            return
        try:
            start_topup_invoice(call.message.chat.id, uid, lang, amount)
        except StorageError:
            bot.answer_callback_query(call.id, t(lang, "temp_error"), show_alert=True)
            return
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        bot.answer_callback_query(call.id)
        return
    if data == "pf_topo":
        _topup_wait[uid] = True
        m = InlineKeyboardMarkup()
        m.add(InlineKeyboardButton(text=t(lang, "cancel"), callback_data="pf_wallet"))
        _pf_show(call, wt(lang, "topup_other_prompt").format(min=TOPUP_MIN, max=TOPUP_MAX), m)
        bot.answer_callback_query(call.id)
        return

    try:
        p = prof_get(uid)
        avail_c = wallet_avail_c(p)
        if data == "pf_profile":
            text = wt(lang, "profile").format(
                id=uid, name=html.escape(call.from_user.first_name or "-"),
                joined=_fmt_date(p["joined"]), buys=p["buys"], spent=_money(p["spent_c"]),
            )
            markup = _pf_markup(lang, "profile")
        elif data == "pf_hist":
            text = (
                wt(lang, "history").format(
                    lines=_history_lines(lang, uid), done=p["buys"],
                    canc=p["cancelled"], pct=_success_pct(p["buys"], p["cancelled"]),
                )
                + "\n\n" + wt(lang, "wallet_note")
            )
            markup = _pf_markup(lang, "hist", f"{wt(lang, 'btn_wallet')} | ${_money(avail_c)}")
        elif data == "pf_wallet":
            text = (
                wt(lang, "wallet").format(
                    rewards=_money(p["reward_c"]), topup=_money(p["topup_c"]),
                    used=_money(p["redeemed_c"] + p["wspent_c"]), avail=_money(avail_c),
                    pct=WALLET_PCT, gift_pct=GIFT_REWARD_PCT,
                )
                + "\n\n" + wt(lang, "wallet_note")
            )
            markup = _pf_markup(lang, "wallet")
        else:
            bot.answer_callback_query(call.id)
            return
    except Exception as e:
        print(f"profile view error: {e}")
        bot.answer_callback_query(call.id, wt(lang, "unavailable"), show_alert=True)
        return
    _pf_show(call, text, markup)
    bot.answer_callback_query(call.id)

# ---------- شحن المحفظة / الدفعات الناقصة / الدفع من المحفظة ----------
_topup_wait = {}  # user_id -> ينتظر مبلغ الشحن مكتوباً

def _ilock(inv_id):
    try:
        return bool(kv_set(f"rk:invlock:{inv_id}", "1", ex=30, nx=True))
    except StorageError:
        return False

def _iunlock(inv_id):
    try:
        kv_del(f"rk:invlock:{inv_id}")
    except StorageError:
        pass

def part_add(inv_id):
    if db:
        try:
            db.sadd("rk:partset", inv_id)
        except Exception as e:
            print(f"part_add error: {e}")

def part_remove(inv_id):
    if db:
        try:
            db.srem("rk:partset", inv_id)
        except Exception as e:
            print(f"part_remove error: {e}")

def part_list():
    if not db:
        return []
    try:
        return [str(x) for x in (db.smembers("rk:partset") or [])]
    except Exception as e:
        print(f"part_list error: {e}")
        return []

def _edit_invoice_msg(invoice, text):
    """يعدّل رسالة الفاتورة ويحذف أزرارها."""
    if invoice and invoice.get("message_id"):
        try:
            bot.edit_message_text(
                text, invoice.get("chat_id") or invoice["user_id"], invoice["message_id"],
                parse_mode="HTML", reply_markup=InlineKeyboardMarkup(),
            )
        except Exception as e:
            print(f"edit invoice failed: {e}")

def _wallet_covers(uid, price):
    """هل رصيد المحفظة يكفي كامل السعر؟ (لإظهار زر الدفع من المحفظة)."""
    if not db or price is None:
        return False
    try:
        need_c = int((_to_decimal(price) * 100).to_integral_value())
        return need_c > 0 and wallet_avail_c(prof_get(uid)) >= need_c
    except Exception:
        return False

def build_topup_invoice_text(lang, invoice):
    return (
        f"<b>{t(lang, 'invoice_title')}</b>\n\n"
        f"{html.escape(wt(lang, 'topup_name'))}\n"
        f"{t(lang, 'invoice_amount')} <b>{html.escape(str(invoice['price_usdt']))} USDT</b>\n\n"
        f"💳 <b>Binance Pay ID:</b>\n<code>{html.escape(BINANCE_PAY_ID)}</code>\n\n"
        f"{wt(lang, 'topup_steps')}\n\n"
        f"⏱️ {t(lang, 'invoice_expire')}"
    )

def start_topup_invoice(chat_id, uid, lang, amount):
    price = f"{amount:.2f}"
    inv_id = create_invoice(uid, TOPUP_PID, "topup", price, "💳 شحن المحفظة")
    invoice = get_invoice(inv_id) or {"price_usdt": price}
    sent = bot.send_message(
        chat_id, build_topup_invoice_text(lang, invoice),
        parse_mode="HTML", reply_markup=build_invoice_markup(lang, inv_id),
    )
    attach_invoice_msg(inv_id, sent)

def _awaiting_topup(m):
    return (
        bool(m.text) and not m.text.startswith("/")
        and m.chat.type == "private" and m.from_user.id in _topup_wait
    )

@bot.message_handler(func=_awaiting_topup, content_types=["text"])
def handle_topup_amount(message):
    uid = message.from_user.id
    lang = get_lang(uid)
    amount = _parse_price(message.text)
    if amount is None or amount < TOPUP_MIN or amount > TOPUP_MAX:
        bot.reply_to(message, wt(lang, "topup_bad").format(min=TOPUP_MIN, max=TOPUP_MAX))
        return
    _topup_wait.pop(uid, None)
    try:
        start_topup_invoice(message.chat.id, uid, lang, amount)
    except StorageError:
        bot.send_message(message.chat.id, t(lang, "temp_error"))

def _handle_topup_tx(chat_id, uid, lang, inv_id, invoice, tx):
    """دفعة على فاتورة شحن: يُضاف المبلغ الحقيقي المدفوع للمحفظة (بدون مكافأة)."""
    canon = tx["tx_id"]
    if not db:
        bot.send_message(chat_id, wt(lang, "unavailable"))
        return
    cents = int((tx["amount"] * 100).to_integral_value())
    if cents <= 0:
        bot.send_message(chat_id, t(lang, "not_found"))
        return
    if not _ilock(inv_id):
        bot.send_message(chat_id, t(lang, "temp_error"))
        return
    try:
        if kv_get(f"rk:invpaid:{inv_id}") is not None or not kv_set(f"rk:txu:{canon}", f"topup:{inv_id}", nx=True):
            bot.send_message(chat_id, t(lang, "used"))
            return
        kv_set(f"rk:invpaid:{inv_id}", canon, nx=True)
        try:
            wallet_credit(uid, cents, "topup", "Binance")
        except Exception as e:
            print(f"topup credit error: {e}")
            kv_del(f"rk:txu:{canon}")
            kv_del(f"rk:invpaid:{inv_id}")
            bot.send_message(chat_id, t(lang, "temp_error"))
            return
    except StorageError:
        bot.send_message(chat_id, t(lang, "temp_error"))
        return
    finally:
        _iunlock(inv_id)

    clear_pending(uid)
    inv_live_remove(inv_id)
    _edit_invoice_msg(invoice, wt(lang, "topup_edit_done").format(amount=_money(cents)))
    try:
        avail = _money(wallet_avail_c(prof_get(uid)))
    except Exception:
        avail = "—"
    bot.send_message(chat_id, wt(lang, "topup_credited").format(amount=_money(cents), avail=avail), parse_mode="HTML")
    monitor_send(f"💳 <b>شحن محفظة</b>\n\n👤 {_user_link(uid)}\n💵 ${_money(cents)}\n💼 المتاح الآن: ${avail}")

def convert_partial(inv_id):
    """فاتورة لم يكتمل دفعها: المبلغ المدفوع يتحول إلى محفظة الزبون (بدون مكافأة)."""
    if not db or not _ilock(inv_id):
        return
    uid = None
    cents = 0
    acc = None
    try:
        acc = kv_get_json(f"rk:invp:{inv_id}")
        if not acc or kv_get(f"rk:invpaid:{inv_id}") is not None:
            part_remove(inv_id)
            return
        if not kv_set(f"rk:invconv:{inv_id}", "1", nx=True):
            part_remove(inv_id)
            return
        uid = acc["uid"]
        cents = int((_to_decimal(acc.get("sum", 0)) * 100).to_integral_value())
        try:
            if cents > 0:
                wallet_credit(uid, cents, "partial", acc.get("pname", ""))
        except Exception as e:
            print(f"convert_partial credit error: {e}")
            kv_del(f"rk:invconv:{inv_id}")  # نعيد المحاولة في الدورة القادمة
            return
        kv_del(f"rk:invp:{inv_id}")
        part_remove(inv_id)
    except StorageError as e:
        print(f"convert_partial storage error: {e}")
        return
    finally:
        _iunlock(inv_id)

    if uid is None or cents <= 0:
        return
    record_cancel(uid, inv_id)
    lang = get_lang(uid)
    try:
        bot.send_message(uid, wt(lang, "converted").format(amount=_money(cents)), parse_mode="HTML",
                         reply_markup=support_markup(lang))
    except Exception as e:
        print(f"converted notice failed: {e}")
    monitor_send(
        f"⚠️ <b>دفعة غير مكتملة تحولت للمحفظة</b>\n\n👤 {_user_link(uid)}\n"
        f"📦 {html.escape(str(acc.get('pname', '')))}\n💵 ${_money(cents)} (من أصل {acc.get('need')} USDT)"
    )

def expire_partials():
    for inv_id in part_list():
        acc = kv_get_json(f"rk:invp:{inv_id}")
        if not acc:
            part_remove(inv_id)
            continue
        if time.time() >= float(acc.get("exp", 0)):
            convert_partial(inv_id)

@bot.callback_query_handler(func=lambda c: c.data.startswith("wpay_"))
def handle_wallet_pay(call):
    """دفع فاتورة تلقائية (Gemini/بطاقات الهداية) من المحفظة. كامل المبلغ، بدون مكافأة."""
    uid = call.from_user.id
    lang = get_lang(uid)
    chat_id = call.message.chat.id
    inv_id = call.data[5:]
    if not db:
        bot.answer_callback_query(call.id, wt(lang, "unavailable"), show_alert=True)
        return
    try:
        invoice = get_invoice(inv_id)
    except StorageError:
        bot.answer_callback_query(call.id, t(lang, "temp_error"), show_alert=True)
        return
    if (not invoice or str(invoice.get("user_id")) != str(uid)
            or invoice.get("product_id") == TOPUP_PID
            or time.time() - invoice["created_at"] > INVOICE_TTL):
        bot.answer_callback_query(call.id, wt(lang, "wpay_expired"), show_alert=True)
        return

    pid, label = invoice["product_id"], invoice["label"]
    cents = int((_to_decimal(invoice["price_usdt"]) * 100).to_integral_value())

    # التأكد من توفر المنتج قبل أي خصم
    out = False
    try:
        if pid == GEMINI_ID:
            out = gemini_stock() < int(str(label).lstrip("x") or 1)
        else:
            mapping = fazer_resolve(pid, label, allow_fetch=False)
            out = bool(mapping and mapping.get("stock") is not None and int(mapping["stock"]) <= 0)
    except Exception:
        out = False
    if out:
        bot.answer_callback_query(call.id, wt(lang, "wpay_out"), show_alert=True)
        return

    if not _ilock(inv_id):
        bot.answer_callback_query(call.id, wt(lang, "wpay_busy"), show_alert=True)
        return
    if not _wlock(uid):
        _iunlock(inv_id)
        bot.answer_callback_query(call.id, wt(lang, "wpay_busy"), show_alert=True)
        return

    canon = f"wallet-{inv_id}"
    claim = None
    err = None
    deducted = False
    try:
        if kv_get(f"rk:invpaid:{inv_id}") is not None or kv_get(f"rk:invconv:{inv_id}") is not None:
            err = "wpay_expired"
        elif kv_get(f"rk:invp:{inv_id}") is not None:
            err = "wpay_mixed"  # دفع جزءاً بـ Binance: لا دفع مختلط
        elif wallet_avail_c(prof_get(uid)) < cents:
            err = "wpay_short"
        else:
            claim = {
                "user_id": uid, "invoice_id": inv_id, "product_id": pid, "label": label,
                "product_name": invoice["product_name"], "price": invoice["price_usdt"],
                "paid": invoice["price_usdt"], "via": "wallet", "status": "claimed", "ts": int(time.time()),
            }
            if not kv_set(f"rk:tx:{canon}", json.dumps(claim), nx=True):
                err = "wpay_expired"
            elif not kv_set(f"rk:invpaid:{inv_id}", canon, nx=True):
                kv_del(f"rk:tx:{canon}")
                err = "wpay_expired"
            else:
                db.hincrby(_prof_key(uid), "wspent_c", cents)
                deducted = True
                try:
                    wlog_add(uid, "wpay", cents, invoice["product_name"])
                except Exception as e:
                    print(f"wlog wpay failed: {e}")
    except Exception as e:
        print(f"wallet pay error: {e}")
        err = "unavailable"
        if claim and not deducted:
            try:
                kv_del(f"rk:tx:{canon}")
                kv_del(f"rk:invpaid:{inv_id}")
            except Exception:
                pass
    finally:
        _wunlock(uid)
        _iunlock(inv_id)

    if err:
        bot.answer_callback_query(call.id, wt(lang, err), show_alert=True)
        return

    bot.answer_callback_query(call.id)
    _edit_invoice_msg(invoice, wt(lang, "wpay_done").format(
        product=html.escape(invoice["product_name"]), amount=html.escape(str(invoice["price_usdt"]))))
    fulfill_order(chat_id, uid, lang, claim, canon)

    if claim.get("status") == "delivered":
        monitor_send(
            f"💼 <b>شراء من المحفظة</b>\n\n📦 {html.escape(invoice['product_name'])}\n"
            f"👤 {_user_link(uid)}\n💵 ${_money(cents)}"
        )
        return

    # فشل التسليم: نرجع المبلغ للمحفظة ونلغي الطلب
    try:
        db.hincrby(_prof_key(uid), "wspent_c", -cents)
        wlog_add(uid, "refund", cents, invoice["product_name"])
    except Exception as e:
        print(f"wallet refund error: {e}")
        alert_admin(f"🚨 <b>تعذر إرجاع رصيد المحفظة</b>\n👤 <code>{uid}</code>\n💵 ${_money(cents)}\n"
                    f"استعمل /walletadd {uid} {_money(cents)}")
    pend_remove(canon)
    try:
        kv_del(f"rk:tx:{canon}")
    except StorageError:
        pass
    clear_pending(uid)
    inv_live_remove(inv_id)
    bot.send_message(chat_id, wt(lang, "wpay_fail").format(amount=_money(cents)),
                     parse_mode="HTML", reply_markup=support_markup(lang))
    alert_admin(f"↩️ <b>فشل تسليم طلب بالمحفظة وتم إرجاع المبلغ</b>\n📦 {html.escape(invoice['product_name'])}\n"
                f"👤 <code>{uid}</code>\n💵 ${_money(cents)}")
    monitor_send(f"↩️ <b>فشل تسليم طلب بالمحفظة</b> — أُرجع ${_money(cents)}\n👤 {_user_link(uid)}\n"
                 f"📦 {html.escape(invoice['product_name'])}")

# ---------- أدوات الأدمن: المحفظة والشراء اليدوي ----------
_adm_wait = {}  # admin_id -> حالة المعالج بالأزرار

def _acct_exists(uid):
    uid = str(uid)
    if uid in known_users or uid in user_lang:
        return True
    try:
        return bool(db and db.exists(_prof_key(uid)))
    except Exception:
        return False

def _wlock(uid):
    try:
        return bool(kv_set(f"rk:wlock:{uid}", "1", ex=10, nx=True))
    except StorageError:
        return False

def _wunlock(uid):
    try:
        kv_del(f"rk:wlock:{uid}")
    except StorageError:
        pass

def _adm_precheck(uid):
    if not db:
        return "⚠️ Upstash غير متصل."
    if not _acct_exists(uid):
        return "❌ هذا الزبون غير موجود (ما استعمل البوت من قبل)."
    return None

def wallet_use(uid, amount, note=""):
    err = _adm_precheck(uid)
    if err:
        return False, err
    cents = int(amount * 100)
    if not _wlock(uid):
        return False, "⏳ عملية أخرى جارية على هذا الزبون، أعد المحاولة بعد ثانية."
    try:
        ensure_profile(uid)
        p = prof_get(uid)
        avail = wallet_avail_c(p)
        if cents > avail:
            return False, f"❌ المبلغ أكبر من الرصيد المتاح (${_money(avail)})."
        db.hincrby(_prof_key(uid), "redeemed_c", cents)
        wlog_add(uid, "use", cents, note)
        new_avail = avail - cents
    except Exception as e:
        return False, f"❌ خطأ: {str(e)[:150]}"
    finally:
        _wunlock(uid)
    monitor_send(
        f"➖ <b>خصم من المحفظة</b>\n\n👤 {_user_link(uid)}\n💵 ${_money(cents)}\n"
        f"💼 المتاح الآن: ${_money(new_avail)}" + (f"\n📝 {html.escape(note)}" if note else "")
    )
    return True, f"✅ تم خصم ${_money(cents)} من محفظة <code>{uid}</code>\n💼 الرصيد المتاح الآن: <b>${_money(new_avail)}</b>"

def wallet_add(uid, amount, note=""):
    err = _adm_precheck(uid)
    if err:
        return False, err
    cents = int(amount * 100)
    if not _wlock(uid):
        return False, "⏳ عملية أخرى جارية على هذا الزبون، أعد المحاولة بعد ثانية."
    try:
        ensure_profile(uid)
        p = prof_get(uid)
        if cents > p["redeemed_c"]:
            return False, f"❌ لا يمكن إرجاع أكثر مما تم استبداله (${_money(p['redeemed_c'])})."
        db.hincrby(_prof_key(uid), "redeemed_c", -cents)
        wlog_add(uid, "add", cents, note)
        new_avail = wallet_avail_c(p) + cents
    except Exception as e:
        return False, f"❌ خطأ: {str(e)[:150]}"
    finally:
        _wunlock(uid)
    monitor_send(
        f"↩️ <b>إرجاع رصيد للمحفظة</b>\n\n👤 {_user_link(uid)}\n💵 ${_money(cents)}\n"
        f"💼 المتاح الآن: ${_money(new_avail)}" + (f"\n📝 {html.escape(note)}" if note else "")
    )
    return True, f"✅ تم إرجاع ${_money(cents)} إلى محفظة <code>{uid}</code>\n💼 الرصيد المتاح الآن: <b>${_money(new_avail)}</b>"

def add_manual_purchase(uid, amount, pname):
    err = _adm_precheck(uid)
    if err:
        return False, err
    pname = (pname or "").strip() or "شراء يدوي"
    record_purchase(uid, None, pname, amount, f"manual:{uuid.uuid4().hex[:12]}", via="manual")
    try:
        p = prof_get(uid)
    except Exception as e:
        return False, f"❌ خطأ: {str(e)[:150]}"
    avail = wallet_avail_c(p)
    monitor_send(
        f"➕ <b>شراء يدوي مسجل</b>\n\n👤 {_user_link(uid)}\n📦 {html.escape(pname)}\n💵 ${amount:.2f}\n"
        f"💼 المتاح الآن: ${_money(avail)}"
    )
    return True, (
        f"✅ سُجل شراء يدوي للزبون <code>{uid}</code>: {html.escape(pname)} — ${amount:.2f}\n"
        f"🛒 مجموع مشترياته: {p['buys']} | 💵 ${_money(p['spent_c'])}\n"
        f"💼 الرصيد المتاح: <b>${_money(avail)}</b>"
    )

def admin_view_text(uid):
    err = _adm_precheck(uid)
    if err:
        return err
    try:
        p = prof_get(uid)
        name = p["name"]
        if not name:
            try:
                name = bot.get_chat(int(uid)).first_name or "-"
            except Exception:
                name = "-"
        kinds = {
            "buy": "🛒 شراء", "reward": "🎁 مكافأة", "use": "➖ خصم", "add": "↩️ إرجاع",
            "topup": "💳 شحن", "partial": "⚠️ دفعة ناقصة→محفظة", "wpay": "💼 شراء بالمحفظة", "refund": "↩️ استرجاع تسليم",
        }
        ops = []
        for r in wlog_list(uid, 5):
            when = time.strftime("%m-%d %H:%M", time.gmtime(r.get("t", 0)))
            ops.append(f"• {when} | {kinds.get(r.get('k'), r.get('k'))} ${_money(r.get('c', 0))} {html.escape(str(r.get('n', ''))[:40])}")
        return (
            f"👤 <b>ملف الزبون</b>\n\n🆔 <code>{uid}</code>\n📛 {html.escape(name)}\n"
            f"📅 الانضمام: {_fmt_date(p['joined'])}\n"
            f"🛒 المكتملة: {p['buys']} | ❌ الملغاة: {p['cancelled']} | 📊 النجاح: {_success_pct(p['buys'], p['cancelled'])}%\n"
            f"💵 الإنفاق: ${_money(p['spent_c'])}\n\n"
            f"💼 <b>المحفظة</b>\n🎁 المكافآت: ${_money(p['reward_c'])} | 💳 المشحون: ${_money(p['topup_c'])}\n"
            f"➖ المستخدم: ${_money(p['redeemed_c'] + p['wspent_c'])} | "
            f"✅ المتاح: <b>${_money(wallet_avail_c(p))}</b>\n\n"
            f"🧾 آخر العمليات:\n" + ("\n".join(ops) if ops else "— لا شيء —")
        )
    except Exception as e:
        return f"❌ خطأ: {str(e)[:150]}"

def _adm_args(message):
    return (message.text or "").split(maxsplit=3)[1:]

@bot.message_handler(commands=["wallet"])
def wallet_cmd(message):
    if not is_admin_msg(message):
        return
    a = _adm_args(message)
    if not a or not a[0].isdigit():
        bot.reply_to(message, "الاستعمال: /wallet ID")
        return
    bot.send_message(message.chat.id, admin_view_text(a[0]), parse_mode="HTML")

@bot.message_handler(commands=["walletuse", "walletadd"])
def wallet_change_cmd(message):
    if not is_admin_msg(message):
        return
    cmd = message.text.split()[0].lstrip("/").split("@")[0]
    a = _adm_args(message)
    amount = _parse_price(a[1]) if len(a) > 1 else None
    if len(a) < 2 or not a[0].isdigit() or amount is None:
        bot.reply_to(message, f"الاستعمال: /{cmd} ID المبلغ [ملاحظة]")
        return
    fn = wallet_use if cmd == "walletuse" else wallet_add
    ok, msg = fn(a[0], amount, a[2] if len(a) > 2 else "")
    bot.send_message(message.chat.id, msg, parse_mode="HTML")

@bot.message_handler(commands=["addpurchase"])
def addpurchase_cmd(message):
    if not is_admin_msg(message):
        return
    a = _adm_args(message)
    amount = _parse_price(a[1]) if len(a) > 1 else None
    if len(a) < 2 or not a[0].isdigit() or amount is None:
        bot.reply_to(message, "الاستعمال: /addpurchase ID المبلغ [اسم المنتج]")
        return
    name = " ".join(a[2:]) if len(a) > 2 else ""
    ok, msg = add_manual_purchase(a[0], amount, name)
    bot.send_message(message.chat.id, msg, parse_mode="HTML")

@bot.message_handler(commands=["admin"])
def admin_panel_cmd(message):
    if not is_admin_msg(message):
        return
    _adm_wait.pop(message.from_user.id, None)
    _price_wait.pop(message.from_user.id, None)
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(text="➖ خصم من المحفظة", callback_data="adm_use"),
        InlineKeyboardButton(text="↩️ إرجاع رصيد", callback_data="adm_add"),
    )
    markup.add(InlineKeyboardButton(text="➕ تسجيل شراء يدوي", callback_data="adm_buy"))
    markup.add(InlineKeyboardButton(text="👤 ملف زبون", callback_data="adm_view"))
    bot.send_message(message.chat.id, "🛠️ <b>لوحة الأدمن</b>\nاختر العملية:", parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("adm_"))
def handle_admin_panel(call):
    if not _is_admin_user(call.from_user.id):
        bot.answer_callback_query(call.id)
        return
    op = call.data[4:]
    if op not in ("use", "add", "buy", "view"):
        bot.answer_callback_query(call.id)
        return
    _price_wait.pop(call.from_user.id, None)
    _adm_wait[call.from_user.id] = {"op": op, "step": "id"}
    bot.send_message(call.message.chat.id, "🆔 أرسل ID الزبون:\n(أو /admin للإلغاء)")
    bot.answer_callback_query(call.id)

def _awaiting_admin_wizard(m):
    return (
        bool(m.text) and not m.text.startswith("/")
        and m.chat.type == "private" and _is_admin_user(m.from_user.id)
        and m.from_user.id in _adm_wait
    )

@bot.message_handler(func=_awaiting_admin_wizard, content_types=["text"])
def handle_admin_wizard(message):
    aid = message.from_user.id
    st = _adm_wait[aid]
    text = message.text.strip()

    if st["step"] == "id":
        if not text.isdigit():
            bot.reply_to(message, "❌ ID غير صالح، أرسل أرقاماً فقط.")
            return
        st["uid"] = text
        if st["op"] == "view":
            _adm_wait.pop(aid, None)
            bot.send_message(message.chat.id, admin_view_text(text), parse_mode="HTML")
            return
        st["step"] = "amount"
        bot.reply_to(message, "💵 أرسل المبلغ بالدولار (مثال: 4.55):")
        return

    if st["step"] == "amount":
        amount = _parse_price(text)
        if amount is None:
            bot.reply_to(message, "❌ مبلغ غير صالح. أرسل مثلاً: 4.55")
            return
        st["amount"] = amount
        if st["op"] == "buy":
            st["step"] = "name"
            bot.reply_to(message, "📦 أرسل اسم المنتج (أو أرسل - لتخطيه):")
            return
        _adm_wait.pop(aid, None)
        fn = wallet_use if st["op"] == "use" else wallet_add
        ok, msg = fn(st["uid"], amount, "")
        bot.send_message(message.chat.id, msg, parse_mode="HTML")
        return

    if st["step"] == "name":
        _adm_wait.pop(aid, None)
        ok, msg = add_manual_purchase(st["uid"], st["amount"], "" if text == "-" else text)
        bot.send_message(message.chat.id, msg, parse_mode="HTML")

# ========== استقبال رقم العملية من الزبون (يجب أن يبقى بعد باقي معالجات النصوص) ==========
ORDER_ID_RE = re.compile(r"[A-Za-z0-9_\-]{8,64}")

def _awaiting_order_id(m):
    try:
        if not m.text or m.text.startswith("/") or m.chat.type != "private":
            return False
        return get_pending_invoice_id(m.from_user.id) is not None
    except Exception:
        return False

@bot.message_handler(func=_awaiting_order_id, content_types=["text"])
def handle_order_id_message(message):
    text = (message.text or "").strip()
    lang = get_lang(message.from_user.id)
    if not ORDER_ID_RE.fullmatch(text):
        bot.send_message(message.chat.id, t(lang, "send_id_hint"))
        return
    process_order_id(message, text)

set_default_commands()

UPDATE_ANNOUNCE_TEXTS = {
    "ar": "📢 حدّثنا البوت! اضغط على زر «🔄 تحديث» في الأسفل (أو أرسل /update) باش تشوف آخر تحديث فالمنتجات.",
    "en": "📢 The bot got an update! Tap the «🔄 Refresh» button below (or send /update) to see the latest products.",
    "fr": "📢 Le bot a été mis à jour ! Appuyez sur le bouton « 🔄 Actualiser » en bas (ou envoyez /update) pour voir les derniers produits.",
}

@bot.message_handler(commands=["broadcast_update"])
def broadcast_update_button(message):
    if str(message.chat.id) != str(ADMIN_CHAT_ID):
        return
    sent, failed = 0, 0
    for uid_str in list(known_users):
        lang = get_lang(uid_str)
        try:
            bot.send_message(
                int(uid_str),
                UPDATE_ANNOUNCE_TEXTS.get(lang, UPDATE_ANNOUNCE_TEXTS["ar"]),
                reply_markup=build_reply_keyboard(lang),
            )
            sent += 1
        except ApiTelegramException as e:
            failed += 1
            if e.error_code == 403:
                remove_user(uid_str)
        except Exception as e:
            failed += 1
            print(f"broadcast_update: failed for {uid_str}: {e}")
        time.sleep(0.05)
    bot.send_message(message.chat.id, f"✅ تم الإرسال إلى {sent} زبون. فشل: {failed}.")

@bot.message_handler(commands=["stats"])
def stats_command(message):
    if str(message.chat.id) != str(ADMIN_CHAT_ID):
        return
    storage = "Upstash ✅" if db else "ملف محلي فقط ⚠️"
    bot.reply_to(message, f"👥 عدد الزبانة المسجلين: {len(known_users)}\n🗄️ التخزين: {storage}")

def get_broadcastable_products():
    return [p for p in products if p.get("type") != "separator"]

def _retry_after(e):
    try:
        return int(e.result_json.get("parameters", {}).get("retry_after", 5))
    except Exception:
        return 5

def send_product_post(chat_id, item, caption, markup):
    photo = item.get("image", UNIFIED_IMAGE_URL)
    for _ in range(3):
        try:
            try:
                bot.send_photo(chat_id, photo, caption=caption, parse_mode="HTML", reply_markup=markup)
            except ApiTelegramException as e:
                if e.error_code in (403, 429):
                    raise
                bot.send_message(chat_id, caption, parse_mode="HTML", reply_markup=markup)
            return True
        except ApiTelegramException as e:
            if e.error_code == 429:
                time.sleep(_retry_after(e) + 1)
                continue
            if e.error_code == 403 or "chat not found" in str(e).lower():
                return False
            print(f"Broadcast error to {chat_id}: {e}")
            return None
        except Exception as e:
            print(f"Broadcast error to {chat_id}: {e}")
            return None
    return None

def send_channel_post(chat_id, item):
    sync_stock()
    stock_display = item["stock"] if item["stock"] == "♾️" else str(item["stock"])
    caption = (
        f"{item['icon']} <b>{html.escape(item['name'])}</b>\n\n"
        f"📦 Current stock: {html.escape(stock_display)}\n"
        f"💰 Price: {html.escape(item['price'])}"
    )
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="🛒 Buy now", url=BOT_LINK))
    return send_product_post(chat_id, item, caption, markup)

def send_user_post(user_id, item):
    sync_stock()
    lang = get_lang(user_id)
    stock_display = item["stock"] if item["stock"] == "♾️" else str(item["stock"])
    caption = (
        f"{item['icon']} <b>{html.escape(tr(item, 'name', lang))}</b>\n\n"
        f"{t(lang, 'available')} {html.escape(stock_display)}\n"
        f"{t(lang, 'price')} {html.escape(item['price'])}"
    )
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text=t(lang, "order_now"), callback_data=f"buy_{item['id']}"))
    return send_product_post(int(user_id), item, caption, markup)

def channel_round(item):
    send_channel_post(BROADCAST_CHAT_ID, item)

def users_round(item):
    sent = blocked = 0
    for uid in list(known_users):
        if uid == str(BROADCAST_CHAT_ID):
            continue
        result = send_user_post(uid, item)
        if result is True:
            sent += 1
        elif result is False:
            remove_user(uid)
            blocked += 1
        time.sleep(0.05)
    print(f"Users broadcast '{item['id']}': sent={sent}, removed={blocked}")

def run_broadcast_loop(name, interval, send_round):
    items = get_broadcastable_products()
    if not items:
        return
    index = db_get_int(f"{name}_bc_index", 0)
    last = db_get_int(f"{name}_bc_last", 0)
    wait = last + interval - int(time.time())
    if wait > 0:
        time.sleep(wait)
    while True:
        try:
            send_round(items[index % len(items)])
        except Exception as e:
            print(f"Broadcast round '{name}' failed: {e}")
        index += 1
        db_set(f"{name}_bc_index", index)
        db_set(f"{name}_bc_last", int(time.time()))
        time.sleep(interval)

threading.Thread(
    target=run_broadcast_loop, args=("channel", BROADCAST_INTERVAL_SECONDS, channel_round), daemon=True
).start()

if USER_BROADCAST_ENABLED:
    threading.Thread(
        target=run_broadcast_loop, args=("users", USER_BROADCAST_INTERVAL_SECONDS, users_round), daemon=True
    ).start()

# تسخين كتالوج FAZER وتحديثه دورياً (لعرض المخزون بسرعة)
def fazer_catalog_refresher():
    while True:
        try:
            if FAZER_API_KEY:
                fazer_load_catalog(force=True)
                print("FAZER catalog refreshed.")
        except Exception as e:
            print(f"FAZER catalog refresh failed: {e}")
        time.sleep(FAZER_CACHE_SECONDS)

threading.Thread(target=fazer_catalog_refresher, daemon=True).start()
threading.Thread(target=pending_retry_loop, daemon=True).start()

# ========== إلغاء الفواتير المنتهية تلقائياً (Gemini + بطاقات الهداية) ==========
def expire_invoice(inv_id):
    inv = get_invoice(inv_id)
    if not inv:
        inv_live_remove(inv_id)
        return
    age = time.time() - inv["created_at"]
    if age < INVOICE_TTL:
        return
    uid = inv["user_id"]
    if kv_get(f"rk:invpaid:{inv_id}") is not None:  # دُفعت: لا نلغيها
        inv_live_remove(inv_id)
        return
    current = get_pending_invoice_id(uid) == inv_id

    # المرحلة 1: عند انتهاء 20 دقيقة (مرة واحدة فقط)
    if kv_set(f"rk:invexp:{inv_id}", "1", ex=INVOICE_TTL + INVOICE_GRACE + 3600, nx=True):
        if inv.get("product_id") != TOPUP_PID and kv_get(f"rk:invp:{inv_id}") is None:
            record_cancel(uid, inv_id)  # الجزئية تُحسب عند تحويلها للمحفظة أو تُسلَّم
        lang = get_lang(uid)
        chat_id = inv.get("chat_id") or uid
        mins = {"ttl": INVOICE_TTL // 60, "grace": INVOICE_GRACE // 60}
        if inv.get("message_id"):
            try:
                bot.edit_message_text(
                    t(lang, "inv_expired_edit").format(
                        product=html.escape(inv.get("product_name", "")),
                        amount=html.escape(str(inv.get("price_usdt", ""))),
                        **mins,
                    ),
                    chat_id, inv["message_id"], parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup(),  # فارغ = يحذف الأزرار
                )
            except Exception as e:
                print(f"expire edit failed: {e}")
        if current:
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(text=t(lang, "kb_products"), callback_data="back_to_main"))
            try:
                bot.send_message(chat_id, t(lang, "inv_expired_notice").format(**mins), reply_markup=markup)
            except Exception as e:
                print(f"expire notice failed: {e}")
            monitor_send(
                f"⌛ <b>فاتورة انتهت تلقائياً</b>\n\n📦 {html.escape(inv.get('product_name', ''))}\n"
                f"💵 {html.escape(str(inv.get('price_usdt', '')))} USDT\n👤 {_user_link(uid)}"
            )

    # المرحلة 2: بعد مهلة السماح نمسح الانتظار كلياً
    if age >= INVOICE_TTL + INVOICE_GRACE:
        if current:
            clear_pending(uid)
        inv_live_remove(inv_id)

def invoice_expiry_loop():
    time.sleep(20)
    while True:
        try:
            for inv_id in inv_live_list():
                try:
                    expire_invoice(inv_id)
                except StorageError as e:
                    print(f"expire_invoice storage error: {e}")
                except Exception as e:
                    print(f"expire_invoice error for {inv_id}: {e}")
            expire_partials()
        except Exception as e:
            print(f"invoice_expiry_loop error: {e}")
        time.sleep(15)

threading.Thread(target=invoice_expiry_loop, daemon=True).start()

monitor_send("🟢 <b>البوت اشتغل</b>", key="boot", cooldown=120)
print("Bot is running...")
bot.infinity_polling()
