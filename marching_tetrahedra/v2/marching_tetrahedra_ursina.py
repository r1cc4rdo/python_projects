import numpy as np
import ursina as ua

from cool_normals_shader import cool_normals
from isosurface2 import precompute_surface_from_cube, render


def sample_fun(xx, yy, zz):

    def gaussian_3d(mu, gamma):
        xmmu = np.linalg.norm(np.stack([xx, yy, zz], axis=-1) - mu, axis=-1)  # x minus mu
        return np.exp(-xmmu ** 2 / (2 * gamma ** 2)) / gamma * np.sqrt(2 * np.pi)

    displacement = 0.3 * np.sin(ua.time.time())
    return gaussian_3d([-0.5, 0, 0], 0.4) + gaussian_3d([-0.2, 0.7, 0], 0.2) + gaussian_3d([0.5 + displacement, 0, 0], 0.3)


face_lut = precompute_surface_from_cube()
# verts, tris = render(((-1, 1),) * 3, 0.04, sample_fun, 6, face_lut)  # if commented below, compute once here


def update():
    verts, tris = render(((-1, 1), ) * 3, 0.04, sample_fun, 6, face_lut)  # comment to test engine performance
    surface.model.vertices = verts
    surface.model.triangles = tris
    surface.model.generate()


if __name__ == '__main__':
    app = ua.Ursina()
    ua.window.exit_button.visible = True
    ua.window.fps_counter.enabled = True

    surface = ua.Entity(model=ua.Mesh())  #, shader=cool_normals)
    # ua.Entity(model='sphere', subdivision=3, position=(-5.5, 4), shader=cool_normals)
    ua.EditorCamera()
    app.run()
