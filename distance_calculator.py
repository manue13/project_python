# =========================================================
# DISTANCE CALCULATOR
# =========================================================

import math

def euclidean_distance(point1, point2):

    x1, y1 = point1
    x2, y2 = point2

    distance = math.sqrt(
        (x2 - x1)**2 +
        (y2 - y1)**2
    )

    return round(distance, 2)
