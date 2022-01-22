import itertools
import numpy as np

tetra_faces = [[1, 2, 3], [0, 3, 2], [0, 1, 3], [0, 2, 1]]  # face[k] is missing vertex k
cube_tetras = [[0, 1, 2, 4], [0, 1, 4, 7], [0, 2, 3, 4], [1, 2, 4, 5], [1, 4, 7, 5], [1, 6, 5, 7]]


def make_cube(origin=(0, 0, 0), side=1, return_normals=False):
    """
    Return vertices for a cube with 'side' length, centered at 'origin'.
    Consecutive vertices are connected by edges, i.e. have a distance of 1 from each other.
    Example usage:
      |  /|
    | |_|_|
    |___|

    vertices_normals = make_cube((0, 0, 0), 4, return_normals=True)
    vertices, normals = zip(*map(lambda x: x.transpose(), vertices_normals))
    quads = [[3, 2, 1, 0], [7, 6, 5, 4], [0, 1, 6, 7], [2, 3, 4, 5], [1, 2, 5, 6], [0, 7, 4, 3]]
    ua.Entity(model=ua.Mesh(vertices=vertices, normals=normals, triangles=quads))
    """
    vertices = np.array(list(itertools.product([-side, side], repeat=3)))
    vertices = vertices[[0, 2, 6, 4, 5, 7, 3, 1]]  # gray-like ordering
    translated_vertices = origin + vertices / 2
    if return_normals:
        normals = vertices / np.linalg.norm(vertices, axis=1)[:, None]
        return np.stack((translated_vertices, normals), axis=-1)
    return translated_vertices


def tetra_triangles():
    """
    Return a list of triangles for each tetrahedron in the cube.
    Output is like: [[[0, 1, 2], [0, 1, 3], [0, 2, 3], [1, 2, 3]], ...]
    len(output) == 6  # number of tetrahedrons
    len(output[0]) == 4  # number of triangles in each tetra
    len(output[0][0]) == 3  # number of vertices in each triangle
    """
    return [[[tetrahedron[index] for index in face]
             for face in tetra_faces]
            for tetrahedron in cube_tetras]


def surface_from_tetra(vertices, values, threshold):
    """
    Returns a list of triangles for the iso-surface at level 'threshold'.
    Whatever is passed into vertices is interpolated, e.g. coordinates and/or normals.
    """
    outside = [index for index, val in enumerate(values) if val > threshold]
    inside = list(set(range(4)) - set(outside))

    if len(outside) in (0, 4):  # nothing to do, the iso-surface does not intersect the tetra
        return []

    def interp(i, j):
        t = (threshold - values[j]) / (values[i] - values[j])
        return t * vertices[i] + (1 - t) * vertices[j]

    if len(outside) in (1, 3):  # the iso-surface split vertexes in a 3/1 fashion, output a single triangle

        base_is_out = len(outside) == 3
        top_index = inside[0] if base_is_out else outside[0]
        base_indexes = tetra_faces[top_index] if base_is_out else tetra_faces[top_index][::-1]
        return [interp(top_index, base_index) for base_index in base_indexes]

    #  if here, count == 2. Split is 2/2, need to output two triangles

    indexes = tetra_faces[outside[0]]
    while indexes[1] != outside[1]:
        indexes = indexes[1:] + [indexes[0]]
    indexes = indexes + [outside[0]]

    quad = [interp(sidx, eidx) for sidx, eidx in zip(indexes, indexes[1:] + [indexes[0]])]
    return [quad[idx] for idx in (0, 2, 1, 0, 3, 2)]  # triangles


def surface_from_cube(vertices, potentials, threshold):
    """
    Returns a list of triangles for the iso-surface at level 'threshold'.
    """
    return [triangle
            for tetra in cube_tetras
            for triangle in surface_from_tetra(vertices[tetra], potentials[tetra], threshold)]

"""
face_lut = []
for configuration in range(256):
    inside_out = [configuration >> pow2 & 1 for pow2 in range(8)]
    faces = surface_from_tetra(inside_out)
    unique_faces, indexes = np.unique(faces, return_inverse=True)
    face_lut.append(unique_faces, indexes)
"""

# limits = ((-1, 1), (-1, 1), (-1, 1))  # np.finfo(float).eps
# # optimization: use arange and interval
# # optimization: lut for cube faces, return [edges_ij], [faces_ijk]
# # optimization: scale returned faces with origin + interval * faces
#
# bits = 5
# sampling = np.linspace(-1, 1, 2 ** bits + 1)
# xx, yy, zz = np.meshgrid(sampling, sampling, sampling)
#
# def gaussian_3d(mu, gamma):
#     xmmu = np.linalg.norm(np.stack([xx, yy, zz], axis=-1) - mu, axis=-1)  # x minus mu
#     return np.exp(-xmmu ** 2 / (2 * gamma ** 2)) / gamma * np.sqrt(2 * np.pi)
#
# displacement = np.sin(ua.time.time()) * 0.3
# potentials = gaussian_3d([-0.5, 0, 0], 0.4) + gaussian_3d([-0.2, 0.7, 0], 0.2) + gaussian_3d([0.5 + displacement, 0, 0], 0.3)
# threshold = 6
#
# indicator = potentials < threshold
# min_indicator = indicator[:, :, :-1] & indicator[:, :, 1:]
# min_indicator = min_indicator[:, :-1, :] & min_indicator[:, 1:, :]
# min_indicator = min_indicator[:-1, :, :] & min_indicator[1:, :, :]
# max_indicator = indicator[:, :, :-1] | indicator[:, :, 1:]
# max_indicator = max_indicator[:, :-1, :] | max_indicator[:, 1:, :]
# max_indicator = max_indicator[:-1, :, :] | max_indicator[1:, :, :]
# indicator = min_indicator ^ max_indicator
#
# tris = []
# for ix, iy, iz in zip(*np.where(indicator)):
#
#     coordinates = np.stack(list(ii[ix:ix + 2, iy:iy + 2, iz:iz + 2] for ii in (xx, yy, zz)), axis=-1)
#     coordinates = coordinates.reshape((-1, 3))
#     values_at_coords = potentials[ix:ix+2, iy:iy+2, iz:iz+2].reshape((-1,))
#     swizzle = [1, 5, 7, 3, 2, 6, 4, 0]
#     tris.extend(surface_from_cube(coordinates[swizzle], values_at_coords[swizzle], threshold))
#
# # normals = ...

# surface.model.vertices = tris
# surface.model.generate()
