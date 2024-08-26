import numpy as np


CHUNK_SIZE = 25
MAX_CHUNK_VERTICIES = 50_000


class ObjectHandler:
    def __init__(self, scene) -> None:
        # Reference to the scene
        self.scene = scene
        self.ctx   = scene.ctx
        self.vbos  = scene.vao_handler.vbo_handler.vbos
        self.program = scene.vao_handler.shader_handler.programs['batch']

        self.view_distance = 8

        # List containig all objects
        self.objects = []

        # Contain lists with objects positioned in a bounding box in space (Spatial partitioning)
        self.dynamic_chunks = {}
        self.static_chunks  = {}

        # ...
        self.dynamic_batches = {}
        self.static_batches  = {}

        self.update_chunks = set()

    def render(self):

        cam_position = self.scene.camera.position
        render_range_x = [int(cam_position.x // CHUNK_SIZE - self.view_distance), int(cam_position.x // CHUNK_SIZE + self.view_distance + 1)]
        render_range_y = [int(cam_position.y // CHUNK_SIZE - self.view_distance), int(cam_position.y // CHUNK_SIZE + self.view_distance + 1)]
        render_range_z = [int(cam_position.z // CHUNK_SIZE - self.view_distance), int(cam_position.z // CHUNK_SIZE + self.view_distance + 1)]

        if self.scene.camera.pitch > 25:
            render_range_y[0] += self.view_distance
        elif self.scene.camera.pitch < -25:
            render_range_y[1] -= self.view_distance

        fov = 40

        if 270 - fov < self.scene.camera.yaw < 270 + fov:
            render_range_z[1] -= self.view_distance
        elif 90 - fov < self.scene.camera.yaw < 90 + fov:
            render_range_z[0] += self.view_distance

        if 180 - fov < self.scene.camera.yaw < 180 + fov:
            render_range_x[1] -= self.view_distance
        elif -fov < self.scene.camera.yaw < fov or self.scene.camera.yaw > 360 - fov:
            render_range_x[0] += self.view_distance

        for x in range(*render_range_x):
            for y in range(*render_range_y):
                for z in range(*render_range_z):
                    chunk = (x, y, z)
                    if chunk in self.dynamic_batches:
                        self.dynamic_batches[chunk][1].render()
                    if chunk in self.static_batches:
                        self.static_batches[chunk][1].render()

    def update(self):
        if len(self.update_chunks):
            chunk = self.update_chunks.pop()
            if chunk[1]:
                self.batch_static_chunk(chunk[0])
            else:
                self.batch_dynamic_chunk(chunk[0])

    def batch_all(self):
        for chunk in self.static_chunks:
            self.batch_static_chunk(chunk)
        for chunk in self.dynamic_chunks:
            self.batch_dynamic_chunk(chunk)

    def batch_static_chunk(self, chunk_key: tuple):
        chunk = self.static_chunks[chunk_key]

        batch_data = []

        for object in chunk:
            vertex_data = np.copy(self.vbos[object.vbo].vertex_data)
            model_data = np.array([*object.position, *object.rotation, *object.scale, *object.texture])

            object_data = np.zeros(shape=(vertex_data.shape[0], 19), dtype='f4')

            object_data[:,:8] = vertex_data
            object_data[:,8:] = model_data

            batch_data.append(object_data)

        batch_data = np.vstack(batch_data)

        if chunk_key in self.static_batches:
            self.static_batches[chunk_key][0].release()
            self.static_batches[chunk_key][1].release()

        vbo = self.ctx.buffer(batch_data)
        vao = self.ctx.vertex_array(self.program, [(vbo, '3f 2f 3f 3f 3f 3f 2f', *['in_position', 'in_uv', 'in_normal', 'obj_position', 'obj_rotation', 'obj_scale', 'obj_texture'])], skip_errors=True)

        self.static_batches[chunk_key] = (vbo, vao)

    def batch_dynamic_chunk(self, chunk_key: tuple):
        chunk = self.dynamic_chunks[chunk_key]

        batch_data = np.zeros(shape=(MAX_CHUNK_VERTICIES, 19), dtype='f4')
        vertex_index = 0

        for object in chunk:
            vertex_data = self.vbos[object.vbo].vertex_data
            model_data = np.array([*object.position, *object.rotation, *object.scale, *object.texture])

            num_vertices = vertex_data.shape[0]

            if vertex_index+num_vertices > MAX_CHUNK_VERTICIES: break

            batch_data[vertex_index:vertex_index+num_vertices,:8] = vertex_data
            batch_data[vertex_index:vertex_index+num_vertices,8:] = model_data

            vertex_index += num_vertices


        if chunk_key not in self.dynamic_batches:
            vbo = self.ctx.buffer(reserve=((19 * 4) * MAX_CHUNK_VERTICIES))
            vao = self.ctx.vertex_array(self.program, [(vbo, '3f 2f 3f 3f 3f 3f 2f', *['in_position', 'in_uv', 'in_normal', 'obj_position', 'obj_rotation', 'obj_scale', 'obj_texture'])], skip_errors=True)
            self.dynamic_batches[chunk_key] = (vbo, vao)

        self.dynamic_batches[chunk_key][0].write(batch_data)

    def add(self, vbo, texture, position: tuple, rotation: tuple, scale: tuple, static: bool=True) -> None:
        """
        Add an object to the scene
        """

        # The key of the chunk the object will be added to
        chunk = (position[0] // CHUNK_SIZE, position[1] // CHUNK_SIZE, position[2] // CHUNK_SIZE)

        # Choose the correct dictionary for the chunk
        if static:
            chunk_dict = self.static_chunks
        else:
            chunk_dict = self.dynamic_chunks

        # Create empty list if the chunk does not already exist
        if chunk not in chunk_dict:
            chunk_dict[chunk] = []

        # Create a new object from the given parameters
        new_object = Object(vbo, texture, position, rotation, scale, static)

        # Add the object to the objects list and to its correct chunk list
        self.objects.append(new_object)
        chunk_dict[chunk].append(new_object)


class Object:
    def __init__(self, handler, vbo, texture, position: tuple, rotation: tuple, scale: tuple, static: bool=True) -> None:
        # Rendering specifications
        self.vbo     = vbo
        self.texture = texture
        self.handler = handler
        
        # Chunk that the object is in
        self.chunk = (position[0] // CHUNK_SIZE, position[1] // CHUNK_SIZE, position[2] // CHUNK_SIZE)

        # Model matrix vectors
        self.position = position
        self.rotation = rotation
        self.scale    = scale

        # Determines if the object can move
        self.static   = static

    def set_position(self, x, y, z):        
        self.position = x, y, z

        old_chunk = self.chunk
        self.chunk = (x // CHUNK_SIZE, y // CHUNK_SIZE, z // CHUNK_SIZE)

        self.handler.update_chunks.add((old_chunk, self.static))
        self.handler.update_chunks.add((self.chunk, self.static))

    def __repr__(self) -> str:
        return f'<Object: {self.position.x},{self.position.y},{self.position.z}>'