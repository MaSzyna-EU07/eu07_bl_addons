import bpy

def get_firstinit():
    text = bpy.data.texts.get("FirstInit")
    if text:
        return f"FirstInit\n\n{text.as_string()}"
    else:
        return "FirstInit\n\n"
