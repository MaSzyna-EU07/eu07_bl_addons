from .operator import EU07_OT_GameEnginePreviewModel

def draw(self, context):
    self.layout.operator(EU07_OT_GameEnginePreviewModel.bl_idname, icon="PLAY", text="Run Preview")

    settings = context.scene.eu07_model_preview

    self.layout.prop(settings, "executable_command")
    lightbox = self.layout.box()
    lightbox.label(text="Lights")
    lightbox.prop(settings, "lights", text="States")
    lightbox.prop(settings, "lightcolors", text="Colors")
    lightbox.prop(settings, "transition")
    self.layout.prop(settings, "angles")
    self.layout.prop(settings, "use_ground")
    self.layout.prop(settings, "use_track")
