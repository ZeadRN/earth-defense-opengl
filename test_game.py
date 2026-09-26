import unittest
from game_state import Game, EARTH, EARTH_RADIUS, PLAYER_RADIUS, distance

class GameTests(unittest.TestCase):
    def test_restart_preserves_session_records_and_clears_round(self):
        g = Game(1)
        g.score = g.high_score = 5
        g.finish('hit', True)
        g.finish('hit', True)
        g.explosions.append([1, 2, 3, 4, 0.4])
        g.reset()
        self.assertEqual((g.high_score, g.destroyed_ships), (5, 1))
        self.assertFalse(g.game_over or g.player_hit)
        self.assertEqual((g.score, g.earth_hits, len(g.explosions)), (0, 0, 0))
        self.assertGreater(distance(g.player_pos, EARTH), EARTH_RADIUS + PLAYER_RADIUS)

    def test_shot_heading_and_cooldown(self):
        g = Game()
        g.gun_angle = 90
        g.shoot()
        g.shoot()
        self.assertEqual(len(g.bullets), 1)
        self.assertAlmostEqual(g.bullets[0][0], g.player_pos[0])
        self.assertAlmostEqual(g.bullets[0][1], g.player_pos[1] + 65)

    def test_asteroid_speed_all_axes(self):
        g = Game()
        for pos in ([700, 0, 100, 30], [0, 700, 100, 30]):
            g.enemies = [pos.copy()]
            g.update(1/120)
            self.assertAlmostEqual(distance(pos, g.enemies[0]), 36/120)

    def test_hit_at_boundary_does_not_remove_next_bullet(self):
        g = Game()
        g.enemies = [[1220, 0, 100, 30]]
        g.bullets = [[1199, 0, 100, 0], [400, 100, 100, 0]]
        g.update(1/120)
        self.assertEqual((g.score, g.missed_bullets, len(g.bullets)), (1, 0, 1))
        self.assertEqual(g.bullets[0][1], 100)

    def test_swept_collision(self):
        g = Game()
        g.enemies = [[500, 0, 100, 30]]
        g.bullets = [[400, 0, 100, 0]]
        g.update(0.5)
        self.assertEqual(g.score, 1)

    def test_ship_loss_counted_once_and_flag_persists(self):
        g = Game()
        g.shields = 1
        g.enemies = [[*g.player_pos, 30], [*g.player_pos, 30]]
        g.update(1/120)
        g.update(1/120)
        self.assertTrue(g.game_over and g.player_hit)
        self.assertEqual(g.destroyed_ships, 1)

    def test_earth_loss_is_not_ship_collision(self):
        g = Game()
        g.earth_hits = 4
        g.enemies = [[0, 0, 50, 30], [0, 0, 50, 30]]
        g.update(1/120)
        self.assertEqual((g.earth_hits, g.destroyed_ships), (5, 0))
        self.assertTrue(g.game_over)

    def test_explosions_expire_without_enemies(self):
        g = Game()
        g.explosions = [[0, 0, 0, 50, 0.01]]
        g.update(0.02)
        self.assertEqual(g.explosions, [])

    def test_pause_freezes_everything(self):
        g = Game()
        g.paused = True
        before = g.player_pos.copy()
        g.update(10, {b'w', b' '})
        self.assertEqual(g.player_pos, before)
        self.assertEqual(g.enemies + g.bullets, [])

    def test_movement_time_and_earth_barrier(self):
        a, b = Game(1), Game(1)
        for _ in range(60): a.update(1/60, {b'w'})
        for _ in range(120): b.update(1/120, {b'w'})
        for x, y in zip(a.player_pos, b.player_pos): self.assertAlmostEqual(x, y)
        for _ in range(500): a.update(1/120, {b's'})
        self.assertGreaterEqual(distance(a.player_pos, EARTH), EARTH_RADIUS + PLAYER_RADIUS)

    def test_nearest_asteroid_is_hit_first(self):
        g = Game()
        g.enemies = [[650, 0, 100, 30], [470, 0, 100, 30]]
        g.bullets = [[400, 0, 100, 0]]
        g.update(0.5)
        self.assertEqual(g.score, 1)
        self.assertGreater(g.enemies[0][0], 600)

    def test_assisted_shot_hits_low_asteroid_from_above(self):
        g = Game(1)
        g.player_pos[2] = 180
        g.enemies = [[650, 0, 55, 30]]
        g.spawn_remaining = 100
        self.assertIsNotNone(g.aim_solution())
        g.shoot()
        self.assertLess(g.bullets[0][6], 0)
        for _ in range(120):
            g.update(1/120)
        self.assertEqual(g.score, 1)

    def test_assisted_shot_hits_high_asteroid(self):
        g = Game(1)
        g.enemies = [[650, 0, 300, 30]]
        g.spawn_remaining = 100
        g.shoot()
        self.assertGreater(g.bullets[0][6], 0)
        for _ in range(120):
            g.update(1/120)
        self.assertEqual(g.score, 1)

    def test_assist_does_not_target_through_earth_or_behind_ship(self):
        g = Game()
        g.enemies = [[-600, 0, 60, 30]]
        self.assertIsNone(g.aim_solution())
        g.gun_angle = 180
        self.assertIsNone(g.aim_solution())

    def test_manual_pitch_and_assist_toggle(self):
        g = Game()
        g.enemies = [[600, 0, 60, 30]]
        g.aim_assist = False
        g.gun_pitch = 30
        self.assertIsNone(g.aim_solution())
        g.shoot()
        self.assertAlmostEqual(g.bullets[0][6], 0.5)
        initial_z = g.bullets[0][2]
        g.update(1/120)
        self.assertGreater(g.bullets[0][2], initial_z)

    def test_shields_and_invulnerability(self):
        g = Game()
        for _ in range(2):
            g.enemies = [[*g.player_pos, 30]]
            g.update(1/120)
        self.assertEqual(g.shields, 2)
        self.assertFalse(g.game_over)
        g.invulnerable = 0
        g.enemies = [[*g.player_pos, 30]]
        g.update(1/120)
        self.assertEqual(g.shields, 1)

    def test_restart_restores_shields_and_aim(self):
        g = Game()
        g.shields = 1
        g.gun_pitch = -50
        g.aim_assist = False
        g.invulnerable = 1
        g.reset()
        self.assertEqual((g.shields, g.gun_pitch, g.invulnerable), (3, 0, 0))
        self.assertTrue(g.aim_assist)

    def test_difficulty_is_bounded(self):
        g = Game()
        g.score = 5
        self.assertEqual((g.level, g.asteroid_speed), (2, 40))
        g.score = 1000
        self.assertEqual(g.asteroid_speed, 64)

    def test_spawned_asteroids_stay_in_reachable_altitude_band(self):
        g = Game(3)
        for _ in range(100):
            g.spawn()
        self.assertTrue(all(60 <= e[2] <= 160 for e in g.enemies))
        # Each path approaches z=50 and cannot fall below the ship's z=35 floor.
        for e in g.enemies:
            z = e[2]
            velocity = g.enemy_velocity(e)
            self.assertLessEqual(velocity[2], 0)
            self.assertGreater(z, 35)

if __name__ == '__main__':
    unittest.main()
