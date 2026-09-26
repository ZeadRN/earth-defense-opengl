from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math

WINDOW_WIDTH, WINDOW_HEIGHT = 1000, 800
GRID_LENGTH = 600
fovY = 120

# Camera settings
camera_pos = (0, 500, 500)  # Default third-person camera
first_person_view = False  # Toggle for switching between 1st and 3rd person views

# Player variables
gun_angle = 0
player_pos = [150, 150, 150]
player_speed = 7
player_hit = False  # Flag for player collision

# Game stats
score = 0
missed_bullets = 0
lives = 10
game_over = False
destroyed_ships = 0  # Count of player ships destroyed
high_score = 0  # Track highest score

# Global variable initialization
earth_hits = 0  # Initialize the earth_hits counter to 0
max_earth_hits = 5  # Set maximum hits before game over
total_asteroids_created = 0
total_asteroids_destroyed = 0



# Game objects
enemies = []  # Will hold asteroids and comets
bullets = []

# Celestial variables
earth_angle = 0  # Earth rotation angle
moon_angle = 0   # Moon orbit angle

# Object types for diversity
ASTEROID = 0


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(0, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_shapes():
    global moon_angle, earth_angle

    draw_stars()

    # Earth with rotation
    glPushMatrix()
    glTranslatef(0, 0, 50)
    glRotatef(earth_angle, 0, 0, 1)  # Rotate Earth on its axis
    glColor3f(0,0,1)
    glutSolidSphere(200, 30, 30)

    
    
    glColor3f(0, 0.7, 0)
    for i in range(5):  
        glPushMatrix()
        angle = i * 72
        glRotatef(angle, 0, 0, 1)
        glTranslatef(0, 30, 25)
        glScalef(1, 0.7, 0.3)
        glutSolidSphere(20, 10, 10)
        glPopMatrix()
    glPopMatrix()  # This matches the Earth push matrix

    # Moon
    moon_distance = 250
    moon_x = moon_distance * math.cos(math.radians(moon_angle))
    moon_y = moon_distance * math.sin(math.radians(moon_angle))
    glPushMatrix()
    glTranslatef(moon_x, moon_y, 50)
    glColor3f(0.6, 0.6, 1.0)  # More realistic moon color
    glutSolidSphere(40, 20, 20)
    glPopMatrix()

    # Spaceship
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])  # Use player_pos[2] for z-axis
    glRotatef(gun_angle, 0, 0, 1)
    
    # Main hull - central body
    glColor3f(0.7, 0.7, 0.9)  # Metallic blue-gray
    glPushMatrix()
    glScalef(1.0, 0.6, 0.3)
    glutSolidSphere(25, 24, 24)  # Smoother, more oval body
    glPopMatrix()
    
    # Cockpit - clear dome on top
    glPushMatrix()
    glTranslatef(0, 0, 10)
    glColor4f(0.6, 0.9, 1.0, 0.7)  # Light blue transparent
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glScalef(0.5, 0.5, 0.5)
    glutSolidSphere(15, 20, 20)
    glDisable(GL_BLEND)
    glPopMatrix()
    
    # Front section/nose
    glPushMatrix()
    glTranslatef(30, 0, 0)
    glRotatef(90, 0, 1, 0)
    glColor3f(0.8, 0.3, 0.2)  # Reddish front
    glutSolidCone(15, 30, 20, 20)
    glPopMatrix()
    
    # Main wings (larger, swept back)
    glColor3f(0.2, 0.4, 0.8)  # Deep blue wings
    
    # Left wing
    glPushMatrix()
    glTranslatef(0, 25, 0)
    glRotatef(-20, 0, 0, 1)  # Swept back angle
    glRotatef(90, 1, 0, 0)
    glScalef(1.5, 0.7, 0.1)
    glutSolidCube(30)
    glPopMatrix()
    
    # Right wing
    glPushMatrix()
    glTranslatef(0, -25, 0)
    glRotatef(20, 0, 0, 1)  # Swept back angle
    glRotatef(90, 1, 0, 0)
    glScalef(1.5, 0.7, 0.1)
    glutSolidCube(30)
    glPopMatrix()
    
    # Engine nacelles (two)
    glColor3f(0.5, 0.5, 0.5)  # Metallic gray
    
    # Left engine
    glPushMatrix()
    glTranslatef(-15, 15, 0)
    glRotatef(90, 0, 1, 0)
    glutSolidCylinder(6, 25, 16, 16)
    glPopMatrix()
    
    # Right engine
    glPushMatrix()
    glTranslatef(-15, -15, 0)
    glRotatef(90, 0, 1, 0)
    glutSolidCylinder(6, 25, 16, 16)
    glPopMatrix()
    
    # Engine exhaust (animated)
    if random.random() > 0.5:  # Flickering effect
        glColor3f(1, 0.5, 0)  # Orange-yellow
    else:
        glColor3f(1, 0.3, 0)  # Red-orange
    
    # Left exhaust
    glPushMatrix()
    glTranslatef(-20, 15, 0)
    glRotatef(-90, 0, 1, 0)
    glutSolidCone(5, 10 + random.uniform(0, 5), 12, 12)  # Varying length
    glPopMatrix()
    
    # Right exhaust
    glPushMatrix()
    glTranslatef(-20, -15, 0)
    glRotatef(-90, 0, 1, 0)
    glutSolidCone(5, 10 + random.uniform(0, 5), 12, 12)  # Varying length
    glPopMatrix()
    
    # Weapon mounts (dual cannons)
    glColor3f(0.3, 0.3, 0.3)  # Dark gray
    
    # Left cannon
    glPushMatrix()
    glTranslatef(20, 12, 0)
    glRotatef(90, 0, 1, 0)
    glutSolidCylinder(3, 30, 10, 10)
    glPopMatrix()
    
    # Right cannon
    glPushMatrix()
    glTranslatef(20, -12, 0)
    glRotatef(90, 0, 1, 0)
    glutSolidCylinder(3, 30, 10, 10)
    glPopMatrix()
    
    # Small vertical stabilizer
    glPushMatrix()
    glTranslatef(-15, 0, 10)
    glColor3f(0.2, 0.4, 0.8)  # Match wing color
    glScalef(0.7, 0.2, 1.2)
    glutSolidCube(15)
    glPopMatrix()
    
    # Center thruster
    glPushMatrix()
    glTranslatef(-20, 0, 0)
    glRotatef(-90, 0, 1, 0)
    glColor3f(0.5, 0.5, 0.5)
    glutSolidCylinder(8, 10, 16, 16)
    
    # Center exhaust
    if random.random() > 0.6:  # Different flicker rate
        glColor3f(1, 0.6, 0.2)
    else:
        glColor3f(1, 0.4, 0.1)
    glutSolidCone(7, 15 + random.uniform(0, 8), 16, 16)
    glPopMatrix()
    
    glPopMatrix()

    # Asteroids
    for e in enemies:
        x, y, z, size = e[0], e[1], e[2], e[3]
        # Draw asteroid (rocky appearance)
        glPushMatrix()
        glTranslatef(x, y, z)
        glRotatef(moon_angle * 2, 1, 0.5, 0.3)  # Rotate for visual effect
        glColor3f(0.6, 0.6, 0.6)
        glutSolidSphere(size, 20, 20)  # Asteroid sphere
        glPopMatrix()


    
    # Draw explosions
    for exp in explosions:
        draw_explosion(exp[0], exp[1], exp[2], exp[3], exp[4])

    # Bullets
    glColor3f(1, 1, 0)
    for b in bullets:
        glPushMatrix()
        glTranslatef(b[0], b[1], b[2])
        glutSolidSphere(5, 10, 10)
        
        # Bullet trail
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(1, 0.5, 0, 0.5)
        glPushMatrix()
        angle = b[3]  # Bullet direction
        dx = -math.cos(math.radians(angle))  # Reverse direction for trail
        dy = -math.sin(math.radians(angle))
        
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0, 0, 0)  # Bullet center
        trail_length = 15
        trail_width = 3
        
        # Trail perpendicular vectors
        px = -dy * trail_width
        py = dx * trail_width
        
        glVertex3f(px, py, 0)
        for i in range(5):
            factor = (i + 1) / 5.0
            glColor4f(1, 0.5, 0, 0.5 * (1 - factor))
            glVertex3f(dx*trail_length*factor, dy*trail_length*factor, 0)
        glVertex3f(-px, -py, 0)
        glEnd()
        
        glPopMatrix()
        glDisable(GL_BLEND)
        glPopMatrix()

    # Transparent grid
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0, 1, 1, 0.2)
    grid_step = 50
    for i in range(-GRID_LENGTH, GRID_LENGTH + grid_step, grid_step):
        glBegin(GL_LINES)
        glVertex3f(i, -GRID_LENGTH, 0)
        glVertex3f(i, GRID_LENGTH, 0)
        glVertex3f(-GRID_LENGTH, i, 0)
        glVertex3f(GRID_LENGTH, i, 0)
        glEnd()
    glDisable(GL_BLEND)

