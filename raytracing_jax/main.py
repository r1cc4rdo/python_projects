from matplotlib import pyplot as plot
from jax import jit, vmap, lax
import jax.numpy as jnp


def screen_rays(width, aspect=16/9):
    height = jnp.round(width / aspect).astype(int)
    xs, ys = jnp.meshgrid(jnp.linspace(-aspect, aspect, width), jnp.linspace(1, -1, height))
    origins = jnp.zeros((height, width, 3))
    directions = jnp.stack([xs, ys, -jnp.ones_like(xs)], axis=-1)
    return jnp.stack((origins, directions), axis=2)  # (U, V, [origin, direction], [X, Y, Z])


def ray_sphere_intersection(center, radius, ray):
    origin, direction = ray
    oc = origin - center
    a = jnp.dot(direction, direction)
    hb = jnp.dot(oc, direction)
    c = jnp.dot(oc, oc) - radius ** 2
    discriminant = hb ** 2 - a * c
    return lax.cond(discriminant >= 0, lambda: (-hb - jnp.sqrt(discriminant)) / a, lambda: -1.)


@jit
@vmap
def cast(ray):
    center_a, center_b = jnp.array([0, 0, -1]), jnp.array([0, -100.5, -1])
    intersection_a = ray_sphere_intersection(center_a, 0.5, ray)
    intersection_b = ray_sphere_intersection(center_b, 100, ray)

    def sphere_color(intersection, center):
        origin, direction = ray
        normal = (origin + intersection * direction) - center
        normal = normal / jnp.linalg.norm(normal)
        return 0.5 * (normal + 1)

    def bg_color():
        _, direction = ray
        direction /= jnp.linalg.norm(direction)
        t = 0.5 * (direction[1] + 1)
        return (1 - t) * jnp.array([1, 1, 1]) + t * jnp.array([0.5, 0.7, 1.0])

    conditional = lax.cond(intersection_b > 0, lambda: sphere_color(intersection_b, center_b), bg_color)
    return lax.cond(intersection_a > 0, lambda: sphere_color(intersection_a, center_a), lambda: conditional)


def plot_image(image, save_as=None, display=True, dpi=32):
    figure = plot.figure(frameon=False)
    figure.set_size_inches(jnp.array(image.shape[1::-1]) / dpi)
    plot.imshow(image)
    plot.axis("off")
    if save_as:
        plot.savefig(save_as, dpi=dpi)
    if display:
        plot.show()
    plot.close()


if __name__ == "__main__":
    width = 400
    rays = jnp.reshape(screen_rays(width), (-1, 2, 3))
    image = jnp.reshape(cast(rays), (-1, width, 3))
    plot_image(image, 'chapter4.png')
