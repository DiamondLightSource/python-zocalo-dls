import mock
import tempfile
import os

from zocalo_dls.wrapper.generic import ProcessRegisterWrapper


@mock.patch("workflows.recipe.RecipeWrapper")
@mock.patch("procrunner.run")
def test_process_wrapper(mock_runner, mock_wrapper):

    mock_runner.return_value = {"runtime": 5.0}

    command = "ls"

    fh = tempfile.NamedTemporaryFile()
    fh_log = tempfile.NamedTemporaryFile()

    params = {"wrapped_commands": command, "filename": fh.name, "logname": fh_log.name}

    mock_wrapper.recipe_step = {"job_parameters": params}
    mock_wrapper.recwrap.send_to.return_value = None

    wrapper = ProcessRegisterWrapper()
    wrapper.set_recipe_wrapper(mock_wrapper)
    wrapper.run()

    mock_runner.assert_called_with(command)
    p, f = os.path.split(fh.name)
    payload = {"file_path": p, "file_name": f, "file_type": "Result"}

    pl, fl = os.path.split(fh_log.name)
    payloadl = {"file_path": pl, "file_name": fl, "file_type": "Log"}

    mes = "result-individual-file"

    calls = [mock.call(mes, payload), mock.call(mes, payloadl)]
    mock_wrapper.send_to.assert_has_calls(calls)