def draw_stars():
    random.seed(42)  # Use any fixed number as your seed
    
    glDisable(GL_LIGHTING)  # Disable lighting for stars
    
    # First batch: Small stars
    glPointSize(2.0)
    glBegin(GL_POINTS)
    glColor3f(1.0, 1.0, 1.0)  # White color for stars
    
    for i in range(1000):
        x = random.uniform(-2000, 2000)
        y = random.uniform(-2000, 2000)
        z = random.uniform(-2000, 2000)
        glVertex3f(x, y, z)
    glEnd()  # End the first batch
    
    # Second batch: Larger stars
    glPointSize(3.0)
    glBegin(GL_POINTS)
    glColor3f(1.0, 1.0, 0.9)  # Slightly yellowish white
    
    for i in range(400):
        x = random.uniform(-1800, 1800)
        y = random.uniform(-1800, 1800)
        z = random.uniform(-1800, 1800)
        glVertex3f(x, y, z)
    glEnd()  # End the second batch
    
    random.seed()  # Reset random seed

def draw_dashboard():
    dashboard_x = WINDOW_WIDTH - 260  # Push to right side
    dashboard_y = WINDOW_HEIGHT - 10

    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0.1, 0.1, 0.3, 0.6)  # Dark blue with transparency

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Draw dashboard box on the right side
    glBegin(GL_QUADS)
    glVertex2f(dashboard_x, dashboard_y - 240)
    glVertex2f(dashboard_x + 250, dashboard_y - 240)
    glVertex2f(dashboard_x + 250, dashboard_y)
    glVertex2f(dashboard_x, dashboard_y)
    glEnd()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    
    glDisable(GL_BLEND)
    
    # Draw text inside dashboard box
    draw_text(dashboard_x + 10, dashboard_y - 30, "MISSION DASHBOARD", GLUT_BITMAP_HELVETICA_18)
    draw_text(dashboard_x + 10, dashboard_y - 60, f"Asteroids Created: {total_asteroids_created}", GLUT_BITMAP_HELVETICA_12)
    draw_text(dashboard_x + 10, dashboard_y - 80, f"Asteroids Destroyed: {total_asteroids_destroyed}", GLUT_BITMAP_HELVETICA_12)
    draw_text(dashboard_x + 10, dashboard_y - 100, f"Current Score: {score}", GLUT_BITMAP_HELVETICA_12)
    draw_text(dashboard_x + 10, dashboard_y - 120, f"High Score: {high_score}", GLUT_BITMAP_HELVETICA_12)
    #draw_text(dashboard_x + 10, dashboard_y - 140, f"Remaining Lives: {lives}", GLUT_BITMAP_HELVETICA_12)
    draw_text(dashboard_x + 10, dashboard_y - 160, f"Earth Hits: {earth_hits}/{max_earth_hits}", GLUT_BITMAP_HELVETICA_12)
    draw_text(dashboard_x + 10, dashboard_y - 180, f"Missed Bullets: {missed_bullets}", GLUT_BITMAP_HELVETICA_12)
    draw_text(dashboard_x + 10, dashboard_y - 200, f"Total Ships Destroyed: {destroyed_ships}", GLUT_BITMAP_HELVETICA_12)
    
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)

