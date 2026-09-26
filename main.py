"""Earth Defense - CSE423 portfolio revision. Original submission: original/."""
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time
from celestial import draw_bodies, draw_stars
from game_state import Game, EARTH, EARTH_RADIUS, direction, segment_hit

WINDOW_WIDTH, WINDOW_HEIGHT = 1100, 800
GRID_LENGTH = 1000
first_person_view = False
chase_camera = False
show_grid = False
camera_yaw = 45.0
camera_distance = 1450.0
camera_height = 850.0
g = Game()
keys = set()
visual_rng = random.Random(42)
last_time = 0.0
accumulator = 0.0

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18, color=(0.82, 0.92, 1.0)):
    glColor3f(*color)
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

    draw_stars()
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_NORMALIZE)
    glLightfv(GL_LIGHT0, GL_POSITION, (600, -400, 1200, 1))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.28, 0.32, 0.42, 1))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.95, 0.88, 0.75, 1))

    draw_bodies(g.earth_angle, g.moon_angle)
    # Restore slightly brighter fill light for the small gameplay objects.
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.25, 0.27, 0.32, 1))

    # Spaceship
    glPushMatrix()
    glTranslatef(g.player_pos[0], g.player_pos[1], g.player_pos[2])  # Use player_pos[2] for z-axis
    glRotatef(g.gun_angle, 0, 0, 1)
    
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
    if visual_rng.random() > 0.5:  # Flickering effect
        glColor3f(1, 0.5, 0)  # Orange-yellow
    else:
        glColor3f(1, 0.3, 0)  # Red-orange
    
    # Left exhaust
    glPushMatrix()
    glTranslatef(-20, 15, 0)
    glRotatef(-90, 0, 1, 0)
    glutSolidCone(5, 10 + visual_rng.uniform(0, 5), 12, 12)  # Varying length
    glPopMatrix()
    
    # Right exhaust
    glPushMatrix()
    glTranslatef(-20, -15, 0)
    glRotatef(-90, 0, 1, 0)
    glutSolidCone(5, 10 + visual_rng.uniform(0, 5), 12, 12)  # Varying length
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
    if visual_rng.random() > 0.6:  # Different flicker rate
        glColor3f(1, 0.6, 0.2)
    else:
        glColor3f(1, 0.4, 0.1)
    glutSolidCone(7, 15 + visual_rng.uniform(0, 8), 16, 16)
    glPopMatrix()
    
    glPopMatrix()

    # Asteroids
    for e in g.enemies:
        x, y, z, size = e[0], e[1], e[2], e[3]
        # Draw asteroid (rocky appearance)
        glPushMatrix()
        glTranslatef(x, y, z)
        glRotatef(g.moon_angle * 2, 1, 0.5, 0.3)  # Rotate for visual effect
        glColor3f(0.58, 0.44, 0.33)
        glutSolidSphere(size, 9, 7)  # Faceted asteroid
        glPopMatrix()


    
    glDisable(GL_LIGHTING)
    # Draw explosions
    for exp in g.explosions:
        draw_explosion(exp[0], exp[1], exp[2], exp[3], exp[4])

    # Bullets
    glColor3f(1, 1, 0)
    for b in g.bullets:
        glColor3f(1, 1, 0)
        glPushMatrix()
        glTranslatef(b[0], b[1], b[2])
        glutSolidSphere(5, 10, 10)
        
        glColor3f(1.0, 0.55, 0.16)
        vector = b[4:7] if len(b) >= 7 else direction(b[3])
        glLineWidth(2)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(*(-25*v for v in vector))
        glEnd()
        glLineWidth(1)
        glPopMatrix()

    # A short firing guide makes vertical aim visible in the overview camera.
    if not g.game_over:
        vector = g.shot_direction()
        glColor3f(0.35, 0.8, 0.85)
        glBegin(GL_LINES)
        for start, end in [(70, 90), (100, 120), (130, 150)]:
            glVertex3f(*(g.player_pos[i]+start*vector[i] for i in range(3)))
            glVertex3f(*(g.player_pos[i]+end*vector[i] for i in range(3)))
        glEnd()

    # Optional navigation grid (G); hidden by default for a cleaner space scene.
    if not show_grid:
        return
    # Transparent grid
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0.15, 0.5, 0.65, 0.12)
    grid_step = 100
    for i in range(-GRID_LENGTH, GRID_LENGTH + grid_step, grid_step):
        glBegin(GL_LINES)
        glVertex3f(i, -GRID_LENGTH, 0)
        glVertex3f(i, GRID_LENGTH, 0)
        glVertex3f(-GRID_LENGTH, i, 0)
        glVertex3f(GRID_LENGTH, i, 0)
        glEnd()
    glDisable(GL_BLEND)

