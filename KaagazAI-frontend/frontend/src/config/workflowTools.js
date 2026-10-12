/**
 * workflowTools.js - the tools the Workflow Builder can chain, and the
 * parameters each one needs. `tool` names match the backend's TOOL_REGISTRY.
 *
 * param.kind: "text" (sent as-is) | "number" | "list" (1,3,5 -> [1,3,5])
 */

export const WORKFLOW_TOOLS = {
  rotate: {
    label: "Rotate",
    params: [
      { name: "angle", label: "Angle", kind: "number", type: "select", default: "90", options: ["90", "180", "270"] },
      { name: "pages", label: "Only pages (empty = all)", kind: "list", type: "text", optional: true, placeholder: "1,3" },
    ],
  },
  delete_pages: {
    label: "Delete pages",
    params: [{ name: "pages", label: "Pages to delete", kind: "list", type: "text", placeholder: "2,5" }],
  },
  extract_pages: {
    label: "Extract pages",
    params: [{ name: "pages", label: "Pages to keep", kind: "list", type: "text", placeholder: "3,1,5" }],
  },
  reorder_pages: {
    label: "Reorder pages",
    params: [{ name: "new_order", label: "New order", kind: "list", type: "text", placeholder: "3,1,2" }],
  },
  remove_blank_pages: { label: "Remove blank pages", params: [] },
  compress: {
    label: "Compress",
    params: [{ name: "quality", label: "Quality", kind: "text", type: "select", default: "medium", options: ["low", "medium", "high"] }],
  },
  watermark: {
    label: "Watermark",
    params: [{ name: "text", label: "Text", kind: "text", type: "text", default: "CONFIDENTIAL" }],
  },
  crop: {
    label: "Crop",
    params: ["left", "right", "top", "bottom"].map((name) => ({
      name, label: `Trim ${name}`, kind: "number", type: "number", default: "0", optional: true,
    })),
  },
  add_page_numbers: {
    label: "Add page numbers",
    params: [{ name: "position", label: "Position", kind: "text", type: "select", default: "bottom-center",
      options: ["bottom-center", "bottom-right", "bottom-left"] }],
  },
};

/** Starting parameter values for a freshly added step. */
export function defaultParams(toolKey) {
  const params = {};
  WORKFLOW_TOOLS[toolKey].params.forEach((p) => { params[p.name] = p.default ?? ""; });
  return params;
}

/**
 * Converts the builder's step list into the JSON the backend expects:
 *   [{ tool: "rotate", params: { angle: 90, pages: [1] } }, ...]
 * Throws a readable error if a required value is missing or malformed.
 */
export function serializeSteps(steps) {
  return steps.map((step, i) => {
    const def = WORKFLOW_TOOLS[step.tool];
    const params = {};

    for (const p of def.params) {
      const raw = (step.params[p.name] ?? "").toString().trim();
      if (raw === "") {
        if (!p.optional) throw new Error(`Step ${i + 1} (${def.label}): "${p.label}" is required.`);
        continue;
      }
      if (p.kind === "list") {
        const numbers = raw.split(",").map((x) => x.trim()).filter(Boolean).map(Number);
        if (numbers.length === 0 || numbers.some((n) => !Number.isInteger(n))) {
          throw new Error(`Step ${i + 1} (${def.label}): "${p.label}" must be numbers like 1,3,5.`);
        }
        params[p.name] = numbers;
      } else if (p.kind === "number") {
        const n = Number(raw);
        if (Number.isNaN(n)) throw new Error(`Step ${i + 1} (${def.label}): "${p.label}" must be a number.`);
        params[p.name] = n;
      } else {
        params[p.name] = raw;
      }
    }
    return { tool: step.tool, params };
  });
}
