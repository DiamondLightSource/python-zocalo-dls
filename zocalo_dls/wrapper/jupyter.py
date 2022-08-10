from zocalo.wrapper import BaseWrapper
import os
import procrunner
import logging
from pathlib import Path
from shutil import copyfile
import nbformat

logger = logging.getLogger("zocalo_dls.wrapper.jupyter")


class JupyterWrapper(BaseWrapper):
    """
    A zocalo wrapper for jupyter headless processing

    Copies notebook to run directory, injects filenames,
    and runs in place, before making html copy as log

    """

    run_script = "/dls_sw/apps/wrapper-scripts/execute_notebook.sh"
    param_prefix = "jupyter_"
    notebook = "notebook"
    module = "module"
    payload_key = "target_file"
    default_module = "python/3"

    def run(self):
        assert hasattr(self, "recwrap"), "No recipewrapper object found"

        payload = self.recwrap.payload
        jp = self.recwrap.recipe_step["job_parameters"]
        target_file = self._get_target_file(payload, jp)

        ispyb_params = jp["ispyb_parameters"].copy()
        ispyb_rd = jp["result_directory"]
        override_path = jp["override_path"]

        prefix = self._get_prefix(jp)

        rd = self._get_run_directory(ispyb_rd, override_path)

        note_key = prefix + JupyterWrapper.notebook
        notebook, result_path, html_log = self._copy_notebook(
            ispyb_params, target_file, rd, note_key
        )

        mod_key = prefix + JupyterWrapper.module
        mod = ispyb_params.get(mod_key, [JupyterWrapper.default_module])[0]

        # remove non execution parameters before notebook injection
        if mod_key in ispyb_params:
            del ispyb_params[mod_key]
        del ispyb_params[note_key]
        self._inject_parameters(
            ispyb_params, target_file, result_path, notebook, prefix
        )

        command = [self._get_run_script()]
        command.append(mod)
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

    def _get_target_file(self, payload, jp):
        if (
            JupyterWrapper.payload_key not in payload
            and JupyterWrapper.payload_key not in jp
        ):
            raise RuntimeError("Target file not in payload or job parameters")

        if JupyterWrapper.payload_key in payload:
            return payload[JupyterWrapper.payload_key]

        if JupyterWrapper.payload_key in jp:
            return jp[JupyterWrapper.payload_key]

    def _copy_notebook(self, params, target, rd, note_key):
        if note_key not in params:
            raise RuntimeError("No notebook parameter registered")

        note_path = params[note_key][0]
        if not os.path.isfile(note_path):
            raise RuntimeError("Notebook does not exist: %s" % note_path)

        prd = Path(rd)
        name = Path(Path(target).stem + "_" + Path(note_path).name)
        note_dir = prd / "notebooks"
        note_dir.mkdir(parents=True, exist_ok=True)
        fullpath = note_dir / name
        copyfile(note_path, fullpath)

        nxspath = rd / name.with_suffix(".nxs")
        html = fullpath.with_suffix(".html")
        return str(fullpath), str(nxspath), str(html)

    def _get_run_directory(self, ispyb_rd, override):

        if not override.startswith("{") and os.path.exists(override):
            return override

        return ispyb_rd

    def _get_run_script(self):
        return JupyterWrapper.run_script

    def _inject_parameters(self, ispyb_params, target, result, notebook, prefix):
        nb = nbformat.read(notebook, nbformat.NO_CONVERT)
        nb["cells"][0]["source"] = 'inpath = "{}"'.format(target)
        nb["cells"][1]["source"] = 'outpath = "{}"'.format(result)
        nbformat.write(nb, notebook)

    def _get_prefix(self, jp):
        db_namespace = jp.get("namespace", "")

        if db_namespace:
            db_namespace = db_namespace + "_"

        return JupyterWrapper.param_prefix + db_namespace
