export default function StatTile({ label, value, color }) {
  return (
    <div className="card h-100">
      <div className="card-body">
        <div className="d-flex align-items-center gap-1 text-muted small mb-1">
          {color && (
            <span
              aria-hidden="true"
              style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: color, flexShrink: 0 }}
            />
          )}
          <span>{label}</span>
        </div>
        <div className="fs-3 fw-semibold">{value}</div>
      </div>
    </div>
  )
}
