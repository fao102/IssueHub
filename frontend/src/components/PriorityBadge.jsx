import { PRIORITY_MAP } from '../constants/tickets'

export default function PriorityBadge({ priority }) {
  const option = PRIORITY_MAP[priority]
  if (!option) return null
  return (
    <span className="d-inline-flex align-items-center gap-1">
      <span
        aria-hidden="true"
        style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: option.color, flexShrink: 0 }}
      />
      <span>{option.label}</span>
    </span>
  )
}
