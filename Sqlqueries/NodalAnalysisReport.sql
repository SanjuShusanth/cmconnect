WITH top_officers AS (
    SELECT 
        TRIM(ticket_currently_pending_with) AS officer,
        COUNT(DISTINCT grievance_id) AS pending_grievances
    FROM staging_grievance
    WHERE status = 'Pending'
    GROUP BY TRIM(ticket_currently_pending_with)
    ORDER BY COUNT(DISTINCT grievance_id) DESC
    LIMIT 20
)
SELECT 
    TRIM(sg.ticket_currently_pending_with) AS "User",
    sg.new_category AS "Category",
    COUNT(DISTINCT sg.grievance_id) AS "Pending Grievances",
    MAX(t.pending_grievances) AS "Total Pending (All Categories)"
FROM staging_grievance sg
JOIN top_officers t
    ON TRIM(sg.ticket_currently_pending_with) = t.officer
WHERE sg.status = 'Pending'
GROUP BY 
    TRIM(sg.ticket_currently_pending_with),
    sg.new_category
ORDER BY 
    MAX(t.pending_grievances) DESC,
    "User",
    "Pending Grievances" DESC;











