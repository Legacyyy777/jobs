from aiogram.fsm.state import State, StatesGroup

class UserStates(StatesGroup):
    """Состояния для FSM пользователя"""
    waiting_for_profession = State()

class OrderStates(StatesGroup):
    """Состояния для FSM заказа"""
    waiting_for_photo = State()
    waiting_for_order_number = State()
    waiting_for_set_type = State()
    waiting_for_size = State()
    waiting_for_alumochrome = State()
    waiting_for_suspensia_type = State()
    waiting_for_suspensia_quantity = State()
    waiting_for_spraying = State()
    waiting_for_deep_spraying = State()
    waiting_for_shallow_spraying = State()
    order_confirmed = State()

class EditOrderStates(StatesGroup):
    """Состояния для FSM редактирования заказов"""
    waiting_for_order_number = State()
    waiting_for_new_price = State()