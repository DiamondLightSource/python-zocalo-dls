import mock
from zocalo_dls.wrapper.jupyter import JupyterWrapper
import utils
import pytest

jupyter_injected = {"override": True, "add_db_module": True, "namespace": ""}

jupyter_injected2 = {"override": False, "add_db_module": False, "namespace": "a"}

static_params = {
    "wrapper_under_test": JupyterWrapper(),
    "code": [
        """\
       inpath = "" """,
        """\
       outpath = "" """,
    ],
}


@pytest.mark.parametrize("jupyter_params", [jupyter_injected, jupyter_injected2])
@mock.patch("workflows.recipe.RecipeWrapper")
@mock.patch("procrunner.run")
def test_jupyter_wrapper(mock_runner, mock_wrapper, tmp_path, jupyter_params):
    utils.build_and_wrap_notebook(
        mock_runner, mock_wrapper, tmp_path, False, static_params, jupyter_params
    )
