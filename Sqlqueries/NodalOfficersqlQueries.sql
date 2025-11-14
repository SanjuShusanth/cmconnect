WITH base AS (
    SELECT 
        new_department,
        grievance_id,
        status,
        ticket_currently_pending_with
    FROM staging_grievance
),
summary AS (
    SELECT 
        new_department,
        COUNT(DISTINCT grievance_id)::int AS total_tickets,
        COUNT(DISTINCT CASE WHEN status = 'Pending' THEN grievance_id END)::int AS pending_tickets,
        COUNT(DISTINCT CASE WHEN status = 'Closed' THEN grievance_id END)::int AS closed_tickets
    FROM base
    GROUP BY new_department
),
officer_rank AS (
    SELECT 
        new_department,
        ticket_currently_pending_with AS nodal_officer,
        COUNT(DISTINCT grievance_id)::int AS officer_pending,
        ROW_NUMBER() OVER (
            PARTITION BY new_department 
            ORDER BY COUNT(DISTINCT grievance_id) DESC
        ) AS rn
    FROM base
    WHERE status = 'Pending'
    GROUP BY new_department, ticket_currently_pending_with
),
final AS (
    SELECT 
        s.new_department AS department_name,
        s.total_tickets,
        s.pending_tickets,
        s.closed_tickets,
        COALESCE(o.nodal_officer, 'Unassigned') AS nodal_officer,
        COALESCE(o.officer_pending, 0)::int AS nodal_officer_pending_count
    FROM summary s
    LEFT JOIN officer_rank o 
        ON s.new_department = o.new_department AND o.rn = 1
),
combined AS (
    SELECT 
        department_name,
        total_tickets,
        pending_tickets,
        closed_tickets,
        nodal_officer,
        nodal_officer_pending_count,
        0 AS sort_order
    FROM final

    UNION ALL

    SELECT 
        'Grand Total' AS department_name,
        SUM(total_tickets)::int,
        SUM(pending_tickets)::int,
        SUM(closed_tickets)::int,
        '—' AS nodal_officer,
        SUM(nodal_officer_pending_count)::int,
        1 AS sort_order
    FROM final
)
SELECT 
    department_name AS "Department Name",
    total_tickets AS "Total Ticket",
    pending_tickets AS "Pending Ticket",
    closed_tickets AS "Closed Ticket",
    nodal_officer AS "Pending With Nodal Officer",
    nodal_officer_pending_count AS "Nodal Officer Pending Count"
FROM combined
ORDER BY sort_order, total_tickets DESC;