def draw_explosion(x, y, z, size, lifetime):
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(1.0, 0.5, 0.0)  # Orange explosion
    glutSolidSphere(size, 20, 20)
    glPopMatrix()

# Keep track of recent explosions
explosions = []  # Format: [x, y, z, size, remaining_lifetime]

def keyboardListener(key, x, y):
    global gun_angle, player_pos, game_over, score, missed_bullets, lives, enemies, bullets, first_person_view, destroyed_ships, high_score, earth_hits,total_asteroids_created, total_asteroids_destroyed
    
    if key == b'r' and game_over:
        # Update high score before reset
        if score > high_score:
            high_score = score
        
        # Reset dashboard statistics
        total_asteroids_created = 0
        total_asteroids_destroyed = 0
        earth_hits = 0  # Reset earth hits

        # Add to destroyed ships count if game is over (but don't double count)
        if not player_hit:  # Only increment if we haven't already counted this destruction
            destroyed_ships += 1
        
        # Reset game
        score = 0
        missed_bullets = 0
        lives = 10
        earth_hits = 0  # Move this line here
        game_over = False
        player_hit = False
        player_pos = [0, 0, 0]  # Reset position
        gun_angle = 0  # Reset angle
        enemies.clear()
        bullets.clear()
        return
        
    if game_over:
        return  # Don't process other keys if game is over
        
    # Movement speed
    speed = player_speed
    
    if key == b'w':
        player_pos[0] += speed * math.cos(math.radians(gun_angle))
        player_pos[1] += speed * math.sin(math.radians(gun_angle))
    elif key == b's':
        player_pos[0] -= speed * math.cos(math.radians(gun_angle))
        player_pos[1] -= speed * math.sin(math.radians(gun_angle))
    elif key == b'a':
        gun_angle += 5
    elif key == b'd':
        gun_angle -= 5

    elif key == b' ':  # Spacebar for shooting
        bx = player_pos[0] + 30 * math.cos(math.radians(gun_angle))
        by = player_pos[1]  # Lock bullet to player's Y position
        bz = player_pos[2]
        bullets.append([bx, by, bz, gun_angle])

    elif key == b'v':  # Toggle view between 1st and 3rd person
        first_person_view = not first_person_view
    elif key == b'q':  # Ascend
        player_pos[2] += speed
    elif key == b'e':  # Descend
        player_pos[2] -= speed
        if player_pos[2] < 0:
            player_pos[2] = 0  # Don't go below ground level

