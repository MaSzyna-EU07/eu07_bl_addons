class HierarchyMaker:
    # TODO: This class isn't making hierarchy anymore, so should be called like ObjectFilter?

    def make_hierarchy(self, objects):
        objects = list(self._filter_objects(objects))

        full_hierarchy = list(self.iter_default_hierarchy(objects))

        print(full_hierarchy)
        print("that was full, now selected")
        print(list(objects))

        for o in full_hierarchy:
            if o in objects:
                yield o

    def iter_default_hierarchy(self, objects):
        for obj in objects:
            if obj.parent not in objects:
                yield obj
                for child in obj.children_recursive:
                    yield child

    def _filter_objects(self, objects):
        for o in objects:
            is_mesh = (o.type == 'MESH')
            is_freespotlight = (o.type == 'LIGHT' and o.data.type == 'SPOT')

            is_stars_container = (o.type == 'EMPTY' and o.empty_display_type == "PLAIN_AXES")
            has_star_child = (any(c.type == "LIGHT" and c.data.type == "POINT" for c in o.children))
            is_stars = is_stars_container and has_star_child
            is_banan = o.type == 'EMPTY' and o.empty_display_type != 'IMAGE' and not has_star_child

            if is_mesh or is_freespotlight or is_stars or is_banan:
                yield o