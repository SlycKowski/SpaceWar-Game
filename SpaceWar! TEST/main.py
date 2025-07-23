#Stuff To Do:
#Things to change:
import pygame
import math
import random

pygame.init()
explosionIMG = []
for i in range(1,21):
    image = pygame.image.load(f'NicePng_space-ship-png_{i}.png')
    imageResize = pygame.transform.scale(image, (64,64))
    explosionIMG.append(imageResize)
screen = pygame.display.set_mode((800, 800))
clock = pygame.time.Clock()
endGame = False
BLUE = (100, 100, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUEShipX = 200
BLUEShipY = 600
BLUEShipVel_X = 0
BLUEShipVel_Y = 0
BLUEShipAngle = 90
# BLUEShipAngle = 0
BLUEShipVel = pygame.Vector2(0, 0)
BLUEShipPos = pygame.Vector2(200, 600)
REDShipX = 700
REDShipY = 100
REDShipVel_X = 0
REDShipVel_Y = 0
REDShipAccel = 0.05
REDShipAngle = 270
REDShipPos = (700,100)
REDShipVel = (0,0)
acceleration = 0.006
RedShipFuel = 3600
BlueShipFuel = 3600
#
bhPos = pygame.Vector2(400, 400)
max_velocity = 5
trailTimer = 0
RedShipTorpedoes = []
BlueShipTorpedoes = []
RedShipTorpedoCount = 30
BlueShipTorpedoCount = 30
radius = 2.5
friction = 1  # inertia effect, 0 for infinite friction, 1 for no friction
frame_count = 0
DT = 1 / 60

font = pygame.font.SysFont("Arial", 24)
pygame.display.set_caption("SpaceWars!")
img = font.render('^', True, BLUE)
img2 = font.render('^', True, GREEN)
blackHole = font.render('o', True, RED)
btrail = []
rtrail = []


class Torpedo:
    def __init__(self, position, direction, ship_velocity, angle, speed=5):
        self.pos = pygame.Vector2(position)
        self.vel = ship_velocity + direction.normalize() * speed
        self.angle = angle  # Store the angle for drawing
        # self.lifetime = 120
        self.lifetime = 99999
        self.radius = 3

    def update(self):
        self.pos += self.vel
        self.lifetime -= 1

    def crossBorder(self):
        if self.pos.x < 0:
            self.pos.x = 800
        if self.pos.x > 800:
            self.pos.x = 0
        if self.pos.y < 0:
            self.pos.y = 800
        if self.pos.y > 800:
            self.pos.y = 0

    def draw(self, screen):
        # Line representing the torpedo's direction
        direction = pygame.Vector2(1, 0).rotate(-self.angle)
        length = 12  # Length of the torpedo line
        start = self.pos - direction * (length / 2)
        end = self.pos + direction * (length / 2)
        pygame.draw.line(screen, (255, 0, 0), start, end, 3)

    def is_alive(self):
        return self.lifetime > 0


class Ship:
    def __init__(self, position, direction, velocity, surface, source_pos,acceleration=0.01):
        self.pos = position
        self.direction = direction
        self.vel = velocity
        self.accel = acceleration
        self.surf = surface
        self.sourcePos = source_pos
        self.teleporting = False
        self.teleport_timer = 0
        self.teleport_cooldown = 180  # Frames between allowed teleports
        self.last_teleport_frame = -999
        self.isDying = False
        self.isDead = False
        self.deathFrames = 120
        self.dyingAnim = 0
        self.dyingFrames = 0
    def draw_ship(self, color, alpha):
        if self.teleporting:
            return

        if self.isDying == True:
            if self.dyingAnim == 20:
                self.deathFrames -= 1
                if self.deathFrames <=0:
                    self.isDead = True


            else:
                self.surf.blit(explosionIMG[self.dyingAnim], pygame.Vector2(self.pos.x - 32, self.pos.y - 32))
                self.dyingFrames += 1
                if self.dyingFrames%45 == 0:
                    self.dyingAnim += 1
            return
        rad = math.radians(self.direction)
        tip = (self.pos.x + math.cos(rad) * 8, self.pos.y - math.sin(rad) * 8)
        left = (self.pos.x + math.cos(rad + math.radians(140)) * 6, self.pos.y - math.sin(rad + math.radians(140)) * 6)
        right = (self.pos.x + math.cos(rad - math.radians(140)) * 6, self.pos.y - math.sin(rad - math.radians(140)) * 6)

        ship_surface = pygame.Surface((800, 800), pygame.SRCALPHA)
        pygame.draw.polygon(ship_surface, (*color, alpha), [tip, left, right])
        self.surf.blit(ship_surface, (0, 0))

    def WrapAround(self, color):
        WRAP_MARGIN = 20  # How close to the edge triggers wrapping

        def wraparound(self):
            if self.pos.x < -WRAP_MARGIN:
                self.pos.x = 800 + WRAP_MARGIN
            elif self.pos.x > 800 + WRAP_MARGIN:
                self.pos.x = -WRAP_MARGIN

            if self.pos.y < -WRAP_MARGIN:
                self.pos.y = 800 + WRAP_MARGIN
            elif self.pos.y > 800 + WRAP_MARGIN:
                self.pos.y = -WRAP_MARGIN

    def trail(self):
        global trailTimer
        if trailTimer % 2 == 0:
            btrail.append((BLUEShipPos, BLUEShipAngle))
            if len(btrail) > 10:
                btrail.pop(0)
            rtrail.append((REDShipX, REDShipY, REDShipAngle))
            if len(rtrail) > 10:
                rtrail.pop(0)
            for i, (btp, bta) in enumerate(btrail):
                alpha = int(255 * (i + 1) / len(btrail)) // 2  # fade out
                self.draw_ship(BLUE, alpha)
                self.fire_trail((155, 0, 0, 2 * alpha))
                self.WrapAround(BLUE)
            for i, (rtx, rty, rta) in enumerate(rtrail):
                alpha = int(255 * (i + 1) / len(rtrail)) // 2  # fade out
                self.draw_ship(GREEN, alpha)
                self.fire_trail((155, 0, 0, alpha + 100))
                self.WrapAround(GREEN)
            trailTimer = 1
        else:
            trailTimer += 1
            for i, (btp, bta) in enumerate(btrail):
                alpha = int(255 * (i + 1) / len(btrail)) // 2  # fade out
                self.draw_ship(BLUE, alpha)
                self.WrapAround(BLUE)
            for i, (rtx, rty, rta) in enumerate(rtrail):
                alpha = int(255 * (i + 1) / len(rtrail)) // 2  # fade out
                self.draw_ship(GREEN, alpha)
                self.WrapAround(GREEN)

    # fire trail
    def fire_trail(self, fireColor, ship_length=20, rect_width=3 ):
        if self.teleporting:
            return
        if self.isDying:
            return
        # Convert angle to direction vector
        rad = math.radians(self.direction)
        direction = pygame.Vector2(math.cos(rad), -math.sin(rad))

        # Calculate back of the ship (center - half-length forward)
        back_pos = self.pos - direction * ((ship_length - 3) / 2)
        # Random length of the rectangle
        rect_length = random.randint(7, 20)

        # Create the surface and fill with color
        rect_surface = pygame.Surface((rect_length, rect_width), pygame.SRCALPHA)
        rect_surface.fill(fireColor)
        # Rotate to align with back direction
        rotated_surface = pygame.transform.rotate(rect_surface, self.direction)
        rotated_rect = rotated_surface.get_rect(center=(back_pos.x, back_pos.y))

        # Draw it to the screen
        screen.blit(rotated_surface, rotated_rect.topleft)

    def Controls(self):
        if self.isDying != True:
            self.vel += self.calculate_gravity()
            self.pos += self.vel
            if self.teleporting:
                self.teleport_timer -= 1
                print(self.teleport_timer)
                if self.teleport_timer <= 0:
                    self.pos = pygame.Vector2(
                        random.randint(50, 800),
                        random.randint(50, 800)
                    )
                    self.teleporting = False


    def WraparoundFix(self):
        if self.pos.x < 0:
            self.pos.x = 800
        if self.pos.x > 800:
            self.pos.x = 0
        if self.pos.y < 0:
            self.pos.y = 800
        if self.pos.y > 800:
            self.pos.y = 0

    def calculate_gravity(self, G=1000):
        # Calculate gravitational acceleration vector toward a gravity source.
        #
        # Parameters:
        #     pos (pygame.Vector2): Position of the object being affected.
        #     source_pos (pygame.Vector2): Position of the gravity source (e.g., star).
        #     G (float): Gravitational constant (affects strength).
        #
        # Returns:
        #     pygame.Vector2: Acceleration vector due to gravity.

        direction = self.sourcePos - self.pos
        distance = direction.length()

        # Avoid division by zero
        if distance == 0:
            return pygame.Vector2(0, 0)

        force_magnitude = G / (distance ** 2)
        acceleration = direction.normalize() * force_magnitude
        return acceleration

    def touchingBH(self):
        #   pos (pygame.Vector2): Position of the object being affected.
        #   source_pos (pygame.Vector2): Position of the gravity source (e.g., star).
        #   vel (pygame.Vector2): Velocity of the ship
        randDirectionX = random.randint(0, 1)
        randDirectionY = random.randint(0, 1)

        #   randDirectionX: Makes a random x variable for ship to teleport to.
        #   randDirectionY: Makes a random y variable for ship to teleport to.
        direction = self.sourcePos - self.pos
        distance = direction.length()
        if distance <= 9:
            self.pos = pygame.Vector2(randDirectionX * 800, randDirectionY * 800)
            self.vel = pygame.Vector2(0, 0)

        return self.pos, self.vel

    def start_teleport(self, frame_count):
        # Prevent spamming
        if frame_count - self.last_teleport_frame < self.teleport_cooldown:
            return

        self.teleporting = True
        self.teleport_timer = 120  # Duration the ship is invisible (in frames)
        self.last_teleport_frame = frame_count

    def isDead(self):
        return self.isDead


BlueShip=Ship(pygame.Vector2(200,600),90,pygame.Vector2(0,0),screen,bhPos)
RedShip=Ship(pygame.Vector2(600,200), 270, pygame.Vector2(0,0), screen, bhPos)










while not endGame:
    frame_count += 1  # Add this at the top of the main loop
    print(frame_count)
    if BlueShip.isDead == True and RedShip.isDying != True:
        print("Red Ship Won!")
        endGame = True
    if RedShip.isDead == True and BlueShip.isDying != True:
        print("Blue Ship Won!")
        endGame = True
    if RedShip.isDead == True and BlueShip.isDead == True:
        print("No Ship Won!")
        endGame = True
    dt = clock.tick(60) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # endGame = True
            break
    screen.fill(BLACK)
    BlueShip.Controls()
    RedShip.Controls()
    #Controls
    keys = pygame.key.get_pressed()

    if keys[pygame.K_a]:
        BlueShip.direction += 3
    if keys[pygame.K_d]:
        BlueShip.direction -= 3
    if keys[pygame.K_w]:
        if BlueShipTorpedoCount > 0:

            if len(BlueShipTorpedoes) == 0 or BlueShipTorpedoes[-1].lifetime < 188:  # Fire rate limit
                BlueShipTorpedoCount -= 1
                direction = pygame.Vector2(1, 0).rotate(-BlueShip.direction)  # Use negative angle
                spawn_offset = direction.normalize() * (radius + 3)
                torpedo_pos = BlueShip.pos + spawn_offset
                BlueShipTorpedoes.append(Torpedo(torpedo_pos, direction, BlueShip.vel, BlueShip.direction))
    if keys[pygame.K_s]:
        if BlueShipFuel >= 1:
            BlueShipFuel -= 1
            rad = math.radians(BlueShip.direction)
            thrust = pygame.Vector2(math.cos(rad), -math.sin(rad)) * acceleration
            BlueShip.vel += thrust
            BlueShip.fire_trail((255, 0, 0, 255))
    if keys[pygame.K_q]:
        BlueShip.start_teleport(frame_count)
    if keys[pygame.K_j]:
        RedShip.direction += 3
    if keys[pygame.K_l]:
        RedShip.direction -= 3
    if keys[pygame.K_i]:
        if RedShipTorpedoCount > 0:
            if len(RedShipTorpedoes) == 0 or RedShipTorpedoes[-1].lifetime < 99999:  # Fire rate limit
                RedShipTorpedoCount -= 1
                direction = pygame.Vector2(1, 0).rotate(-RedShip.direction)  # Use negative angle
                spawn_offset = direction.normalize() * (radius + 3)
                torpedo_pos = RedShip.pos + spawn_offset
                RedShipTorpedoes.append(Torpedo(torpedo_pos, direction, RedShip.vel, RedShip.direction))
    if keys[pygame.K_k]:
        if RedShipFuel >= 1:
            RedShipFuel -= 1
            rad = math.radians(RedShip.direction)
            thrust = pygame.Vector2(math.cos(rad), -math.sin(rad)) * acceleration
            RedShip.vel += thrust
            RedShip.fire_trail((255, 0, 0, 255))
    if keys[pygame.K_u]:
        RedShip.start_teleport(frame_count)

    REDShipPos, REDShipVel = RedShip.touchingBH()
    BLUEShipPos, BLUEShipVel = BlueShip.touchingBH()

    BlueShip.trail()
    RedShip.trail()
    fire_length = random.randint(4, 16)

    BlueShip.draw_ship(BLUE, 255)
    BlueShip.WrapAround(BLUE)
    BlueShip.WraparoundFix()
    # BlueShip.draw_ship(GREEN, 255)
    # BlueShip.WrapAround(GREEN)

    RedShip.draw_ship(GREEN, 255)
    RedShip.WrapAround(GREEN)
    RedShip.WraparoundFix()
    # RedShip.draw_ship(GREEN, 255)
    # RedShip.WrapAround(GREEN)
    screen.blit(blackHole, bhPos)
    for torpedo in BlueShipTorpedoes:
        torpedo.update()
    for torpedo in RedShipTorpedoes:
        torpedo.update()
    BlueShipTorpedoes = [t for t in BlueShipTorpedoes if t.is_alive()]
    RedShipTorpedoes = [t for t in RedShipTorpedoes if t.is_alive()]
    for torpedo in RedShipTorpedoes:
        torpedo.draw(screen)
        torpedo.crossBorder()
        BlueShipDirection = torpedo.pos - BlueShip.pos
        BlueShipDistance = BlueShipDirection.length()
        if BlueShipDistance <= 9:
            BlueShip.isDying = True
#             # endGame = True

            pass
        RedShipDirection = torpedo.pos - RedShip.pos
        RedShipDistance = RedShipDirection.length()
        if RedShipDistance <= 9:
            RedShip.isDying = True
#             # endGame = True
            pass
    for torpedo in BlueShipTorpedoes:
        torpedo.draw(screen)
        torpedo.crossBorder()
        RedShipDirection = torpedo.pos - RedShip.pos
        RedShipDistance = RedShipDirection.length()
        if RedShipDistance <= 9:
            RedShip.isDying = True
#             # endGame = True
            pass
        BlueShipDirection = torpedo.pos - BlueShip.pos
        BlueShipDistance = BlueShipDirection.length()
        if BlueShipDistance <= 9:
            BlueShip.isDying = True
#             endGame = True
            pass
    ShipDirection = BlueShip.pos - RedShip.pos
    ShipDistance = ShipDirection.length()
    if ShipDistance <= 9:
        RedShip.isDying = True
        BlueShip.isDying = True
#         endGame = True
        pass
    pygame.display.update()

pygame.quit()
