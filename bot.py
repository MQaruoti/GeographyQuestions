import logging
import random
import nest_asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import os

# --- CONFIGURATION ---
TOKEN = "8726326578:AAGDpnmRmGaYt9BWViQi5UXWwZjdvww5LBM"
nest_asyncio.apply()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- QUESTIONS DATABASE ---
QUESTIONS = [
    {"q": "في أي محافظة أردنية تقع مدينة البتراء الأثرية؟", "options": ["الكرك", "العقبة", "معان", "الطفيلة"], "correct": 2},
    {"q": "أين يقع وادي رم؟", "options": ["شمال الأردن", "جنوب الأردن (محافظة العقبة)", "شرق الأردن", "وسط الأردن"], "correct": 1},
    {"q": "ما هي أعلى قمة جبلية في الأردن؟", "options": ["جبل رم", "جبل نيبو", "جبل أم الدامي", "جبل شيحان"], "correct": 2},
    {"q": "ما هي أخفض منطقة في الأردن والعالم؟", "options": ["وادي عربة", "البحر الميت", "غور الصافي", "دير علا"], "correct": 1},
    {"q": "كم عدد محافظات الأردن؟", "options": ["10 محافظات", "12 محافظة", "14 محافظة", "8 محافظات"], "correct": 1},
    {"q": "ما هو أطول نهر في الأردن؟", "options": ["نهر اليرموك", "نهر الأردن", "نهر الزرقاء", "وادي الموجب"], "correct": 1},
    {"q": "ما هي أكبر محافظة في الأردن من حيث المساحة؟", "options": ["عمّان", "المفرق", "محافظة معان", "العقبة"], "correct": 2},
    {"q": "في أي قارة يقع الأردن؟", "options": ["أفريقيا", "قارة آسيا", "أوروبا", "أمريكا الجنوبية"], "correct": 1},
    {"q": "ما هي الدولة التي تحد الأردن من الجهة الشمالية؟", "options": ["العراق", "السعودية", "سوريا", "فلسطين"], "correct": 2},
    {"q": "ما هو المنفذ البحري الوحيد للأردن؟", "options": ["البحر الميت", "مدينة العقبة", "وادي عربة", "خليج السويس"], "correct": 1},
    {"q": "ما اسم الجبل الأعلى في الأردن؟", "options": ["جبل القلعة", "جبل عجلون", "جبل أم الدامي", "جبل مبارك"], "correct": 2},
    {"q": "ما اسم المضيق الذي يربط خليج العقبة بالبحر الأحمر ويطل عليه الأردن؟", "options": ["مضيق هرمز", "مضيق باب المندب", "مضيق تيران", "مضيق جبل طارق"], "correct": 2},
    {"q": "ما هو أعلى سد في الأردن؟", "options": ["سد الملك طلال", "سد الوحدة", "سد الوالة", "سد كفرنجة"], "correct": 1},
    {"q": "ما اسم المنطقة الزراعية الخصبة شمال الأردن؟", "options": ["وادي الأردن", "سهل حوران", "الأغوار الوسطى", "البادية الشمالية"], "correct": 1},
    {"q": "ما اسم الصحراء التي تغطي شرق وجنوب الأردن؟", "options": ["صحراء النقب", "البادية الأردنية", "صحراء سيناء", "الربع الخالي"], "correct": 1},
    {"q": "ما هي المحافظة الملقبة بـ 'عروس الشمال'؟", "options": ["جرش", "عجلون", "إربد", "المفرق"], "correct": 2},
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"مرحباً بك {user_name} في مسابقة جغرافيا الأردنّ 🇯🇴\n\n"
        "اضغط /quiz للبدء باختبار معلوماتك!"
    )

async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Pick a random question from the entire list
    random_idx = random.randint(0, len(QUESTIONS) - 1)
    q_data = QUESTIONS[random_idx]
    
    context.user_data['current_q_idx'] = random_idx

    # Create buttons for options
    keyboard = [[InlineKeyboardButton(opt, callback_data=f"ans_{i}")] for i, opt in enumerate(q_data['options'])]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = f"سؤال الجغرافيا:\n\n{q_data['q']}"
    
    # If called from a button, edit the message; if from /quiz, send new
    if update.callback_query:
        await update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("ans_"):
        selected = int(data.replace("ans_", ""))
        q_idx = context.user_data.get('current_q_idx')
        
        correct = QUESTIONS[q_idx]['correct']
        
        if selected == correct:
            result_text = "✅ إجابة صحيحة! أحسنت."
        else:
            ans_text = QUESTIONS[q_idx]['options'][correct]
            result_text = f"❌ إجابة خاطئة.\nالصحيح هو: {ans_text}"

        # Show result and button for next question
        keyboard = [[InlineKeyboardButton("سؤال آخر 🔄", callback_data="next_question")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=f"السؤال: {QUESTIONS[q_idx]['q']}\n\n{result_text}",
            reply_markup=reply_markup
        )

    elif data == "next_question":
        await send_question(update, context)

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("quiz", send_question))
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    print("البوت يعمل الآن... جرب إرسال /quiz")
    app.run_polling(close_loop=False)

if __name__ == '__main__':
    main()
