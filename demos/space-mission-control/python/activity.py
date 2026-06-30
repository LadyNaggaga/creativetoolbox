"""Command Line activity panel — terminal renderer. Mirrors dotnet/Activity.cs exactly."""
import sys

INK = "\033[1m"; FAINT = "\033[2m"; RESET = "\033[0m"; BOX = "\033[7m"


def _box(label):
    return f"{BOX} {label} {RESET}"


def user(msg):
    print(f"\n{INK}>_ user:{RESET} \"{msg}\"")


def tool_search(query, round_trip):
    print(f"   {_box('tool_search')} query: \"{query}\"   {FAINT}// round-trip #{round_trip}{RESET}")


def matched(names):
    print(f"   {_box('matched')} {', '.join(names) if names else '(none)'}")


def call_tool(name, arguments):
    print(f"   {_box('call_tool')} {name}({arguments})")


def result(text):
    print(f"   {FAINT}=> {text}{RESET}")


def counter(box_size, context_size, pinned=0):
    extra = f" (+{pinned} pinned)" if pinned else ""
    print(f"\n{BOX} tools in box: {box_size} {RESET}   ·   "
          f"{BOX} tools in model context: {context_size}{extra} {RESET}")
    print(f"{FAINT}// the box grew to {box_size}; the model still saw only the meta-tools. flat cost.{RESET}")


def header(title):
    print(f"{INK}{title}{RESET}")
    print(f"{FAINT}// one endpoint, many tools, flat cost — watch the counter{RESET}")
