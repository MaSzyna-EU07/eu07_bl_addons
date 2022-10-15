import math
import os
import pathlib
import shutil
import subprocess

import bpy

import eu07_tools
from common import get_viewport_camera_location, get_viewport_camera_rotation
from material_tools.output.exporter import MaterialExporter

SCENERY_FILENAME = "_blender_preview.scn"
MODEL_FILENAME = "_blender_preview.t3d"
SUBDIR_NAME = "_blender_preview"
NODE_MODEL_NAME = "model_preview"


def make_preview_path(path):
    filename = pathlib.Path(path).name
    return str(pathlib.Path(SUBDIR_NAME, filename))

def transfer_material_assets(tex_subdir):
    shutil.rmtree(tex_subdir, ignore_errors=True)
    os.makedirs(tex_subdir, exist_ok=True)

    print(bpy.context.visible_objects)

    for obj in bpy.context.visible_objects:
        if not obj.active_material:
            continue

        eu07_material = obj.active_material.eu07_material

        for image in eu07_material.iter_image_textures():
            _transfer_texture(image, tex_subdir)

        if eu07_material.is_mat:
            exporter = MaterialExporter()
            mapping = exporter.matblock_to_mapping(eu07_material.mat_root)

            mapping = _rewrite_texture_paths(mapping, SUBDIR_NAME)
            outpath = pathlib.Path(tex_subdir) / pathlib.Path(eu07_material.mat_source_path).with_suffix(".mat").name

            with open(outpath, "w+", encoding="windows-1250", newline="\r\n") as of:
                eu07_tools.mat.dump(mapping, of)


def _rewrite_texture_paths(mapping, tex_subdir):
    for key, value in mapping.items():
        if key.startswith("texture"):
            texobj = value
            if texobj.use_set:
                mapping[key] = [make_preview_path(path) for path in texobj.set]
            else:
                mapping[key] = make_preview_path(texobj.path)

        if key in eu07_tools.mat.NESTED_MAPPING_KEYS:
            mapping[key] = _rewrite_texture_paths(value, tex_subdir)

    return mapping



def _transfer_texture(image, tex_subdir):
    texpath = pathlib.Path(bpy.path.abspath(image.filepath))
    dst = pathlib.Path(tex_subdir, texpath.name)

    print(f"Transfering: {texpath}\n --> {dst}")

    if image.packed_file:
        data = image.packed_file.data
        with open(dst, "wb+") as outimage:
            outimage.write(data)
    elif image.source == 'GENERATED':
        name = image.name.replace(".", "_")

        newimg = bpy.data.images.new(
            f"{name}_forpreview",
            width=image.size[0],
            height=image.size[1]
        )

        newimg.pixels = [pix for pix in image.pixels]
        newimg.filepath_raw = str(dst / f"{name}.tga")
        newimg.file_format = 'TARGA'
        newimg.save()

        bpy.data.images.remove(newimg)

    else:
        try:
            dst.symlink_to(texpath)
        except FileExistsError:
            pass

def create_camera_from_viewport():
    camera = eu07_tools.scn.create_element("camera")

    camera.location = eu07_tools.utils.swizzle_coords(get_viewport_camera_location())

    camera_rotation = get_viewport_camera_rotation()
    degrees = [math.degrees(x) for x in camera_rotation]
    swizzled = [
        degrees[1],
        degrees[2] + 90,
        degrees[0]
    ]

    camera.rotation = swizzled

    return camera


def run_preview_command(root, command):
    cwd = os.getcwd()
    os.chdir(root)

    args = [*command.split(" "), "-s", pathlib.Path(SUBDIR_NAME, SCENERY_FILENAME)]

    subprocess.Popen(args)

    os.chdir(cwd)