def mouseListener(button, state, x, y):
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN and not game_over:
        bx = player_pos[0] + 30 * math.cos(math.radians(gun_angle))
        by = player_pos[1] + 30 * math.sin(math.radians(gun_angle))
        bullets.append([bx, by, player_pos[2], gun_angle])  # Use player z-position

def specialKeyListener(key, x, y):
    global camera_pos
    
    if game_over:
        return  # Don't adjust camera if game is over
        
    cx, cy, cz = camera_pos
    if key == GLUT_KEY_LEFT:
        cx -= 10
    elif key == GLUT_KEY_RIGHT:
        cx += 10
    elif key == GLUT_KEY_UP:
        cz += 10
    elif key == GLUT_KEY_DOWN:
        cz -= 10
    elif key == GLUT_KEY_PAGE_UP:
        cy += 10
    elif key == GLUT_KEY_PAGE_DOWN:
        cy -= 10
    camera_pos = (cx, cy, cz)

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, WINDOW_WIDTH / WINDOW_HEIGHT, 0.1, 2000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    if first_person_view:
        # First-person view from spaceship
        look_x = player_pos[0] + 100 * math.cos(math.radians(gun_angle))
        look_y = player_pos[1] + 100 * math.sin(math.radians(gun_angle))
        look_z = player_pos[2]
        
        # Position slightly above the ship for better view
        pos_x = player_pos[0] - 5 * math.cos(math.radians(gun_angle))
        pos_y = player_pos[1] - 5 * math.sin(math.radians(gun_angle))
        pos_z = player_pos[2] + 20  # Above the spaceship
        
        gluLookAt(pos_x, pos_y, pos_z, look_x, look_y, look_z, 0, 0, 1)
    else:
        # Third-person view (adjustable)
        x, y, z = camera_pos
        gluLookAt(x, y, z, 0, 0, 0, 0, 0, 1)