def screen_begin():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()


def screen_end():
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def panel(x, y, width, height, color=(0.025, 0.055, 0.1, 0.92)):
    screen_begin()
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(*color)
    glBegin(GL_QUADS)
    for px, py in [(x,y), (x+width,y), (x+width,y+height), (x,y+height)]:
        glVertex2f(px,py)
    glEnd()
    glDisable(GL_BLEND)
    screen_end()


def bar(x, y, width, fraction, color):
    panel(x,y,width,6,(0.12,0.18,0.25,1))
    panel(x,y,width*max(0,min(1,fraction)),6,(*color,1))


def draw_dashboard():
    small = GLUT_BITMAP_HELVETICA_12
    x, top = WINDOW_WIDTH-246, WINDOW_HEIGHT-94
    panel(x, top-190, 228, 210)
    draw_text(x+16,top,'DEFENSE STATUS', color=(0.28,0.86,1))
    draw_text(x+16,top-28,f'Earth integrity   {100-20*g.earth_hits}%', small)
    bar(x+16,top-43,196,1-g.earth_hits/g.max_earth_hits,(0.2,0.8,0.58))
    draw_text(x+16,top-67,f'Ship shields      {g.shields} / 3', small)
    bar(x+16,top-82,196,g.shields/3,(0.26,0.64,1))
    draw_text(x+16,top-107,f'Altitude  {g.player_pos[2]:.0f}   |   Pitch {g.gun_pitch:+.0f}',small)
    draw_text(x+16,top-129,'Aim assist: '+('ON' if g.aim_assist else 'OFF')+'  [T]',small)
    draw_text(x+16,top-151,f'Asteroids: {len(g.enemies)}  |  Misses: {g.missed_bullets}',small)
    solution = g.aim_solution()
    if solution:
        delta = solution[0][2]-g.player_pos[2]
        label = 'BELOW' if delta < -12 else ('ABOVE' if delta > 12 else 'LEVEL')
        draw_text(x+16,top-174,f'TARGET {label}  {abs(delta):.0f} units',small,color=(1,0.75,0.28))
    else:
        draw_text(x+16,top-174,'Turn toward a target to acquire',small)
    draw_radar()


def draw_radar():
    size = min(210, max(100, WINDOW_HEIGHT-426))
    x,y = WINDOW_WIDTH-size-28,104
    panel(x-10,y-16,size+10,size+38)
    draw_text(x,y+size+3,'RADAR / TOP VIEW',GLUT_BITMAP_HELVETICA_12,color=(0.28,0.86,1))
    cx,cy,scale = x+size/2,y+size/2,size/2333
    screen_begin()
    glColor3f(0.1,0.3,0.4)
    for radius in (size*0.214,size*0.428):
        glBegin(GL_LINE_LOOP)
        for i in range(64):
            a=i*math.tau/64
            glVertex2f(cx+radius*math.cos(a),cy+radius*math.sin(a))
        glEnd()
    glColor3f(0.12,0.45,0.75)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(cx,cy)
    for i in range(33):
        a=i*math.tau/32
        glVertex2f(cx+200*scale*math.cos(a),cy+200*scale*math.sin(a))
    glEnd()
    glPointSize(5)
    glColor3f(1,0.48,0.26)
    glBegin(GL_POINTS)
    for enemy in g.enemies:
        glVertex2f(cx+enemy[0]*scale,cy+enemy[1]*scale)
    glEnd()
    px,py = cx+g.player_pos[0]*scale,cy+g.player_pos[1]*scale
    a=math.radians(g.gun_angle)
    glColor3f(0.35,1,0.85)
    glBegin(GL_TRIANGLES)
    for angle,radius in [(a,8),(a+2.5,5),(a-2.5,5)]:
        glVertex2f(px+math.cos(angle)*radius,py+math.sin(angle)*radius)
    glEnd()
    glPointSize(1)
    screen_end()


