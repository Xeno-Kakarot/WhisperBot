import shortuuid
from pyrogram import Client, filters
from pyrogram.types import *
from Whisper_db import Whispers

# Initialize the Toji client
hasnaikk = Client(
    "hasnainkkBot",
    api_id=123456,  # Replace with your API ID
    api_hash="your_api_hash",  # Replace with your API Hash
    bot_token="your_bot_token",  # Replace with your Bot Token
)


# Start command handler
@hasnainkk.on_message(filters.command("start") & filters.private)
async def start(_, message: Message):
    await message.reply_photo(
        "https://telegra.ph/file/fbfa4262e467652e75d83.jpg",
        caption=(
            "👋 Welcome to Whisper Bot!\n\n"
            "I allow you to send secret messages to anyone on Telegram. "
            "Only the recipient can read the message, and no one else!\n\n"
            "Send /help to learn more about how to use me."
        ),
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Help", callback_data="help")]
            ]
        )
    )


# Help command handler
@hasnainkk.on_message(filters.command("help") & filters.private)
async def help(_, message: Message):
    await message.reply_text(
        (
            "🛠 **How to use Whisper Bot**\n\n"
            "1. **Send a Whisper**: Type the username or ID of the user you want to send a secret message to.\n"
            "2. **Use Inline**: You can use the bot inline by typing `@YourBotUsername` in any chat followed by the recipient's username and your message.\n\n"
            "⚠️ Remember, whispers can be up to 200 characters long!"
        ),
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Back to Start", callback_data="start")]
            ]
        )
    )


# Inline query handler for whisper messages
@hasnainkk.on_inline_query()
async def mainwhisper(_, query):
    if not query.query:
        return await query.answer(
            [],
            switch_pm_text="Give me a username or ID!",
            switch_pm_parameter="ghelp_whisper",
        )

    text = query.query.split(" ")
    user = text[0]
    first = True
    message = ""
    if not user.startswith("@") and not user.isdigit():
        user = text[-1]
        first = False
    if first:
        message = " ".join(text[1:])
    else:
        text.pop()
        message = " ".join(text)
    if len(message) > 200:
        return
    usertype = "username"
    whisperType = "inline"
    if user.startswith("@"):
        usertype = "username"
    elif user.isdigit():
        usertype = "id"
    if user.isdigit():
        try:
            chat = await Toji.get_chat(int(user))
            user = f"@{chat.username}" if chat.username else chat.first_name
        except:
            user = user

    if len(message) > 200:
        await query.answer(
            [],
            switch_pm_text="Only text up to 200 characters is allowed!",
            switch_pm_parameter="ghelp_whisper",
        )
        return

    whisperData = {
        "user": query.from_user.id,
        "withuser": user,
        "usertype": usertype,
        "type": "inline",
        "message": message,
    }
    whisperId = shortuuid.uuid()

    # Add the whisper to the database
    await Whispers.add_whisper(whisperId, whisperData)

    answers = [
        InlineQueryResultArticle(
            title=f"🔐 Send a whisper message to {user}!",
            description="Only they can see it!",
            input_message_content=InputTextMessageContent(
                f"🔐 A Whisper Message For {user}\nOnly they can see it!"
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "😏 Show Whisper",
                            callback_data=f"whisper_{whisperId}",
                        )
                    ]
                ]
            ),
        )
    ]

    await query.answer(answers)


@hasnainkk.on_callback_query(filters.regex("^whisper_"))
async def showWhisper(_, callback_query):
    whisperId = callback_query.data.split("_")[-1]
    whisper = await Whispers.get_whisper(whisperId)

    if not whisper:
        await callback_query.answer("This whisper is not valid anymore!")
        return

    userType = whisper["usertype"]

    if callback_query.from_user.id == whisper["user"]:
        await callback_query.answer(whisper["message"], show_alert=True)
    elif (
        userType == "username"
        and callback_query.from_user.username
        and callback_query.from_user.username.lower()
        == whisper["withuser"].replace("@", "").lower()
    ):
        await callback_query.answer(whisper["message"], show_alert=True)
        await Whispers.del_whisper(whisperId)
        await callback_query.edit_message_text(
            f"{whisper['withuser']} read the Whisper."
        )
    elif userType == "id" and callback_query.from_user.id == int(whisper["withuser"]):
        user = await Toji.get_users(int(whisper["withuser"]))
        username = user.username or user.first_name
        await callback_query.answer(whisper["message"], show_alert=True)
        await Whispers.del_whisper(whisperId)
        await callback_query.edit_message_text(f"{username} read the whisper.")
    else:
        await callback_query.answer("Not your Whisper!", show_alert=True)


# Callback for help and start navigation
@hasnainkk.on_callback_query(filters.regex("help"))
async def callback_help(_, callback_query):
    await help(_, callback_query.message)


@hasnainkk.on_callback_query(filters.regex("start"))
async def callback_start(_, callback_query):
    await start(_, callback_query.message)


# Start the client
hasnainkk.run()
                  
