from flask import Blueprint, request, Response
import csv
import io

reporting_bp = Blueprint("reporting", __name__)

@reporting_bp.get("/summary")
def summary():
    # TODO: replace with real aggregated data from DB
    data = {
        "members": 2,
        "tournaments": 1,
        "matches_recorded": 3,
    }
    return data, 200

@reporting_bp.get("/export")
def export():
    # Example CSV export
    format_ = (request.args.get("format") or "csv").lower()
    rows = [
        {"member_id": 1, "name": "Alice", "points": 5},
        {"member_id": 2, "name": "Bob", "points": 1},
    ]

    if format_ == "csv":
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=["member_id", "name", "points"])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
        return Response(
            buf.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=report.csv"},
        )
    # Fallback JSON
    return {"rows": rows}, 200
