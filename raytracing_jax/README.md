# Raytracing with Python and JAX
This project follows the [Raytracing in a weekend book 1](https://raytracing.github.io).

I am using this to teach myself JAX fundamentals, explore JAX promise of transparent
acceleration and parallelization, and discover the inevitable pitfalls that are sure
to arise from having a recursive function calls.

## Chapters
Each link here leads to the state of the repository after completing the relevant chapter. 
- [Chapters 1--3](https://github.com/r1cc4rdo/raytracing_jax/tree/c59ad262270d9e350713690bc22ff0bbd06b0381)
  - Instead of writing .PPM as output, we leverage the matplotlib library both for showing and saving the resulting image to disk.
  - We do not loop explicitly over all pixels, preferring to directly compose the final image.
  - We forego explicit creation of a vector class, since Numpy-like arrays already have equivalent APIs.
- [Chapter 4](https://github.com/r1cc4rdo/raytracing_jax/tree/272bc28a83c198d45b6d7f45ee5d317ab9a911ae)
  - Instead of creating a class, a ray for us is a 2x3 matrix where ray\[0, :\] is the origin, and ray\[1, :\] is the direction.
  - Instead of using loop, we generate all camera rays at once in the function screen_rays, and apply the cast function to all of them using JAX vmap.
- [Chapter 5--6](https://github.com/r1cc4rdo/raytracing_jax/tree/164c392dd77072dcbf9698bad350392e022e645e)
  - JAX is not well suited to branched computations. This was expected. In order to implement chapters 5 and 6, I had to resort to use LAX primitives. Given this understanding, I'll stop trying to use JAX for something it's not naturally suited for, **and abandon the project**.
  - Because of the above, the closest depth selection is specialized for the specific two sphere case.
