# Sabhi global variables bina kisi space ke bilkul left margin se chipka kar likhein
EMOJI_CAMERA = "\U0001F4F8"
EMOJI_USER = "\U0001F464"
EMOJI_ID = "\U0001F194"
#!/usr/bin/env python3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from flask import Flask
import threading
import os

# --- CONFIGURATION ---
BOT_TOKEN = "8912203562:AAGUjAEL1s4GWSGjX1HhMUT-nvB8rmEnyTg"
ADMIN_ID = 8934747857
SUPPORT_USERNAME = "@FrontMan4u"

# 🎥 Video ka File ID (Jo tumne provide kiya)
VIDEO_FILE_ID = "BAACAgUAAxkBAAMNaiRPcu_EDDwEg0TJtoR5UVN9pP0AAqYeAAImdCBVAbbbZYdIM3E7BA" 

# Premium Styled Welcome Text
# Emojis ko safe unicode mein define karein
emoji_video = "\U0001F4F9"     # 📹 Video
emoji_movie = "\U0001F3AC"     # 🎥 Movie camera
emoji_hand = "\U0001F449"      # 👉 Hand pointing right
emoji_blue_dot = "\U0001F539"  # 🔹 Blue diamond / dot

WELCOME_TEXT = (
    f"{emoji_video} Video ka File ID (Jo tumne provide kiya)\n\n"
    f"{emoji_movie} process samajhne ke liye upar di gayi video ko dhyan se dekhe!\n\n"
    f"{emoji_hand} Step 1: Niche diye gaye link par click karein aur App download karein.\n"
    f"https://link.super.money/ZRV6EQnc9Ub"
    f"{emoji_blue_dot} Step 2: App open karke apna Registration complete karein iske baad bank account link karke 11 rs dost ko send karein.\n"
    f"{emoji_blue_dot} Step 3: Task complete hone ke baad ek saaf screenshot le lein.\n"
    f"{emoji_blue_dot} Step 4: Us screenshot ko is bot mein send karein.\n\n"
    f"ℹ️ *Verification ke baad aapko app ki link or step mil jayengi.*\n\n"
    f"📩 text=\"*Help & Support:* @Frontman4u\""
)
# --- FLASK DUMMY SERVER (For Render Free Tier 24/7) ---
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Fake WhatsApp Numbers Task Bot is Alive and Running 24/7!"

def run_server():
    port = int(os.environ.get('PORT', 8080))
    flask_app.run(host='0.0.0.0', port=port)

# --- BOT HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if VIDEO_FILE_ID != "YAHAN_FILE_ID_PASTE_KARNA":
        try:
            await update.message.reply_video(
                video=VIDEO_FILE_ID,
                caption=WELCOME_TEXT,
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Error sending video: {e}")
            await update.message.reply_text(WELCOME_TEXT, parse_mode="Markdown")
    else:
        await update.message.reply_text("⚠️ *Admin Note: Video File ID set nahi hai!*\n\n" + WELCOME_TEXT, parse_mode="Markdown")

# Admin Tool to get Video File ID (Agar future mein video change karni ho)
async def get_video_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        file_id = update.message.video.file_id
        await update.message.reply_text(f"🎥 **Video File ID:**\n\n`{file_id}`", parse_mode="Markdown")

#📸 SCREENSHOT HANDLER (AUTOMATIC SYSTEM)
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    photo = update.message.photo[-1].file_id

    # Admin Panel ke liye buttons
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user.id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user.id}")
        ]
    ])
        async def photo_handler(update, context):
    user = update.message.from_user
    photo = update.message.photo[-1].file_id

    # Sabhi global variables ka use karke caption banana
    admin_caption = (
        f"{EMOJI_CAMERA} New Screenshot Received\n"
        f"{EMOJI_USER} Name: {user.first_name}\n"
        f"{EMOJI_ID} User ID: {user.id}"
    )

    try:
        # 1. Admin ko screenshot bhejna approval ke liye
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo,
            caption=admin_caption,
            reply_markup=buttons
        )

        # Premium Styled Automatic Reply Text for User
        # Sabhi Emojis ke Unicode Codes
        emoji_rocket = "\U0001F680"    # 🚀 Rocket
        emoji_check = "\u2705"         # ✅ Green Check Mark
        emoji_tv = "\U0001F4FA"        # 📺 Television
        emoji_finger = "\U0001F449"    # 👉 Backhand Index Pointing Right
        emoji_alert = "\u2757"         # ❗️ Exclamation Mark

        # Premium Styled Automatic Reply Text for User
        automatic_reply = (
            f"{emoji_rocket} SCREENSHOT RECEIVED SUCCESSFULLY! {emoji_rocket}\n\n"
            f"{emoji_check} Aapka screenshot verification ke liye chala gaya hai.\n\n"
            f"{emoji_tv} chabbel pe video hai how to use dekho :\n\n"
            f"{emoji_finger} [Yahan Click Karke Next Channel Join Karein](https://t.me)\n"
            f"{emoji_alert} *channel pe jakar dekho step nahi to problem hoga bro !*"
        )

        # 2. User ko instant automatic link aur message bhejnah
        await update.message.reply_text(
            text=automatic_reply,
            parse_mode="Markdown",
            disable_web_page_preview=False
        )
    except Exception as e:
        print(f"Error in photo_handler: {e}")
        await update.message.reply_text("⚠️ Server busy hai, please thodi der baad try karein.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    action, user_id = data.split("_")
    user_id = int(user_id)

    if action == "approve":
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text="🎉 **CONGRATULATIONS!**\n\nAapka screenshot **Approve** ho gaya hai aur verification complete hai! ✅",
                parse_mode="Markdown"
            )
            await query.edit_message_caption(
                caption=query.message.caption + "\n\n🟢 STATUS: APPROVED"
            )
        except Exception as e:
            print(f"Error approving: {e}")

    elif action == "reject":
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text="❌ **TASK REJECTED!**\n\nAapka screenshot **Reject** ho gaya hai. Kripya sahi se task karke dubara original screenshot bhejein. 🔄",
                parse_mode="Markdown"
            )
            await query.edit_message_caption(
                caption=query.message.caption + "\n\n🔴 STATUS: REJECTED"
            )
        except Exception as e:
            print(f"Error rejecting: {e}")

# --- MAIN RUNNER ---
def main():
    print("Starting Web Server...")
    threading.Thread(target=run_server, daemon=True).start()

    print("Bot Starting...")
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    # ✅ FIX: Yahan filter.VIDEO ko MessageHandler ke andar daal diya hai
    app.add_handler(MessageHandler(filters.VIDEO, get_video_id))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Polling started successfully!")
    app.run_polling()

if __name__ == "__main__":
    main()
