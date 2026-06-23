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

# --- CONFIGURATION ---
BOT_TOKEN = "8912203562:AAGUjAEL1s4GWSGjX1HhMUT-nvB8rmEnyTg"
ADMIN_ID = 8934747857
SUPPORT_USERNAME = "@FrontMan4u"
CHANNEL_USERNAME = "@BuynSellLoots" 
CHANNEL_LINK = "https://t.me/BuynSellLoots"

# Updated Valid Video File ID
VIDEO_FILE_ID = "BAACAgUAAxkBAAMZajpE7Xz073kZu4E5VJWDlcD0qKkAAqQiAALfXNFVhAigRIO2guE8BA" 

WELCOME_TEXT = (
    f"🎥 <b>Process samajhne ke liye upar di gayi video ko dhyan se dekhe!</b>\n\n"
    f"👉 <b>Step 1:</b> Niche diye gaye link par click karein aur App download karein.\n"
    f"https://link.super.money/ZRV6EQnc9Ub\n\n"
    f"🔹 <b>Step 2:</b> App open karke apna Registration complete karein iske baad bank account link karke 11 rs dost ko send karein.\n"
    f"🔹 <b>Step 3:</b> Task complete hone ke baad ek saaf <b>screenshot</b> le lein.\n"
    f"🔹 <b>Step 4:</b> Us screenshot ko is bot mein send karein.\n\n"
    f"ℹ️ <i>Verification ke baad aapko app ki link or step mil jayengi.</i>\n\n"
    f"📩 <b>Help & Support:</b> {SUPPORT_USERNAME}"
)

flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot is Running!"

def run_server():
    port = int(os.environ.get('PORT', 8080))
    flask_app.run(host='0.0.0.0', port=port)

# --- CHECK JOIN FUNCTION ---
async def is_user_joined(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception as e:
        print(f"Join Check Error: {e}")
        return False

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
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

    await send_welcome_content(context, user_id)

async def send_welcome_content(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    try:
        await context.bot.send_video(
            chat_id=chat_id,
            video=VIDEO_FILE_ID,
            caption=WELCOME_TEXT,
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Video Error: {e}")
        await context.bot.send_message(chat_id=chat_id, text=WELCOME_TEXT, parse_mode="HTML")

async def get_video_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text(f"🎥 <b>Video File ID:</b>\n<code>{update.message.video.file_id}</code>", parse_mode="HTML")

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    joined = await is_user_joined(context, user.id)
    
    if not joined:
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)]])
        await update.message.reply_text("⚠️ <b>Pehle channel join karein, tabhi screenshot verify hoga!</b>", reply_markup=keyboard, parse_mode="HTML")
        return

    photo = update.message.photo[-1].file_id
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"app_{user.id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user.id}")
        ]
    ])

    admin_caption = f"📸 <b>New Screenshot Received</b>\n👤 Name: {user.first_name}\n🆔 User ID: {user.id}"

    try:
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=photo, caption=admin_caption, reply_markup=buttons, parse_mode="HTML")
        
        automatic_reply = (
            "🚀 <b>SCREENSHOT RECEIVED SUCCESSFULLY!</b> 🚀\n\n"
            "✅ Aapka screenshot verification ke liye chala gaya hai.\n\n"
            "📺 Channel pe video hai how to use dekho:\n"
            "👉 <a href='https://t.me/BuynSellLoots'>Yahan Click Karke Next Channel Join Karein</a>"
        )
        await update.message.reply_text(text=automatic_reply, parse_mode="HTML", disable_web_page_preview=True)
    except Exception as e:
        print(f"Photo Handler Error: {e}")

# --- FIX BUTTON HANDLER ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id

    # Har click par answer dena zaroori hai taaki loading clock hat jaye
    await query.answer()

    if data == "check_join":
        if await is_user_joined(context, user_id):
            try:
                await query.message.delete()
            except Exception:
                pass
            await send_welcome_content(context, user_id)
        else:
            await context.bot.send_message(chat_id=user_id, text="❌ <b>Aapne abhi tak channel join nahi kiya hai!</b>")
        return

    # Split logic safety check
    if "_" not in data:
        return

    action, target_user_id = data.split("_")
    target_user_id = int(target_user_id)

    # Shortened callback prefix string matching ('app' and 'rej')
    if action == "app":
        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text="🎉 <b>CONGRATULATIONS!</b>\n\nAapka screenshot <b>Approve</b> ho gaya hai aur verification complete hai! ✅",
                parse_mode="HTML"
            )
            await query.edit_message_caption(caption=f"{query.message.caption}\n\n🟢 STATUS: APPROVED", parse_mode="HTML")
        except Exception as e:
            print(f"Approve Action Error: {e}")

    elif action == "rej":
        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text="❌ <b>TASK REJECTED!</b>\n\nAapka screenshot <b>Reject</b> ho gaya hai. Kripya sahi se task karke dubara original screenshot bhejein. 🔄",
                parse_mode="HTML"
            )
            await query.edit_message_caption(caption=f"{query.message.caption}\n\n🔴 STATUS: REJECTED", parse_mode="HTML")
        except Exception as e:
            print(f"Reject Action Error: {e}")

def main():
    threading.Thread(target=run_server, daemon=True).start()
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(MessageHandler(filters.VIDEO, get_video_id))  
    app.add_handler(CallbackQueryHandler(button_handler))
    
    app.run_polling()

if __name__ == "__main__":
    main()
