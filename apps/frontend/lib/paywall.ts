import type { Essay, Paywall } from "./content";
import type { SessionTier } from "./session";

export type Visitor = "anon" | SessionTier;

export type GateState = "open" | "email-gate" | "paywall";

const GATE_MARKER = "<!--gate-->";
const DEFAULT_VISIBLE_FRACTION_EMAIL = 0.3;
const DEFAULT_VISIBLE_FRACTION_PAID = 0.12;

export interface SplitBody {
  visible: string;
  hidden: string;
  hasGate: boolean;
}

// Split essay body at the explicit `<!--gate-->` marker if present;
// otherwise split on a paragraph boundary near the target fraction.
export function splitBody(body: string, fraction: number): SplitBody {
  const idx = body.indexOf(GATE_MARKER);
  if (idx !== -1) {
    return {
      visible: body.slice(0, idx).trimEnd(),
      hidden: body.slice(idx + GATE_MARKER.length).trimStart(),
      hasGate: true,
    };
  }
  if (!body.length) {
    return { visible: "", hidden: "", hasGate: false };
  }
  const target = Math.floor(body.length * fraction);
  const split = body.indexOf("\n\n", target);
  if (split === -1 || split >= body.length - 1) {
    return { visible: body, hidden: "", hasGate: false };
  }
  return {
    visible: body.slice(0, split),
    hidden: body.slice(split),
    hasGate: true,
  };
}

export function gateStateFor(
  paywall: Paywall | undefined,
  visitor: Visitor
): GateState {
  const wall = paywall ?? "free";
  if (wall === "free") return "open";
  if (wall === "email-gate") {
    return visitor === "anon" ? "email-gate" : "open";
  }
  if (wall === "paid") {
    if (visitor === "paid" || visitor === "founder") return "open";
    return "paywall";
  }
  return "open";
}

export interface GatedEssay {
  state: GateState;
  visible: string;
  hidden: string;
}

export function gateEssay(essay: Essay, visitor: Visitor): GatedEssay {
  const state = gateStateFor(essay.paywall, visitor);
  if (state === "open") {
    return { state, visible: essay.content, hidden: "" };
  }
  const fraction =
    state === "paywall"
      ? DEFAULT_VISIBLE_FRACTION_PAID
      : DEFAULT_VISIBLE_FRACTION_EMAIL;
  const { visible, hidden } = splitBody(essay.content, fraction);
  return { state, visible, hidden };
}
