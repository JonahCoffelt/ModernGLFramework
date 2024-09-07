from scripts.generic.data_types import vec3


CHUNK_SIZE = 40


class Object:
    def __init__(self, handler, vbo, texture, position: tuple, rotation: tuple, scale: tuple) -> None:
        # Rendering specifications
        self.__handler = handler
        self.vbo     = vbo
        self.texture = texture

        # Chunk that the object is in
        self.chunk = (position[0] // CHUNK_SIZE, position[1] // CHUNK_SIZE, position[2] // CHUNK_SIZE)
        self.prev_chunk = self.chunk
        
        # Variables for detecting attribute changes
        self.__prev_position = [0, 0, 0]
        self.__prev_rotation = [0, 0, 0]
        self.__prev_scale    = [1, 1, 1]

        # Model matrix vectors
        self.position = vec3(position, self.update_position)
        self.rotation = vec3(rotation, self.update_rotation)
        self.scale    = vec3(scale   , self.update_scale)  

    # Sets each of the editable object attributes as properties
    @property
    def position(self): return self._position
    @property
    def rotation(self): return self._rotation
    @property
    def scale(self): return self._scale
    @property
    def x(self): return self.position.x
    @property
    def y(self): return self.position.y
    @property
    def z(self): return self.position.z

    # Defines setters at the attribute level
    @position.setter
    def position(self, value):
        self._position = value
        self.update_position()
    @rotation.setter
    def rotation(self, value):
        self._rotation = value
        self.update_rotation()
    @scale.setter
    def scale(self, value):
        self._scale = value
        self.update_scale()
    @x.setter
    def x(self, value): self.position.x = value
    @y.setter
    def y(self, value): self.position.y = value
    @z.setter
    def z(self, value): self.position.z = value

    def update_position(self):
        """
        Checks if the object has moved enough to update the chunk mesh
        """
        
        self.chunk = (self.x // CHUNK_SIZE, self.y // CHUNK_SIZE, self.z // CHUNK_SIZE)

        if abs(self.__prev_position[0] - self.position[0]) < 0.001 and abs(self.__prev_position[1] - self.position[1]) < 0.001 and abs(self.__prev_position[2] - self.position[2]) < 0.001: return False   

        if self.prev_chunk != self.chunk:
            if self.chunk not in self.__handler.chunks:
                self.__handler.chunks[self.chunk] = []
            
            self.__handler.chunks[self.chunk].append(self)
            self.__handler.chunks[self.prev_chunk].remove(self)

        self.__handler.updated_chunks.add(self.prev_chunk)
        self.__handler.updated_chunks.add(self.chunk)

        self.prev_chunk = self.chunk
        self.__prev_position = self.position[:]

    def update_scale(self):
        """
        Checks if the object has been scaled enough to update the chunk mesh
        """

        if abs(self.__prev_scale[0] - self.scale.x) < 0.001 and abs(self.__prev_scale[1] - self.scale.y) < 0.001 and abs(self.__prev_scale[2] - self.scale.z) < 0.001: return False  
        
        self.__handler.updated_chunks.add(self.chunk)

        self.__prev_scale = self.scale[:]

    def update_rotation(self):
        """
        Checks if the object has been rotated enough to update the chunk mesh
        """

        if abs(self.__prev_rotation[0] - self.rotation.x) < 0.001 and abs(self.__prev_rotation[1] - self.rotation.y) < 0.001 and abs(self.__prev_rotation[2] - self.rotation.z) < 0.001: return False  
        
        self.__handler.updated_chunks.add(self.chunk)

        self.__prev_rotation = self.rotation[:]

    def __repr__(self) -> str:
        return f'<Object: {self.position[0]},{self.position[1]},{self.position[2]}>'