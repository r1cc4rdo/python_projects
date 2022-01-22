import itertools
import numpy as np


def surface_from_tetra(cube_indexes, outside):
    """
    Returns a list of triangles for the iso-surface at level 'threshold'.
    Whatever is passed into vertices is interpolated, e.g. coordinates and/or normals.
    """
    tetra_faces = [[1, 2, 3], [0, 3, 2], [0, 1, 3], [0, 2, 1]]  # face[k] is missing vertex k
    outside = [index for index, is_out in enumerate(outside) if is_out]
    inside = list(set(range(4)) - set(outside))

    if len(outside) in (0, 4):  # nothing to do, the iso-surface does not intersect the tetra
        return []

    if len(outside) in (1, 3):  # the iso-surface split vertexes in a 3/1 fashion, output a single triangle

        base_is_out = len(outside) == 3
        top_index = inside[0] if base_is_out else outside[0]
        base_indexes = tetra_faces[top_index] if base_is_out else tetra_faces[top_index][::-1]
        return [(cube_indexes[top_index], cube_indexes[base_index]) for base_index in base_indexes]

    #  if here, count == 2. Split is 2/2, need to output two triangles

    indexes = tetra_faces[outside[0]]
    while indexes[1] != outside[1]:
        indexes = indexes[1:] + [indexes[0]]
    indexes = indexes + [outside[0]]

    quad = [(cube_indexes[sidx], cube_indexes[eidx]) for sidx, eidx in zip(indexes, indexes[1:] + [indexes[0]])]
    return [quad[idx] for idx in (0, 2, 1, 0, 3, 2)]  # triangles


def precompute_surface_from_cube():
    """
    Returns a structure specifying the surface though the cube given the field values at the cube's corners.
    Each index corresponds to the binary representation of the inside/outside state of each corner.
    The order is the following:

           7    ,4
        0  |  3  |
        |  6__|__5
        1_____2

        vertices = np.array(list(itertools.product([0, 1], repeat=3)))
        vertices = vertices[[0, 2, 6, 4, 5, 7, 3, 1]]  # gray-like ordering

    Each element of the structure contains a list of vertices given as a pair of cube indexes,
    and a list of faces given as a list of triplets of vertex indexes.
    """
    cube_tetras = [[0, 1, 2, 4], [0, 1, 4, 7], [0, 2, 3, 4], [1, 2, 4, 5], [1, 4, 7, 5], [1, 6, 5, 7]]

    face_lut = []
    for configuration in range(256):
        outside = [configuration >> pow2 & 1 == 1 for pow2 in range(8)]

        faces = []
        for tetra in cube_tetras:  # returned as [(i, j), (i, k), (i, w), ...] each 3 a triangle
            faces.extend(surface_from_tetra(tetra, [outside[index] for index in tetra]))

        vertices, faces = np.unique(np.array(faces), axis=0, return_inverse=True)
        face_lut.append((vertices, faces))

    return face_lut


def render(volume, interval, threshold, face_lut):

    # optimization: do it in slices

    vertices = np.array(list(itertools.product([0, 1], repeat=3)))
    vertices = vertices[[0, 2, 6, 4, 5, 7, 3, 1]]  # gray-like ordering
    x_range, y_range, z_range = [np.arange(volume[dim][0], volume[dim][1] + interval, interval) for dim in range(3)]
    xx, yy = np.meshgrid(x_range, y_range)

    xs, ys = xx.shape
    z0 = z_range[0]
    p0 = sample_fun(xx, yy, z0)
    o0 = p0 > threshold
    lut_indexes = np.zeros(np.array(o0.shape) - 1, dtype=int)
    for z1 in z_range[1:]:  # one slice at a time
        p1 = sample_fun(xx, yy, z1)
        o1 = p1 > threshold

        lut_indexes[:] = 0
        samples_slice = np.stack((o0, o1), axis=-1)
        for index, (xd, yd, zd) in enumerate(vertices):
            lut_indexes += 2 ** index * samples_slice[xd:xs - 1 + xd, yd:ys - 1 + yd, zd:zs - 1 + zd]

        ...

        z0, p0, o0 = z1, p1, o1

    xx, yy, zz = np.meshgrid(x_range, y_range, z_range)
    potentials = sample_fun(xx, yy, zz)

    vertices = np.array(list(itertools.product([0, 1], repeat=3)))
    vertices = vertices[[0, 2, 6, 4, 5, 7, 3, 1]]  # gray-like ordering

    xs, ys, zs = potentials.shape
    outside = potentials > threshold
    lut_indexes = np.zeros([d - 1 for d in outside.shape], dtype=int)
    for index, (xd, yd, zd) in enumerate(vertices):
        lut_indexes += 2 ** index * outside[xd:xs - 1 + xd, yd:ys - 1 + yd, zd:zs - 1 + zd]

    vertices *= interval
    valid = 0 < lut_indexes < 255
    lut_indexes = lut_indexes[valid]
    origins = np.stack([xx[valid], yy[valid], zz[valid]], axis=-1)
    coords = origins.reshape() + vertices.reshape()
    values = ...

    verts, tris = [], []
    for lut_index, coord_list, value_list in zip(lut_indexes, coords, values):
        displacement = len(verts)
        v_template, f_template = face_lut[lut_index]
        for i, j in v_template:
            t = (threshold - value_list[j]) / (value_list[i] - value_list[j])
            verts.append(t * coord_list[i] + (1 - t) * coord_list[j])
        tris.extend(f_template + displacement)

    return verts, tris


if __name__ == '__main__':
    face_lut = precompute_surface_from_cube()
    print(f'{face_lut=}')

    render(((-1, 1),) * 3, 0.05, 6, face_lut)

    pass
