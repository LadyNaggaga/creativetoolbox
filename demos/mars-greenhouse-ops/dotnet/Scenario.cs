namespace MarsGreenhouseOpsDemo;

/// <summary>The scenario — keep at parity with python/scenario.py (same turns, same intents).</summary>
public record Turn(string User, string Intent, string CallName, object CallArgs);

public static class Scenario
{
    public static readonly Turn[] Turns =
    {
        new("morning! how's the air in the dome today — are the plants happy?",
            "check the greenhouse air: CO2, oxygen and humidity for the plants",
            "sensors.read_air", new { }),

        new("the tomatoes in bed 3 look a little thirsty — can we give them a drink?",
            "schedule a drip-watering cycle for a planting bed",
            "irrigation.schedule", new { bed = "bed 3" }),

        new("the grow-lights are pulling a lot of juice — are we ok on power?",
            "rebalance the greenhouse power budget across the grow-lights",
            "power.balance_load", new { }),

        new("wait — how deep should I actually be sowing the basil seeds?",
            "look up the planting guide for basil sowing depth and spacing",
            "kb.search_guides", new { topic = "basil" }),

        new("nice — let the crew know the harvest is coming along great",
            "post a friendly harvest update to the colony crew board",
            "notify.crew",
            new { message = "Dome air dialed in, bed 3 watered, basil on the way — first salad harvest in a few days!" }),
    };
}
