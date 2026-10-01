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

PICK_AMOUNT = {
    "ar": "👇 اختر قيمة البطاقة:",
    "en": "👇 Choose the card amount:",
    "fr": "👇 Choisissez la valeur de la carte :",
}

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
        "stock": 20,
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
    return invoice_id

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
        if not retry:
            bot.send_message(chat_id, t(lang, "processing"), reply_markup=support_markup(lang))

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
            try:
                bot.send_message(chat_id, text, parse_mode="HTML")
            except Exception as e:
                alert_admin(
                    f"⚠️ <b>تعذر إرسال الكود للزبون</b> <code>{uid}</code>\n"
                    f"🧾 <code>{html.escape(canon)}</code>\n" + codes_html
                )
                print(f"deliver failed: {e}")
            mark("delivered")
            clear_pending(uid)
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
            if FAZER_API_KEY:
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

    need = _to_decimal(invoice["price_usdt"])
    if tx["amount"] < need:
        bot.send_message(
            chat_id,
            t(lang, "underpaid").format(paid=tx["amount"].normalize(), need=need),
            reply_markup=support_markup(lang),
        )
        return

    canon = tx["tx_id"]
    claim = {
        "user_id": uid,
        "invoice_id": inv_id,
        "product_id": invoice["product_id"],
        "label": invoice["label"],
        "product_name": invoice["product_name"],
        "price": invoice["price_usdt"],
        "paid": str(tx["amount"].normalize()),
        "status": "claimed",
        "ts": int(time.time()),
    }
    try:
        if kv_set(f"rk:tx:{canon}", json.dumps(claim), nx=True):
            # عملية جديدة: اربطها بالفاتورة (مرة واحدة فقط)
            if not kv_set(f"rk:invpaid:{inv_id}", canon, nx=True):
                if str(kv_get(f"rk:invpaid:{inv_id}")) != canon:
                    kv_del(f"rk:tx:{canon}")
                    bot.send_message(chat_id, t(lang, "used"))
                    return
        else:
            existing = kv_get_json(f"rk:tx:{canon}")
            if not existing or str(existing.get("user_id")) != str(uid):
                bot.send_message(chat_id, t(lang, "used"))
                return
            if existing.get("status") == "delivered":
                clear_pending(uid)
                bot.send_message(chat_id, t(lang, "used"), reply_markup=support_markup(lang))
                return
            claim = existing  # إعادة محاولة لعملية مدفوعة لم تُسلَّم
    except StorageError:
        bot.send_message(chat_id, t(lang, "temp_error"))
        return

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
        bot.set_my_commands(
            [
                BotCommand("update", t(lang, "cmd_update")),
                BotCommand("language", t(lang, "cmd_language")),
                BotCommand("support", t(lang, "cmd_support")),
            ],
            scope=BotCommandScopeChat(chat_id),
        )
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
    markup = InlineKeyboardMarkup(row_width=2)
    for item in products:
        if item.get("type") == "separator":
            markup.add(InlineKeyboardButton(text=tr(item, "text", lang), callback_data="noop"))
            continue
        stock_display = item["stock"] if item["stock"] == "♾️" else f"📦 {item['stock']}"
        button_text = f"{item['icon']} {tr(item, 'name', lang)} | {item['price']} | {stock_display}"
        markup.add(InlineKeyboardButton(text=button_text, callback_data=f"buy_{item['id']}"))
    markup.add(InlineKeyboardButton(text=t(lang, "change_lang"), callback_data="change_lang"))
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

# ========== بطاقات الهداية: أزرار القيم (بدون وصف) ==========
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

    # أزرار القيم (زر لكل قيمة، مثل أزرار المنتجات)
    gift_markup = InlineKeyboardMarkup(row_width=1)
    for i, (label, price) in enumerate(GIFT_VARIANTS[product_id]):
        gift_markup.add(InlineKeyboardButton(
            text=f"{selected_product['icon']} {label} | ${price}",
            callback_data=f"var_{product_id}_{i}",
        ))
    gift_markup.add(InlineKeyboardButton(text=t(lang, "back"), callback_data="back_to_main"))

    gift_caption = (
        f"{t(lang, 'chosen')} *{tr(selected_product, 'name', lang)}*\n\n"
        f"{PICK_AMOUNT[lang]}"
    )
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    send_card(call.message.chat.id, selected_product, gift_caption, gift_markup)
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

def build_invoice_markup(lang, invoice_id):
    markup = InlineKeyboardMarkup()
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
    bot.send_message(
        call.message.chat.id,
        build_invoice_text(lang, invoice, product),
        parse_mode="HTML",
        reply_markup=build_invoice_markup(lang, invoice_id),
    )
    bot.answer_callback_query(call.id)

# ========== زر النسخ (احتياطي للنسخ القديمة من المكتبة) ==========
@bot.callback_query_handler(func=lambda call: call.data.startswith("copy_id_"))
def handle_copy_id(call):
    bot.answer_callback_query(call.id, f"💳 {BINANCE_PAY_ID}", show_alert=True)

# ========== إلغاء الفاتورة ==========
@bot.callback_query_handler(func=lambda call: call.data.startswith("cancel_"))
def handle_cancel_invoice(call):
    lang = get_lang(call.from_user.id)
    clear_pending(call.from_user.id)
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    send_main_menu(call.message.chat.id, lang)
    bot.answer_callback_query(call.id, t(lang, "cancelled"))

# ========== منتجات عادية (ليست بطاقات هداية) ==========
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_") and find_product(call.data[4:]) and find_product(call.data[4:]).get("id") not in GIFT_VARIANTS)
def handle_product_view(call):
    product_id = call.data.replace("buy_", "")
    selected_product = find_product(product_id)
    if not selected_product:
        bot.answer_callback_query(call.id)
        return

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

print("Bot is running...")
bot.infinity_polling()
