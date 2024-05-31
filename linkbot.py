import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes, ConversationHandler
import re

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = "7339045905:AAH5Ke335jEwt_yFjz_OC8l_ryJesViG-0E"

LANGUAGE, PHONE_NUMBER = range(2)

# Messages in different languages
messages = {
    'en': {
        'welcome': "Welcome {username}!\n\nMy name is John.\n\nPlease give me the number of whomever you want to chat on WhatsApp. So that I can create a whatsapp link using his number (e.g. for USA 19726281639, not +19726281639):",
        'invalid_number': "Please enter a valid phone number with country code (e.g. for USA 19726281639, not +19726281639):",
        'link_created': "WhatsApp click-to-chat link: {link}",
        'ask_another': "Please send another contact number with the country code but without the plus sign (e.g. for USA 19726281639, not +19726281639):"
    },
    'es': {
        'welcome': "¡Bienvenido {username}!\n\nMe llamo John.\n\nPor favor, dame el número de la persona con la que quieres chatear en WhatsApp para que pueda crear un enlace usando su número (ej. para USA 19726281639, no +19726281639):",
        'invalid_number': "Por favor, introduce un número de teléfono válido con el código del país (ej. para USA 19726281639, no +19726281639):",
        'link_created': "Enlace de clic para chatear en WhatsApp: {link}",
        'ask_another': "Por favor, envía otro número de contacto con el código del país pero sin el signo más (ej. para USA 19726281639, no +19726281639):"
    },
    'bn': {
        'welcome': "স্বাগতম {username}!\n\nআমার নাম জন।\n\nদয়া করে আপনার যে ব্যক্তির সাথে হোয়াটসঅ্যাপে চ্যাট করতে চান তার নম্বর দিন, যাতে আমি তার নম্বর ব্যবহার করে একটি হোয়াটসঅ্যাপ লিঙ্ক তৈরি করতে পারি (যেমন, USA এর জন্য 19726281639, +19726281639 নয়):",
        'invalid_number': "দয়া করে একটি বৈধ ফোন নম্বর দিন দেশের কোড সহ (যেমন, USA এর জন্য 19726281639, +19726281639 নয়):",
        'link_created': "WhatsApp ক্লিক-টু-চ্যাট লিঙ্ক: {link}",
        'ask_another': "দয়া করে আরেকটি যোগাযোগ নম্বর পাঠান দেশের কোড সহ কিন্তু প্লাস চিহ্ন ছাড়াই (যেমন, USA এর জন্য 19726281639, +19726281639 নয়):"
    },
    'fr': {
        'welcome': "Bienvenue {username}!\n\nJe m'appelle John.\n\nVeuillez me donner le numéro de la personne avec laquelle vous souhaitez discuter sur WhatsApp afin que je puisse créer un lien en utilisant son numéro (par ex. pour USA 19726281639, pas +19726281639):",
        'invalid_number': "Veuillez entrer un numéro de téléphone valide avec l'indicatif du pays (par ex. pour USA 19726281639, pas +19726281639):",
        'link_created': "Lien de clic pour discuter WhatsApp : {link}",
        'ask_another': "Veuillez envoyer un autre numéro de contact avec l'indicatif du pays mais sans le signe plus (par ex. pour USA 19726281639, pas +19726281639):"
    },
    'de': {
        'welcome': "Willkommen {username}!\n\nMein Name ist John.\n\nBitte geben Sie mir die Nummer der Person, mit der Sie auf WhatsApp chatten möchten, damit ich einen WhatsApp-Link mit ihrer Nummer erstellen kann (z.B. für USA 19726281639, nicht +19726281639):",
        'invalid_number': "Bitte geben Sie eine gültige Telefonnummer mit Ländervorwahl ein (z.B. für USA 19726281639, nicht +19726281639):",
        'link_created': "WhatsApp-Klick-zum-Chat-Link: {link}",
        'ask_another': "Bitte senden Sie eine weitere Kontaktnummer mit der Ländervorwahl, aber ohne das Pluszeichen (z.B. für USA 19726281639, nicht +19726281639):"
    },
    'it': {
        'welcome': "Benvenuto {username}!\n\nMi chiamo John.\n\nPer favore, dammi il numero della persona con cui vuoi chattare su WhatsApp così posso creare un link usando il suo numero (es. per USA 19726281639, non +19726281639):",
        'invalid_number': "Per favore, inserisci un numero di telefono valido con il prefisso internazionale (es. per USA 19726281639, non +19726281639):",
        'link_created': "Link clicca per chattare su WhatsApp: {link}",
        'ask_another': "Per favore, invia un altro numero di contatto con il prefisso internazionale ma senza il segno più (es. per USA 19726281639, non +19726281639):"
    },
    'pt': {
        'welcome': "Bem-vindo {username}!\n\nMeu nome é John.\n\nPor favor, forneça o número da pessoa com quem você deseja conversar no WhatsApp para que eu possa criar um link usando o número dela (por ex., para os EUA 19726281639, não +19726281639):",
        'invalid_number': "Por favor, insira um número de telefone válido com o código do país (por ex., para os EUA 19726281639, não +19726281639):",
        'link_created': "Link de clique para conversar no WhatsApp: {link}",
        'ask_another': "Por favor, envie outro número de contato com o código do país, mas sem o sinal de mais (por ex., para os EUA 19726281639, não +19726281639):"
    },
    'ru': {
        'welcome': "Добро пожаловать, {username}!\n\nМеня зовут Джон.\n\nПожалуйста, дайте мне номер человека, с которым вы хотите пообщаться в WhatsApp, чтобы я мог создать ссылку с его номером (например, для США 19726281639, не +19726281639):",
        'invalid_number': "Пожалуйста, введите действительный номер телефона с кодом страны (например, для США 19726281639, не +19726281639):",
        'link_created': "Ссылка на чат в WhatsApp: {link}",
        'ask_another': "Пожалуйста, отправьте еще один контактный номер с кодом страны, но без плюса (например, для США 19726281639, не +19726281639):"
    },
    'zh': {
        'welcome': "欢迎 {username}!\n\n我叫 John。\n\n请告诉我您想在 WhatsApp 上聊天的人的号码，以便我可以使用该号码创建 WhatsApp 链接（例如，美国 19726281639，而不是 +19726281639）：",
        'invalid_number': "请输入带有国家代码的有效电话号码（例如，美国 19726281639，而不是 +19726281639）：",
        'link_created': "WhatsApp 点击聊天链接: {link}",
        'ask_another': "请发送另一个带有国家代码的联系电话号码，但不要加号（例如，美国 19726281639，而不是 +19726281639）："
    },
    'hi': {
        'welcome': "स्वागत है {username}!\n\nमेरा नाम जॉन है।\n\nकृपया मुझे उस व्यक्ति का नंबर दें जिससे आप व्हाट्सएप पर चैट करना चाहते हैं ताकि मैं उसके नंबर का उपयोग करके एक व्हाट्सएप लिंक बना सकूं (उदाहरण के लिए, USA के लिए 19726281639, +19726281639 नहीं):",
        'invalid_number': "कृपया देश के कोड के साथ एक मान्य फोन नंबर दर्ज करें (उदाहरण के लिए, USA के लिए 19726281639, +19726281639 नहीं):",
        'link_created': "WhatsApp क्लिक-टू-चैट लिंक: {link}",
        'ask_another': "कृपया देश के कोड के साथ एक और संपर्क नंबर भेजें लेकिन प्लस साइन के बिना (उदाहरण के लिए, USA के लिए 19726281639, +19726281639 नहीं):"
    },
    'ar': {
        'welcome': "مرحبًا {username}!\n\nاسمي جون.\n\nمن فضلك أعطني رقم الشخص الذي تريد الدردشة معه على WhatsApp حتى أتمكن من إنشاء رابط WhatsApp باستخدام رقمه (على سبيل المثال، للولايات المتحدة 19726281639، وليس +19726281639):",
        'invalid_number': "يرجى إدخال رقم هاتف صالح مع رمز البلد (على سبيل المثال، للولايات المتحدة 19726281639، وليس +19726281639):",
        'link_created': "رابط النقر للدردشة في WhatsApp: {link}",
        'ask_another': "يرجى إرسال رقم اتصال آخر مع رمز البلد ولكن بدون علامة الزائد (على سبيل المثال، للولايات المتحدة 19726281639، وليس +19726281639):"
    },
    'ja': {
        'welcome': "ようこそ {username}!\n\n私の名前はジョンです。\n\nWhatsAppでチャットしたい相手の番号を教えてください。その番号を使ってWhatsAppリンクを作成します（例：アメリカの場合、19726281639、+19726281639ではなく）：",
        'invalid_number': "国コード付きの有効な電話番号を入力してください（例：アメリカの場合、19726281639、+19726281639ではなく）：",
        'link_created': "WhatsApp クリックでチャットリンク: {link}",
        'ask_another': "国コード付きの別の連絡先番号をプラス記号なしで送ってください（例：アメリカの場合、19726281639、+19726281639ではなく）："
    },
    'ko': {
        'welcome': "환영합니다, {username}!\n\n제 이름은 John입니다.\n\nWhatsApp에서 채팅하고 싶은 사람의 번호를 알려주세요. 그 번호를 사용하여 WhatsApp 링크를 생성하겠습니다 (예: 미국의 경우 19726281639, +19726281639 아님):",
        'invalid_number': "국가 코드와 함께 유효한 전화번호를 입력하세요 (예: 미국의 경우 19726281639, +19726281639 아님):",
        'link_created': "WhatsApp 클릭 투 채팅 링크: {link}",
        'ask_another': "국가 코드와 함께 다른 연락처 번호를 플러스 기호 없이 보내주세요 (예: 미국의 경우 19726281639, +19726281639 아님):"
    },
    'tr': {
        'welcome': "Hoş geldiniz, {username}!\n\nBenim adım John.\n\nWhatsApp'ta sohbet etmek istediğiniz kişinin numarasını verin, böylece numarasını kullanarak bir WhatsApp bağlantısı oluşturabilirim (örneğin ABD için 19726281639, +19726281639 değil):",
        'invalid_number': "Lütfen ülke kodu ile geçerli bir telefon numarası girin (örneğin ABD için 19726281639, +19726281639 değil):",
        'link_created': "WhatsApp sohbet bağlantısı: {link}",
        'ask_another': "Lütfen ülke kodu ile birlikte başka bir iletişim numarası gönderin ama artı işareti olmadan (örneğin ABD için 19726281639, +19726281639 değil):"
    },
    'nl': {
        'welcome': "Welkom, {username}!\n\nMijn naam is John.\n\nGeef me het nummer van degene met wie je op WhatsApp wilt chatten, zodat ik een WhatsApp-link kan maken met zijn nummer (bijv. voor de VS 19726281639, niet +19726281639):",
        'invalid_number': "Voer een geldig telefoonnummer in met de landcode (bijv. voor de VS 19726281639, niet +19726281639):",
        'link_created': "WhatsApp klik-om-te-chatten link: {link}",
        'ask_another': "Stuur een ander contactnummer met de landcode, maar zonder het plusteken (bijv. voor de VS 19726281639, niet +19726281639):"
    },
    'sv': {
        'welcome': "Välkommen, {username}!\n\nJag heter John.\n\nGe mig numret till den du vill chatta med på WhatsApp så att jag kan skapa en WhatsApp-länk med hans nummer (t.ex. för USA 19726281639, inte +19726281639):",
        'invalid_number': "Ange ett giltigt telefonnummer med landskod (t.ex. för USA 19726281639, inte +19726281639):",
        'link_created': "WhatsApp klicka-för-att-chatta länk: {link}",
        'ask_another': "Skicka ett annat kontaktnummer med landskod men utan plustecken (t.ex. för USA 19726281639, inte +19726281639):"
    }
}

