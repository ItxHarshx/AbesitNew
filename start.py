from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from info import SUDO_USERS

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
mention = update.effective_user.mention_html(
update.effective_user.first_name
)
bot = await context.bot.get_me()

if update.effective_chat.type == "private":  
    text = (  
        f'👋 Hey <b>{mention}</b>!\n\n'  
        f'I am <a href="tg://user?id={bot.id}"><b>{context.bot.first_name}</b></a>, a community management bot designed for the group Abesit Batch 2026-27.\n\n'  
    )  

    keyboard = [  
         [  
             InlineKeyboardButton(  
                 "Help & Commands",  
                 callback_data="help"  
             )  
         ],  
        [  
            InlineKeyboardButton(  
                "Bot Dev",  
                url="https://t.me/BrandedPsycho"  
            ),  
            InlineKeyboardButton(  
                "Admins",  
                callback_data="sudoers"  
            ),  
            InlineKeyboardButton(  
                "ℹ️ About",  
                callback_data="about"  
            )  
        ]  
    ]  

    reply_markup = InlineKeyboardMarkup(keyboard)  

    await update.message.reply_html(  
        text,  
        reply_markup=reply_markup  
    )  

else:  
    text = (  
        f'👋 Hey <b>{mention}</b>!\n\n'  
        f'I am <a href="tg://user?id={bot.id}"><b>{context.bot.first_name}</b></a>, a community management bot designed for the group Abesit Batch 2026-27.\n\n'  
    )  

    keyboard = [  
        [  
            InlineKeyboardButton(  
                "Open Bot in Dm",  
                url=f"https://t.me/{bot.username}?start=start"  
            )  
        ]  
    ]  

    reply_markup = InlineKeyboardMarkup(keyboard)  

    await update.message.reply_html(  
        text,  
        reply_markup=reply_markup  
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
query = update.callback_query
await query.answer()
mention = update.effective_user.mention_html(
update.effective_user.first_name
)
bot = await context.bot.get_me()

if query.data == "sudoers":  

    sudo_text = "<b>👮 Official Admins</b>\n\n"  

    for user_id in SUDO_USERS:  
        try:  
            user = await context.bot.get_chat(user_id)  

            sudo_text += (  
                f'• <a href="tg://user?id={user.id}">'  
                f'{user.first_name}</a>\n'  
            )  

        except Exception:  
            pass  

    keyboard = [  
        [  
            InlineKeyboardButton(  
                "⬅️ Back",  
                callback_data="back_start"  
            )  
        ]  
    ]  

    await query.edit_message_text(  
        sudo_text,  
        parse_mode="HTML",  
        reply_markup=InlineKeyboardMarkup(keyboard)  
    )  

elif query.data == "back_start":  

    bot = await context.bot.get_me()  

    text = (  
        f'👋 Hey <b>{mention}</b>!\n\n'  
        f'I am <a href="tg://user?id={bot.id}">'  
        f'<b>{context.bot.first_name}</b></a>, your ABESIT assistant.\n\n'  
    )  
      
    keyboard = [  
         [  
             InlineKeyboardButton(  
                 "Help & Commands",  
                 callback_data="help"  
             )  
         ],  
        [  
            InlineKeyboardButton(  
                "Bot Dev",  
                url="https://t.me/BrandedPsycho"  
            ),  
            InlineKeyboardButton(  
                "Admins",  
                callback_data="sudoers"  
            ),  
            InlineKeyboardButton(  
                "ℹ️ About",  
                callback_data="about",  
            )  
        ]  
    ]  

    await query.edit_message_text(  
        text,  
        parse_mode="HTML",  
        reply_markup=InlineKeyboardMarkup(keyboard)  
    )  
      
elif query.data == "about":  
      
    text = (  
    "<b>ℹ️ About ABESIT Assistant</b>\n\n"  
    "Version: 1.0\n\n"  
    "ABESIT Assistant is a community management bot "  
    "designed for the ABESIT Batch group.\n\n"  
    "Developed and maintained by @BrandedPsycho."  
)  
      
    keyboard = [  
    [  
        InlineKeyboardButton(  
            "⬅️ Back",  
            callback_data="back_start"  
        )  
    ]  
]  
    await query.edit_message_text(  
    text,  
    parse_mode="HTML",  
    reply_markup=InlineKeyboardMarkup(keyboard)  
)  
      
elif query.data == "help":  
    text = (  
        "<b>🤖 ABESIT Assistant</b>\n\n"  
        "Current Features:\n\n"  
        "- Announcements\n"  
        "- Group Lock System\n"  
        "- Admin Management\n"  
        "- Bot Monitoring\n\n"  
        "Choose a category below."  
    )  
    keyboard = [  
        [  
            InlineKeyboardButton(  
                "General",  
                callback_data="help_general"  
            ),  
            InlineKeyboardButton(  
                "Admin",  
                callback_data="help_admin"  
            ),  
            InlineKeyboardButton(  
                "Features",  
                callback_data="help_features"  
            )  
        ],  
        [  
            InlineKeyboardButton(  
                "📞 Contact",  
                callback_data="help_contact"  
            )  
        ],  
        [  
                  
            InlineKeyboardButton(  
                "⌧ Close",  
                callback_data="help_close"  
            )  
        ]  
    ]  
      
    await query.edit_message_text(  
        text,  
        parse_mode="HTML",  
        reply_markup=InlineKeyboardMarkup(keyboard)  
    )  
  
elif query.data == "help_general":  
    text = (  
        "<b>👥 General Commands</b>\n\n"  
        "/start - Open bot menu\n"  
        "/ping - Check bot status\n"  
        "/lockstatus - View group lock status\n"  
        "/contacts - get college contacts"  
    )  
    keyboard = [  
        [  
            InlineKeyboardButton(  
                "General",  
                callback_data="help_general"  
            ),  
            InlineKeyboardButton(  
                "Admin",  
                callback_data="help_admin"  
            ),  
            InlineKeyboardButton(  
                "Features",  
                callback_data="help_features"  
            )  
        ],  
        [  
            InlineKeyboardButton(  
                "📞 Contact",  
                callback_data="help_contact"  
            )  
        ],  
        [  
            InlineKeyboardButton(  
                "⌧ Close",  
                callback_data="help_close"  
            )  
        ]  
    ]  
      
    await query.edit_message_text(  
        text,  
        parse_mode="HTML",  
        reply_markup=InlineKeyboardMarkup(keyboard)  
    )  
  
elif query.data == "help_admin":  
    text = (  
        "<b>🛡️ Admin Commands</b>\n\n"  
        "/announce - Post announcement\n"  
        "/pin - Pin a message\n"  
        "/unpin - Remove pinned messages\n"  
        "/lockgroup - Lock the group\n"  
        "/unlockgroup - Unlock the group"  
    )  
      
    keyboard = [  
        [  
            InlineKeyboardButton(  
                "General",  
                callback_data="help_general"  
            ),  
            InlineKeyboardButton(  
                "Admin",  
                callback_data="help_admin"  
            ),  
            InlineKeyboardButton(  
                "Features",  
                callback_data="help_features"  
            )  
        ],  
        [  
            InlineKeyboardButton(  
                "📞 Contact",  
                callback_data="help_contact"  
            )  
        ],  
        [  
            InlineKeyboardButton(  
                "⌧ Close",  
                callback_data="help_close"  
            )  
        ]  
    ]  
      
    await query.edit_message_text(  
        text,  
        parse_mode="HTML",  
        reply_markup=InlineKeyboardMarkup(keyboard)  
    )  
  
elif query.data == "help_features":  
    text = (  
        "<b>Features</b>\n\n"  
        "- Announcement System\n"  
        "- Group Lock System\n"  
        "- Pin Management\n"  
        "- Sudo Management\n"  
        "- Bot Monitoring\n"  
        "- Interactive Menus"  
    )  
    keyboard = [  
        [  
            InlineKeyboardButton(  
                "General",  
                callback_data="help_general"  
            ),  
            InlineKeyboardButton(  
                "Admin",  
                callback_data="help_admin"  
            ),  
            InlineKeyboardButton(  
                "Features",  
                callback_data="help_features"  
            )  
        ],  
        [  
            InlineKeyboardButton(  
                "📞 Contact",  
                callback_data="help_contact"  
            )  
        ],  
        [  
            InlineKeyboardButton(  
                "⌧ Close",  
                callback_data="help_close"  
            )  
        ]  
    ]  
      
    await query.edit_message_text(  
        text,  
        parse_mode="HTML",  
        reply_markup=InlineKeyboardMarkup(keyboard)  
    )  
  
elif query.data == "help_contact":  
    text = (  
        "<b>📞 Important Contacts: College</b>\n\n"  
        "<b>• Contact</b>\n"  
        "<code>+91 97110 60923</code>\n\n"  
          
        "<b>• Whatsapp/Calling</b>\n"  
        "<code>+91 97110 60929</code>\n"   
        "<code>+91 82875 16759</code>\n\n"  
          
        "<b>• Email & Website</b>\n"  
        "- - - -"  
          
    )  
      
    keyboard = [  
        [  
            InlineKeyboardButton(  
                "General",  
                callback_data="help_general"  
            ),  
            InlineKeyboardButton(  
                "Admin",  
                callback_data="help_admin"  
            ),  
            InlineKeyboardButton(  
                "Features",  
                callback_data="help_features"  
            )  
        ],  
        [  
            InlineKeyboardButton(  
                "📞 Contact",  
                callback_data="help_contact"  
            )  
        ],  
        [  
            InlineKeyboardButton(  
                "⌧ Close",  
                callback_data="help_close"  
            )  
        ]  
    ]  
      
    await query.edit_message_text(  
        text,  
        parse_mode="HTML",  
        reply_markup=InlineKeyboardMarkup(keyboard),  
        disable_web_page_preview=True  
    )  
elif query.data == "help_close":  
    try:  
        await query.message.delete()  
    except:  
        pass    
