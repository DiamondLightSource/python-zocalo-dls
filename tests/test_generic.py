import mock
import workflows
import procrunner
import tempfile
import os

from zocadls.wrapper.generic import ProcessRegisterWrapper

@mock.patch('workflows.recipe.RecipeWrapper')
@mock.patch('procrunner.run')
def test_process_wrapper(mock_runner, mock_wrapper):
    
    mock_runner.return_value = {"runtime" : 5.0}

    command = "ls"
    logpath = "test.log"

    fh = tempfile.NamedTemporaryFile()
    fh.write(b'Hello world!')
    params = {"wrapped_commands" : command,
              "filename" : fh.name,
              "logname" : logpath}

    mock_wrapper.recipe_step = {"job_parameters" : params} 
    mock_wrapper.recwrap.send_to.return_value = None

    wrapper = ProcessRegisterWrapper()
    wrapper.set_recipe_wrapper(mock_wrapper)
    wrapper.run()

    assert mock_runner.called
    p,f = os.path.split(fh.name)
    payload = {'file_path': p,
          'file_name': f,
          'file_type': "Result"};
    mock_wrapper.send_to.assert_called_with("result-individual-file", payload)
