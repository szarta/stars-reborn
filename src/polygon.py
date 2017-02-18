"""
    polygon.py

    Very basic polygon math (probably slow an unoptimized).
    Mostly just a container for the polygon to give later to an actual
    optimized geometry polygon clipping library.

    :author: Brandon Arrendondo
    :license: MIT, see LICENSE.txt for more details.
"""


class Polygon(object):
    def __init__(self, boundaries):
        self.boundaries = list(boundaries)

        self.x_arr = []
        self.y_arr = []

        for i in xrange(len(self.boundaries)):
            (x, y) = self.boundaries[i]
            self.x_arr.append(x)
            self.y_arr.append(y)

    def area(self):
        sum1 = 0
        sum2 = 0
        for i in xrange(len(self.boundaries) - 1):
            sum1 += self.x_arr[i] * self.y_arr[i+1]

        for i in xrange(len(self.boundaries) - 1):
            sum2 += self.y_arr[i] * self.x_arr[i+1]

        area = (sum2 - sum1) / 2.0
        return area

    def bounds(self):
        """
        Returns (min_x, min_y, max_x, max_y)
        """
        min_x = min(self.x_arr)
        max_x = max(self.x_arr)
        min_y = min(self.y_arr)
        max_y = max(self.y_arr)

        return (min_x, min_y, max_x, max_y)
