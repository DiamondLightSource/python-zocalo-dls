import os


def get_target_file(payload, params, key="target_file"):
    if key not in payload and key not in params:
        raise RuntimeError("Target file not in payload or job parameters")

    if key in payload:
        return payload[key]

    if key in params:
        return params[key]


def broadcast_primary_result(recwrap, result_path, success, key="target_file"):
    if not success or not os.path.isfile(result_path):
        return
    recwrap.send_to("result-primary", {key: result_path})


def record_result(wrapper, path, file_type):
    if os.path.isfile(path):
        p, f = os.path.split(path)
        wrapper.record_result_individual_file(
            {"file_path": p, "file_name": f, "file_type": file_type}
        )
