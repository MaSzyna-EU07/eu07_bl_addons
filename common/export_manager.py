import pathlib

import io
from common import includes
from common import utils


class ExportManager:
    def __init__(self, includes_list, aggregate_includes=False):
        self._buffers = dict()
        self._outputs = dict()
        self._includes_list = includes_list
        self.aggregate_includes = aggregate_includes

    def create_buffers(self):
        self._buffers[includes.MASTER_IDENTIFIER] = io.StringIO()

        if not self.aggregate_includes:
            for include in self._includes_list:
                if include.is_exportable:
                    self._buffers[include.identifier] = io.StringIO()

    def create_outputs(self, output_cls):
        self._outputs[includes.MASTER_IDENTIFIER] = output_cls(self._buffers[includes.MASTER_IDENTIFIER])

        if not self.aggregate_includes:
            for identifier, buffer in self._buffers.items():
                self._outputs[identifier] = output_cls(buffer)

    def flush_buffers_to_files(self, root, main_filepath):
        root = pathlib.Path(root)

        for identifier, buffer in self._buffers.items():
            if identifier == includes.MASTER_IDENTIFIER:
                out_path = main_filepath
            else:
                include = self._includes_list[identifier]

                out_path = root / include.file_path
                out_dir = out_path.parent
                out_dir.mkdir(parents=True, exist_ok=True)

            with open(out_path, mode="w+", encoding="windows-1250", newline="\r\n") as out_file:
                out_file.write(buffer.getvalue())

    def get_buffer(self, identifier):
        return self._buffers.get(identifier)

    def get_output(self, identifier):
        return self._outputs.get(identifier)

    @property
    def master_buffer(self):
        return self.get_buffer(includes.MASTER_IDENTIFIER)

    @property
    def master_output(self):
        return self.get_output(includes.MASTER_IDENTIFIER)

    @property
    def buffers(self):
        return self._buffers.values()

    @property
    def outputs(self):
        return self._outputs.values()





