import math as m



def speeddeg_xy(speed,direction):
    return speed * m.cos(m.radians(direction)), speed * m.sin(m.radians(direction))

def angledeg(xy1,xy2):
    x1,y1 = xy1
    x2,y2 = xy2
    return m.degrees(m.atan2(y2-y1,x2-x1))

def distance(xy1,xy2):
    x1,y1 = xy1
    x2,y2 = xy2
    return m.sqrt((x2-x1)**2+(y2-y1)**2)


def get_nearest_sprite(source_sprite, group):
    nearest = None
    min_dist = float('inf')
    sx, sy = source_sprite.rect.center
    for sprite in group:
        dx = sprite.rect.centerx
        dy = sprite.rect.centery
        dist = distance((sx,sy), (dx,dy))
        if dist < min_dist:
            min_dist = dist
            nearest = sprite
    return nearest