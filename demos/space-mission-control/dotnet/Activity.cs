using System.Text.Json;

namespace SpaceMissionControlDemo;

/// <summary>Command Line activity panel — mirrors python/activity.py exactly.</summary>
public static class Activity
{
    const string Ink = "\u001b[1m", Faint = "\u001b[2m", Reset = "\u001b[0m", Box = "\u001b[7m";
    static string B(string label) => $"{Box} {label} {Reset}";

    public static void Header(string title)
    {
        Console.WriteLine($"{Ink}{title}{Reset}");
        Console.WriteLine($"{Faint}// one endpoint, many tools, flat cost — watch the counter{Reset}");
    }

    public static void User(string msg) => Console.WriteLine($"\n{Ink}>_ user:{Reset} \"{msg}\"");

    public static void ToolSearch(string query, int roundTrip) =>
        Console.WriteLine($"   {B("tool_search")} query: \"{query}\"   {Faint}// round-trip #{roundTrip}{Reset}");

    public static void Matched(IEnumerable<string> names) =>
        Console.WriteLine($"   {B("matched")} {string.Join(", ", names)}");

    public static void CallTool(string name, object args) =>
        Console.WriteLine($"   {B("call_tool")} {name}({JsonSerializer.Serialize(args)})");

    public static void Result(string text) => Console.WriteLine($"   {Faint}=> {text}{Reset}");

    public static void Counter(int boxSize, int contextSize, int pinned = 0)
    {
        var extra = pinned > 0 ? $" (+{pinned} pinned)" : "";
        Console.WriteLine($"\n{B($"tools in box: {boxSize}")}   ·   {B($"tools in model context: {contextSize}{extra}")}");
        Console.WriteLine($"{Faint}// the box grew to {boxSize}; the model still saw only the meta-tools. flat cost.{Reset}");
    }
}
