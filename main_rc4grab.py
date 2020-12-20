# RC4Grab skeleton code

import json
import requests
import time
import random
import telegram

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

from secret import * # local secret.py file

URL = "https://api.telegram.org/bot{}/".format(TOKEN)


# UTILITY #

def start(update,context):
    update.message.reply_text("I'm alive!")

def ping(update, context):
    update.message.reply_text("pong! 🏓")

def help(update,context):
    update.message.reply_text("Currently available commands\n\n"
                              
                              "\nTo be implemented for v1.0:\n"
                              "• /new - create a new request\n"
                              "• /viewall - view all currently OPEN requests\n"
                              "• /viewmy - view all my created requests (OPEN/ONGOING)\n"
                              "• /viewtodo - view all my accepted requests (ONGOING)\n"

                              "\nUtility:\n"
                              "• /start\n"
                              "• /ping\n"
                              "• /help\n\n"

                              )



# METHODS TO BE IMPLEMENTED FOR v1.0

def CreateNewRequest(update, context):
    keyboard = [
        [
            InlineKeyboardButton(text="Food Dabao", callback_data='food'),
            InlineKeyboardButton(text="Others", callback_data='other'),
        ]
    ]
    replyMarkup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("What is the category of your new request?", reply_markup = replyMarkup)

# helper function - to handle CreateNewRequests callback queries    
def CreateNewRequestKeyboard(update, context):
    query = update.callback_query
    
    if (query.data == 'food'):
        # query.edit_message_text(f"Selected option: {query.data}", )
        # context.bot.send_message(chat_id=update.effective_chat.id, text="hi from food")
        keyboard = [
            [
                InlineKeyboardButton(text="Create my request!", callback_data='create_new'),
            ]
        ]
        replyMarkup = InlineKeyboardMarkup(keyboard)                       
        
        query.edit_message_text("Food Dabao it is. What is your order?"
                                "\n\n(TODO: implement ability for user to order via typing in, or inline keyboard menu. For now just press the button)", 
                                reply_markup = replyMarkup)          

    elif (query.data == 'create_new'):
        query.edit_message_text("Success! Your request has been created."
                                "\nNote: requests will be in either of 3 states: OPEN, ONGOING, CLOSED"
                                "\nTODO: add newly created request to a 'masterlist'")

    elif (query.data == 'other'):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Coming soon!")
    
    query.answer()

def ViewAllRequests(update, context):
    update.message.reply_text(f"Here are all the currently OPEN requests:\n\n{request1}\n\n{request2}\n\n{request3}")
    update.message.reply_text("Notes:"
                              "\nCan be called via PM and in a group chat. This is the only command that can be called from a group chat."
                              "\nTODO: if called via pm, implement ability for user to accept requests (send a request from OPEN to ONGOING)")

def ViewMyRequests(update, context):
    update.message.reply_text(f"Your currently OPEN/ONGOING requests:\n\n{request1}\n\n{request2}")
    update.message.reply_text("Notes:"
                              "\nCan only be called via PM."
                              "\nTODO: implement ability to delete requests.")

def ViewAcceptedRequests(update,context):
    update.message.reply_text(f"You have accepted these requests (ONGOING):\n\n{request2}\n\n{request3}")
    update.message.reply_text("Notes:"
                              "\nCan only be called via PM."
                              "\nTODO: implement ability to manage requests. 1) 'unaccept' a request (send from ONGOING back to OPEN), or 2) mark a request as completed (send from ONGOING to CLOSED).")

# some filler data
request1 = "User: @xxx\nRequest Type: food\nRequest Details: lorem ipsum 111"
request2 = "User: @yyy\nRequest Type: food\nRequest Details: lorem ipsum 222"
request3 = "User: @zzz\nRequest Type: food\nRequest Details: lorem ipsum 333"


# REFERENCE CODE #

def redblack(update, context):
    question = "Red / Black"
    options= ["Red","Black"]
    keyboard = [[InlineKeyboardButton("Close round", callback_data='Close')]]
    context.bot.send_poll(chat_id=update.effective_chat.id,
                          question=question,
                          options=options,
                          is_anonymous=True,
                          allows_multiple_answers=False,
                          reply_markup=InlineKeyboardMarkup(keyboard),
                          is_closed=False,
                          disable_notification=True,
                          )

# helper function - redblack callback queries
def Button(update,context):
    query = update.callback_query

    if (query.data == "Close"):
        keyboard = [[InlineKeyboardButton("RESET", callback_data='Reset')]]
        context.bot.stop_poll(chat_id=update.effective_chat.id,
                              message_id=update.effective_message.message_id,
                              reply_markup=InlineKeyboardMarkup(keyboard)
                              )
        query.answer()

    elif (query.data == "Reset"):
        update.effective_message.delete()
        question = "Red / Black"
        options= ["Red","Black"]
        keyboard = [[InlineKeyboardButton("Close round", callback_data='Close')]]
        update.effective_chat.send_poll(question=question,
                                        options=options,
                                        is_anonymous=True,
                                        allows_multiple_answers=False,
                                        reply_markup=InlineKeyboardMarkup(keyboard),
                                        is_closed=False,
                                        disable_notification=True,
                                        )
        query.answer()

def set_timer(update, context):
    # Add a job to the queue.
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(context.args[0])
        if due < 0:
            update.message.reply_text("Usage: /set <seconds> <message>")
            return
            
        if context.args[1] == "":
            update.message.reply_text("Usage: /set <seconds> <message>")
            return

        # Add job to queue and stop current one if there is a timer already
        #if 'job' in context.chat_data: #remove current job, if it exists
        #    old_job = context.chat_data['job']
        #    old_job.schedule_removal()
        
        argv = " ".join(context.args).split(" ")
        usr_msg = ""
        for i in range (1, len(argv)):
            usr_msg = usr_msg + " " + argv[i]
        
        new_job = context.job_queue.run_once(alarm, due, context = {"chat_id": update.message.chat_id, "str": usr_msg})
        context.chat_data['job'] = new_job

        update.message.reply_text("I will remind you in {} seconds! ({} minutes)".format(due, round(due/60,2)))
        
    except (IndexError, ValueError):
        update.message.reply_text("Usage: /set <seconds> <message>")
        
def alarm(context):
    """Send the alarm message."""
    job = context.job
    context.bot.send_message(job.context["chat_id"], job.context["str"])


def main():

  # Create Updater object and attach dispatcher to it
  updater = Updater(TOKEN, use_context=True)
  dp = updater.dispatcher

  # Add '<command>' command handler to dispatcher

  # Utility
  dp.add_handler(CommandHandler('start',start))
  dp.add_handler(CommandHandler('help',help))
  dp.add_handler(CommandHandler('ping',ping))

  # To be implemented for v1.0
  dp.add_handler(CommandHandler('new',CreateNewRequest))
  dp.add_handler(CallbackQueryHandler(CreateNewRequestKeyboard))
  dp.add_handler(CommandHandler('viewall',ViewAllRequests))
  dp.add_handler(CommandHandler('viewmy',ViewMyRequests))
  dp.add_handler(CommandHandler('viewtodo',ViewAcceptedRequests))

  #   dp.add_handler(CommandHandler('redblack',redblack))
  #   dp.add_handler(CallbackQueryHandler(Button))
  #   dp.add_handler(CommandHandler('set', set_timer, pass_args=True, pass_job_queue=True, pass_chat_data=True))

  # Start the bot
  updater.start_polling()

  print("hello world")

  # Run the bot until you press Ctrl-C
  updater.idle()

if __name__ == '__main__':
  main()
