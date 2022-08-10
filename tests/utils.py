import nbformat
import mock


def write_notebook(path, code):

    nb = nbformat.v4.new_notebook()

    nb["metadata"]["kernelspec"] = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }

    nb["metadata"]["language_info"] = {"name": "python", "version": 3}

    nb["cells"] = []

    for c in code:
        newcell = nbformat.v4.new_code_cell(c)
        nb["cells"].append(newcell)

    nb["cells"][0].metadata["tags"] = ["parameters"]

    with open(path, "w") as f:
        nbformat.write(nb, f)


# def make_notebook_test_paths():


def build_notebook_run_job_param(
    ispyb_parameters, tmp_path, use_override, override_params
):

    wd = tmp_path / "wd"
    rd = tmp_path / "rd"
    wd.mkdir()
    rd.mkdir()

    op = "{override_path}"
    out_run_dir = rd

    if use_override:
        op = tmp_path
        rd = tmp_path
        out_run_dir = tmp_path
        ispyb_parameters.update(override_params)

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
    params = {
        "ispyb_parameters": ispyb_parameters,
        "working_directory": wd,
        "result_directory": rd,
        "override_path": op,
    }

    return params


def check_notebook_wrapper_calls(out_run_dir, notebook_name, key, mock_wrapper):
    p1 = {
        "file_path": out_run_dir,
        "file_name": notebook_name + ".nxs",
        "file_type": "Result",
    }

    p1a = {
        "file_path": out_run_dir + "/notebooks",
        "file_name": notebook_name + ".ipynb",
        "file_type": "Result",
    }

    p1b = {
        "file_path": out_run_dir + "/notebooks",
        "file_name": notebook_name + ".html",
        "file_type": "Log",
    }

    m1 = "result-individual-file"

    p2 = {key: "{}/{}.nxs".format(out_run_dir, notebook_name)}
    m2 = "result-primary"

    calls = [
        mock.call(m1, p1),
        mock.call(m1, p1a),
        mock.call(m1, p1b),
        mock.call(m2, p2),
    ]
    mock_wrapper.send_to.assert_has_calls(calls)


def build_and_wrap_notebook(
    mock_runner, mock_wrapper, tmp_path, use_override, static_params, jupyter_params
):

    """
    Take target_file, template notebook, generate output notebook path, nxs path, html path
    pass off to script, fire messages
    """

    target_file = "/test/input.nxs"

    processing_file = tmp_path / "notebook.ipynb"

    write_notebook(processing_file, static_params["code"])

    db_key = "jupyter_"

    if jupyter_params["namespace"]:
        db_key = db_key + jupyter_params["namespace"] + "_"

    if "db_params" in static_params and static_params["db_params"]:
        ispyb_parameters = {
            db_key + k: [str(v)] for k, v in static_params["db_params"].items()
        }
    else:
        ispyb_parameters = {}

    ispyb_parameters[db_key + "notebook"] = [str(processing_file)]

    mod = "python/3"
    if jupyter_params["add_db_module"]:
        mod = "python/special"
        ispyb_parameters[db_key + "module"] = [mod]

    params = build_notebook_run_job_param(ispyb_parameters, tmp_path, use_override, {})

    if jupyter_params["namespace"]:
        params["namespace"] = jupyter_params["namespace"]

    mock_runner.return_value = {"runtime": 5.0, "exitcode": 0}

    notebook_path = params["result_directory"] + "/" + "notebooks/input_notebook.ipynb"

    module_name = (
        mod
        if (db_key + "module") not in ispyb_parameters
        else ispyb_parameters[db_key + "module"][0]
    )

    wrapper = static_params["wrapper_under_test"]

    command = [wrapper.run_script, module_name, notebook_path]

    payload = {wrapper.payload_key: target_file}

    mock_wrapper.recipe_step = {"job_parameters": params}
    mock_wrapper.payload = payload
    mock_wrapper.recwrap.send_to.return_value = None

    wrapper.set_recipe_wrapper(mock_wrapper)
    wrapper.run()
    mock_runner.assert_called_with(command)

    check_notebook_wrapper_calls(
        params["result_directory"], "input_notebook", wrapper.payload_key, mock_wrapper
    )

    return params["result_directory"] + "/notebooks/input_notebook.ipynb"
