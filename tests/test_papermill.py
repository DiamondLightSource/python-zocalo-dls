import mock
from zocalo_dls.wrapper.papermill import PapermillWrapper
import nbformat
import utils
import pytest


papermill_params_dict = {
    "override": True,
    "add_db_module": True,
    "namespace": "a",
}

papermill_params_dict2 = {
    "override": False,
    "add_db_module": False,
    "namespace": "",
}

static_params = {
    "wrapper_under_test": PapermillWrapper(),
    "code": [
        """\
    x = 1
    y = 'y'
    z: float= 1.1"""
    ],
    "db_params": {"x": 10, "y": "a_string", "z": 2.2},
}


@pytest.mark.parametrize(
    "papermill_params", [papermill_params_dict, papermill_params_dict2]
)
@mock.patch("workflows.recipe.RecipeWrapper")
@mock.patch("procrunner.run")
def test_papermill_wrapper(mock_runner, mock_wrapper, tmp_path, papermill_params):
    nb_path = utils.build_and_wrap_notebook(
        mock_runner, mock_wrapper, tmp_path, False, static_params, papermill_params
    )

    nb = nbformat.read(nb_path, as_version=4)
    code = nb.cells[1]["source"]

    assert 'y = "a_string"' in code
    assert "x = 10" in code
    assert "z = 2.2" in code
    assert "inpath" in code
    assert "outpath" in code
