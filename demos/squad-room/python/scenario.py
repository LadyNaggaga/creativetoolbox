"""
The squad-room scenario: a feature request flows through an AI TEAM that all shares ONE governed
Toolbox. Each turn is owned by a different team MEMBER (lead / researcher / builder) firing its own
tool_search against the same box. The story: give a whole team one curated, searchable, policy-bound
set of tools instead of wiring each agent separately.

Scripted mode (default, no model key) sends these real queries to the shared emulator, so the
matches + results are genuinely produced by its ranking. In LIVE mode each member would be its own
agent loop (Squad team) emitting tool_search/call_tool itself.
"""

TURNS = [
    {
        "member": "lead",
        "user": "new request landed: 'add dark mode'. break it down and assign it.",
        "intent": "plan and break a feature request into work items and assign them to the team",
        "call": {"name": "issues.assign", "arguments": {"feature": "add dark mode"}},
    },
    {
        "member": "researcher",
        "user": "how is theming already done in our codebase?",
        "intent": "search our docs and codebase for the existing theming pattern",
        "call": {"name": "kb.search_docs", "arguments": {"topic": "theming"}},
    },
    {
        "member": "researcher",
        "user": "what design tokens do we have for colors?",
        "intent": "look up the design system color tokens and theming variables",
        "call": {"name": "design.lookup_tokens", "arguments": {}},
    },
    {
        "member": "builder",
        "user": "open a PR with the dark-mode toggle",
        "intent": "open a pull request with the code changes on a branch",
        "call": {"name": "repo.open_pr", "arguments": {"title": "Add dark-mode toggle"}},
    },
    {
        "member": "builder",
        "user": "run the tests on the branch",
        "intent": "run the CI test suite on a branch and check it is green",
        "call": {"name": "ci.run_tests", "arguments": {"branch": "feature/dark-mode"}},
    },
    {
        "member": "lead",
        "user": "looks good — cut a preview release",
        "intent": "cut a tagged preview release from the branch and deploy it",
        "call": {"name": "releases.cut", "arguments": {"tag": "v1.4.0-preview"}},
    },
]
