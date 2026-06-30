"""Hero tool: issues.assign — lead breaks a feature into work items and assigns them."""
def run(args):
    feature = (args or {}).get("feature", "the feature")
    return (f"Planned '{feature}': #312 research theming (-> researcher), "
            f"#313 build toggle (-> builder), #314 cut preview (-> lead). 3 work items assigned.")
