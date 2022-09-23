import math
import os
import pathlib
import shutil
import subprocess

import bpy

import eu07_tools
from common import get_viewport_camera_location, get_viewport_camera_rotation

SCENERY_FILENAME = "_blender_preview.scn"
MODEL_FILENAME = "_blender_preview.t3d"
SUBDIR_NAME = "_blender_preview"
NODE_MODEL_NAME = "model_preview"


def transfer_external_textures(tex_subdir):
    shutil.rmtree(tex_subdir, ignore_errors=True)
    os.makedirs(tex_subdir, exist_ok=True)

    for obj in bpy.context.visible_objects:
        if not obj.active_material:
            break

        # TODO: .mat support

        diffuse = obj.active_material.eu07_material.get_

        if not diffuse:
            break

        diffuse_filepath = pathlib.Path(bpy.path.abspath(diffuse.filepath))
        dst = pathlib.Path(tex_subdir, diffuse_filepath.name)

        print(f"Symlink: {diffuse_filepath}\n Destination: {dst}")

        if diffuse.packed_file:
            data = diffuse.packed_file.data
            with open(dst, "wb+") as outimage:
                outimage.write(data)
        elif diffuse.source == 'GENERATED':
            name = diffuse.name.replace(".", "_")
            # TODO: Make it happen xD
            #
            # newimg = bpy.data.images.new(
            #     f"{name}_forpreview",
            #     width=diffuse.generated_width,
            #     height=diffuse.generated_height
            # )
            #
            # newimg.pixels = diffuse.pixels
            # newimg.filepath_raw = str(dst / f"{name}.tga")
            # newimg.file_format = 'TARGA'
            # newimg.save()
            #
            # bpy.data.images.remove(newimg)

        else:
            try:
                dst.symlink_to(diffuse_filepath)
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

