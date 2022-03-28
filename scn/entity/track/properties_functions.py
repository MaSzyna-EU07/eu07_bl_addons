
# TODO: Create validators for entities to avoid long if if if
def get_length(self):
    obj = bpy.context.object
    if obj.type != 'CURVE' and obj.data.type != 'BEZIER':
        return 0



