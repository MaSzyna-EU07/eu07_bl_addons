import bpy



class SectionTextBuffer(bpy.types.PropertyGroup):
    text: bpy.props.PointerProperty(
        type=bpy.types.Text,
    )



class Section(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        
    )

    id: bpy.props.FloatVectorProperty(
        size=2,
        default=[0, 0],
    )

    collection: bpy.props.PointerProperty(
        type=bpy.types.Collection,
    )

    text_buffer: bpy.props.PointerProperty(
        type=SectionTextBuffer,
    )

    def init(self, ids):
        self.collection = bpy.data.collections.new(self.name)
        self.text_buffer = bpy.data.texts.new(self.name)
        self.name = f"Section x{ids[0]} y{ids[1]}"
        self.id = ids

    def show(self):
        bpy.context.scene.collection.children.link(self.collection)

    def hide(self):
        bpy.context.scene.collection.children.unlink(self.collection)

    def insert(self, obj):
        # TODO: un-insert from previous section
        self.collection.objects.link(obj)



class SectionsManager(bpy.types.PropertyGroup):
    SECTION_SIZE = 1000

    sections: bpy.props.CollectionProperty(
        type=Section,
    )

def get_sections_in_range(self, center_point, radius):
    pass

def get_section_by_id(self, ids):
    for section in self.sections:
        if section.id == ids:
            return section

def get_section_by_location(self, location):
    ids = self.specify_section_id(location)
    return self.get_section_by_id(ids)

def show_sections(self, sections):
    for section in sections:
        section.show()

def hide_sections(self, sections):
    for section in sections:
        section.hide()

def create_section(self, id):
    section = self.sections.add()
    section.init(id)

    return section

def specify_section_id(self, location):
    ids = [0, 0]
    for i in range(2):
        coord = abs(location[i])
        if coord != 0:
            coord_sign = coord / location[i]
        else:
            coord_sign = 1

        if coord >= self.SECTION_SIZE:
            ids[i] = int(coord // self.SECTION_SIZE * coord_sign)
        else:
            ids[i] = int(round(coord / self.SECTION_SIZE) * coord_sign)

    return ids
