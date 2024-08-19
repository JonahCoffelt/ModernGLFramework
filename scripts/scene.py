import pygame as pg
from scripts.camera import Camera
from scripts.object_handler import ObjectHandler

class Scene:
    def __init__(self, engine, project) -> None:
        """
        Contains all data for scene
        """

        # Stores the engine, project, and ctx
        self.engine = engine
        self.project = project
        self.ctx = self.engine.ctx

        # Makes a free cam
        self.camera = Camera(self.engine)

        # Gets handlers from parent project
        self.vao_handler = self.project.vao_handler
        # Object handler
        self.object_handler = ObjectHandler(self.project)

        self.object_handler.add(self.vao_handler.vaos['cube'], 'box', (0, 0, 0), (0, 0, 0), (1, 1, 2))
        self.object_handler.add(self.vao_handler.vaos['cube'], 'container', (4, 0, 0), (0, 0, 0), (1, 2, 1))
        self.object_handler.add(self.vao_handler.vaos['cube'], 'metal', (-4, 0, 0), (0, 0, 0), (2, 1, 1))

        self.object_handler.add(self.vao_handler.vaos['cow'], 'cow', (4, 4, 4), (0, 0, 0), (1, 1, 1))

        self.object_handler.add(self.vao_handler.vaos['lucy'], 'cow', (-8, 4, 4), (-1.5, 0, 3.14), (.01, .01, .01))

    def use(self):
        """
        Updates project handlers to use this scene
        """

        self.vao_handler.shader_handler.set_camera(self.camera)
        self.camera.use()
        self.vao_handler.shader_handler.write_all_uniforms()
        self.project.texture_handler.write_textures()

    def update(self):
        """
        Updates uniforms, and camera
        """
        
        self.vao_handler.shader_handler.update_uniforms()
        self.camera.update()

    def render(self):
        """
        Redners all instances
        """

        self.ctx.screen.use()
        self.object_handler.render()

    def release(self):
        """
        Releases scene's VAOs
        """

        self.vao_handler.release()