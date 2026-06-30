using System.Text.Json;

namespace SquadRoomDemo;

/// <summary>Command Line activity panel — squad-room team variant. Mirrors python/activity.py exactly.</summary>
public static class Activity
{
    const string Ink = "\u001b[1m", Faint = "\u001b[2m", Reset = "\u001b[0m", Box = "\u001b[7m";
    static string B(string label) => $"{Box} {label} {Reset}";

    public static void Header(string title)
    {
        Console.WriteLine($"{Ink}{title}{Reset}");
        Console.WriteLine($"{Faint}// a whole AI team shares one governed Toolbox — watch every member hit the same box{Reset}");
    }

    public static void Member(string name, string msg) =>
        Console.WriteLine($"\n{Ink}>_ [{name}]{Reset} \"{msg}\"");

    public static void ToolSearch(string query, int roundTrip) =>
        Console.WriteLine($"   {B("tool_search")} query: \"{query}\"   {Faint}// round-trip #{roundTrip}{Reset}");

    public static void Matched(IEnumerable<string> names) =>
        Console.WriteLine($"   {B("matched")} {string.Join(", ", names)}");

    public static void CallTool(string name, object args) =>
        Console.WriteLine($"   {B("call_tool")} {name}({JsonSerializer.Serialize(args)})");

    public static void Result(string text) => Console.WriteLine($"   {Faint}=> {text}{Reset}");

    public static void Counter(int boxSize, int contextSize, int members)
    {
        Console.WriteLine($"\n{B($"tools in the shared box: {boxSize}")}   ·   {B($"tools in each member's context: {contextSize}")}");
        Console.WriteLine($"{Faint}// {members} team members, one governed box. each sees only the meta-tools. flat cost for the whole team.{Reset}");
    }
}
