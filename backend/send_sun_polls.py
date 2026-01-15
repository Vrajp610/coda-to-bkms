from backend.common_polls import build_targets_from_env, send_polls_to_targets

def main() -> None:
    prefix = "SUN_"
    targets = build_targets_from_env(prefix)
    send_polls_to_targets(targets, for_prefix=prefix)

if __name__ == "__main__":
    main()