from zocalo.wrapper import BaseWrapper
import os
import procrunner
import logging
from pathlib import Path
from shutil import copyfile

logger = logging.getLogger("DawnWrapper")


class JupyterWrapper(BaseWrapper):
    """
    A zocalo wrapper for jupyter headless processing

    Copies notebook to run directory, injects filenames,
    and runs in place, before making html copy as log

    """

    run_script = "/dls_sw/apps/wrapper-scripts/jupyter_autoprocessing.sh"
    param_prefix = "jupyter_"
    notebook = "notebook"
    module = "module"
    payload_key = "target_file"
    default_module = "python/3"

    def run(self):
        assert hasattr(self, "recwrap"), "No recipewrapper object found"

        payload = self.recwrap.payload
        target_file = payload[JupyterWrapper.payload_key]

        jp = self.recwrap.recipe_step["job_parameters"]

        ispyb_params = jp["ispyb_parameters"]
        ispyb_rd = jp["result_directory"]
        override_path = jp["override_path"]

        # determine run_directory
        rd = self._get_run_directory(ispyb_rd, override_path)
        notebook, result_path = self._copy_notebook(ispyb_params, target_file, rd)

        mod_key = JupyterWrapper.param_prefix + JupyterWrapper.module
        mod = ispyb_params.get(mod_key, JupyterWrapper.default_module)

        html_log = str(Path(notebook).with_suffix(".html"))

        command = [JupyterWrapper.run_script]
        command.append(mod)
        command.append(target_file)
        command.append(result_path)
        command.append(notebook)
        logger.info("Command: %s", " ".join(command))
        result = procrunner.run(command)
        logger.info("Command successful, took %.1f seconds", result["runtime"])

        self._record_result(result_path, "Result")
        self._record_result(notebook, "Result")
        self._record_result(html_log, "Log")
        self._broadcast_primary_result(result_path, not result["exitcode"])

        return not result["exitcode"]

    def _broadcast_primary_result(self, result_path, success):
        if not success or not os.path.isfile(result_path):
            return

        if getattr(self, "recwrap", None):
            self.recwrap.send_to(
                "result-primary", {JupyterWrapper.payload_key: result_path}
            )

    def _record_result(self, path, file_type):
        if os.path.isfile(path):
            p, f = os.path.split(path)
            self.record_result_individual_file(
                {"file_path": p, "file_name": f, "file_type": file_type}
            )
        else:
            logger.warning("No file found at %s", path)

    def _copy_notebook(self, params, target, rd):
        note_key = JupyterWrapper.param_prefix + JupyterWrapper.notebook
        if note_key not in params:
            raise RuntimeError("No notebook parameter registered")

        note_path = params[note_key]
        if not os.path.isfile(note_path):
            raise RuntimeError("Notebook does not exist: %s" % note_path)

        name = Path(target).stem + "_" + Path(note_path).name
        note_dir = rd + "/notebooks/"
        Path(note_dir).mkdir(parents=True, exist_ok=True)
        fullpath = note_dir + name
        copyfile(note_path, fullpath)

        nxspath = rd + "/" + Path(name).stem + ".nxs"
        return fullpath, nxspath

    def _get_run_directory(self, ispyb_rd, override):

        if not override.startswith("{") and os.path.exists(override):
            return override

        return ispyb_rd
