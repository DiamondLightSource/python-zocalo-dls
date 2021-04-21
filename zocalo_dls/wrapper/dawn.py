from zocalo.wrapper import BaseWrapper
import os
import procrunner
import logging

logger = logging.getLogger("DawnWrapper")


class DawnWrapper(BaseWrapper):
    DAWN_RUN_SCRIPT = "/dls/somewhere"

    PARAMETER_PREFIX = "dawn_"
    BASE_CONFIG_PATH = "config"
    VERSION = "version"

    MEMORY = "xmx"
    NCORES = "numberOfCores"
    PROCFILE = "processingPath"
    DATASET = "datasetPath"
    OVERWRITE = "monitorForOverwrite"
    SCANRANK = "scanRank"
    TIMEOUT = "timeOut"
    READABLE = "readable"
    KEY = "dataKey"
    LINKPARENT = "linkParentEntry"
    PUBLISHER = "publisherURI"

    DEFAULT_VERSION = "stable"
    DEFAULTS = {
        MEMORY: "2048m",
        NCORES: 1,
        TIMEOUT: 60000,
        READABLE: True,
        LINKPARENT: True,
        OVERWRITE: False,
        KEY: "/entry/solstice_scan",
    }

    REQUIRED = {SCANRANK}

    def run(self):
        assert hasattr(self, "recwrap"), "No recipewrapper object found"

        payload = self.recwrap.payload

        target_file = payload["target_file"]

        jp = self.recwrap.recipe_step["job_parameters"]

        ispyb_params = jp["ispyb_parameters"]
        ispyb_wd = jp["working_directory"]
        ispyb_rd = jp["result_directory"]
        override_name = jp["override_name"]

        config = {}

        if DawnWrapper.PARAMETER_PREFIX + DawnWrapper.BASE_CONFIG_PATH in ispyb_params:
            config = self._load_config(
                ispyb_params[
                    DawnWrapper.PARAMETER_PREFIX + DawnWrapper.BASE_CONFIG_PATH
                ]
            )
        else:
            config = dict(DawnWrapper.DEFAULTS)

        self._update_config(config, ispyb_params, target_file)

        self._validate_config(config)

        result_path = self._make_results_directory(
            self, config, ispyb_rd, override_name
        )

        working_dir, log_path = self._make_directories(
            self, config, ispyb_wd, override_name
        )

        config_path = self._write_config(config, working_dir)
        command = [DawnWrapper.DAWN_RUN_SCRIPT]
        command.append("-path")
        command.append(config_path)
        command.append("-ncores")
        command.append(config[DawnWrapper.NCORES])
        command.append("-working_dir")
        command.append(working_dir)
        command.append("-log_path")
        command.append(log_path)

        logger.info("Command: %s", " ".join(command))
        result = procrunner.run(command)
        logger.info("Command successful, took %.1f seconds", result["runtime"])

        self.record_result(result_path, "Result")
        self.record_result(log_path, "Log")

        return True

    def record_result(self, path, file_type):
        if os.path.isfile(path):
            p, f = os.path.split(path)
            self.record_result_individual_file(
                {"file_path": p, "file_name": f, "file_type": file_type}
            )
        else:
            logger.warning("No file found at %s", path)

    def _load_config(self, config_path):
        pass

    def _update_config(self, config, ispyb_config, target_file):
        pass

    def _validate_config(self, config):
        pass
