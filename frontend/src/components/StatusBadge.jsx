import { STATUS_MAP } from '../constants/tickets'

export default function StatusBadge({ status }) {
  const option = STATUS_MAP[status]
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
