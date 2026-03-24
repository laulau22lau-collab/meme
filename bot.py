import Logger
import config.telegram
import handlers.createAccount , handlers.error , handlers.button , handlers.syriatel_cash_deposit , handlers.sendGifts ,handlers.reseiveGifts
import handlers.command.start , handlers.command.balance , handlers.adminMessage , handlers.depositAccount, handlers.withdrawalAccount
from iChancyAPI import iChancyAPI
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

logger = Logger.getLogger()

try:
    config.telegram.validate_tokens()
except ValueError as e:
    logger.error(str(e))
    exit(1)


def main() -> None:
    """Main function to start the bot"""
    try:
                
        # Create application
        application = Application.builder().token(config.telegram.TOKEN).build()
        # Add conversations

        # Add handlers
        application.add_handler(handlers.createAccount.conversationHandler())
        application.add_handler(handlers.syriatel_cash_deposit.conversationHandler())
        application.add_handler(handlers.sendGifts.conversationHandler())
        application.add_handler(handlers.reseiveGifts.conversationHandler())
        application.add_handler(handlers.depositAccount.conversationHandler())
        application.add_handler(handlers.withdrawalAccount.conversationHandler())
        application.add_handler(handlers.adminMessage.conversationHandler())
        application.add_handler(CommandHandler('start', handlers.command.start.start))
        application.add_handler(CommandHandler('balance', handlers.command.balance.balance))
        # application.add_handler(CallbackQueryHandler(ichancy))
        application.add_handler(CallbackQueryHandler(handlers.button.button))
        application.add_error_handler(handlers.error.error_handler)

        # application.add_handler(CallbackQueryHandler(handlers.transactions_handlers.handle_transaction_callback))
        # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.transactions_handlers.handle_message))
        
        # Start the bot
        logger.info("Starting iChancy Account Manager Bot...")
        logger.info("Bot is running. Press Ctrl+C to stop.")
        
        application.run_polling(
            poll_interval=2.0,
            timeout=30,
            drop_pending_updates=True
        )
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
    finally:
        logger.info("Bot shutdown complete")

if __name__ == '__main__':
    import sys
    
    logger.info("Initializing iChancy Account Manager Bot...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        sys.exit(1)
    
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}", exc_info=True)
