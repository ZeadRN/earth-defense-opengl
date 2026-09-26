"""Game rules, independent of OpenGL. Distances are world units; time is seconds."""
import math
import random

EARTH = (0.0, 0.0, 50.0)
EARTH_RADIUS = 200
PLAYER_RADIUS = 35
START_POSITION = (320.0, 0.0, 100.0)
WORLD_LIMIT = 1000
MIN_ALTITUDE = 35
MAX_ALTITUDE = 500
BULLET_SPEED = 480


def direction(yaw, pitch=0):
    yaw, pitch = math.radians(yaw), math.radians(pitch)
    return (math.cos(pitch) * math.cos(yaw), math.cos(pitch) * math.sin(yaw), math.sin(pitch))


def distance(a, b):
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


def segment_hit(start, end, center, radius):
    """Return the first intersection fraction, or None (prevents tunnelling)."""
    delta = [end[i] - start[i] for i in range(3)]
    offset = [start[i] - center[i] for i in range(3)]
    c = sum(v * v for v in offset) - radius * radius
    if c <= 0:
        return 0.0
    a = sum(v * v for v in delta)
    b = 2 * sum(offset[i] * delta[i] for i in range(3))
    disc = b * b - 4 * a * c
    if a == 0 or disc < 0:
        return None
    t = (-b - math.sqrt(disc)) / (2 * a)
    return t if 0 <= t <= 1 else None


