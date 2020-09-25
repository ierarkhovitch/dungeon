# -*- coding: utf-8 -*-

import hero
import location
import re
import datetime
import time
import sys
import pandas
from decimal import Decimal

REMAINING_TIME = '123456.0987654321'
FIELD_NAMES = ['current_location', 'current_experience', 'current_date']


# Подземелье было выкопано ящеро-подобными монстрами рядом с аномальной рекой, постоянно выходящей из берегов.
# Из-за этого подземелье регулярно затапливается, монстры выживают, но не герои, рискнувшие спуститься к ним в поисках
# приключений.
# Почуяв безнаказанность, ящеры начали совершать набеги на ближайшие деревни. На защиту всех деревень не хватило
# солдат и вас, как известного в этих краях героя, наняли для их спасения.
#
# Карта подземелья представляет собой json-файл под названием rpg.json. Каждая локация в лабиринте описывается объектом,
# в котором находится единственный ключ с названием, соответствующем формату "Location_<N>_tm<T>",
# где N - это номер локации (целое число), а T (вещественное число) - это время,
# которое необходимо для перехода в эту локацию. Например, если игрок заходит в локацию "Location_8_tm30000",
# то он тратит на это 30000 секунд.
# По данному ключу находится список, который содержит в себе строки с описанием монстров а также другие локации.
# Описание монстра представляет собой строку в формате "Mob_exp<K>_tm<M>", где K (целое число) - это количество опыта,
# которое получает игрок, уничтожив данного монстра, а M (вещественное число) - это время,
# которое потратит игрок для уничтожения данного монстра.
# Например, уничтожив монстра "Boss_exp10_tm20", игрок потратит 20 секунд и получит 10 единиц опыта.
# Гарантируется, что в начале пути будет две локации и один монстр
# (то есть в коренном json-объекте содержится список, содержащий два json-объекта, одного монстра и ничего больше).
#
# На прохождение игры игроку дается 123456.0987654321 секунд.
# Цель игры: за отведенное время найти выход ("Hatch")
#
# По мере прохождения вглубь подземелья, оно начинает затапливаться, поэтому
# в каждую локацию можно попасть только один раз,
# и выйти из нее нельзя (то есть двигаться можно только вперед).
#
# Чтобы открыть люк ("Hatch") и выбраться через него на поверхность, нужно иметь не менее 280 очков опыта.
# Если до открытия люка время заканчивается - герой задыхается и умирает, воскрешаясь перед входом в подземелье,
# готовый к следующей попытке (игра начинается заново).
#
# Гарантируется, что искомый путь только один, и будьте аккуратны в рассчетах!
# При неправильном использовании библиотеки decimal человек, играющий с вашим скриптом рискует никогда не найти путь.
#
# Также, при каждом ходе игрока ваш скрипт должен запоминать следущую информацию:
# - текущую локацию
# - текущее количество опыта
# - текущие дату и время (для этого используйте библиотеку datetime)
# После успешного или неуспешного завершения игры вам необходимо записать
# всю собранную информацию в csv файл dungeon.csv.
# Названия столбцов для csv файла: current_location, current_experience, current_date
#
#
# Пример взаимодействия с игроком:
#
# Вы находитесь в Location_0_tm0
# У вас 0 опыта и осталось 123456.0987654321 секунд до наводнения
# Прошло времени: 00:00
#
# Внутри вы видите:
# — Вход в локацию: Location_1_tm1040
# — Вход в локацию: Location_2_tm123456
# Выберите действие:
# 1.Атаковать монстра
# 2.Перейти в другую локацию
# 3.Сдаться и выйти из игры
#
# Вы выбрали переход в локацию Location_2_tm1234567890
#
# Вы находитесь в Location_2_tm1234567890
# У вас 0 опыта и осталось 0.0987654321 секунд до наводнения
# Прошло времени: 20:00
#
# Внутри вы видите:
# — Монстра Mob_exp10_tm10
# — Вход в локацию: Location_3_tm55500
# — Вход в локацию: Location_4_tm66600
# Выберите действие:
# 1.Атаковать монстра
# 2.Перейти в другую локацию
# 3.Сдаться и выйти из игры
#
# Вы выбрали сражаться с монстром
#
# Вы находитесь в Location_2_tm0
# У вас 10 опыта и осталось -9.9012345679 секунд до наводнения
#
# Вы не успели открыть люк!!! НАВОДНЕНИЕ!!! Алярм!
#
# У вас темнеет в глазах... прощай, принцесса...
# Но что это?! Вы воскресли у входа в пещеру... Не зря матушка дала вам оберег :)
# Ну, на этот-то раз у вас все получится! Трепещите, монстры!
# Вы осторожно входите в пещеру... (текст умирания/воскрешения можно придумать свой ;)
#
# Вы находитесь в Location_0_tm0
# У вас 0 опыта и осталось 123456.0987654321 секунд до наводнения
# Прошло уже 0:00:00
# Внутри вы видите:
#  ...
#  ...
#
# и так далее...


# если изначально не писать число в виде строки - теряется точность!


def csv_records(file_path='dungeon.csv', player_object=None):
    """
    Выполняет запись параметров игрока в .csv файл
    @param file_path: путь записи файла .csv
    @param player_object: сам герой
    """
    date_now = str(datetime.datetime.now().strftime("Дата:%d.%m.%Y Время:%H.%M.%S"))
    data = [
        {FIELD_NAMES[0]: player_object.current_location_name,
         FIELD_NAMES[1]: player_object.experience,
         FIELD_NAMES[2]: date_now}]
    with open(file_path, 'w', encoding='cp1251', newline='') as out_csv:
        data_frame = pandas.DataFrame.from_records(data)
        data_frame.to_csv(out_csv, sep=';', header=FIELD_NAMES, index=False)


