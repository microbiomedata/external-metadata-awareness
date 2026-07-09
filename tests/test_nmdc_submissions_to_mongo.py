import importlib.util
import sys
import types
from pathlib import Path


def _install_stub_modules():
    try:
        import dotenv  # noqa: F401
    except ModuleNotFoundError:
        dotenv = types.ModuleType("dotenv")

        def _dotenv_values(path=None):
            if not path:
                return {}
            values = {}
            for line in Path(path).read_text(encoding="utf-8").splitlines():
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                values[key] = value
            return values

        dotenv.dotenv_values = _dotenv_values
        sys.modules["dotenv"] = dotenv

    try:
        import tqdm  # noqa: F401
    except ModuleNotFoundError:
        tqdm_mod = types.ModuleType("tqdm")
        tqdm_mod.tqdm = lambda iterable, **_kwargs: iterable
        sys.modules["tqdm"] = tqdm_mod

    try:
        import pymongo  # noqa: F401
    except ModuleNotFoundError:
        pymongo = types.ModuleType("pymongo")

        class _MongoClient:
            def __init__(self, *_args, **_kwargs):
                pass

            def __enter__(self):
                return self

            def __exit__(self, _exc_type, _exc, _tb):
                return False

        pymongo.MongoClient = _MongoClient
        uri_parser = types.ModuleType("pymongo.uri_parser")
        uri_parser.parse_uri = lambda _uri: {}
        sys.modules["pymongo"] = pymongo
        sys.modules["pymongo.uri_parser"] = uri_parser

    try:
        import linkml_runtime  # noqa: F401
    except ModuleNotFoundError:
        linkml_runtime = types.ModuleType("linkml_runtime")
        linkml_runtime.SchemaView = object
        sys.modules["linkml_runtime"] = linkml_runtime

    try:
        import oaklib  # noqa: F401
    except ModuleNotFoundError:
        oaklib = types.ModuleType("oaklib")
        oaklib.get_adapter = lambda *_args, **_kwargs: None
        sys.modules["oaklib"] = oaklib


def _load_module():
    _install_stub_modules()
    script_path = (
        Path(__file__).resolve().parent.parent
        / "external_metadata_awareness"
        / "nmdc-submissions-to-mongo.py"
    )
    spec = importlib.util.spec_from_file_location(
        "nmdc_submissions_to_mongo",
        script_path,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_resolve_env_config_preserves_falsy_cli_overrides(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "MONGO_URI=mongodb://from-env\nBASE_URL=https://from-env\nOUTPUT_FILE=from-env.tsv\n",
        encoding="utf-8",
    )
    module = _load_module()

    resolved = module.resolve_env_config(
        str(env_file),
        mongo_uri="",
        base_url=None,
        output_file=0,
    )

    assert resolved["MONGO_URI"] == ""
    assert resolved["BASE_URL"] == "https://from-env"
    assert resolved["OUTPUT_FILE"] == 0
