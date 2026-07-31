# Brownfield qualification fixture

- This is an isolated synthetic repository with no secrets or network dependencies.
- Modify only `retry_policy.py`.
- Preserve the existing default of three attempts.
- Run `python -B -m unittest discover -s tests -v` after the change.
- Do not change tests, install dependencies, access the network, commit, push, or deploy.
- Report the actual command and result; do not claim checks that did not run.
