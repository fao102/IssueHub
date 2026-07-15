// Status is a workflow-identity encoding (which stage), so it draws from the
// validated categorical palette. Priority is a severity encoding, so it draws
// from the fixed status palette (good/warning/serious/critical). Both sets
// pass scripts/validate_palette.js (CVD + normal-vision floors) from the
// dataviz skill; colors are always paired with a text label, never used alone
// (the light-surface contrast WARN on a couple of steps is mitigated by that
// label always being present).

export const STATUS_OPTIONS = [
  { value: 'open', label: 'Open', color: '#2a78d6' },
  { value: 'in_progress', label: 'In Progress', color: '#eda100' },
  { value: 'resolved', label: 'Resolved', color: '#008300' },
  { value: 'closed', label: 'Closed', color: '#e87ba4' },
]

export const PRIORITY_OPTIONS = [
  { value: 'low', label: 'Low', color: '#0ca30c' },
  { value: 'medium', label: 'Medium', color: '#fab219' },
  { value: 'high', label: 'High', color: '#ec835a' },
  { value: 'urgent', label: 'Urgent', color: '#d03b3b' },
]

export const STATUS_MAP = Object.fromEntries(STATUS_OPTIONS.map((o) => [o.value, o]))
export const PRIORITY_MAP = Object.fromEntries(PRIORITY_OPTIONS.map((o) => [o.value, o]))
