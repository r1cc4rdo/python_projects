import ursina as ua

vertex_shader = '''
#version 140
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelMatrix;
in vec4 p3d_Vertex;
in vec3 p3d_Normal;
out vec3 normal_direction;

void main()
{
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    normal_direction = mat3(p3d_ModelMatrix) * vec3(-p3d_Vertex.x, p3d_Vertex.y, -p3d_Vertex.z);
}
'''

fragment_shader = '''
#version 140
in vec3 normal_direction;
out vec4 fragColor;

void main()
{
    fragColor = vec4(normalize(normal_direction) * 0.5 + 0.5, 1);
}
'''

cool_normals = ua.Shader(language=ua.Shader.GLSL, vertex=vertex_shader, fragment=fragment_shader)  # cold colors
