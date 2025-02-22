class Party:
    def __init__(self, short_name, name, color, left_to_right):
        self.short_name = short_name
        self.name = name
        self.color = color
        self.left_to_right = left_to_right
        self.seats = 0
        self.state_seats = {}
        self.district_seats = {}
from collections import namedtuple

Party = namedtuple('Party', ['name', 'color', 'size', 'left_to_right', 'votes'])