def draw_target_marker(projected):
    if projected is None:
        return
    x,y,z=projected
    if not (0 <= z <= 1 and 0 < x < WINDOW_WIDTH and 95 < y < WINDOW_HEIGHT-70):
        return
    screen_begin()
    glColor3f(1,0.72,0.22)
    glLineWidth(2)
    glBegin(GL_LINES)
    for sx,sy in [(-1,-1),(-1,1),(1,-1),(1,1)]:
        glVertex2f(x+sx*20,y+sy*12); glVertex2f(x+sx*20,y+sy*20)
        glVertex2f(x+sx*20,y+sy*20); glVertex2f(x+sx*12,y+sy*20)
    glEnd()
    glLineWidth(1)
    screen_end()
    draw_text(x-24,y+28,'LOCK',GLUT_BITMAP_HELVETICA_12,color=(1,0.72,0.22))


def draw_explosion(x, y, z, size, lifetime):
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(1.0, 0.5, 0.0)  # Orange explosion
    glutSolidSphere(size * max(0.15, lifetime / 0.45), 20, 20)
    glPopMatrix()


def keyboardListener(key, x, y):
    global first_person_view, chase_camera, show_grid, accumulator
    key = key.lower()
    if key == b'\x1b':
        glutLeaveMainLoop()
        return
    if key in keys:
        return
    if key == b'r' and g.game_over:
        g.reset()
        keys.clear()
        accumulator = 0.0
        return
    if key == b'p' and not g.game_over:
        g.paused = not g.paused
        keys.clear()
    elif key == b'g':
        show_grid = not show_grid
    elif key == b't':
        g.aim_assist = not g.aim_assist
    elif key == b'j':
        g.gun_pitch = 0.0
    elif key == b'c':
        chase_camera = not chase_camera
        first_person_view = False
    elif key == b'v':
        first_person_view = not first_person_view
    elif key == b' ':
        g.shoot()
    keys.add(key)


def keyboardUp(key, x, y):
    keys.discard(key.lower())


def mouseListener(button, state, x, y):
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        g.shoot()


def specialKeyListener(key, x, y):
    global camera_yaw, camera_height, camera_distance
    if key == GLUT_KEY_LEFT:
        camera_yaw -= 5
    elif key == GLUT_KEY_RIGHT:
        camera_yaw += 5
    elif key == GLUT_KEY_UP:
        camera_height = min(1800, camera_height + 50)
    elif key == GLUT_KEY_DOWN:
        camera_height = max(150, camera_height - 50)
    elif key == GLUT_KEY_PAGE_UP:
        camera_distance = max(400, camera_distance - 50)
    elif key == GLUT_KEY_PAGE_DOWN:
        camera_distance = min(2400, camera_distance + 50)


def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, WINDOW_WIDTH / WINDOW_HEIGHT, 1, 6500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    if first_person_view:
        dx,dy,dz = direction(g.gun_angle,g.gun_pitch)
        x,y,z = g.player_pos
        gluLookAt(x+70*dx,y+70*dy,z+70*dz,x+170*dx,y+170*dy,z+170*dz,0,0,1)
    elif chase_camera:
        dx,dy,dz = direction(g.gun_angle)
        x,y,z = g.player_pos
        desired = (x-260*dx, y-260*dy, z+145)
        hit = segment_hit(g.player_pos, desired, EARTH, EARTH_RADIUS+10)
        fraction = max(0.01, hit-0.03) if hit is not None else 1
        camera = [g.player_pos[i]+fraction*(desired[i]-g.player_pos[i]) for i in range(3)]
        gluLookAt(*camera,x+160*dx,y+160*dy,z,0,0,1)
    else:
        yaw = math.radians(camera_yaw)
        gluLookAt(camera_distance*math.cos(yaw), camera_distance*math.sin(yaw),
                  camera_height, 0, 0, 50, 0, 0, 1)


def reshape(width, height):
    global WINDOW_WIDTH, WINDOW_HEIGHT
    WINDOW_WIDTH, WINDOW_HEIGHT = max(1, width), max(1, height)
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)


def visibility(state):
    if state != GLUT_VISIBLE:
        keys.clear()
        if not g.game_over:
            g.paused = True


