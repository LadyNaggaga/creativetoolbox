// --real mode: create the actual Toolbox version on Foundry with Tool Search enabled.
// Verified API in references/toolbox-api.md (§3-4). Uncomment the package refs in the .csproj first.
//
// using Azure.Identity;
// using Azure.AI.Projects;
//
// namespace PizzaShopOpsDemo;
//
// public static class ToolboxSetup
// {
//     public static async Task Run()
//     {
//         var endpoint = Environment.GetEnvironmentVariable("FOUNDRY_PROJECT_ENDPOINT")!;
//         AIProjectClient project = new(new Uri(endpoint), new DefaultAzureCredential());
//         AgentToolboxes toolboxes = project.AgentAdministrationClient.GetAgentToolboxes();
//
//         // {"type":"toolbox_search_preview"} must be first; then the themed MCP server(s).
//         // Build the tool list from ../mock-backends/tools.json so it matches the demo.
//         ProjectsAgentTool searchPreview = ProjectsAgentTool.FromTypeDirective("toolbox_search_preview");
//         ProjectsAgentTool mcp = ProjectsAgentTool.AsProjectTool(ResponseTool.CreateMcpTool(
//             serverLabel: "pizza-shop-ops".Replace("-", ""),
//             serverUri: new Uri(Environment.GetEnvironmentVariable("THEME_MCP_SERVER_URL")!),
//             toolCallApprovalPolicy: new McpToolCallApprovalPolicy(
//                 GlobalMcpToolCallApprovalPolicy.NeverRequireApproval)));
//
//         ToolboxVersion v = await toolboxes.CreateToolboxVersionAsync(
//             toolboxName: "pizza-shop-ops",
//             tools: [searchPreview, mcp],
//             description: "Pizza Shop Ops — built by toolbox-demo-builder, tool search enabled");
//
//         Console.WriteLine($"created toolbox '{v.Name}' version {v.Version}");
//         Console.WriteLine($"consumer endpoint: {endpoint}/toolboxes/pizza-shop-ops/mcp?api-version=v1");
//     }
// }
//
// NOTE: exact symbol names (FromTypeDirective / search-preview helper) vary by preview build.
// If the SDK lacks a direct toolbox_search_preview helper, create the version via REST
// (references/toolbox-api.md §3) with the raw tools array — that contract is stable.
