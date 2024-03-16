import os
import pytest

if os.getenv("_PYTEST_RAISE", "0") != "0":
    # For debugging tests with pytest and vscode:
    # Configure pytest to not swallow exceptions, so that vscode can catch them before the debugging session ends.
    # See https://stackoverflow.com/a/62563106/130164
    # The .vscode/launch.json configuration should be:
    # "configurations": [
    #     {
    #         "name": "Python: Debug Tests",
    #         "type": "python",
    #         "request": "launch",
    #         "program": "${file}",
    #         "purpose": ["debug-test"],
    #         "console": "integratedTerminal",
    #         "justMyCode": false,
    #         "env": {
    #             "_PYTEST_RAISE": "1"
    #         },
    #     },
    # ]
    @pytest.hookimpl(tryfirst=True)
    def pytest_exception_interact(call):
        raise call.excinfo.value

    @pytest.hookimpl(tryfirst=True)
    def pytest_internalerror(excinfo):
        raise excinfo.value
