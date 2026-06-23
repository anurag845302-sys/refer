#!/usr/bin/env python3
import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from telegram.error import BadRequest

# --- GLOBAL EMOJIS FOR ADMIN ---
EMOJI_CAMERA = "📸"
EMOJI_USER = "👤"
EMOJI_ID = "🆔"

# --- CONFIGURATION ---
BOT_TOKEN = "8912203562:AAGUjAEL1s4GWSGjX1HhMUT-nvB8rmEnyTg"
ADMIN_ID = 8934747857
SUPPORT_USERNAME = "@FrontMan4u"

# Telegram Channel Configuration (Force Join)
# NOTE: Bot ko is channel me ADMIN banana compulsory hai!
CHANNEL_USERNAME = "@BuynSellLoots" 
CHANNEL_LINK = "https://t.me/BuynSellLoots"

# 🎥 Video ka File ID (Updated with your new valid ID)
VIDEO_FILE_ID = "BAACAgUAAxkBAAMZajpE7Xz073kZu4E5VJWDlcD0qKkAAqQiAALfXNFVhAigRIO2guE8BA" 

# Premium Styled Welcome Text Emojis
emoji_video = "📹"     
emoji_movie = "🎥"     
emoji_hand = "👉"      
emoji_blue_dot = "🔹"  

WELCOME_TEXT = (
    f"{emoji_movie} <b>Process samajhne ke liye upar di gayi video ko dhyan se dekhe!</b>\n\n"
    f"{emoji_hand} <b>Step 1:</b> Niche diye gaye link par click karein aur App download karein.\n"
    f"https://link.super.money/ZRV6EQnc9Ub\n\n"
    f"{emoji_blue_dot} <b>Step 2:</b> App open karke apna Registration complete karein iske baad bank account link karke 11 rs dost ko send karein.\n"
    f"{emoji_blue_dot} <b>Step 3:</b> Task complete hone ke baad ek saaf <b>screenshot</b> le lein.\n"
    f"{emoji_blue_dot} <b>Step 4:</b> Us screenshot ko is bot mein send karein.\n\n"
    f"ℹ️ <i>Verification ke baad aapko app ki link or step mil jayengi.</i>\n\n"
    f"📩 <b>Help & Support:</b> {SUPPORT_USERNAME}"
)

# --- FLASK DUMMY SERVER (For Render Free Tier 24/7) ---
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot is Alive and Running 24/7!"

def run_server():
    port = int(os.environ.get('PORT', 8080))
    flask_app.run(host='0.0.0.0', port=port)

# --- HELPER FUNCTION: CHECK CHANNEL JOIN ---
async def is_user_joined(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except BadRequest:
        return False
    except Exception as e:
        print(f"Error checking join status: {e}")
        return False

# --- BOT HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Force Join Check
    joined = await is_user_joined(context, user_id)
    if not joined:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)],
            [InlineKeyboardButton("✅ I Have Joined / Check Again", callback_data="check_join")]
        ])
        await update.message.reply_text(
            "⚠️ <b>Aapko pehle humare Telegram Channel ko join karna hoga tabhi bot kaam karega!</b>",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        return

    # Agar already joined hai toh seedhe video send karo
    await send_welcome_content(context, user_id)

# Content sender logic (Video + Text)
async def send_welcome_content(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    try:
        await context.bot.send_video(
            chat_id=chat_id,
            video=VIDEO_FILE_ID,
            caption=WELCOME_TEXT,
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Error sending video: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"⚠️ <i>(Video send nahi ho payi, Admin please check File ID)</i>\n\n{WELCOME_TEXT}",
            parse_mode="HTML"
        )

# Admin Tool: Kisi bhi video ko bot par forward karo to file ID mil jayegi
async def get_video_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        file_id = update.message.video.file_id
        await update.message.reply_text(f"🎥 <b>Video File ID:</b>\n\n<code>{file_id}</code>", parse_mode="HTML")

# 📸 SCREENSHOT HANDLER
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    joined = await is_user_joined(context, user.id)
    if not joined:
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)]])
        await update.message.reply_text(
            "⚠️ <b>Pehle channel join karein, uske baad hi screenshot verify hoga!</b>",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        return

    photo = update.message.photo[-1].file_id

    # Admin Panel Controls
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user.id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user.id}")
        ]
    ])

    admin_caption = (
        f"{EMOJI_CAMERA} <b>New Screenshot Received</b>\n"
        f"{EMOJI_USER} Name: {user.first_name}\n"
        f"{EMOJI_ID} User ID: {user.id}"
    )

    try:
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo,
            caption=admin_caption,
            reply_markup=buttons,
            parse_mode="HTML"
        )

        automatic_reply = (
            "🚀 <b>SCREENSHOT RECEIVED SUCCESSFULLY!</b> 🚀\n\n"
            "✅ Aapka screenshot verification ke liye chala gaya hai.\n\n"
            "📺 Channel pe video hai how to use dekho:\n\n"
            "👉 <a href='https://t.me/BuynSellLoots'>Yahan Click Karke Next Channel Join Karein</a>\n\n"
            "❗ <i>Channel pe jakar dekho step nahi to problem hoga bro !</i>"
        )

        await update.message.reply_text(
            text=automatic_reply,
            parse_mode="HTML",
            disable_web_page_preview=True
        )
    except Exception as e:
        print(f"Error in photo_handler: {e}")
        await update.message.reply_text("⚠️ Server busy hai, please thodi der baad try karein.")

# Callback button handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "check_join":
        user_id = query.from_user.id
        joined = await is_user_joined(context, user_id)
        if joined:
            try:
                await query.message.delete()
            except Exception:
                pass
            await send_welcome_content(context, user_id)
        else:
            await context.bot.send_message(
                chat_id=user_id,
                text="❌ <b>Aapne abhi tak channel join nahi kiya hai!</b> Kripya pehle join karein.",
                parse_mode="HTML"
            )
        return

    # Admin Approve/Reject Logic
    action, user_id = data.split("_")
    user_id = int(user_id)

    if action == "approve":
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text="🎉 <b>CONGRATULATIONS!</b>\n\nAapka screenshot <b>Approve</b> ho gaya hai aur verification complete hai! ✅",
                parse_mode="HTML"
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
                text="❌ <b>TASK REJECTED!</b>\n\nAapka screenshot <b>Reject</b> ho gaya hai. Kripya sahi se task karke dubara original screenshot bhejein. 🔄",
                parse_mode="HTML"
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
    app.add_handler(MessageHandler(filters.VIDEO, get_video_id))  
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Polling started successfully!")
    app.run_polling()

if __name__ == "__main__":
    main()
