# -*- coding: utf-8 -*-

import json
import copy


class Location:
    def __init__(self, file_game):
        """
        @param file_game: .json файл с данными данжа
        """
        self.file_game = file_game
        self.current_location_name = None
        self.current_location = None
        self.first_location_name = None
        self.first_location = None

        self.monsters_in_current_location = []
        self.next_locations = {}

    def open_game_json(self):
        """
        Чтение данных из файла данжа
        """
        with open(self.file_game, "r") as read_file:
            loaded_json_file = json.load(read_file)
        self.first_location_name = [i for i in loaded_json_file][0]
        self.first_location = loaded_json_file

        self.current_location_name = self.first_location_name
        self.current_location = copy.deepcopy(self.first_location[self.first_location_name])
        self.current_location_data()

    def output_current_location_data(self):
        """
        Вывод данных текущей локации
        """
        for unit in self.current_location:
            if type(unit) == str:
                print(f"- {unit}")
            if type(unit) == dict:
                for location in unit:
                    print(f"- Вход в локацию: {location}")

    def current_location_data(self):
        """
        Подсчёт данных текущей локации
        """
        key_location = 1
        for unit in self.current_location:
            if type(unit) == str:
                self.monsters_in_current_location.append(unit)
            if type(unit) == dict:
                for key, value in unit.items():
                    if str(key_location) in self.next_locations:
                        key_location += 1
                        self.next_locations[str(key_location)] = {key: value}
                    else:
                        self.next_locations[str(key_location)] = {key: value}

    def return_first_location(self):
        """
        Присвоение начальных атрибутов
        """
        self.current_location_name = self.first_location_name
        self.current_location = copy.deepcopy(self.first_location[self.first_location_name])
        self.change_of_location()

    def change_of_location(self):
        """
        Смена локации
        """
        self.next_locations = {}
        self.monsters_in_current_location.clear()
        self.current_location_data()
