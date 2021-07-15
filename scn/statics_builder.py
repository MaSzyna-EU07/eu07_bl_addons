import eu07_tools
import bpy

class StaticsBuilder:
    def __init__(self, config):
        self.config = config

    def load_static(self, static):
        if static.typename == "include":
            pass

        if static.typename == "node:model":
            self.load_model(static)

    def load_model(self, model):
        path = self.config["asset_searcher"].models.find(model.path)
        if path:
            pass


