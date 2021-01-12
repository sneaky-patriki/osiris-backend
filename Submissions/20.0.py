from math import pi

class Circle:
    def __init__(self, centre, radius):
        self.centre = centre
        self.radius = radius

    def circumference(self):
        return 2 * pi * self.radius

    def area(self):
        return pi * (self.radius ** 2)

c = Circle((0, 0), 5)
print(c.radius)
print(c.centre)
print(c.circumference())
print(c.area())