def return_to_start():
    """
    Присваивает игроку начальные параметры
    """
    csv_records(player_object=player)
    player.time_to_wash()
    dungeon.return_first_location()


def convert_to_hours(player_time):
    """
    Конвертирует дни в часы
    @param player_time: текущее время до затопления
    @return: Общее количество часов
    """
    if time.gmtime(float(player_time)).tm_yday > 1:
        hours = time.gmtime(float(player_time)).tm_hour + ((time.gmtime(float(player_time)).tm_yday - 1) * 24)
    else:
        hours = time.gmtime(float(player_time)).tm_hour
    return hours


def output_menu(player, dungeon):
    """
    Вывод основного меню
    @param player: Объект героя
    @param dungeon: Объект данжа
    """
    format_hours = convert_to_hours(player.current_time)
    print(f"Вы внутри локации: {player.current_location_name}. Опыта: {player.experience}. "
          f"Осталось времени до затопления подземелия - {format_hours}"
          f"{time.strftime(':%M:%S', time.gmtime(float(player.current_time)))}.(Часы:Минуты:Секунды)\n"
          f"Внутри вы видите:")
    dungeon.output_current_location_data()
    print("Выберите действие:\n1 Атаковать монстра\n2 Перейти в другую локацию\n3 Сдаться и выйти из игры")


def attack(player, dungeon):
    """
    @param player: Объект героя
    @param dungeon: Объект данжа
    """
    while True:
        if len(dungeon.monsters_in_current_location) == 0:
            print("В этой локации нет монстров!")
            break
        elif len(dungeon.monsters_in_current_location) == 1:
            monster = dungeon.monsters_in_current_location[0]
            kill_monster(player=player, dungeon=dungeon, monster=monster)
            break
        else:
            print("Выберите монстра:")
            for number, mob in enumerate(dungeon.monsters_in_current_location):
                print(number + 1, mob)
            enter = input("")
            try:
                if int(enter) < 1:
                    raise Exception
                else:
                    monster = dungeon.monsters_in_current_location[int(enter) - 1]
                    kill_monster(player=player, dungeon=dungeon, monster=monster)
                    break
            except Exception:
                print(f"Не верный ввод номера монстра: {enter}\n")
                break


def kill_monster(player, dungeon, monster):
    """
    @param player: Объект героя
    @param dungeon: Объект данжа
    @param monster: Монстр, которого атакуем
    """
    player.current_time = Decimal(player.current_time) - Decimal(re.search(r'tm(\d+)', monster)[1])
    player.experience += int(re.search(r'exp(\d+)', monster)[1])
    print(f"Вы убили монстра {monster}!")
    dungeon.current_location.remove(monster)
    dungeon.monsters_in_current_location.remove(monster)


def change_location(player, dungeon):
    """
    @param player: Объект героя
    @param dungeon: Объект данжа
    """
    while True:
        if len(dungeon.next_locations) == 0:
            print("Нет локаций для перехода\n")
            break
        elif len(dungeon.next_locations) == 1:
            try_to_current_location = dungeon.next_locations['1']
            go(player=player, dungeon=dungeon, location=try_to_current_location)
            break
        else:
            print("Выберите локацию:")
            for num, loc in dungeon.next_locations.items():
                for key in loc:
                    print(num, key)
            enter = input("")
            try:
                next_location = dungeon.next_locations[enter]
                go(player=player, dungeon=dungeon, location=next_location)
                break
            except Exception:
                print(f"Не верный ввод номера локации для перехода: {enter}")
                break


def go(player, dungeon, location):
    """
    @param player: Объект героя
    @param dungeon: Объект данжа
    @param location: локация для перехода (dict)
    """
    next_location_name = [key for key in location][0]
    journey_time = re.search(r'tm(\d+)', next_location_name)[1]
    time_after_journey = Decimal(player.current_time) - Decimal(journey_time)

    if time_after_journey < 0:
        return_to_start()
    else:
        if next_location_name.startswith("Hatch") and player.experience > 279:
            print("Вы вышли из поземелия! Поздравляем!")
            player.current_location_name = location
            csv_records(player_object=player)
            sys.exit()
        elif next_location_name.startswith("Hatch") and player.experience < 280:
            print(f"У вас {player.experience} очков опыта! "
                  f"Для выхода из подземелия необходимо не менее 280 очков опыта!\n")
        else:
            player.current_location_name = next_location_name
            player.current_time = time_after_journey
            dungeon.current_location = location[next_location_name]
            print(f"Вы перешли в локацию {next_location_name}!")
            dungeon.change_of_location()


if __name__ == "__main__":
    dungeon = location.Location("rpg.json")
    dungeon.open_game_json()
    player = hero.Hero(dungeon.current_location_name, 0, REMAINING_TIME)
    while True:
        if float(player.current_time) < 0:
            print("\nВы не успели выйти из подземелия и утонули!")
            return_to_start()
        elif len(dungeon.monsters_in_current_location) == 0 and len(dungeon.next_locations) == 0:
            print("\nВы зашли в тупик и утонули!")
            return_to_start()
        else:
            output_menu(player=player, dungeon=dungeon)
            enter_player = input("")
            if enter_player == "1":
                attack(player=player, dungeon=dungeon)
            elif enter_player == "2":
                change_location(player=player, dungeon=dungeon)
            elif enter_player == "3":
                csv_records(player_object=player)
                print("Выход из игры")
                break
            else:
                print(f"Не верный выбор действия: {enter_player}\n")

# зачет!
