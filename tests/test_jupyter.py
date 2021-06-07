import mock
from zocalo_dls.wrapper.jupyter import JupyterWrapper


@mock.patch("workflows.recipe.RecipeWrapper")
@mock.patch("procrunner.run")
def test_jupyter_wrapper(mock_runner, mock_wrapper, tmp_path):
    inner_test(mock_runner, mock_wrapper, tmp_path, False)


@mock.patch("workflows.recipe.RecipeWrapper")
@mock.patch("procrunner.run")
def test_jupyter_wrapper_override(mock_runner, mock_wrapper, tmp_path):
    inner_test(mock_runner, mock_wrapper, tmp_path, True)


def inner_test(mock_runner, mock_wrapper, tmp_path, use_override):

    """
    Take target_file, template notebook, generate output notebook path, nxs path, html path
    pass off to script, fire messages
    """
    wd = tmp_path / "wd"
    rd = tmp_path / "rd"
    wd.mkdir()
    rd.mkdir()

    op = "{override_path}"
    out_run_dir = rd
    mod = "python/3"

    if use_override:
        op = tmp_path
        out_run_dir = op
        mod = "python/special"

    processing_file = tmp_path / "notebook.ipynb"
    processing_file.touch()

    mock_runner.return_value = {"runtime": 5.0, "exitcode": 0}

    target_file = "/test/input.nxs"
    result_path = out_run_dir / "input_notebook.nxs"
    notebook_path = out_run_dir / "notebooks/input_notebook.ipynb"
    html_path = out_run_dir / "notebooks/input_notebook.html"

    result_path.touch()
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.touch()

    # make paths strings here
    result_path = str(result_path)
    html_path = str(html_path)
    notebook_path = str(notebook_path)
    out_run_dir = str(out_run_dir)
    wd = str(wd)
    rd = str(rd)
    op = str(op)

    command = [JupyterWrapper.run_script, mod, target_file, result_path, notebook_path]

    payload = {JupyterWrapper.payload_key: target_file}
    ispyb_parameters = {"jupyter_notebook": [processing_file]}

    if use_override:
        ispyb_parameters["jupyter_module"] = [mod]

    params = {
        "ispyb_parameters": ispyb_parameters,
        "working_directory": wd,
        "result_directory": rd,
        "override_path": op,
    }

    mock_wrapper.recipe_step = {"job_parameters": params}
    mock_wrapper.payload = payload
    mock_wrapper.recwrap.send_to.return_value = None

    wrapper = JupyterWrapper()
    wrapper.set_recipe_wrapper(mock_wrapper)
    wrapper.run()
    mock_runner.assert_called_with(command)

    p1 = {
        "file_path": out_run_dir,
        "file_name": "input_notebook.nxs",
        "file_type": "Result",
    }

    p1a = {
        "file_path": out_run_dir + "/notebooks",
        "file_name": "input_notebook.ipynb",
        "file_type": "Result",
    }

    p1b = {
        "file_path": out_run_dir + "/notebooks",
        "file_name": "input_notebook.html",
        "file_type": "Log",
    }

    m1 = "result-individual-file"

    p2 = {JupyterWrapper.payload_key: result_path}
    m2 = "result-primary"

    calls = [
        mock.call(m1, p1),
        mock.call(m1, p1a),
        mock.call(m1, p1b),
        mock.call(m2, p2),
    ]
    mock_wrapper.send_to.assert_has_calls(calls)
