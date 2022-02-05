import bpy
from common.utils import uilist_safe_index_after_delete

#TODO: Nested includes


MASTER_IDENTIFIER = -1


def get_active_include():
    scene = bpy.context.scene

    if scene.eu07_includes:
        return scene.eu07_includes[scene.eu07_active_include_index]

    return None


def get_include_by_identifier(identifier):
    for include in bpy.context.scene.eu07_includes:
        if include.identifier == identifier:
            return include


def get_include_index(include):
    scene = bpy.context.scene
    for i, include_candidate in enumerate(scene.eu07_includes):
        if include_candidate.identifier == include.identifier:
            return i

    return -1


def add_include():
    if not bpy.context.scene.eu07_includes:
        bpy.context.scene.eu07_include_identifier_counter = 0

    added = bpy.context.scene.eu07_includes.add()
    added.identifier = bpy.context.scene.eu07_include_identifier_counter
    bpy.context.scene.eu07_active_include_index = get_include_index(added)

    bpy.context.scene.eu07_include_identifier_counter += 1

    return added


def delete_include(include):
    scene = bpy.context.scene
    include_index = get_include_index(include)
    if include_index != MASTER_IDENTIFIER:
        scene.eu07_includes.remove(include_index)

    scene.eu07_active_include_index = uilist_safe_index_after_delete(scene.eu07_includes, include_index)

    for obj in bpy.data.objects:
        if obj.eu07_include_identifier == get_include_index(include):
            obj.eu07_include_identifier = MASTER_IDENTIFIER


def assign_to_include(obj, include):
    scene = bpy.context.scene
    obj.eu07_include_identifier = include.identifier


def unassign_from_include(obj):
    obj.eu07_include_identifier = MASTER_IDENTIFIER


def iter_included_objects(include):
    for obj in bpy.data.objects:
        if obj.eu07_include_identifier == get_include_index(include):
            yield obj


class EU07Include(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name="Name",
    )

    file_path: bpy.props.StringProperty(
        name="Path",
        description="Path to included file, relative to main file",
    )

    # Default is false, because it's more idiot-proof: it minimizes risk of overwriting includes (like Turbokibel did)
    is_exportable: bpy.props.BoolProperty(
        name="Exportable",
        description="When enabled, objects assigned to this include will export to file at given path",
        default=False
    )

    identifier: bpy.props.IntProperty(min=0)


class EU07_UL_Includes(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = 'FILE_TICK'

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=f"{item.name}", icon=custom_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon=custom_icon)


class EU07_PT_Includes(bpy.types.Panel):
    bl_idname = "EU07_PT_Includes"
    bl_label = "Includes"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "[EU07] Developer Tools"

    def draw(self, context):
        item = get_active_include()

        list_row = self.layout.row()
        list_row.template_list(
            "EU07_UL_Includes", "",
            bpy.context.scene, "eu07_includes",
            bpy.context.scene, "eu07_active_include_index"
        )
        addrem_col = list_row.column()
        addrem_col.operator("eu07.add_include", icon="ADD", text="")
        addrem_col.operator("eu07.delete_include", icon="REMOVE", text="")

        ops_row = self.layout.row()
        assign_op = ops_row.operator("eu07.assign_to_include", text="Assign")

        ops_row.operator("eu07.unassign_from_include", text="Unassign")
        ops_row.operator("eu07.select_included", text="Select")

        if item:
            name_row = self.layout.row()
            name_row.prop(item, "name")

            path_row = self.layout.row()
            path_row.prop(item, "file_path")

            exportable_row = self.layout.row()
            exportable_row.prop(item, "is_exportable")


class EU07_OT_AddInclude(bpy.types.Operator):
    bl_idname = "eu07.add_include"
    bl_label = "Add new Include to the list"

    def execute(self, context):
        add_include()

        return {'FINISHED'}


class EU07_OT_DeleteInclude(bpy.types.Operator):
    bl_idname = "eu07.delete_include"
    bl_label = "Delete Include from list"

    @classmethod
    def poll(cls, context):
        return context.scene.eu07_includes

    def execute(self, context):
        delete_include(get_active_include())

        return {'FINISHED'}


class EU07_OT_AssignToInclude(bpy.types.Operator):
    bl_idname = "eu07.assign_to_include"
    bl_label = "Assign selected objects to Include"

    @classmethod
    def poll(cls, context):
        return context.scene.eu07_includes

    def execute(self, context):
        include = get_active_include()

        for obj in context.selected_objects:
            assign_to_include(obj, include)

        return {'FINISHED'}


class EU07_OT_UnassignFromInclude(bpy.types.Operator):
    bl_idname = "eu07.unassign_from_include"
    bl_label = "Unassign object from this include"

    @classmethod
    def poll(cls, context):
        return context.scene.eu07_includes

    def execute(self, context):
        for obj in context.selected_objects:
            unassign_from_include(obj)

        return {'FINISHED'}


class EU07_OT_SelectIncluded(bpy.types.Operator):
    bl_idname = "eu07.select_included"
    bl_label = "Select objects assigned to Include"

    @classmethod
    def poll(cls, context):
        return context.scene.eu07_includes

    def execute(self, context):
        include = get_active_include()

        for obj in context.visible_objects:
            if obj.eu07_include_identifier == get_include_index(include):
                obj.select_set(True)

        return {'FINISHED'}


classes = (
    EU07Include,
    EU07_UL_Includes,
    EU07_PT_Includes,
    EU07_OT_AddInclude,
    EU07_OT_DeleteInclude,
    EU07_OT_AssignToInclude,
    EU07_OT_UnassignFromInclude,
    EU07_OT_SelectIncluded
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

        bpy.types.Scene.eu07_includes = bpy.props.CollectionProperty(type=EU07Include)
        bpy.types.Scene.eu07_active_include_index = bpy.props.IntProperty(min=0)
        bpy.types.Scene.eu07_include_identifier_counter = bpy.props.IntProperty(min=0)
        bpy.types.Object.eu07_include_identifier = bpy.props.IntProperty(min=-1, default=-1)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)