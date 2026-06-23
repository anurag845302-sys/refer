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

# --- CONFIGURATION ---
# ⚠️ ATTENTION: BotFather se "Revoke current token" karne ke baad mila NAYA token hi yahan dalein.
# Agar purana token dalenge toh Render fir se InvalidToken ka error dega.
BOT_TOKEN = "8912203562:AAHm6s4id2SOMkfxXVrHqEtlzmWJouimMFQ" 
ADMIN_ID = 8934747857
SUPPORT_USERNAME = "@FrontMan4u"
CHANNEL_USERNAME = "@BuynSellLoots" 
CHANNEL_LINK = "https://t.me/BuynSellLoots"

# Video File ID
VIDEO_FILE_ID = "BAACAgUAAxkBAAMZajpE7Xz073kZu4E5VJWDlcD0qKkAAqQiAALfXNFVhAigRIO2guE8BA" 

# --- 🚀 AUTOMATIC REWARD CONFIGURATION ---
SUCCESS_LINK = "https://t.me/buynsellloots"  

# 📂 Jab aap APK file forward karenge aur niche handler se ID milegi, toh use yahan dalein
SUCCESS_FILE_ID = "BQACAgUAAxkBAANDajqWHHAWTwOnip55NTn5zFZwPtIAArghAAK_aVhV3r8er5hy1RE8BA"  

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
    return "Bot is Running Perfectly!"

def run_server():
    port = int(os.environ.get('PORT', 8080))
    flask_app.run(host='0.0.0.0', port=port)

async def is_user_joined(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception as e:
        print(f"Join Check Error: {e}")
        return False

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

# --- 🛠️ FIXED ADMIN TOOLS (CRASH FREE ID GETTER) ---
async def get_file_ids(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    # Video ID fetcher
    if update.message.video:
        file_id = update.message.video.file_id
        await update.message.reply_text(f"🎥 <b>Video File ID:</b>\n\n<code>{file_id}</code>", parse_mode="HTML")
        return
    
    # APK/Document ID fetcher
    if update.message.document:
        file_id = update.message.document.file_id
        file_name = update.message.document.file_name
        await update.message.reply_text(f"📦 <b>File/APK ID ({file_name}):</b>\n\n<code>{file_id}</code>", parse_mode="HTML")
        return

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
            InlineKeyboardButton("✅ Approve", callback_data=f"ap_{user.id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"rj_{user.id}")
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

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id

    await query.answer()

    if data == "check_join":
        if await is_user_joined(context, user_id):
            try:
                await query.message.delete()
            except Exception as e:
                print(f"Delete Error: {e}")
            await send_welcome_content(context, user_id)
        else:
            await context.bot.send_message(chat_id=user_id, text="❌ <b>Aapne abhi tak channel join nahi kiya hai!</b> Kripya pehle upar diye link se join karein.", parse_mode="HTML")
        return

    if "_" not in data:
        return

    action, target_user_id = data.split("_")
    target_user_id = int(target_user_id)

    # Approve Action
    if action == "ap":
        try:
            success_msg = (
                "🎉 <b>CONGRATULATIONS!</b>\n\n"
                "Aapka screenshot <b>Approve</b> ho gaya hai aur verification complete hai! ✅\n\n"
                f"🎁 <b>Aapka Reward Link/Secret Link yeh raha:</b>\n"
                f"👉 {SUCCESS_LINK}\n\n"
                "<i>Niche diye gaye link par click karke join/access karein!</i>"
            )
            await context.bot.send_message(chat_id=target_user_id, text=success_msg, parse_mode="HTML", disable_web_page_preview=True)
            
            if SUCCESS_FILE_ID:
                await context.bot.send_document(
                    chat_id=target_user_id,
                    document=SUCCESS_FILE_ID,
                    caption="📦 <b>Aapki requested file/app yeh rahi!</b>"
                )

            await query.message.delete()
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"🟢 <b>Task Approved Successfully!</b>\n👤 User ID: {target_user_id}\n🎁 Reward sent automatically.",
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"Approve Action Error: {e}")

    # Reject Action
    elif action == "rj":
        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text="❌ <b>TASK REJECTED!</b>\n\nAapka screenshot <b>Reject</b> ho gaya hai. Kripya sahi se task karke dubara original screenshot bhejein. 🔄",
                parse_mode="HTML"
            )
            await query.message.delete()
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"🔴 <b>Task Rejected!</b>\n👤 User ID: {target_user_id}",
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"Reject Action Error: {e}")

def main():
    threading.Thread(target=run_server, daemon=True).start()
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    
    # ✅ FIX: Fixed standard library filters compatibility 
    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.ALL, get_file_ids))  
    
    app.add_handler(CallbackQueryHandler(button_handler))
    
    app.run_polling()

if __name__ == "__main__":
    main()
