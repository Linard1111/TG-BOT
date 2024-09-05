from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

# Вставьте сюда ваш токен
TOKEN = '7026950118:AAG3t0m8bG6hrQa5wPOgO0sn66a_4fprhXc'
ADMIN_ID = 5782338073

# Множество для хранения уникальных ID пользователей
users_set = set()

def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    # Добавляем пользователя в множество
    users_set.add(user_id)

    update.message.reply_text(
        'Привет! Отправьте пост и я передам его 3-ему админу! '
        'Хочу напомнить, что мы тут НИКОГО НЕ ИЩЕМ, я не удаляю посты для этого пишите @amwwo, и не ищу админов!'
    )

def forward_to_admin(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user

    if user.id == ADMIN_ID and not update.message.text.startswith('/'):
        update.message.reply_text("Вы не можете отправлять сообщения самому себе.")
        return

    keyboard = [
        [
            InlineKeyboardButton("Кто отправил?", callback_data=f'who_sent_{user.id}')  # Передаем ID пользователя
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(
        chat_id=ADMIN_ID,
        text=update.message.text,
        reply_markup=reply_markup
    )

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    # Извлекаем ID пользователя из callback_data
    if query.data.startswith('who_sent_'):
        user_id = int(query.data.split('_')[2])  # Получаем ID пользователя из callback_data
        user = context.bot.get_chat(user_id)  # Получаем объект пользователя

        # Формируем информацию о пользователе
        username = f"@{user.username}" if user.username else f"{user.first_name} {user.last_name}"
        user_info = f"Имя пользователя: {username}\nID пользователя: {user.id}"

        # Отправляем информацию об пользователе админу
        context.bot.send_message(
            chat_id=ADMIN_ID,
            text=user_info
        )

def list_users(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id != ADMIN_ID:
        update.message.reply_text("Только администратор может использовать эту команду.")
        return

    if not users_set:
        update.message.reply_text("Нет пользователей, запустивших бота.")
    else:
        user_list = []
        for user_id in users_set:
            user = context.bot.get_chat(user_id)
            username = f"@{user.username}" if user.username else f"{user.first_name} {user.last_name}"
            user_list.append(f"ID: {user.id}, Имя пользователя: {username}")
        
        total_users = len(users_set)
        update.message.reply_text(f"Список пользователей, запустивших бота:\n" + "\n".join(user_list) + f"\n\nВсего пользователей: {total_users}.")

def main() -> None:
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, forward_to_admin))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(CommandHandler("list", list_users))  # Изменили команду на "/list"

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
