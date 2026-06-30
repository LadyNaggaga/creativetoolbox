namespace PizzaShopOpsDemo;

/// <summary>The scenario — keep at parity with python/scenario.py (same turns, same intents).</summary>
public record Turn(string User, string Intent, string CallName, object CallArgs);

public static class Scenario
{
    public static readonly Turn[] Turns =
    {
        new("Friday rush is kicking off — are we good on mozzarella?",
            "check how much of an ingredient we have left in stock",
            "inventory.check_stock", new { item = "mozzarella" }),

        new("fire up the deck oven for Neapolitan pies",
            "set the oven temperature and preheat it for a style of pizza",
            "oven.set_temp", new { temp = 475, style = "Neapolitan" }),

        new("remind me the dough hydration for Neapolitan",
            "look up the recipe and dough formula for a pizza",
            "kb.search_recipes", new { dish = "Neapolitan dough" }),

        new("table 12 wants a large pepperoni, get it in",
            "create a new food order with items and a table number",
            "orders.create", new { summary = "1 large pepperoni", table = "12" }),

        new("send the next three deliveries out",
            "assign a delivery driver to outgoing orders and dispatch them",
            "delivery.assign_driver", new { count = 3 }),
    };
}
