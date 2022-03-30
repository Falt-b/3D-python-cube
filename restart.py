import pygame
import numpy as np
from sys import exit

WIDTH, HEIGHT = 600, 600
BG = (20, 20, 20)
FPS = 30

camera = np.array([0, 0, 0], np.int16)
light = np.array([-2, 0, -1], np.int16)
aspect_ratio = WIDTH/HEIGHT
fov = 90
fov_rad = 1 / np.tan(fov*.5 / 180/ np.pi)
z_near = .1
z_far = 100


projection_matrix = np.array([
        [aspect_ratio*fov_rad, 0, 0, 0],
        [0, fov_rad, 0, 0],
        [0, 0, z_far/(z_far - z_near), 1],
        [0, 0, (-z_far * z_near) / (z_far - z_near), 0]
], np.float16)

class CUBE:
        def __init__(self, pos, scale, color):
                self.cx, self.cy, self.cz = pos[0], pos[1], pos[2]
                self.scale = scale
                self.color = color
                self.points = np.array([[-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1],
                                        [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1]], int)
                self.triangles = np.array([
                                        #top correct
                                        [self.points[0], self.points[1], self.points[3]],
                                        [self.points[3], self.points[1], self.points[2]],
                                        #bottom correct
                                        [self.points[7], self.points[5], self.points[4]],
                                        [self.points[6], self.points[5], self.points[7]],
                                        #north
                                        [self.points[4], self.points[1], self.points[0]],
                                        [self.points[5], self.points[1], self.points[4]],
                                        #south correct
                                        [self.points[3], self.points[2], self.points[7]],
                                        [self.points[7], self.points[2], self.points[6]],
                                        #east correct
                                        [self.points[2], self.points[1], self.points[6]],
                                        [self.points[6], self.points[1], self.points[5]],
                                        #west correct
                                        [self.points[0], self.points[3], self.points[4]],
                                        [self.points[4], self.points[3], self.points[7]]], int)

        #rotation matricies by given angle
        def rotate_x(self, angle):
                a = np.deg2rad(angle)
                s, c = np.sin(a), np.cos(a)
                return np.array([[1, 0, 0], [0, c, -s], [0, s, c]], np.float16)

        def rotate_y(self, angle):
                a = np.deg2rad(angle)
                s, c = np.sin(a), np.cos(a)
                return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], np.float16)

        def rotate_z(self, angle):
                a = np.deg2rad(angle)
                s, c = np.sin(a), np.cos(a)
                return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], np.float16)


        #point transformation functions
        def rotate_point(self, point, angles):
                return np.dot(self.rotate_z(angles[2]), np.dot(self.rotate_y(angles[1]), np.dot(self.rotate_x(angles[0]), point)))

        def scale_point(self, point):
                return np.array([point[0]*self.scale+self.cx, point[1]*self.scale+self.cy, point[2]], np.float16)

        def translate_point(self, point, z):
                return np.array([point[0], point[1], point[2]+z], np.float16)

        def project_point(self, point):
                p = np.dot(projection_matrix, np.append(point, 1))
                if p[3] != 0:
                        return np.array([p[0]/p[3], p[1]/p[3], p[2]], np.float16)
                return np.array([p[0], p[1], p[2]], np.float16)


        #information functions
        def calc_normal(self, point):
                l = np.sqrt((point[0]*point[0]) + (point[1]*point[1]) + (point[2]*point[2]))
                return np.array([point[0]/l, point[1]/l, point[2]/l], np.float16)

        def dot(self, normal, point, other):
                return (normal[0] * (point[0] - other[0]) +
                        normal[1] * (point[1] - other[1]) +
                        normal[2] * (point[2] - other[2]))

        def shade(self, shade_factor):
                s = [self.color[0] * (1 - shade_factor), self.color[1] * (1 - shade_factor), self.color[2] * (1 - shade_factor)]
                if s[0] > 255: s[0] = 255
                if s[1] > 255: s[1] = 255
                if s[2] > 255: s[2] = 255
                return tuple(s)

        def render(self, surface, angles):
                for tri in self.triangles:
                        rotated_tri = np.array([
                                self.rotate_point(tri[0], angles),
                                self.rotate_point(tri[1], angles),
                                self.rotate_point(tri[2], angles)
                        ], np.float16)
                        translated_tri = np.array([
                                [rotated_tri[0][0], rotated_tri[0][1], rotated_tri[0][2]+3],
                                [rotated_tri[1][0], rotated_tri[1][1], rotated_tri[1][2]+3],
                                [rotated_tri[2][0], rotated_tri[2][1], rotated_tri[2][2]+3]
                        ], np.float16)
                        line1 = translated_tri[1] - translated_tri[0]
                        line2 = translated_tri[2] - translated_tri[0]
                        normal = self.calc_normal(np.cross(line1, line2))
                        if self.dot(normal, translated_tri[0], camera) < 0:
                                final_tri = np.array([
                                        self.scale_point(self.project_point(translated_tri[0])),
                                        self.scale_point(self.project_point(translated_tri[1])),
                                        self.scale_point(self.project_point(translated_tri[2]))
                                ], np.float16)
                                t = final_tri.tolist()
                                light_dir = self.calc_normal(light)
                                color = self.shade((normal[0]*light_dir[0]+normal[1]*light_dir[1]+normal[2]*light_dir[2]))
                                pygame.draw.polygon(surface, color, ((t[0][0], t[0][1]), (t[1][0], t[1][1]), (t[2][0], t[2][1])), 0)

def main():
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("3D Cube")
        clock = pygame.time.Clock()
        running = True

        c1 = CUBE((300, 300, 100), 2, (255, 102, 176))


        a = 0

        while running:
                clock.tick(FPS)
                for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                                running = False
                        if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_ESCAPE:
                                        running = False
                screen.fill(BG)
                if a > 360: a = 0
                a += 1

                c1.render(screen, [30, -a, np.sin(-a*.053)*40])

                pygame.display.update()

if __name__ == "__main__":
        main()
        pygame.quit()
        exit()