def tick(value):
    global last_time, accumulator
    now = time.perf_counter()
    accumulator += min(0.1, max(0, now - last_time))
    last_time = now
    step = 1 / 120
    while accumulator >= step:
        g.update(step, keys)
        accumulator -= step
    glutPostRedisplay()
    glutTimerFunc(16, tick, 0)


def overlay(title, subtitle):
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glColor4f(0, 0, 0.08, 0.82)
    glBegin(GL_QUADS)
    for x, y in [(0, 0), (WINDOW_WIDTH, 0), (WINDOW_WIDTH, WINDOW_HEIGHT), (0, WINDOW_HEIGHT)]:
        glVertex2f(x, y)
    glEnd()
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glDisable(GL_BLEND)
    draw_text(max(10, WINDOW_WIDTH//2-210), WINDOW_HEIGHT//2+40, title, GLUT_BITMAP_TIMES_ROMAN_24)
    draw_text(max(10, WINDOW_WIDTH//2-210), WINDOW_HEIGHT//2, subtitle)
    draw_text(max(10, WINDOW_WIDTH//2-210), WINDOW_HEIGHT//2-40,
              'R: restart | Esc: quit' if g.game_over else 'P: resume | Esc: quit')


def showScreen():
    glClearColor(0.002, 0.003, 0.009, 1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    setupCamera()
    draw_shapes()
    # All HUD elements must ignore scene depth and lighting.
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    solution = g.aim_solution()
    target_screen = gluProject(*solution[0][:3]) if solution else None
    draw_target_marker(target_screen)
    panel(0,WINDOW_HEIGHT-66,WINDOW_WIDTH,66)
    draw_text(20,WINDOW_HEIGHT-29,'EARTH DEFENSE',GLUT_BITMAP_TIMES_ROMAN_24,color=(0.3,0.86,1))
    mode = 'COCKPIT' if first_person_view else ('CHASE' if chase_camera else 'OVERVIEW')
    draw_text(20,WINDOW_HEIGHT-49,mode+'  /  '+('TARGET ACQUIRED' if solution else 'PATROL'),GLUT_BITMAP_HELVETICA_12)
    draw_text(WINDOW_WIDTH-340,WINDOW_HEIGHT-29,f'SCORE {g.score:03d}   BEST {g.high_score:03d}')
    draw_text(WINDOW_WIDTH-340,WINDOW_HEIGHT-49,f'THREAT LEVEL {g.level}',GLUT_BITMAP_HELVETICA_12)
    draw_dashboard()
    panel(0,0,WINDOW_WIDTH,87)
    draw_text(18,65,'W/S fly   A/D turn   Q/E altitude   I/K aim up/down   J level aim',GLUT_BITMAP_HELVETICA_12)
    draw_text(18,45,'Space / click fire   T aim assist   V cockpit   C chase / overview',GLUT_BITMAP_HELVETICA_12)
    draw_text(18,25,'P pause   R restart after loss   Esc quit   G grid   Arrows / PgUp / PgDn camera',GLUT_BITMAP_HELVETICA_12)
    if g.invulnerable > 0 and not g.game_over:
        draw_text(20,WINDOW_HEIGHT-100,'SHIELD HIT - temporary protection',color=(1,0.55,0.3))
    if first_person_view and not g.game_over and not g.paused:
        draw_text(WINDOW_WIDTH//2 - 5, WINDOW_HEIGHT//2 - 6, '+')
    if g.game_over:
        overlay('MISSION FAILED', f'{g.reason} | Score: {g.score}')
    elif g.paused:
        overlay('PAUSED', 'Defend Earth from incoming asteroids')
    glEnable(GL_DEPTH_TEST)
    glutSwapBuffers()


def main():
    global last_time
    if not glutInit:
        raise RuntimeError('FreeGLUT could not load. Run setup_and_run.bat; see README troubleshooting.')
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutCreateWindow(b'Earth Defense - Bullet Frenzy')
    glutSetOption(GLUT_ACTION_ON_WINDOW_CLOSE, GLUT_ACTION_GLUTMAINLOOP_RETURNS)
    glutDisplayFunc(showScreen)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboardListener)
    glutKeyboardUpFunc(keyboardUp)
    glutIgnoreKeyRepeat(1)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutVisibilityFunc(visibility)
    last_time = time.perf_counter()
    glutTimerFunc(0, tick, 0)
    glutMainLoop()


if __name__ == '__main__':
    main()