def spawn_enemy_timer(value):
    global total_asteroids_created, game_over
    
    if not game_over:
        # Choose spawn side
        side = random.choice(['left', 'right', 'top', 'bottom'])
        dist = GRID_LENGTH * 1.5

        # Size of asteroid
        size = random.uniform(40, 50)

        # Determine spawn position
        if side == 'left':
            ex = -dist
            ey = random.uniform(-GRID_LENGTH, GRID_LENGTH)
        elif side == 'right':
            ex = dist
            ey = random.uniform(-GRID_LENGTH, GRID_LENGTH)
        elif side == 'top':
            ex = random.uniform(-dist, dist)
            ey = dist
        else:  # bottom
            ex = random.uniform(-dist, dist)
            ey = -dist

        ez = random.uniform(30, 150)

        enemies.append([ex, ey, ez, size])
        total_asteroids_created += 1

        # Schedule next spawn after **5 seconds (5000 ms)**
        glutTimerFunc(5000, spawn_enemy_timer, 0)
    else:
        # Keep timer running but don't spawn if game over
        glutTimerFunc(3000, spawn_enemy_timer, 0)


def idle():
    global moon_angle, earth_angle, missed_bullets, score, lives, game_over, player_hit, high_score, destroyed_ships, earth_hits,total_asteroids_destroyed

    if game_over:
        glutPostRedisplay()
        return

    # Update celestial bodies
    moon_angle += 0.2  # Moon orbits faster
    if moon_angle >= 360:
        moon_angle -= 360
        
    earth_angle += 0.05  # Earth rotates slowly
    if earth_angle >= 360:
        earth_angle -= 360


    # Move enemies (asteroids)
    for e in enemies[:]:
        x, y, z, size = e[0], e[1], e[2], e[3]
        
        # Move asteroid towards the Earth in X and Z directions
        earth_pos = [0,0,50]
        dx = earth_pos[0] - e[0]
        dy = earth_pos[1] - e[1]
        dz = earth_pos[2] - e[2]
        dist = math.sqrt(dx*dx + dz*dz)  # Only consider X and Z for movement
        
        if dist > 0:
            speed = 0.05
            dx /= dist
            dy /= dist
            dz /= dist
            e[0] += dx * speed
            e[1] += dy * speed
            e[2] += dz * speed
        

        # Check if enemy hit Earth
        enemy_dist = math.sqrt(e[0]**2 + e[1]**2 + (e[2]- 50)**2)
        if enemy_dist < 200 + e[3]:  # Enemy size + player ship radius
            enemies.remove(e)
            explosions.append([e[0], e[1], e[2], size*1.5, 10])  # Add explosion

            # For debugging - print when an asteroid hits Earth
            print(f"Asteroid hit Earth! Distance: {enemy_dist}, Earth radius: 200, Asteroid size: {size}")

            earth_hits += 1
            # Check if we've reached the maximum number of hits
            if earth_hits >= max_earth_hits:
                game_over = True
                if score > high_score:
                    high_score = score
            continue
        # Update explosions
        for exp in explosions[:]:
            exp[4] -= 1  # Decrease lifetime
            if exp[4] <= 0:
                explosions.remove(exp)
        # Check if enemy hit player ship
        player_dist = math.sqrt((e[0]-player_pos[0])**2 + (e[1]-player_pos[1])**2 + (e[2]-player_pos[2])**2)
        if player_dist < size + 20:  # Enemy size + player ship radius
            enemies.remove(e)
            game_over = True
            if score > high_score:
                high_score = score
            destroyed_ships += 1
            player_hit = True
            continue

# Inside your idle() function → replace the bullet loop with this:

