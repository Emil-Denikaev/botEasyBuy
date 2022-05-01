from aiogram import Dispatcher, types, Bot
from tgbot.messages import MESSAGES
from aiogram.types import ContentType

from tgbot.config import load_config

config = load_config(".env")
pay_token = config.tg_bot.pay_token
tmi = config.tg_bot.tmi
bot = Bot(token=config.tg_bot.token, parse_mode=types.ParseMode.MARKDOWN_V2)


def register_pay(dp: Dispatcher):
    PRICE = types.LabeledPrice(label='Настоящая Машина Времени', amount=4200000)

    @dp.message_handler(commands=['terms'])
    async def process_terms_command(message: types.Message):
        await message.reply(MESSAGES['terms'], reply=False)

    @dp.message_handler(commands=['buy'])
    async def process_buy_command(message: types.Message):
        if pay_token.split(':')[1] == 'TEST':
            await bot.send_message(message.chat.id, MESSAGES['pre_buy_demo_alert'])

        await bot.send_invoice(message.chat.id,
                               description=MESSAGES['tm_description'],
                               title=MESSAGES['tm_title'],
                               provider_token=pay_token,
                               currency='rub',
                               photo_url=tmi,
                               photo_height=512,  # !=0/None, иначе изображение не покажется
                               photo_width=512,
                               photo_size=512,
                               is_flexible=False,  # True если конечная цена зависит от способа доставки
                               prices=[PRICE],
                               start_parameter='time-machine-example',
                               payload='some-invoice-payload-for-our-internal-use'
                               )

    @dp.pre_checkout_query_handler(lambda query: True)
    async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
        await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

    @dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
    async def process_successful_payment(message: types.Message):
        print('successful_payment:')
        pmnt = message.successful_payment.to_python()
        for key, val in pmnt.items():
            print(f'{key} = {val}')

        await bot.send_message(
            message.chat.id,
            MESSAGES['successful_payment'].format(
                total_amount=message.successful_payment.total_amount // 100,
                currency=message.successful_payment.currency
            )
        )
