using System.Text;
using System.Text.Json;

namespace SquadRoomDemo;

// The Squad Room — a toolbox-demo-builder demo (C#).
// A whole AI TEAM (lead / researcher / builder) shares ONE governed Toolbox. Each member fires its
// own tool_search against the same box; every member's context is just the 2 meta-tools.
// Default = scripted mock against the shared local emulator (real ranking + real counter, no key).
// --live / --real: give each member its own Squad/agent loop (see references/squad-integration.md).

class Program
{
    static readonly HttpClient Http = new();
    static readonly string Emu = Environment.GetEnvironmentVariable("TOOLBOX_MCP_ENDPOINT")
        ?? $"http://localhost:{Environment.GetEnvironmentVariable("TOOLBOX_EMULATOR_PORT") ?? "8765"}/toolboxes/squad-room/mcp";
    static int _id = 0;

    static async Task Main(string[] args)
    {
        if (args.Contains("--live") || args.Contains("--real"))
        {
            Console.WriteLine("LIVE/REAL: give each team member its own Squad/agent loop pointed at the same " +
                              "toolbox endpoint (references/squad-integration.md + toolbox-api.md §5). " +
                              "Run ToolboxSetup for --real to create the Toolbox on Foundry first.");
            return;
        }

        await Rpc("initialize");
        await Rpc("notifications/initialized");

        var toolsJson = JsonDocument.Parse(
            File.ReadAllText(Path.Combine("..", "mock-backends", "tools.json")));
        int boxSize = toolsJson.RootElement.GetProperty("tools").GetArrayLength();

        var visible = await ListTools();
        int members = Scenario.Turns.Select(t => t.Member).Distinct().Count();
        Activity.Header("The Squad Room");
        Activity.Counter(boxSize, visible.Count, members);

        int roundTrip = 0;
        foreach (var turn in Scenario.Turns)
        {
            Activity.Member(turn.Member, turn.User);
            roundTrip++;
            Activity.ToolSearch(turn.Intent, roundTrip);
            var matches = await Search(turn.Intent);
            Activity.Matched(matches);
            Activity.CallTool(turn.CallName, turn.CallArgs);
            Activity.Result(await Call(turn.CallName, turn.CallArgs));
        }

        Activity.Counter(boxSize, (await ListTools()).Count, members);
    }

    static async Task<JsonElement> Rpc(string method, object? p = null)
    {
        var body = JsonSerializer.Serialize(new { jsonrpc = "2.0", id = ++_id, method, @params = p ?? new { } });
        using var req = new HttpRequestMessage(HttpMethod.Post, Emu)
        { Content = new StringContent(body, Encoding.UTF8, "application/json") };
        req.Headers.Add("Foundry-Features", "Toolboxes=V1Preview");
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
