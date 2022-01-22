import numpy as np
import ursina as ua

from isosurface import surface_from_cube
# from cool_normals_shader import cool_normals


def update():

    bits = 5
    sampling = np.linspace(-1, 1, 2 ** bits + 1)
    xx, yy, zz = np.meshgrid(sampling, sampling, sampling)

    def gaussian_3d(mu, gamma):
        xmmu = np.linalg.norm(np.stack([xx, yy, zz], axis=-1) - mu, axis=-1)  # x minus mu
        return np.exp(-xmmu ** 2 / (2 * gamma ** 2)) / gamma * np.sqrt(2 * np.pi)

    displacement = np.sin(ua.time.time()) * 0.3
    potentials = gaussian_3d([-0.5, 0, 0], 0.4) + gaussian_3d([-0.2, 0.7, 0], 0.2) + gaussian_3d([0.5 + displacement, 0, 0], 0.3)
    threshold = 6

    indicator = potentials < threshold
    min_indicator = indicator[:, :, :-1] & indicator[:, :, 1:]
    min_indicator = min_indicator[:, :-1, :] & min_indicator[:, 1:, :]
    min_indicator = min_indicator[:-1, :, :] & min_indicator[1:, :, :]
    max_indicator = indicator[:, :, :-1] | indicator[:, :, 1:]
    max_indicator = max_indicator[:, :-1, :] | max_indicator[:, 1:, :]
    max_indicator = max_indicator[:-1, :, :] | max_indicator[1:, :, :]
    indicator = min_indicator ^ max_indicator

    tris = []
    for ix, iy, iz in zip(*np.where(indicator)):

        coordinates = np.stack(list(ii[ix:ix + 2, iy:iy + 2, iz:iz + 2] for ii in (xx, yy, zz)), axis=-1)
        coordinates = coordinates.reshape((-1, 3))
        values_at_coords = potentials[ix:ix+2, iy:iy+2, iz:iz+2].reshape((-1,))
        swizzle = [1, 5, 7, 3, 2, 6, 4, 0]
        tris.extend(surface_from_cube(coordinates[swizzle], values_at_coords[swizzle], threshold))

    # normals = ...

    surface.model.vertices = tris
    surface.model.generate()


if __name__ == '__main__':
    app = ua.Ursina()
    ua.window.exit_button.visible = True
    ua.window.fps_counter.enabled = False

    surface = ua.Entity(model=ua.Mesh())  #, shader=cool_normals)  #, double_sided=True)
    ua.Entity(model='sphere', subdivision=3, position=(-5.5, 4))  #, shader=cool_normals)
    ua.EditorCamera()
    app.run()
