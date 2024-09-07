import pygame as pg
import numpy as np
import glm
from PIL import Image
from scripts.camera import Camera
from scripts.object_handler import ObjectHandler
from scripts.transform_handler import TransformHander
from scripts.render.light_handler import LightHandler
from random import uniform, randrange


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

        # Creates scene-specific handlers
        self.object_handler = ObjectHandler(self)
        self.transform_handler = TransformHander(self)
        self.light_handler = LightHandler(self)

        spacing = 6
        n = 10

        models = ['cube', 'cow']
        textures = ['box', 'container', 'metal', 'cow']

        for x in range(-n, n):
            for y in range(-n, n):
                for z in range(-n, n):
                    self.object_handler.add(models[randrange(2)], textures[randrange(4)], (x * spacing, y * spacing, z * spacing), (uniform(0, 6.3), uniform(0, 6.3), uniform(0, 6.3)), (1, 1, 1))

        self.selected_object = self.object_handler.add("cow", "box")

    def use(self):
        """
        Updates project handlers to use this scene
        """

        self.vao_handler.shader_handler.set_camera(self.camera)
        self.camera.use()
        self.vao_handler.generate_framebuffer()
        self.vao_handler.shader_handler.write_all_uniforms()
        self.project.texture_handler.write_textures()
        self.project.texture_handler.write_textures('batch')
        self.light_handler.write('batch')

    def update(self):
        """
        Updates uniforms, and camera
        """
                
        self.object_handler.update()
        self.vao_handler.shader_handler.update_uniforms()
        self.camera.update()


    def render(self):
        """
        Redners all instances
        """

        self.vao_handler.framebuffer.clear(color=(0.08, 0.16, 0.18, 1.0))
        self.vao_handler.framebuffer.use()
        self.object_handler.render()
        self.ctx.screen.use()
        self.vao_handler.shader_handler.programs['frame']['screenTexture'] = 0
        self.vao_handler.frame_texture.use(location=0)
        self.vao_handler.vaos['frame'].render()

    def release(self):
        """
        Releases scene's VAOs
        """

        self.vao_handler.release()