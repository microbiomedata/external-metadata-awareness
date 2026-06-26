import importlib.util
import sys
import types
from datetime import datetime as real_datetime


def _load_script_module(monkeypatch):
    if 'dotenv' not in sys.modules:
        monkeypatch.setitem(sys.modules, 'dotenv', types.SimpleNamespace(dotenv_values=lambda _p: {}))
    if 'tqdm' not in sys.modules:
        monkeypatch.setitem(sys.modules, 'tqdm', types.SimpleNamespace(tqdm=lambda iterable, **_kwargs: iterable))
    if 'pymongo' not in sys.modules:
        monkeypatch.setitem(sys.modules, 'pymongo', types.SimpleNamespace(MongoClient=object))
    if 'pymongo.uri_parser' not in sys.modules:
        monkeypatch.setitem(sys.modules, 'pymongo.uri_parser', types.SimpleNamespace(parse_uri=lambda _u: {}))
    if 'linkml_runtime' not in sys.modules:
        monkeypatch.setitem(sys.modules, 'linkml_runtime', types.SimpleNamespace(SchemaView=object))
    if 'oaklib' not in sys.modules:
        monkeypatch.setitem(sys.modules, 'oaklib', types.SimpleNamespace(get_adapter=lambda _x: None))

    path = '/home/runner/work/external-metadata-awareness/external-metadata-awareness/external_metadata_awareness/nmdc-submissions-to-mongo.py'
    spec = importlib.util.spec_from_file_location('nmdc_submissions_to_mongo_script', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_resolve_env_config_preserves_falsy_cli_override(monkeypatch):
    module = _load_script_module(monkeypatch)
    monkeypatch.setattr(module, 'dotenv_values', lambda _p: {'MONGO_URI': 'env-mongo'})

    cfg = module.resolve_env_config('/fake.env', mongo_uri='')
    assert cfg['MONGO_URI'] == ''

    cfg_none = module.resolve_env_config('/fake.env', mongo_uri=None)
    assert cfg_none['MONGO_URI'] == 'env-mongo'


def test_process_submissions_uses_unique_temp_collection_name(monkeypatch, tmp_path):
    module = _load_script_module(monkeypatch)

    class FakeSchemaView:
        def __init__(self, _url):
            pass

        def usage_index(self):
            return {'ControlledTermValue': []}

    class FixedDateTime:
        @staticmethod
        def utcnow():
            return real_datetime(2024, 1, 2, 3, 4, 5, 6789)

    class FakeTempCollection:
        def __init__(self):
            self.renamed_to = None

        def delete_many(self, _query):
            return None

        def insert_many(self, docs):
            return types.SimpleNamespace(inserted_ids=list(range(len(docs))))

        def rename(self, name, dropTarget=True):  # noqa: N803
            self.renamed_to = (name, dropTarget)

    class FakeSubmissionsCollection:
        def count_documents(self, _query):
            return 1

        def find(self):
            return [
                {
                    'id': 'sub-1',
                    'created': '2024-01-01',
                    'date_last_modified': '2024-01-02',
                    'status': 'submitted',
                    'metadata_submission': {
                        'sampleData': {'soil_data': [{'foo': 'bar'}]}
                    },
                }
            ]

    class FakeDB:
        def __init__(self):
            self.submissions = FakeSubmissionsCollection()
            self.temp_collection_name = None
            self.temp_collection = FakeTempCollection()

        def __getitem__(self, key):
            if key == 'nmdc_submissions':
                return self.submissions
            self.temp_collection_name = key
            return self.temp_collection

    class FakeMongoClient:
        def __init__(self, _url):
            self.db = FakeDB()

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def __getitem__(self, _name):
            return self.db

    tqdm_calls = []

    def fake_tqdm(iterable, **kwargs):
        tqdm_calls.append(kwargs)
        return iterable

    monkeypatch.setattr(module, 'SchemaView', FakeSchemaView)
    monkeypatch.setattr(module, 'build_ontology_adapters', lambda _x: {})
    monkeypatch.setattr(module, 'load_ontology_labels', lambda _x: {})
    monkeypatch.setattr(module, 'find_obsolete_terms', lambda _x: [])
    monkeypatch.setattr(module, 'parse_uri', lambda _u: {'database': 'misc_metadata'})
    monkeypatch.setattr(module, 'MongoClient', FakeMongoClient)
    monkeypatch.setattr(module, 'datetime', FixedDateTime)
    monkeypatch.setattr(module.os, 'getpid', lambda: 4321)
    monkeypatch.setattr(module, 'tqdm', fake_tqdm)

    ok = module.process_submissions('mongodb://example/misc_metadata', str(tmp_path / 'out.tsv'))
    assert ok is True

    assert (tmp_path / 'out.tsv').exists()

    # Re-run with access to the client instance used in the function
    client = FakeMongoClient('mongodb://example/misc_metadata')
    monkeypatch.setattr(module, 'MongoClient', lambda _u: client)
    module.process_submissions('mongodb://example/misc_metadata', str(tmp_path / 'out2.tsv'))
    assert client.db.temp_collection_name == 'flattened_submission_biosamples_tmp_20240102030405006789_4321'

    inner_calls = [c for c in tqdm_calls if 'desc' in c and ('sampleData processing' in c['desc'] or 'Processing samples' in c['desc'])]
    assert inner_calls
    assert all(call.get('disable') is True for call in inner_calls)