class Game:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.high_score = 0
        self.destroyed_ships = 0
        self.max_earth_hits = 5
        self.reset()

    def reset(self):
        self.player_pos = list(START_POSITION)
        self.gun_angle = 0.0
        self.gun_pitch = 0.0
        self.aim_assist = True
        self.shields = 3
        self.invulnerable = 0.0
        self.player_hit = False
        self.score = self.missed_bullets = self.earth_hits = 0
        self.total_asteroids_created = self.total_asteroids_destroyed = 0
        self.game_over = self.paused = False
        self.reason = ""
        self.enemies, self.bullets, self.explosions = [], [], []
        self.moon_angle = self.earth_angle = 0.0
        self.spawn_remaining = 2.0
        self.shot_remaining = 0.0

    @property
    def level(self):
        return 1 + self.score // 5

    @property
    def asteroid_speed(self):
        return min(64, 36 + (self.level - 1) * 4)

    def enemy_velocity(self, enemy):
        length = distance(enemy, EARTH)
        return tuple((EARTH[i] - enemy[i]) / length * self.asteroid_speed for i in range(3)) if length else (0, 0, 0)

    def aim_solution(self):
        """Lead a target in a forward cone, without aiming through Earth.

        Assistance chooses a fixed shot direction; bullets never home.
        Returns (enemy, unit direction), or None for manual aim.
        """
        if not self.aim_assist:
            return None
        candidates = []
        for enemy in self.enemies:
            relative = [enemy[i] - self.player_pos[i] for i in range(3)]
            yaw = math.degrees(math.atan2(relative[1], relative[0]))
            angle = abs((yaw - self.gun_angle + 180) % 360 - 180)
            if angle > 22 or distance(enemy, self.player_pos) > 1000:
                continue
            velocity = self.enemy_velocity(enemy)
            # Include the 65-unit muzzle offset in the interception equation.
            a = sum(v*v for v in velocity) - BULLET_SPEED**2
            b = 2 * (sum(relative[i]*velocity[i] for i in range(3)) - 65*BULLET_SPEED)
            c = sum(v*v for v in relative) - 65**2
            disc = b*b - 4*a*c
            if disc < 0:
                continue
            roots = [t for t in ((-b-math.sqrt(disc))/(2*a), (-b+math.sqrt(disc))/(2*a)) if t >= 0]
            t = min(roots) if roots else 0
            target = [enemy[i] + velocity[i]*t for i in range(3)]
            length = distance(target, self.player_pos)
            if not length:
                continue
            vector = tuple((target[i]-self.player_pos[i])/length for i in range(3))
            if abs(math.degrees(math.asin(vector[2]))) > 70:
                continue
            if segment_hit(self.player_pos, target, EARTH, EARTH_RADIUS + 5) is not None:
                continue
            candidates.append((angle, length, enemy, vector))
        if not candidates:
            return None
        chosen = min(candidates, key=lambda item: item[:2])
        return chosen[2], chosen[3]

    def shot_direction(self):
        solution = self.aim_solution()
        return solution[1] if solution else direction(self.gun_angle, self.gun_pitch)

    def finish(self, reason, ship_hit=False):
        if self.game_over:
            return
        self.game_over = True
        self.reason = reason
        self.player_hit = ship_hit
        self.destroyed_ships += int(ship_hit)
        self.high_score = max(self.high_score, self.score)

    def shoot(self):
        if self.game_over or self.paused or self.shot_remaining > 1e-9:
            return
        vector = self.shot_direction()
        muzzle = [self.player_pos[i] + 65 * vector[i] for i in range(3)]
        if segment_hit(self.player_pos, muzzle, EARTH, EARTH_RADIUS + 5) is None:
            self.bullets.append([*muzzle, self.gun_angle, *vector])
        else:
            self.missed_bullets += 1
        self.shot_remaining = 0.18

    def spawn(self):
        angle = self.rng.uniform(0, 2 * math.pi)
        self.enemies.append([900 * math.cos(angle), 900 * math.sin(angle),
                             self.rng.uniform(60, 160), self.rng.uniform(30, 45)])
        self.total_asteroids_created += 1

    def update(self, dt, keys=frozenset()):
        """Caller supplies fixed small time steps; paused/end states freeze."""
        if dt <= 0 or self.game_over or self.paused:
            return
        self.shot_remaining = max(0, self.shot_remaining - dt)
        self.invulnerable = max(0, self.invulnerable - dt)
        self.moon_angle = (self.moon_angle + 12 * dt) % 360
        self.earth_angle = (self.earth_angle + 3 * dt) % 360
        self.gun_angle = (self.gun_angle + 110 * dt * ((b'a' in keys) - (b'd' in keys))) % 360
        self.gun_pitch = max(-70, min(70, self.gun_pitch + 65 * dt * ((b'i' in keys) - (b'k' in keys))))
        angle = math.radians(self.gun_angle)
        travel = 180 * dt * ((b'w' in keys) - (b's' in keys))
        candidate = [self.player_pos[0] + travel * math.cos(angle),
                     self.player_pos[1] + travel * math.sin(angle),
                     self.player_pos[2] + 140 * dt * ((b'q' in keys) - (b'e' in keys))]
        candidate[0] = max(-WORLD_LIMIT, min(WORLD_LIMIT, candidate[0]))
        candidate[1] = max(-WORLD_LIMIT, min(WORLD_LIMIT, candidate[1]))
        candidate[2] = max(MIN_ALTITUDE, min(MAX_ALTITUDE, candidate[2]))
        if segment_hit(self.player_pos, candidate, EARTH, EARTH_RADIUS + PLAYER_RADIUS) is None:
            self.player_pos = candidate
        if b' ' in keys:
            self.shoot()
        self.spawn_remaining -= dt
        while self.spawn_remaining <= 0:
            self.spawn()
            self.spawn_remaining += max(2.5, 5.0 - (self.level - 1)*0.35)
        self.explosions = [[*e[:4], e[4] - dt] for e in self.explosions if e[4] > dt]

        # Normalize using all three axes for constant asteroid speed.
        for e in self.enemies:
            length = distance(e, EARTH)
            if length:
                step = min(self.asteroid_speed * dt, length)
                for axis in range(3):
                    e[axis] += (EARTH[axis] - e[axis]) / length * step

        # Each projectile is kept or removed once; choose the closest hit.
        remaining = []
        for bullet in self.bullets:
            start = bullet[:3]
            vector = bullet[4:7] if len(bullet) >= 7 else direction(bullet[3])
            end = [start[i] + BULLET_SPEED * dt * vector[i] for i in range(3)]
            hits = []
            for index, enemy in enumerate(self.enemies):
                t = segment_hit(start, end, enemy, enemy[3] + 5)
                if t is not None:
                    hits.append((t, index))
            earth_t = segment_hit(start, end, EARTH, EARTH_RADIUS + 5)
            nearest = min(hits) if hits else None
            if nearest is not None and (earth_t is None or nearest[0] < earth_t):
                enemy = self.enemies.pop(nearest[1])
                self.explosions.append([*enemy[:3], enemy[3] * 1.5, 0.45])
                self.score += 1
                self.total_asteroids_destroyed += 1
                self.high_score = max(self.high_score, self.score)
            elif earth_t is not None or max(abs(end[0]), abs(end[1])) > 1200 or not -200 <= end[2] <= 900:
                self.missed_bullets += 1
            else:
                remaining.append([*end, bullet[3], *vector])
        self.bullets = remaining

        for enemy in self.enemies[:]:
            if distance(enemy, EARTH) <= EARTH_RADIUS + enemy[3]:
                self.enemies.remove(enemy)
                self.explosions.append([*enemy[:3], enemy[3] * 1.5, 0.45])
                self.earth_hits += 1
                if self.earth_hits >= self.max_earth_hits:
                    self.finish("Earth took too many hits")
                    break
            elif distance(enemy, self.player_pos) <= enemy[3] + PLAYER_RADIUS:
                self.enemies.remove(enemy)
                self.explosions.append([*enemy[:3], enemy[3]*1.5, 0.45])
                if self.invulnerable <= 0:
                    self.shields -= 1
                    self.invulnerable = 1.8
                    if self.shields <= 0:
                        self.finish("Spaceship shields depleted", ship_hit=True)
                        break
