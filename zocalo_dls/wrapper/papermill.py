from .jupyter import JupyterWrapper
import logging
import ast
import papermill as pm

logger = logging.getLogger("zocalo_dls.wrapper.papermill")


class PapermillWrapper(JupyterWrapper):
    def _inject_parameters(self, ispyb_params, target, result, notebook, prefix):
        for_insertion = {}
        prefix_length = len(prefix)
        for k, v in ispyb_params.items():

            if k.startswith(prefix):
                k = k[prefix_length:]
                for_insertion[k] = self.str_to_val(v[0])

        for_insertion["inpath"] = target
        for_insertion["outpath"] = result

        pm.execute_notebook(
            notebook,
            notebook,
            parameters=for_insertion,
            prepare_only=True,
            log_output=True,
        )

    def str_to_val(self, val):
        try:
            return ast.literal_eval(val)
        except Exception:
            return val
