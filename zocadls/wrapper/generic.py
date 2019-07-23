from zocalo.wrapper import BaseWrapper
import os
import procrunner
import logging

logger = logging.getLogger('ProcessRegisterWrapper')

class ProcessRegisterWrapper(BaseWrapper):

    def run(self):
        assert hasattr(self, 'recwrap'), "No recipewrapper object found"
      
        params = self.recwrap.recipe_step["job_parameters"]
     
        command = params["wrapped_commands"]
        logger.info('Command: %s', ' '.join(command))
        result = procrunner.run(command)
        logger.warning("Command successful, took %.1f seconds", result["runtime"])
     
        if "filename" in params:
            self.record_result(params["filename"], "Result")
    
        if "logname" in params:
            self.record_result(params["logname"], "Log")
        return True

    def record_result(self,path,type):
        if os.path.isfile(path):
            p,f = os.path.split(path)
            self.record_result_individual_file({'file_path': p,
                'file_name': f,
                'file_type': "Result"})
        else:
            logger.warning("No file found at %s", path)
