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
            f"{emoji_finger} [Yahan Click Karke Next Channel Join Karein](https://t.me)\n\n"
            f"{emoji_alert} *channel pe jakar dekho step nahi to problem hoga bro !*"
        )

        # 2. User ko instant automatic link aur message bhejna
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
                text="🎉 CONGRATULATIONS!\n\nAapka screenshot Approve ho gaya hai aur verification complete hai! ✅",
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
                text="❌ TASK REJECTED!\n\nAapka screenshot Reject ho gaya hai. Kripya sahi se task karke dubara original screenshot bhejein. 🔄",
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
    app.add_handler(MessageHandler(filters.VIDEO, get_video_id))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Polling started successfully!")
    app.run_polling()

if __name__ == "__main__":
    main()
