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
def current_speed(sprite):
    return m.sqrt(sprite.dx**2+sprite.dy**2)

def add_speed(sprite):
    direction = sprite.direction
    acceleration = sprite.acceleration
    dx,dy = speeddeg_xy(acceleration-current_speed(sprite)/10,direction)
    sprite.dx += dx
    sprite.dy += dy

def friction(sprite):
    sprite.dx -= sprite.dx*sprite.friction
    sprite.dy -= sprite.dy*sprite.friction

def get_rotation_direction(current, target):
    diff = (target - current + 360) % 360
    if diff > 180:
        return -1  # rotate left
    else:
        return 1   # rotate right

def rotate_toward(current, target, rotation_speed):
    if abs(current - target) < rotation_speed:
        return target

    direction = get_rotation_direction(current, target)
    new_angle = current + direction * rotation_speed

    # Clamp to avoid overshooting
    if direction == 1 and (target - new_angle + 360) % 360 < rotation_speed:
        return target
    elif direction == -1 and (new_angle - target + 360) % 360 < rotation_speed:
        return target

    return new_angle % 360

