class Diamond:
    # an asteroid on the map.
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius
        self.points = []
        self.build_diamond()

    def build_diamond(self):
        scaling = range(-int(self.radius), self.radius)
        for ct, x in enumerate(range(self.center[0] - self.radius, self.center[0] + self.radius)):
            for y in range(self.center[1] - self.radius + abs(scaling[ct]),
                           self.center[1] + self.radius - abs(scaling[ct])):
                self.points.append([x, y])

    def intersect(self, points):
        # returns true if this asteroid intersects another
        intsect = [pt for pt in points if pt in self.points]
        if intsect:
            return True
        else:
            return False