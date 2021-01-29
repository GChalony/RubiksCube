from collections import namedtuple

import pygame as pg
from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.GLU import *
from pygame.locals import *
from scipy.spatial.transform.rotation import Rotation

from rubikscube import RubiksCube

EulerAngles = namedtuple("EulerAngle", ["alpha", "beta"])


class NavigationController:
    DEFAULT_CUBE_SPEED = 0.5
    ROT_DELTA = 0.5
    HANDLED_KEYS = [pg.K_SPACE, pg.K_UP, pg.K_DOWN,
                    pg.K_LEFT, pg.K_RIGHT, pg.K_z]

    def __init__(self, cube):
        self.cube_rot_speed = 0
        self.keys_pressed = {}
        self.cube = cube

    def handle_event(self, event):
        # print(event)
        if event.type in [pg.KEYUP, pg.KEYDOWN] and event.key in self.HANDLED_KEYS:
            # Pause / Play rotation
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                self.cube_rot_speed = self.DEFAULT_CUBE_SPEED - self.cube_rot_speed
            # Reset view
            elif event.type == KEYDOWN and event.key == pg.K_z and event.mod in [pg.KMOD_LCTRL, pg.KMOD_RCTRL]:
                self.cube.rotation = Rotation.identity()
                print("Reset view!")
            # Register key down
            elif event.type == pg.KEYDOWN:
                self.keys_pressed[event.key] = pg.time.get_ticks()
            # Unregister key down
            elif event.type == pg.KEYUP:
                self.keys_pressed.pop(event.key, None)

    def animate(self):
        n = pg.time.get_ticks()
        for key, time in self.keys_pressed.items():
            rot_speed = self.rot_speed(n - time)
            if key in [pg.K_RIGHT, pg.K_LEFT]:
                sign = -1 if key == pg.K_RIGHT else 1
                rot = Rotation.from_rotvec([0, sign * rot_speed, 0])
                self.cube.rotation = self.cube.rotation * rot
            else:
                sign = 1 if key == pg.K_UP else -1
                rot = Rotation.from_rotvec([sign * rot_speed, 0, 0])
                self.cube.rotation = rot * self.cube.rotation

    def rot_speed(self, dt):
        return dt / 3000


class CubeController:
    def __init__(self, cube):
        self.cube = cube

    def handle_event(self, event):
        if event.type == pg.KEYDOWN:
            print(event, cube._animation)
            if cube._animation is None:
                reverse = event.mod == pg.KMOD_LSHIFT or event.mod == pg.KMOD_RSHIFT
                if event.key == pg.K_f:
                    cube.move_face("F", reverse=reverse)
                elif event.key == pg.K_b:
                    cube.move_face("B", reverse=reverse)
                elif event.key == pg.K_l:
                    cube.move_face("L", reverse=reverse)
                elif event.key == pg.K_r:
                    cube.move_face("R", reverse=reverse)
                elif event.key == pg.K_u:
                    cube.move_face("U", reverse=reverse)
                elif event.key == pg.K_d:
                    cube.move_face("D", reverse=reverse)
            else:
                print("Warning: animation not finished!")

    def animate(self):
        pass


def handle_events(controllers):
    for event in pg.event.get():
        # Window cross
        if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key in [pg.K_q, pg.K_ESCAPE]):
            pg.quit()
            quit()
        else:
            for controller in controllers:
                controller.handle_event(event)
    animate_controls(controllers)


def animate_controls(controllers):
    for controller in controllers:
        controller.animate()


if __name__ == '__main__':
    cube = RubiksCube()
    cube.shuffle()

    controls = [NavigationController(cube), CubeController(cube)]

    pg.init()
    display = (800, 600)
    pg.display.set_mode(display, DOUBLEBUF | OPENGL)

    glLight(GL_LIGHT0, GL_POSITION, (1, 1, 1, 0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0, 0, 0, 1))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (2, 2, 2, 1))

    vert_shader = """
#version 400 
layout (location = 0) in vec3 VertexPosition;
layout (location = 1) in vec3 VertexNormal;
out vec3 LightIntensity;
struct LightInfo {
vec4 Position;
// Light position in eye coords. 
vec3 La;
// Ambient light intensity 
vec3 Ld;
// Diffuse light intensity 
vec3 Ls;
// Specular light intensity 
};
uniform LightInfo Light;
struct MaterialInfo { 
vec3 Ka;
// Ambient reflectivity 
vec3 Kd;
// Diffuse reflectivity 
vec3 Ks;
// Specular reflectivity 
float Shininess;
// Specular shininess factor 
};
uniform MaterialInfo Material;
uniform mat4 ModelViewMatrix;
uniform mat3 NormalMatrix;
uniform mat4 ProjectionMatrix;
uniform mat4 MVP;
void main() { 
vec3 tnorm = normalize( NormalMatrix * VertexNormal);
vec4 eyeCoords = ModelViewMatrix * vec4(VertexPosition,1.0);
vec3 s = normalize(vec3(Light.Position - eyeCoords));
vec3 v = normalize(-eyeCoords.xyz);
vec3 r = reflect( -s, tnorm );
vec3 ambient = Light.La * Material.Ka;
float sDotN = max( dot(s,tnorm), 0.0 );
vec3 diffuse = Light.Ld * Material.Kd * sDotN;
vec3 spec = vec3(0.0);
if( sDotN > 0.0 ) spec = Light.Ls * Material.Ks * pow( max( dot(r,v), 0.0 ), Material.Shininess );
LightIntensity = ambient + diffuse + spec;
gl_Position = MVP * vec4(VertexPosition,1.0);
} 
    """

    frag_shad = """
        #version 400 
        in vec3 LightIntensity; 
        layout( location = 0 ) out vec4 FragColor; 
        void main() { 
            FragColor = vec4(LightIntensity, 1.0); 
        } 
    """

    # Compiles the vertex and fragment shader
    shader = shaders.compileProgram(shaders.compileShader(str(vert_shader), GL_VERTEX_SHADER),
                                    shaders.compileShader(str(frag_shad), GL_FRAGMENT_SHADER))

    # Camera view
    gluPerspective(30, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0, 0, -10)
    glRotatef(20, 1, 0, 0)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_NORMAL_ARRAY)
    glLineWidth(5.0)
    glPushMatrix()

    while True:
        handle_events(controls)
        cube.animate()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE )

        cube.draw()
        pg.display.flip()
        # TODO constant frame rate ?
        pg.time.wait(10)
