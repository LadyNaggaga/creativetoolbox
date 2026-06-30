namespace SquadRoomDemo;

/// <summary>A squad-room turn — owned by a team MEMBER. Keep at parity with python/scenario.py.</summary>
public record Turn(string Member, string User, string Intent, string CallName, object CallArgs);

public static class Scenario
{
    public static readonly Turn[] Turns =
    {
        new("lead",
            "new request landed: 'add dark mode'. break it down and assign it.",
            "plan and break a feature request into work items and assign them to the team",
            "issues.assign", new { feature = "add dark mode" }),

        new("researcher",
            "how is theming already done in our codebase?",
            "search our docs and codebase for the existing theming pattern",
            "kb.search_docs", new { topic = "theming" }),

        new("researcher",
            "what design tokens do we have for colors?",
            "look up the design system color tokens and theming variables",
            "design.lookup_tokens", new { }),

        new("builder",
            "open a PR with the dark-mode toggle",
            "open a pull request with the code changes on a branch",
            "repo.open_pr", new { title = "Add dark-mode toggle" }),

        new("builder",
            "run the tests on the branch",
            "run the CI test suite on a branch and check it is green",
            "ci.run_tests", new { branch = "feature/dark-mode" }),

        new("lead",
            "looks good — cut a preview release",
            "cut a tagged preview release from the branch and deploy it",
            "releases.cut", new { tag = "v1.4.0-preview" }),
    };
}
