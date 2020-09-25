# -*- coding: utf-8 -*-


class Hero:
    def __init__(self, current_location_name, experience, time_to_beginner):
        self.first_location = current_location_name
        self.time_to_beginner = time_to_beginner
        self.current_time = time_to_beginner

        self.current_location_name = current_location_name
        self.experience = experience

    def time_to_wash(self):
        """
        Присвоение начальных атрибутов
        """
        print("Вы воскресли в начальной локации и полны решимости выбраться из подземелия!\n")
        self.current_location_name = self.first_location
        self.experience = 0
        self.current_time = self.time_to_beginner
