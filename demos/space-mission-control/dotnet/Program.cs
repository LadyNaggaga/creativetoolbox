using System.Text;
using System.Text.Json;

namespace SpaceMissionControlDemo;

// Space Mission Control — a toolbox-demo-builder demo (C#).
// Default = scripted mock against the shared local emulator (real ranking + real counter, no key).
// --live / --real: wire Microsoft Agent Framework + ToolboxMcpClient (see references/toolbox-api.md §5).

class Program
{
    static readonly HttpClient Http = new();
    static readonly string Emu = Environment.GetEnvironmentVariable("TOOLBOX_MCP_ENDPOINT")
        ?? $"http://localhost:{Environment.GetEnvironmentVariable("TOOLBOX_EMULATOR_PORT") ?? "8765"}/toolboxes/space-mission-control/mcp";
    static int _id = 0;

    static async Task Main(string[] args)
    {
        if (args.Contains("--live") || args.Contains("--real"))
        {
            Console.WriteLine("LIVE/REAL: wire a model + ToolboxMcpClient here (references/toolbox-api.md §5). " +
                              "Run ToolboxSetup for --real to create the Foundry toolbox first.");
            return;
        }

        await Rpc("initialize");
        await Rpc("notifications/initialized");

        var toolsJson = JsonDocument.Parse(
            File.ReadAllText(Path.Combine("..", "mock-backends", "tools.json")));
        int boxSize = toolsJson.RootElement.GetProperty("tools").GetArrayLength();

        var visible = await ListTools();
        int pinned = Math.Max(0, visible.Count - 2);
        Activity.Header("Space Mission Control");
        Activity.Counter(boxSize, visible.Count, pinned);

        int roundTrip = 0;
        foreach (var turn in Scenario.Turns)
        {
            Activity.User(turn.User);
            roundTrip++;
            Activity.ToolSearch(turn.Intent, roundTrip);
            var matches = await Search(turn.Intent);
            Activity.Matched(matches);
            Activity.CallTool(turn.CallName, turn.CallArgs);
            Activity.Result(await Call(turn.CallName, turn.CallArgs));
        }

        Activity.Counter(boxSize, (await ListTools()).Count, pinned);
    }

    static async Task<JsonElement> Rpc(string method, object? p = null)
    {
        var body = JsonSerializer.Serialize(new { jsonrpc = "2.0", id = ++_id, method, @params = p ?? new { } });
        using var req = new HttpRequestMessage(HttpMethod.Post, Emu)
        { Content = new StringContent(body, Encoding.UTF8, "application/json") };
        req.Headers.Add("Foundry-Features", "Toolboxes=V1Preview"); // required header (real + emulator)
        var bearer = Environment.GetEnvironmentVariable("TOOLBOX_BEARER");
        if (!string.IsNullOrEmpty(bearer)) req.Headers.Add("Authorization", $"Bearer {bearer}");
        var resp = await Http.SendAsync(req);
        return JsonDocument.Parse(await resp.Content.ReadAsStringAsync()).RootElement.Clone();
    }

    static async Task<List<string>> ListTools()
    {
        var r = await Rpc("tools/list");
        var tools = r.GetProperty("result").GetProperty("tools");
        return tools.EnumerateArray().Select(t => t.GetProperty("name").GetString()!).ToList();
    }

    static async Task<List<string>> Search(string query)
    {
        var r = await Rpc("tools/call", new { name = "tool_search", arguments = new { query, limit = 5 } });
        var text = r.GetProperty("result").GetProperty("content")[0].GetProperty("text").GetString()!;
        return JsonDocument.Parse(text).RootElement.EnumerateArray()
            .Select(m => m.GetProperty("name").GetString()!).ToList();
    }

    static async Task<string> Call(string name, object arguments)
    {
        var r = await Rpc("tools/call", new { name = "call_tool", arguments = new { name, arguments } });
        return r.GetProperty("result").GetProperty("content")[0].GetProperty("text").GetString()!;
    }
}
