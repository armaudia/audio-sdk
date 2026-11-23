"""Replay the checked-in listening design fixture; never read or emit media."""

import hashlib
import json
from pathlib import Path


ORDERING = "sha256-rank-v1"


def order(seed, panel, trial, conditions):
    def rank(condition):
        key = f"{ORDERING}\n{seed}\n{panel}\n{trial}\n{condition}".encode("ascii")
        return hashlib.sha256(key).digest(), condition

    labels = "ABCDE"[:len(conditions)]
    return dict(zip(labels, sorted(conditions, key=rank), strict=True))


def replay(registration, fixture):
    if registration["ordering"] != ORDERING:
        raise ValueError("unsupported_ordering")

    prepared, mock_ratings, key = {}, {}, {}
    registered = registration["trials"]
    stimuli, responses = fixture["stimulus_metadata"], fixture["mock_responses"]
    if (stimuli.keys() | responses.keys()) - registered.keys():
        raise ValueError("unregistered_trial")

    for trial, (panel, stratum) in registered.items():
        conditions = set(registration["panels"][panel])
        mapping = order(registration["seed"], panel, trial, conditions)
        metadata = stimuli.get(trial, {})
        missing = sorted(conditions - metadata.keys())
        invalid = sorted(
            c for c in conditions & metadata.keys()
            if metadata[c] != registration["source_interval"]
            or any(type(sample) is not int for sample in metadata[c])
        )
        extra = sorted(metadata.keys() - conditions)
        status = (
            "invalid" if invalid or extra else "missing" if missing else "metadata_ready"
        )
        prepared[trial] = {
            "panel": panel, "stratum": stratum, "status": status,
            "missing_conditions": missing, "invalid_intervals": invalid,
            "unregistered_conditions": extra,
        }
        row = {"status": "not_run", "reason": "stimuli_not_ready", "result": None}
        mock_ratings[trial] = row
        if status != "metadata_ready":
            continue

        key[trial] = mapping
        response = responses.get(trial)
        if trial not in responses:
            row.update(status="missing", reason="missing_response")
        elif (
            panel == "ab" and isinstance(response, str)
            and (response == "tie" or response in mapping)
        ):
            row.update(status="valid", reason=None,
                       result={"candidate_preferred": int(mapping.get(response) == "candidate")})
        elif panel == "mushra_style" and (
            isinstance(response, dict)
            and response.keys() == mapping.keys()
            and all(type(score) is int and 0 <= score <= 100 for score in response.values())
        ):
            row.update(status="valid", reason=None,
                       result={mapping[label]: score for label, score in response.items()})
        else:
            row.update(status="invalid", reason="invalid_response")

    return {
        "kind": "synthetic_metadata_only",
        "registration_id": registration["id"],
        "prepared_listening_sets": {"media_prepared": 0, "trial_plans": prepared},
        "listener_projection_example": {
            trial: list(mapping) for trial, mapping in key.items()
        },
        "fixture_only_unblinding_key": key,
        "ratings": {"human_status": "not_collected", "mock_only": mock_ratings},
        "cleared_playback": {"status": "not_cleared", "items": 0},
        "aggregation": "per_trial_only_no_pooled_score",
        "release_qualified": False,
    }


def report():
    here = Path(__file__).resolve().parent
    files = {name: (here / name).read_bytes() for name in
             ("registration.json", "fixture.json", "check_fixture.py")}
    record = replay(json.loads(files["registration.json"]), json.loads(files["fixture.json"]))
    record["sha256"] = {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}
    return record


if __name__ == "__main__":
    print(json.dumps(report(), indent=2, sort_keys=True))
