# Schema meta-validation evidence

Using the available CPython 3.12.16/jsonschema environment read-only:

```sh
../audio-bench/.venv/bin/python - <<'PY'
import json
from pathlib import Path
from jsonschema import Draft202012Validator
for path in sorted(Path("schemas").glob("**/*.json")):
    data = json.loads(path.read_text())
    if "$schema" in data:
        Draft202012Validator.check_schema(data)
        print("schema-ok", path)
validator = Draft202012Validator(json.loads(Path("schemas/descriptor.schema.json").read_text()))
for path in sorted(Path("schemas/providers").glob("*.descriptor.json")):
    validator.validate(json.loads(path.read_text()))
    print("descriptor-ok", path)
PY
```

Result: both declared Draft 2020-12 schemas meta-validated, and generated
high-pass and Speex provider descriptors validated against the descriptor
schema. The C conformance suite independently queried effective configurations
from the runtime; complete schema validation of every emitted configuration
and Python round-trip of timestamps above 2^53 remain open.
