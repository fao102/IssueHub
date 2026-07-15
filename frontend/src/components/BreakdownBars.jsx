export default function BreakdownBars({ options, counts, total }) {
  const max = Math.max(1, ...options.map((o) => counts[o.value] || 0))

  return (
    <div className="d-flex flex-column gap-2">
      {options.map((o) => {
        const count = counts[o.value] || 0
        const pct = total > 0 ? Math.round((count / total) * 100) : 0
        const widthPct = (count / max) * 100

        return (
          <div key={o.value} className="d-flex align-items-center gap-2">
            <div className="d-flex align-items-center gap-1 small" style={{ width: 110, flexShrink: 0 }}>
              <span
                aria-hidden="true"
                style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: o.color, flexShrink: 0 }}
              />
              <span>{o.label}</span>
            </div>
            <div className="flex-grow-1 bg-body-secondary" style={{ height: 8, borderRadius: 4 }}>
              <div
                style={{
                  width: `${widthPct}%`,
                  height: '100%',
                  backgroundColor: o.color,
                  borderRadius: 4,
                }}
              />
            </div>
            <div className="text-end small text-muted" style={{ width: 70, flexShrink: 0 }}>
              {count} ({pct}%)
            </div>
          </div>
        )
      })}
    </div>
  )
}
