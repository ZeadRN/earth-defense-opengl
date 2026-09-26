"""Textured celestial bodies and a distant starfield, using legacy OpenGL.

Surface maps: NASA Blue Marble and NASA SVS CGI Moon Kit. See ASSET_CREDITS.md.
Textures use compressed RGB bytes so the game needs no image-decoding package.
"""
from pathlib import Path
import math
import random
import struct
import zlib
from OpenGL.GL import *
from OpenGL.GLU import gluBuild2DMipmaps

_textures = {}
_sphere = None
_stars = None


def texture(name):
    if name not in _textures:
        data = (Path(__file__).parent / 'assets' / (name + '.rgbz')).read_bytes()
        width, height = struct.unpack('<II', data[:8])
        pixels = zlib.decompress(data[8:])
        if len(pixels) != width * height * 3:
            raise ValueError('Invalid planet texture: ' + name)
        tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGB, width, height, GL_RGB, GL_UNSIGNED_BYTE, pixels)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        _textures[name] = tex
    return _textures[name]


def sphere_mesh():
    global _sphere
    if _sphere is None:
        _sphere = glGenLists(1)
        glNewList(_sphere, GL_COMPILE)
        for row in range(64):
            glBegin(GL_QUAD_STRIP)
            for col in range(129):
                u = col / 128
                longitude = math.tau * u - math.pi
                for v in ((row+1)/64, row/64):
                    latitude = math.pi * (v-0.5)
                    normal = (math.cos(latitude)*math.cos(longitude),
                              math.cos(latitude)*math.sin(longitude), math.sin(latitude))
                    glNormal3f(*normal)
                    glTexCoord2f(u,v)
                    glVertex3f(*normal)
            glEnd()
        glEndList()
    return _sphere


def textured_sphere(name, radius):
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture(name))
    glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
    glColor3f(1,1,1)
    glPushMatrix()
    glScalef(radius,radius,radius)
    glCallList(sphere_mesh())
    glPopMatrix()
    glDisable(GL_TEXTURE_2D)


def atmosphere():
    """A thin, view-dependent blue limb, without hiding the surface map."""
    matrix = glGetFloatv(GL_MODELVIEW_MATRIX)
    eye = [-sum(matrix[axis][i]*matrix[3][i] for i in range(3)) for axis in range(3)]
    length = math.sqrt(sum(v*v for v in eye))
    eye = [v/max(length,1) for v in eye]
    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    glDepthMask(GL_FALSE)
    for row in range(32):
        glBegin(GL_QUAD_STRIP)
        for col in range(97):
            lon = math.tau*col/96
            for v in ((row+1)/32,row/32):
                lat = math.pi*(v-0.5)
                n = (math.cos(lat)*math.cos(lon),math.cos(lat)*math.sin(lon),math.sin(lat))
                facing = max(0,sum(n[i]*eye[i] for i in range(3)))
                alpha = 0.28*(1-facing)**5
                glColor4f(0.16,0.48,1.0,alpha)
                glVertex3f(*(204*v for v in n))
        glEnd()
    glDepthMask(GL_TRUE)
    glDisable(GL_CULL_FACE)
    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)


def draw_bodies(earth_angle, moon_angle):
    # Parallel sunlight gives consistent day/night shading on both bodies.
    glLightfv(GL_LIGHT0, GL_POSITION, (0.8, -0.25, 0.8, 0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.1, 0.1, 0.12, 1))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (1, 0.98, 0.95, 1))
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (0.035,0.035,0.045,1))
    glPushMatrix()
    glTranslatef(0,0,50)
    glRotatef(23.4,0,1,0)
    glRotatef(earth_angle + 30,0,0,1)
    textured_sphere('earth',200)
    atmosphere()
    glPopMatrix()

    # Moon/Earth size ratio is approximately 0.27; orbital distance is compressed for gameplay.
    angle = math.radians(moon_angle + 135)
    glPushMatrix()
    glTranslatef(460*math.cos(angle),460*math.sin(angle),90+35*math.sin(angle))
    glRotatef(moon_angle + 30,0,0,1)
    textured_sphere('moon',54.5)
    glPopMatrix()


def draw_stars():
    """Uniform sky directions; camera translation cannot move stars through the arena."""
    global _stars
    if _stars is None:
        rng = random.Random(423)
        _stars = glGenLists(1)
        glNewList(_stars,GL_COMPILE)
        for count,size,low,high in [(2600,1.0,0.18,0.58),(350,1.5,0.55,0.85),(65,2.2,0.8,1.0)]:
            glPointSize(size)
            glBegin(GL_POINTS)
            for _ in range(count):
                z = rng.uniform(-1,1)
                a = rng.uniform(0,math.tau)
                r = math.sqrt(1-z*z)
                brightness = rng.uniform(low,high)
                tint = rng.choice(((0.85,0.91,1),(1,0.94,0.84),(1,1,1)))
                glColor3f(*(brightness*c for c in tint))
                glVertex3f(4000*r*math.cos(a),4000*r*math.sin(a),4000*z)
            glEnd()
        glEndList()
    glPushAttrib(GL_ENABLE_BIT | GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_POINT_BIT)
    glDisable(GL_LIGHTING)
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_DEPTH_TEST)
    glDepthMask(GL_FALSE)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_POINT_SMOOTH)
    glPushMatrix()
    matrix = glGetFloatv(GL_MODELVIEW_MATRIX)
    rotation = [matrix[col][row] if col < 3 or row == 3 else 0 for col in range(4) for row in range(4)]
    glLoadMatrixf(rotation)
    glCallList(_stars)
    glPopMatrix()
    glPopAttrib()
