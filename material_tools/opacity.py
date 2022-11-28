def update_opacity(material, sm_opacity=1):
    mat_opacity = 0.5

    if sm_opacity == 1:
        material.blend_method = 'CLIP'
        material.clip_threshold = mat_opacity

    elif sm_opacity == 0:
        material.blend_method = 'BLEND'
        if mat_opacity < 1:
            material.blend_method = 'CLIP'
            material.clip_threshold = 1 - mat_opacity
