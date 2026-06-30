"""Hero tool: ci.run_tests — builder runs the CI suite on the branch."""
def run(args):
    branch = (args or {}).get("branch", "the branch")
    return f"CI on {branch}: 248 passed, 0 failed, coverage 91%. Build is green."
