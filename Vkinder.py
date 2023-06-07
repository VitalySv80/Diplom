import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from config import group_token
from vk_function import VkInfo

vk = vk_api.VkApi(token=group_token)
longpoll = VkLongPoll(vk)

@staticmethod
    def current_keyboard():
        """
        Creates a keyboard to interact with the chatbot.
        :return Keyboard JSON-object
        """
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('Show', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Add to favorites', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('No, thank you', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button('Favorites list', color=VkKeyboardColor.SECONDARY)
        keyboard.add_button('Black list', color=VkKeyboardColor.SECONDARY)
        return keyboard.get_keyboard()


def start():
    """Функция описывает логику поведения чат-бота при общение с пользователем"""
    temp_count = {}
    token_dict = {}
    tmp = []
    temp_dict = {}
    count_tmp = 0
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            request = event.text
            if count_tmp == 0:
                write_msg_start(event.user_id, f'Нажмите "Старт"')
                count_tmp += 1
                continue
            if request == "Старт":
                write_msg(event.user_id, f"Привет, {event.user_id}. Сейчас найдем пару!"
                                       
                temp_count[event.user_id] = 0
                continue
            if temp_count[event.user_id] == 0:
                test_user = VkInfo(request)
                if test_user.check_token() == 1:
                    write_msg_2_button(event.user_id, f'Теперь укажите фамилию и имя или id пользователя для '
                                                      f'которого будем искать пару. Что выберете? ')
                    token_dict[event.user_id] = request
                    temp_count[event.user_id] = 1
                else:
                    write_msg(event.user_id, f"Токен указан неверный. Проверьте корректность введенного токена")
                continue
            user = VkInfo(token_dict[event.user_id])
            if request == "Ввести фамилию и имя":
                write_msg(event.user_id, f'Введите Фамилию и Имя')
                temp_count['name'] = 1
                continue
            if temp_count.get('name') == 1:
                if user.find_user_by_name(request) != 'error':
                    write_msg_next_2(event.user_id, f'Пользователь идентифицирован. Нажмите "Далее"')
                    temp_dict['user_id'] = user.find_user_by_name(request)
                    tmp = get_list_parametrs(token_dict[event.user_id], temp_dict['user_id'])
                    temp_count['name_2'] = 1
                    temp_count['name'] = 0
                    continue
                else:
                    temp_count['name'] = 0
                    write_msg_id(event.user_id,
                                 f'Не удалось идентифицировать пользователя. Нажмите "Ввести ID пользователя"'
                                 )
            if request == "Далее":
                if user.get_user_info(temp_dict['user_id']) != 'error':
                    write_msg_find(event.user_id, f"Все данные получены")
                else:
                    write_msg_hand(event.user_id,
                                   f'Данных из профиля недостаточно.Нажмите "Задать параметры вручную" '
                                   f'для выбора параметров'
                                   )
            if request == "Ввести ID пользователя":
                write_msg(event.user_id, f'Введите ID пользователя')
                temp_count['id'] = 1
                continue
            if temp_count.get('id') == 1:
                temp_dict['user_id'] = request
                if user.get_user_info(request) != 'error':
                    write_msg_find(event.user_id, f"Все данные получены")
                    tmp = get_list_parametrs(token_dict[event.user_id], temp_dict['user_id'])
                    temp_count['id'] = 0
                    continue
                else:
                    temp_count['id'] = 0
                    write_msg_hand(event.user_id,
                                   f'Данных из профиля недостаточно.Нажмите "Задать параметры вручную" '
                                   f'для выбора параметров'
                                   )
                    continue
            if request == "Задать параметры вручную" or temp_count.get('hand') == 1:
                temp_count['hand'] = 1
                if request == "Задать параметры вручную":
                    write_msg(event.user_id, f"Укажите пол: 1 - женский, 2 - мужской")
                    continue
                if request == "1" or request == "2":
                    tmp.append(request)
                    write_msg(event.user_id, f"Укажите город")
                    temp_count['sex'] = 1
                    continue
                if temp_count['sex'] == 1:
                    users = VkInfo(token_dict[event.user_id])
                    tmp.append(users.get_city(request))
                    write_msg(event.user_id, f"Укажите возраст")
                    temp_count['sex'] = 0
                    continue
                if request.isdigit() and 18 < int(request) < 70:
                    user_year = get_age() - int(request)
                    tmp.append(user_year)
                    write_msg_find(event.user_id, f"Все данные получены")
                    temp_count['hand'] = 0
                    continue
                else:
                    write_msg(event.user_id, f'Недопустимое значение возраста. Введите значение от 18 и выше')
                    continue
            if request == "Начать поиск" or request == "Следующий":
                tmp_list = find_candidate(token_dict[event.user_id], temp_dict['user_id'], tmp[0], tmp[1], tmp[2])
                link = 'https://vk.com/id' + str(tmp_list[0])
                write_msg(event.user_id, link)
                write_msg_main(event.user_id, tmp_list)
            if request == "Задать другие параметры для поиска":
                temp_count[event.user_id] = 0
                continue
            if request == "Выход":
                write_msg(event.user_id, f"Для старта напишите что-нибудь")
                count_tmp = 0
                continue

start()