# Move bullets and check collisions
    bullet_speed = 7
    bullets_to_remove = []
    enemies_to_remove = []

    for i, b in enumerate(bullets):
        b[0] += bullet_speed * math.cos(math.radians(b[3]))
        b[1] += bullet_speed * math.sin(math.radians(b[3]))

        bullet_hit = False  # Track if bullet hit something

        # Check collision with all enemies
        for j, e in enumerate(enemies):
            if j in enemies_to_remove:
                continue  # Skip enemies already marked for removal

            dist_3d = math.sqrt((e[0] - b[0])**2 + (e[1] - b[1])**2 + (e[2] - b[2])**2)

            if dist_3d < e[3] + 20:
                bullets_to_remove.append(i)
                enemies_to_remove.append(j)
                score += 1
                total_asteroids_destroyed += 1
                bullet_hit = True  # Mark this bullet as a hit
                break  # No need to check other enemies

        # Only count as missed if it goes out of bounds AND did NOT hit
        if abs(b[0]) > GRID_LENGTH + 200 or abs(b[1]) > GRID_LENGTH + 200:
            bullets_to_remove.append(i)
            if not bullet_hit:
                missed_bullets += 1

    # Remove bullets and enemies in reverse order
    for i in sorted(bullets_to_remove, reverse=True):
        if i < len(bullets):
            bullets.pop(i)

    for i in sorted(enemies_to_remove, reverse=True):
        if i < len(enemies):
            enemies.pop(i)



    # Reset player hit flag
    player_hit = False
    
    # Update high score if current score is higher
    if score > high_score:
        high_score = score
    
    glutPostRedisplay()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearColor(0.0, 0.0, 0.1, 1.0)  # Dark blue background for space
    glLoadIdentity()

    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    setupCamera()

    # Add ambient light
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    # Set up light position (from direction of sun)
    light_position = [1000.0, 500.0, 1000.0, 1.0]
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)

    # Set ambient light
    ambient_light = [0.3, 0.3, 0.3, 1.0]
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambient_light)

    # Set diffuse light
    diffuse_light = [0.7, 0.7, 0.7, 1.0]
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse_light)

    # Set specular light
    specular_light = [1.0, 1.0, 1.0, 1.0]
    glLightfv(GL_LIGHT0, GL_SPECULAR, specular_light)

    # Draw game objects
    glDisable(GL_LIGHTING)  # Disable lighting for better control of object colors
    draw_shapes()

    # Draw dashboard (moved before game over screen)
    draw_dashboard()

    # Display game information
    view_type = "First Person" if first_person_view else "Third Person"
    # Top-left game info (non-overlapping)
    draw_text(10, WINDOW_HEIGHT - 30, f"Score: {score}  High Score: {high_score}  View: {'First' if first_person_view else 'Third'} Person")
    draw_text(10, WINDOW_HEIGHT - 50, f"Spaceships Lost: {destroyed_ships}  Bullets Missed: {missed_bullets}")
    draw_text(10, WINDOW_HEIGHT - 70, "Controls: WASD=Move, Space/Click=Shoot, V=Toggle View, QE=Up/Down")



    if player_hit:
        # Flash warning if player was hit
        if int(glutGet(GLUT_ELAPSED_TIME) / 250) % 2 == 0:  # Flash every 250ms
            glColor3f(1.0, 0.0, 0.0)  # Red text
            draw_text(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2, "SHIP HIT!")

    if game_over:
        # Draw semi-transparent overlay
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.0, 0.0, 0.2, 0.7)  # Dark blue with transparency

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # Draw overlay rectangle
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(WINDOW_WIDTH, 0)
        glVertex2f(WINDOW_WIDTH, WINDOW_HEIGHT)
        glVertex2f(0, WINDOW_HEIGHT)
        glEnd()

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glDisable(GL_BLEND)

        # Game over text
        draw_text(WINDOW_WIDTH // 2 - 250, WINDOW_HEIGHT // 2 + 50, "EARTH DEFENSE MISSION FAILED", GLUT_BITMAP_TIMES_ROMAN_24)
        draw_text(WINDOW_WIDTH // 2 - 180, WINDOW_HEIGHT // 2, f"Final Score: {score}")
        draw_text(WINDOW_WIDTH // 2 - 180, WINDOW_HEIGHT // 2 - 30, f"High Score: {high_score}  Total Ships Lost: {destroyed_ships}")
        draw_text(WINDOW_WIDTH // 2 - 180, WINDOW_HEIGHT // 2 - 60, "Press R to Deploy New Ship")

    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Earth Defense - Bullet Frenzy")

    # Enable features
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_NORMALIZE)
    
    # Register callbacks
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    
    # Start enemy spawning immediately
    glutTimerFunc(5000, spawn_enemy_timer, 0)  # wait 5 sec before first asteroid


    # Start the main loop
    glutMainLoop()

if __name__ == "__main__":
    main()