from .operator import EU07_OT_GameEnginePreviewScenery


def draw(self, context):
    self.layout.operator(EU07_OT_GameEnginePreviewScenery.bl_idname, icon="PLAY", text="Run Preview")

    settings = context.scene.eu07_scenery_preview

    self.layout.prop(settings, "executable_command")