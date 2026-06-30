"""Command Line activity panel — squad-room team variant. Mirrors dotnet/Activity.cs exactly."""

INK = "\033[1m"; FAINT = "\033[2m"; RESET = "\033[0m"; BOX = "\033[7m"


def _box(label):
    return f"{BOX} {label} {RESET}"


def member(name, msg):
    print(f"\n{INK}>_ [{name}]{RESET} \"{msg}\"")


def tool_search(query, round_trip):
    print(f"   {_box('tool_search')} query: \"{query}\"   {FAINT}// round-trip #{round_trip}{RESET}")


def matched(names):
    print(f"   {_box('matched')} {', '.join(names) if names else '(none)'}")


def call_tool(name, arguments):
    print(f"   {_box('call_tool')} {name}({arguments})")


def result(text):
    print(f"   {FAINT}=> {text}{RESET}")


def counter(box_size, context_size, members):
    print(f"\n{BOX} tools in the shared box: {box_size} {RESET}   ·   "
          f"{BOX} tools in each member's context: {context_size} {RESET}")
    print(f"{FAINT}// {members} team members, one governed box. each sees only the meta-tools. "
          f"flat cost for the whole team.{RESET}")


def header(title):
    print(f"{INK}{title}{RESET}")
    print(f"{FAINT}// a whole AI team shares one governed Toolbox — watch every member hit the same box{RESET}")
