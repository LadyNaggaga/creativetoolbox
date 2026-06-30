namespace SpaceMissionControlDemo;

/// <summary>The scenario — keep at parity with python/scenario.py (same turns, same intents).</summary>
public record Turn(string User, string Intent, string CallName, object CallArgs);

public static class Scenario
{
    public static readonly Turn[] Turns =
    {
        new("the cabin feels stuffy up here — is the air actually okay?",
            "check breathable cabin oxygen air quality and life support status",
            "telemetry.read_o2", new { }),

        new("we need to drop into a lower orbit before the next pass",
            "plan an engine burn to lower our orbit altitude",
            "nav.plot_burn", new { target = "lower orbit" }),

        new("power's getting tight with all the heaters running",
            "rebalance the electrical power budget and shed non-critical load",
            "power.balance_load", new { }),

        new("wait — what's the procedure if the CO2 scrubber fails?",
            "look up the emergency checklist procedure for a scrubber failure",
            "kb.search_procedures", new { topic = "CO2 scrubber failure" }),

        new("ok, tell Houston we're on top of it",
            "send a status message down to houston ground control",
            "comms.send_ground",
            new { message = "Cabin air trending up on CO2; running scrub procedure, all nominal." }),
    };
}
