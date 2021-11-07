class HierarchyMaker:
    def make_hierarchy(self, objects):
        objects = self._filter_objects(objects)

        for o in objects:
            if not o.parent:
                yield from self._sort_branch(o)

    def _sort_branch(self, first):
        children = self._filter_objects(first.children)
        yield first
        for child in children:
            yield from self._sort_branch(child)

    def _filter_objects(self, objects):
        for o in objects:
            is_mesh = (o.type == 'MESH')
            is_freespotlight = (o.type == 'LIGHT' and o.data.type == 'SPOT')

            is_stars_container = (o.type == 'EMPTY' and o.empty_display_type == "PLAIN_AXES")
            has_star_child = (any(c.type == "LIGHT" and c.data.type == "POINT" for c in o.children))
            is_stars = is_stars_container and has_star_child

            if is_mesh or is_freespotlight or is_stars:
                yield o