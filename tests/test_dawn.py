import mock
import json
from pathlib import Path

from zocalo_dls.wrapper.dawn import DawnWrapper


@mock.patch("workflows.recipe.RecipeWrapper")
@mock.patch("procrunner.run")
def test_dawn_wrapper_config(mock_runner, mock_wrapper, tmp_path):
    inner_process_wrapper_run(mock_runner, mock_wrapper, tmp_path, False)


@mock.patch("workflows.recipe.RecipeWrapper")
@mock.patch("procrunner.run")
def test_dawn_wrapper_no_config(mock_runner, mock_wrapper, tmp_path):
    inner_process_wrapper_run(mock_runner, mock_wrapper, tmp_path, True)


def inner_process_wrapper_run(mock_runner, mock_wrapper, tmp_path, use_config):

    wd = str(tmp_path / "wd")
    rd = str(tmp_path / "rd")

    Path(wd).mkdir()

    Path(rd).mkdir()

    processing_file = str(tmp_path / "chain.nxs")
    with open(processing_file, "w") as fh:
        pass

    expected = {
        "dataKey": "/entry/solstice_scan",
        "datasetPath": "/entry/detector",
        "filePath": "/test.nxs",
        "linkParentEntry": True,
        "monitorForOverwrite": False,
        "numberOfCores": 1,
        "outputFilePath": rd + "/test-detector-chain.nxs",
        "processingPath": wd + "/chain.nxs",
        "publisherURI": "tcp://localhost:61616",
        "readable": True,
        "scanRank": 2,
        "timeOut": 1800000,
        "xmx": "2048m",
    }

    mock_runner.return_value = {"runtime": 5.0, "exitcode": 0}

    target_file = expected["filePath"]
    command = [
        DawnWrapper.run_script,
        "-path",
        wd + "/dawn_config.json",
        "-version",
        "stable",
    ]

    payload = {"target_file": target_file}
    ispyb_parameters = {
        "dawn_version": "stable",
        "dawn_processingPath": processing_file,
        "dawn_scanRank": str(expected["scanRank"]),
        "dawn_timeOut": str(expected["timeOut"]),
        "dawn_linkParentEntry": str(expected["linkParentEntry"]),
        "dawn_publisherURI": str(expected["publisherURI"]),
    }

    params = {
        "ispyb_parameters": ispyb_parameters,
        "working_directory": wd,
        "result_directory": rd,
        "dataset_path": expected["datasetPath"] + "/data",
        "override_path": "{override_path}",
    }

    mock_wrapper.recipe_step = {"job_parameters": params}
    mock_wrapper.payload = payload
    mock_wrapper.recwrap.send_to.return_value = None

    out_dir = rd

    if use_config:
        out_dir = str(tmp_path)
        create_config(tmp_path, ispyb_parameters, expected, params)

    with open(expected["outputFilePath"], "w") as fh:
        pass

    wrapper = DawnWrapper()
    wrapper.set_recipe_wrapper(mock_wrapper)
    wrapper.run()
    mock_runner.assert_called_with(command)

    with open(wd + "/dawn_config.json", "r") as fh:
        data = json.load(fh)
        assert expected == data

    p1 = {
        "file_path": out_dir,
        "file_name": "test-detector-chain.nxs",
        "file_type": "Result",
    }
    m1 = "result-individual-file"

    p2 = {"target": expected["outputFilePath"]}
    m2 = "result-primary"

    calls = [mock.call(m1, p1), mock.call(m2, p2)]
    mock_wrapper.send_to.assert_has_calls(calls)


def create_config(tmp_path, ispyb_parameters, expected, params):
    conf = {"numberOfCores": 4}
    expected["numberOfCores"] = 4

    params["override_path"] = str(tmp_path)
    expected["outputFilePath"] = str(tmp_path / "test-detector-chain.nxs")

    conf_path = str(tmp_path / "test_conf.json")
    with open(conf_path, "w") as fh:
        json.dump(conf, fh)

    ispyb_parameters["dawn_config"] = conf_path
