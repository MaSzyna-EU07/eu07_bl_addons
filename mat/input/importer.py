import bpy

import eu07_tools

from mat.nodegroup import NodeGroupWrapper, instantiate_mat_nodegroup


class MATImporter:
    def __init__(self, asset_searcher):
        self.use_fake_user = False
        self.asset_searcher = asset_searcher
        self.material = None

    def import_from_relpath(self, relpath):
        abspath = self.asset_searcher.textures.find(relpath)
        if abspath:
            return self.import_from_abspath(abspath)

        return None

    def import_from_abspath(self, abspath):
        with open(abspath, encoding="latin-1") as file:
            return self.import_from_file(file)

    def import_from_file(self, file):
        mapping = eu07_tools.mat.load(file)
        return self.import_from_mapping(mapping)

    def import_from_mapping(self, mapping):
        # TODO: Naming!
        self.material = bpy.data.materials.new("MAT TEST")
        self.material.use_backface_culling = True
        self.material.blend_method = 'CLIP'
        self.material.use_nodes = True
        self.material.use_fake_user = self.use_fake_user
        self._node_tree = self.material.node_tree

        for node in self.material.node_tree.nodes:
            self.material.node_tree.nodes.remove(node)

        nodegroup_wrapper = self._nodify_mapping(mapping)

        material_output = self.material.node_tree.nodes.new("ShaderNodeOutputMaterial")

        self.material.node_tree.links.new(nodegroup_wrapper.nodegroup.outputs[0], material_output.inputs[0])

    def _nodify_mapping(self, mapping):
        nodegroup = instantiate_mat_nodegroup(self._node_tree)
        wrapper = NodeGroupWrapper(nodegroup, self.material.node_tree)

        shader_params = []

        for key, value in mapping.items():

            if key == "shader":
                wrapper.set_shader_name(value)

            elif "param" in key:
                shader_params.append(
                    f"{key}:" + " ".join(str(v) for v in value)
                )

            elif "texture" in key:
                texture_object = value

                self.asset_searcher.textures.remove_extension(".mat")

                if texture_object.value_type == "TEXTURE_PATH":
                    texture_path = self.asset_searcher.textures.find(texture_object.path)
                    image = bpy.data.images.load(texture_path, check_existing=True)

                    texture_index = eu07_tools.mat.get_texture_index_from_key(key)
                    alias = eu07_tools.mat.get_alias_from_key(key)
                    wrapper.set_texture_image(image, texture_index, alias)

                elif texture_object.value_type == "TEXTURE_SET":
                    pass

                self.asset_searcher.textures.add_extension(".mat", priority=0)

            elif key == "opacity":
                wrapper.set_opacity(value)

            elif key == "selfillum":
                wrapper.set_selfillum(value)

            elif key == "size":
                wrapper.set_size(value)

            elif key == "shadow_rank":
                wrapper.set_shadow_rank(value)

            elif key in eu07_tools.mat.NESTED_MAPPING_KEYS:
                print("nested")
                nested_wrapper = self._nodify_mapping(value)
                wrapper.set_nested(key, nested_wrapper)

        shader_params_joined = ";".join(shader_params)
        wrapper.set_shader_params(shader_params_joined)

        return wrapper

