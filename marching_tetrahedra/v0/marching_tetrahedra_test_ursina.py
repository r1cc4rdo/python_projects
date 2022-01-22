from functools import partial
import numpy as np
import ursina as ua
from ursina.shaders.matcap_shader import matcap_shader

from isosurface import make_cube, tetra_triangles, surface_from_cube

color_wheel = [ua.color.hsv(angle, 1, 1) for angle in range(0, 360, 30)]
color_wheel = color_wheel[::2] + color_wheel[1::2]


def update():
    increment = ua.time.dt if rotate else 0
    cube.rotation += 40 * increment, 30 * increment, 20 * increment
    vertices_normals = surface_from_cube(make_cube(origin, side, return_normals=True), potentials, threshold)
    surface.model.vertices, surface.model.normals = zip(*map(lambda x: x.transpose(), vertices_normals))
    surface.model.generate()


def setup_cube_and_tetrahedrons():
    cube = ua.Entity(model='wireframe_cube', scale=4, color=ua.color.white, position=(2, 0))

    def toggle_tetrahedron(button, tetra):
        on = tetra.mode == 'triangle'
        button.text = 'x' if on else 'o'
        tetra.mode = 'line' if on else 'triangle'
        tetra.generate()

    def toggle_rotation():
        global rotate
        rotate ^= True

    vertices = make_cube(origin, side)  # cannot reuse cube vertices because order matters
    for index, (tetra_faces_indexes, color) in enumerate(zip(tetra_triangles(), color_wheel)):
        tetra_mesh = ua.Mesh(vertices=vertices, triangles=tetra_faces_indexes, mode='line')
        ua.Entity(model=tetra_mesh, parent=cube, scale=0.25, color=color)

        button = ua.Button(color=color, text='x', parent=ua.camera.ui, scale=0.05, position=(-0.75 + 0.06 * index, 0.40))
        button.on_click = partial(toggle_tetrahedron, button, tetra_mesh)

    ua.Text(text='Tetrahedra', position=(-0.66, 0.46), parent=ua.camera.ui)
    ua.Button(color=ua.color.white, text='Toggle rotation', parent=ua.camera.ui, position=(-0.6, 0.34),
              text_color=ua.color.black, on_click=toggle_rotation, scale=(0.36, 0.05))

    return cube


def setup_sliders():

    def set_threshold():
        global threshold
        threshold = threshold_slider.value

    def set_potential(slider, point, index):
        potentials[index] = slider.value
        point.scale = 0.025 * (slider.value + 2)

    vertices = make_cube(origin, side)
    for index, value in enumerate(potentials):
        point = ua.Entity(model='sphere', scale=0.025 * (value + 2), color=color_wheel[index], parent=cube, position=vertices[index])
        point.position /= 4

        slider = ua.ThinSlider(text=str(index), dynamic=True, position=(-0.75, -0.1 - 0.05 * index), scale=(0.7, 1), min=-1, max=1, value=value)
        slider.on_value_changed = partial(set_potential, slider, point, index)
        slider.knob.color = color_wheel[index]

    ua.Text(text='Iso-surface', position=(-0.64, 0.08), parent=ua.camera.ui)
    threshold_slider = ua.ThinSlider(text='th', dynamic=True, position=(-0.75, 0), scale=(0.7, 1),
                                     min=-1, max=1, value=0., on_value_changed=set_threshold)


if __name__ == '__main__':
    app = ua.Ursina()
    ua.window.exit_button.visible = True
    ua.window.fps_counter.enabled = False

    origin, side = (0, 0, 0), 4
    potentials = np.array([-1.] * 4 + [1.] * 4)
    threshold = 0.
    rotate = True

    cube = setup_cube_and_tetrahedrons()
    setup_sliders()
    surface = ua.Entity(model=ua.Mesh(), parent=cube, scale=0.25, color=ua.color.white,
                        double_sided=True, shader=matcap_shader, texture='shore')
    ua.EditorCamera()
    app.run()
