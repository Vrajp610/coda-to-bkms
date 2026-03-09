import os


def write_run_log(lines: list, subdir: str, filename: str) -> str:
    """Write log lines to logs/{subdir}/{filename}. Returns the path written to."""
    log_dir = os.path.join("logs", subdir)
    os.makedirs(log_dir, exist_ok=True)
    path = os.path.join(log_dir, filename)
    with open(path, "w") as f:
        f.write("\n".join(lines))
    return path
