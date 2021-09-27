import bpy


def get_current_scm():
    if bpy.context.scene.scm_files:
        return bpy.context.scene.scm_files[bpy.context.scene.scm_file_index]

    return None


class SCMFile(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name="Name",
    )

    file_path: bpy.props.StringProperty(
        name="Path",
        subtype='FILE_PATH',
    )

    file_index: bpy.props.IntProperty(
        name="File index",
        min=0,
    )


class SCN_UL_SCMFiles(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = 'FILE_TEXT'

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=f"{item.name}", icon=custom_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon=custom_icon)


class LIST_OT_AddSCMFile(bpy.types.Operator):
    bl_idname = "scn.add_scm_file"
    bl_label = "Add new SCM layer to the list"

    def execute(self, context):
        added = context.scene.scm_files.add()
        added.file_index = context.scene.scm_file_index_counter

        context.scene.scm_file_index_counter += 1

        return {'FINISHED'}


class LIST_OT_DeleteSCMFile(bpy.types.Operator):
    bl_idname = "scn.delete_scm_file"
    bl_label = "Delete SCM layer from list"

    @classmethod
    def poll(cls, context):
        return context.scene.scm_files

    def execute(self, context):

        scm_files = context.scene.scm_files
        scm_file_index = context.scene.scm_file_index

        scm_files.remove(scm_file_index)
        context.scene.scm_file_index = min(max(0, scm_file_index - 1), len(scm_files) - 1)

        if not scm_files:
            context.scene.scm_file_index_counter = 0

        return {'FINISHED'}


class LIST_OT_AssignToSCMFile(bpy.types.Operator):
    bl_idname = "scn.assign_to_scm_file"
    bl_label = "Assign selected objects to this layer"

    @classmethod
    def poll(cls, context):
        return context.scene.scm_files

    def execute(self, context):
        current_scm = get_current_scm()
        current_scm_index = current_scm.file_index

        for obj in context.selected_objects:
            obj.scn_properties.scm_file_id = current_scm_index

        return {'FINISHED'}


class LIST_OT_SelectAssignedToSCM(bpy.types.Operator):
    bl_idname = "scn.select_assigned_to_scm"
    bl_label = "Select objects from this layer"

    @classmethod
    def poll(cls, context):
        return context.scene.scm_files

    def execute(self, context):
        current_scm_index = get_current_scm().file_index

        for obj in context.visible_objects:
            if obj.scn_properties.scm_file_id == current_scm_index:
                obj.select_set(True)

        return {'FINISHED'}


class SCN_PT_SCMFiles(bpy.types.Panel):
    bl_idname = "SCN_PT_scm_files"
    bl_label = "SCM Layers"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "[EU07] SCN Editor"

    def draw(self, context):
        list_row = self.layout.row()
        list_row.template_list("SCN_UL_SCMFiles", "", bpy.context.scene, "scm_files", bpy.context.scene, "scm_file_index")
        ops_row = self.layout.row()
        ops_row.operator("scn.add_scm_file", text="Add")
        ops_row.operator("scn.delete_scm_file", text="Remove")
        ops_row.operator("scn.assign_to_scm_file", text="Assign")
        ops_row.operator("scn.select_assigned_to_scm", text="Select")

        item = get_current_scm()

        name_row = self.layout.row()
        name_row.prop(item, "name")

        path_row = self.layout.row()
        path_row.prop(item, "file_path")