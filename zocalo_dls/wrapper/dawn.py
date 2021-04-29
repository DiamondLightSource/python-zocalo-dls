from zocalo.wrapper import BaseWrapper
import os
import procrunner
import logging
import json
from pathlib import Path
from shutil import copyfile

logger = logging.getLogger("DawnWrapper")


class DawnWrapper(BaseWrapper):
    """
    A zocalo wrapper for DAWN headless processing

    Builds and checks the json config file from the input
    parameters, broadcasts result nexus file path on success

    """

    run_script = "/dls_sw/apps/wrapper-scripts/dawn_autoprocessing.sh"
    param_prefix = "dawn_"
    config_name = param_prefix + "config"
    version = "version"
    memory = "xmx"
    ncores = "numberOfCores"
    proc_path = "processingPath"
    target = "filePath"
    dataset_path = "datasetPath"
    overwrite = "monitorForOverwrite"
    scan_rank = "scanRank"
    timeout = "timeOut"
    readable = "readable"
    datakey = "dataKey"
    link_parent = "linkParentEntry"
    publisher = "publisherURI"
    output_file = "outputFilePath"

    default_version = "stable"

    config_vals = {
        memory,
        ncores,
        proc_path,
        dataset_path,
        overwrite,
        scan_rank,
        timeout,
        readable,
        datakey,
        link_parent,
        publisher,
    }

    defaults = {
        memory: "2048m",
        ncores: 1,
        timeout: 60000,
        readable: True,
        link_parent: True,
        overwrite: False,
        datakey: "/entry/solstice_scan",
    }

    # things we cant sensibly default or ignore
    required = {scan_rank, proc_path, dataset_path, target}

    def run(self):
        assert hasattr(self, "recwrap"), "No recipewrapper object found"

        payload = self.recwrap.payload
        target_file = payload["target_file"]

        jp = self.recwrap.recipe_step["job_parameters"]

        ispyb_params = jp["ispyb_parameters"]
        ispyb_wd = jp["working_directory"]
        ispyb_rd = jp["result_directory"]
        ispyb_dspath = jp["dataset_path"]
        override_path = jp["override_path"]

        config = dict(DawnWrapper.defaults)

        if DawnWrapper.config_name in ispyb_params:
            self._load_config(ispyb_params[DawnWrapper.config_name], config)

        self._update_config(config, ispyb_params, target_file, ispyb_dspath)

        self._validate_config(config)

        self._copy_processing_chain(config, ispyb_wd)

        result_path = self._make_results_directory(config, ispyb_rd, override_path)

        config_path = self._write_config(config, ispyb_wd)

        v = DawnWrapper.param_prefix + DawnWrapper.version

        version = ispyb_params.get(v, DawnWrapper.default_version)

        command = [DawnWrapper.run_script]
        command.append("-path")
        command.append(config_path)
        command.append("-version")
        command.append(version)
        logger.info("Command: %s", " ".join(command))
        result = procrunner.run(command)
        logger.info("Command successful, took %.1f seconds", result["runtime"])

        self._record_result(result_path, "Result")
        self._broadcast_primary_result(result_path, not result["exitcode"])

        return not result["exitcode"]

    def _broadcast_primary_result(self, result_path, success):
        if not success or not os.path.isfile(result_path):
            return

        if getattr(self, "recwrap", None):
            self.recwrap.send_to("result-primary", {"target": result_path})

    def _record_result(self, path, file_type):
        if os.path.isfile(path):
            p, f = os.path.split(path)
            self.record_result_individual_file(
                {"file_path": p, "file_name": f, "file_type": file_type}
            )
        else:
            logger.warning("No file found at %s", path)

    def _load_config(self, config_path, config):

        if not os.path.isfile(config_path):
            raise RuntimeError("Config does not exist: %s" % config_path)

        with open(config_path, "r") as fh:
            data = json.load(fh)
            config.update(data)

    def _update_config(self, config, ispyb_config, target_file, dspath):
        config[DawnWrapper.target] = target_file

        if DawnWrapper.dataset_path not in config:
            config[DawnWrapper.dataset_path] = dspath[: dspath.rfind("/")]

        for k in DawnWrapper.config_vals:
            name = DawnWrapper.param_prefix + k
            if name in ispyb_config:
                val = ispyb_config[name]
                out = val
                if val == "False":
                    out = False

                if val == "True":
                    out = True

                if val.isdigit():
                    out = int(val)

                config[k] = out

    def _copy_processing_chain(self, config, working_dir):

        p = config[DawnWrapper.proc_path]
        new_loc = working_dir + "/" + Path(p).name
        copyfile(p, new_loc)
        config[DawnWrapper.proc_path] = new_loc

    def _validate_config(self, config):
        for k in DawnWrapper.required:
            if k not in config:
                raise RuntimeError("Required value missing from dawn config: %s" % k)

    def _make_results_directory(self, config, ispyb_rd, override_name):

        scan = Path(config[DawnWrapper.target]).stem + "-"
        dataset = Path(config[DawnWrapper.dataset_path]).parts[2] + "-"
        process = Path(config[DawnWrapper.proc_path]).stem + ".nxs"

        result_filename = scan + dataset + process

        name = ispyb_rd + "/" + result_filename

        if not override_name.startswith("{") and os.path.exists(override_name):
            name = override_name + "/" + result_filename

        config[DawnWrapper.output_file] = name
        return name

    def _write_config(self, config, working_dir):
        Path(working_dir).mkdir(parents=True, exist_ok=True)
        path = working_dir + "/" + DawnWrapper.config_name + ".json"
        with open(path, "w") as fh:
            json.dump(config, fh, sort_keys=True, indent=2)
        return path
