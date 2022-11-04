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


def make_preview_path(tpo):
    filename = pathlib.Path(tpo.path).name
    return str(pathlib.Path(SUBDIR_NAME, filename)) + tpo.traits_suffix

def transfer_material_assets(tex_subdir):
    shutil.rmtree(tex_subdir, ignore_errors=True)
    os.makedirs(tex_subdir, exist_ok=True)

    for obj in bpy.context.visible_objects:
        if not obj.active_material:
            continue

        eu07_material = obj.active_material.eu07_material

        for image in eu07_material.iter_image_textures():
            _transfer_texture(image, tex_subdir)

        if eu07_material.is_mat:
            exporter = MaterialExporter()
            outmat = exporter.matblock_to_outmat(eu07_material.mat_root)

            outmat = _rewrite_texture_paths(outmat, SUBDIR_NAME)
            outpath = pathlib.Path(tex_subdir) / pathlib.Path(eu07_material.mat_source_path).with_suffix(".mat").name

            with open(outpath, "w+", encoding="windows-1250", newline="\r\n") as of:
                eu07_tools.mat.dump(outmat, of)


def _rewrite_texture_paths(mat, tex_subdir):
    for tex_key, tex_list in mat.iter_texture_lists():
        if len(tex_list) == 1:
            mat.set_texture_path(tex_key, make_preview_path(tex_list[0]))
        else:
            mat.set_textureset(tex_key, [make_preview_path(tpo) for tpo in tex_list])

    for variant_key, variant_mat in mat.iter_variants():
        mat.set_variant(
            variant_key,
            _rewrite_texture_paths(variant_mat, tex_subdir)
        )

    return mat


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

