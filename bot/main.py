import asyncio, json
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineQueryResultArticle, InputTextMessageContent
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.config import BOT_TOKEN, ADMIN_ID, TARIFFS, PAY_TEXT
from bot.db import Session, Order, create_user

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def admin_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="📦 Все заказы", callback_data="orders_all")
    kb.button(text="🟢 В ожидании", callback_data="orders_wait")
    kb.button(text="📊 Статистика", callback_data="admin_stats")
    kb.adjust(2)
    return kb.as_markup()

def admin_order_buttons(order_id):
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Подтвердить", callback_data=f"ok_{order_id}")
    kb.button(text="❌ Отменить", callback_data=f"cancel_{order_id}")
    kb.adjust(2)
    return kb.as_markup()

@dp.message(F.content_type=="web_app_data")
async def webapp_handler(m: Message):
    data = json.loads(m.web_app_data.data)
    action = data.get("action")
    query_id = m.web_app_data.query_id
    async with Session() as session:
        if action.startswith("buy_"):
            tariff_key = action.split("_")[1]
            t = TARIFFS[tariff_key]
            order = Order(user_id=m.from_user.id, username=m.from_user.username,
                          tariff=tariff_key, status="wait", webapp_query_id=query_id)
            session.add(order)
            await session.commit()
            await session.refresh(order)
            await m.answer(PAY_TEXT)
            await bot.send_message(ADMIN_ID, f"💰 Новый заказ #{order.id} ({tariff_key})",
                                   reply_markup=admin_order_buttons(order.id))
        elif action=="connect":
            t = TARIFFS["m1"]
            link = create_user(f"user_{m.from_user.id}", t["days"], t["devices"])
            await m.answer(f"🟢 Ваша ссылка:\n{link}")
        elif action=="stats":
            await m.answer("📊 Трафик: 120GB / 500GB\n🕒 Окончание: 2026-02-11")

@dp.message(F.text=="/admin")
async def admin_start(m: Message):
    if m.from_user.id != ADMIN_ID:
        return
    await m.answer("👨‍💻 Админ-панель", reply_markup=admin_menu())

@dp.callback_query(F.data.startswith("orders_"))
async def list_orders(cb: CallbackQuery):
    if cb.from_user.id != ADMIN_ID:
        return
    status = cb.data.split("_")[1]
    async with Session() as session:
        if status=="all":
            orders = (await session.execute("SELECT * FROM orders")).scalars().all()
        else:
            orders = (await session.execute("SELECT * FROM orders WHERE status='wait'")).scalars().all()
    if not orders:
        await cb.message.answer("📦 Заказы отсутствуют")
        return
    for o in orders:
        text = f"📦 Заказ #{o.id}\nПользователь: @{o.username}\nТариф: {o.tariff}\nСтатус: {o.status}"
        await cb.message.answer(text, reply_markup=admin_order_buttons(o.id))

@dp.callback_query(F.data.startswith("ok_"))
async def approve_order(cb: CallbackQuery):
    if cb.from_user.id != ADMIN_ID:
        return
    order_id = int(cb.data.split("_")[1])
    async with Session() as session:
        order = await session.get(Order, order_id)
        if not order or order.status=="done":
            return
        t = TARIFFS[order.tariff]
        link = create_user(f"user_{order.id}", t["days"], t["devices"])
        order.status = "done"
        await session.commit()
    if getattr(order, "webapp_query_id", None):
        await bot.answer_web_app_query(
            web_app_query_id=order.webapp_query_id,
            result=InlineQueryResultArticle(
                id=str(order.id),
                title="Ссылка Hysteria2",
                input_message_content=InputTextMessageContent(link)
            )
        )
    else:
        await bot.send_message(order.user_id, f"🟢 Ваша ссылка:\n{link}")
    await cb.message.edit_text("✅ Оплата подтверждена")

@dp.callback_query(F.data.startswith("cancel_"))
async def cancel_order(cb: CallbackQuery):
    if cb.from_user.id != ADMIN_ID:
        return
    order_id = int(cb.data.split("_")[1])
    async with Session() as session:
        order = await session.get(Order, order_id)
        if order and order.status=="wait":
            order.status="canceled"
            await session.commit()
    await cb.message.edit_text("❌ Заказ отменён")

@dp.callback_query(F.data=="admin_stats")
async def admin_stats(cb: CallbackQuery):
    async with Session() as session:
        total_orders = (await session.execute("SELECT COUNT(*) FROM orders")).scalar()
        done_orders = (await session.execute("SELECT COUNT(*) FROM orders WHERE status='done'")).scalar()
        wait_orders = (await session.execute("SELECT COUNT(*) FROM orders WHERE status='wait'")).scalar()
    await cb.message.answer(f"📊 Статистика\nВсего заказов: {total_orders}\n✅ Подтверждено: {done_orders}\n⏳ В ожидании: {wait_orders}")

async def main():
    await dp.start_polling(bot)

if __name__=="__main__":
    asyncio.run(main())
