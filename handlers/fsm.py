from aiogram.fsm.state import State, StatesGroup

class OrderStates(StatesGroup):
    """Состояния для FSM заказа"""
    waiting_for_photo = State()
    waiting_for_order_number = State()
    waiting_for_set_type = State()
    waiting_for_size = State()
    waiting_for_alumochrome = State()
    order_confirmed = State()
