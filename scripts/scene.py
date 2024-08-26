import pygame as pg
from scripts.camera import Camera
from scripts.object_handler import ObjectHandler
import random


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
        self.object_handler = ObjectHandler(self)

        spacing = 6

        for x in range(0, 10):
            for y in range(0, 10):
                for z in range(0, 10):
                    self.object_handler.add('cow', [0, 2], (x * spacing, y * spacing, z * spacing), (0, 0, 0), (1, 1, 1), static=True)

        self.selected_object = self.object_handler.objects[0]

        self.object_handler.batch_all()

    def use(self):
        """
        Updates project handlers to use this scene
        """

        self.vao_handler.shader_handler.set_camera(self.camera)
        self.camera.use()
        self.vao_handler.shader_handler.write_all_uniforms()
        self.project.texture_handler.write_textures()
        self.project.texture_handler.write_textures('batch')

    def update(self):
        """
        Updates uniforms, and camera
        """
        
        self.vao_handler.shader_handler.update_uniforms()
        pos = self.selected_object.position
        self.selected_object.set_position(pos[0] - self.engine.dt, )
        self.object_handler.update()
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