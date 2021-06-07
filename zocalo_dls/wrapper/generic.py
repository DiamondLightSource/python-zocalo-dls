from zocalo.wrapper import BaseWrapper
import procrunner
import logging
from . import wrapper_utils_dls as utils


logger = logging.getLogger("ProcessRegisterWrapper")


class ProcessRegisterWrapper(BaseWrapper):
    """
    A zocalo wrapper that runs a specified command in procrunner

    Job parameters require the command to be run ("wrapped_commands"),
    but can also include the name of a file and log which will be
    broadcast as results.

    """

    def run(self):
        assert hasattr(self, "recwrap"), "No recipewrapper object found"

        params = self.recwrap.recipe_step["job_parameters"]

        command = params["wrapped_commands"]

        self.modify_command(command, params)

        logger.info("Command: %s", " ".join(command))
        result = procrunner.run(command)
        logger.info("Command successful, took %.1f seconds", result["runtime"])

        if "filename" in params:
            utils.record_result(self, params["filename"], "Result")
            self.additional_file_actions(params["filename"], not result["exitcode"])

        if "logname" in params:
            utils.record_result(self, params["logname"], "Log")

        return not result["exitcode"]

    def modify_command(self, command, params):
        pass

    def additional_file_actions(self, path, success):
        pass


class TargetProcessRegisterWrapper(ProcessRegisterWrapper):
    """
    A zocalo wrapper that runs a target_file command in procrunner

    Job parameters require the command to be run ("wrapped_commands")
    but for this wrapper the name of a target file from the payload or
    or job parameters will be appended to the command. If a file
    name is included in the job params this will be broadcast on the
    primary-result channel.

    """

    def modify_command(self, command, params):
        payload = self.recwrap.payload
        tf = utils.get_target_file(payload, params)
        command.append(tf)

    def additional_file_actions(self, path, success):
        utils.broadcast_primary_result(self.recwrap, path, success)