# Default language
default_language = 'en'

# Function to create the language selection keyboard
def create_language_keyboard():
    languages = [
        ('English', 'en'), ('Español', 'es'), ('বাংলা', 'bn'), ('Français', 'fr'),
        ('Deutsch', 'de'), ('Italiano', 'it'), ('Português', 'pt'), ('Русский', 'ru'),
        ('中文', 'zh'), ('हिंदी', 'hi'), ('العربية', 'ar'), ('日本語', 'ja'),
        ('한국어', 'ko'), ('Türkçe', 'tr'), ('Nederlands', 'nl'), ('Svenska', 'sv')
    ]
    keyboard = []
    row = []
    for name, code in languages:
        row.append(InlineKeyboardButton(name, callback_data=code))
        if len(row) == 3:  # 3 buttons per row
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    context.user_data['language'] = default_language
    keyboard = create_language_keyboard()
    await update.message.reply_text('Please select your language:', reply_markup=keyboard)
    return LANGUAGE

async def select_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    language = query.data
    context.user_data['language'] = language
    message = messages[language]['welcome'].format(username=query.from_user.username)
    await query.edit_message_text(message)
    return PHONE_NUMBER

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    language = query.data
    context.user_data['language'] = language
    user = query.from_user
    await query.answer()
    welcome_message = messages[language]['welcome'].format(username=user.first_name)
    await query.edit_message_text(welcome_message)
    return PHONE_NUMBER

async def receive_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    language = context.user_data.get('language', 'en')
    phone_number = update.message.text
    if not re.match(r'^\d{11,15}$', phone_number):
        await update.message.reply_text(messages[language]['invalid_number'])
        return PHONE_NUMBER
    else:
        wa_link = f"https://wa.me/{phone_number}"
        keyboard = [
            [InlineKeyboardButton("Open chat", url=wa_link)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(messages[language]['link_created'].format(link=wa_link), reply_markup=reply_markup)
        await update.message.reply_text(messages[language]['ask_another'])
        return PHONE_NUMBER

def main() -> None:
    application = Application.builder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            LANGUAGE: [CallbackQueryHandler(select_language)],
            PHONE_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_number)],
        },
        fallbacks=[CommandHandler('start', start)],
    )
    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()