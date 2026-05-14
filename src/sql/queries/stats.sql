-- :name get_items_logged_today_by_staff :scalar
SELECT COUNT(*) FROM found_item
WHERE staff_num = :staff_num
AND item_date_received::date = CURRENT_DATE;

-- :name get_claims_today_by_staff :scalar
SELECT COUNT(*) FROM claim
WHERE staff_num = :staff_num
AND claim_date::date = CURRENT_DATE;

-- :name get_items_in_storage_by_campus :scalar
SELECT COUNT(*) FROM found_item
WHERE campus_id = :campus_id
AND item_status = 'in storage';

-- :name get_global_stats :one
SELECT
    COUNT(*) FILTER (WHERE item_status = 'in storage') AS in_storage,
    COUNT(*) FILTER (WHERE item_status = 'claimed') AS claimed,
    COUNT(*) FILTER (WHERE item_status = 'disposed') AS disposed
FROM found_item;

-- :name get_stats_by_campus :many
SELECT
    campus.campus_id,
    campus.campus_name,
    COUNT(*) FILTER (WHERE found_item.item_status = 'in storage') AS in_storage,
    COUNT(*) FILTER (WHERE found_item.item_status = 'claimed') AS claimed,
    COUNT(*) FILTER (WHERE found_item.item_status = 'disposed') AS disposed
FROM campus
LEFT JOIN found_item ON campus.campus_id = found_item.campus_id
GROUP BY campus.campus_id, campus.campus_name
ORDER BY campus.campus_name;

-- :name get_analytics_summary :one
SELECT
    COALESCE(COUNT(*) FILTER (WHERE item_status = 'in storage'), 0) AS in_storage,
    COALESCE(COUNT(*) FILTER (WHERE item_status = 'claimed'), 0) AS claimed,
    COALESCE(COUNT(*) FILTER (WHERE item_status = 'disposed'), 0) AS disposed
FROM found_item
WHERE (:campus_id IS NULL OR campus_id = :campus_id)
AND (:year IS NULL OR EXTRACT(YEAR FROM item_date_received) = :year)
AND (:quarter IS NULL OR EXTRACT(QUARTER FROM item_date_received) = :quarter);

-- :name get_most_lost_category :one
SELECT category.category_name, COUNT(*) AS item_count
FROM found_item
JOIN category ON found_item.category_id = category.category_id
WHERE (:campus_id IS NULL OR found_item.campus_id = :campus_id)
AND (:year IS NULL OR EXTRACT(YEAR FROM found_item.item_date_received) = :year)
AND (:quarter IS NULL OR EXTRACT(QUARTER FROM found_item.item_date_received) = :quarter)
GROUP BY category.category_name
ORDER BY item_count DESC
LIMIT 1;

-- :name get_category_distribution :many
SELECT category.category_name,
       COUNT(*) AS item_count,
       COALESCE(ROUND(COUNT(*) * 100.0 / NULLIF(SUM(COUNT(*)) OVER(), 0), 1), 0) AS percentage
FROM found_item
JOIN category ON found_item.category_id = category.category_id
WHERE (:campus_id IS NULL OR found_item.campus_id = :campus_id)
AND (:year IS NULL OR EXTRACT(YEAR FROM found_item.item_date_received) = :year)
AND (:quarter IS NULL OR EXTRACT(QUARTER FROM found_item.item_date_received) = :quarter)
GROUP BY category.category_name
ORDER BY item_count DESC;

-- :name get_campus_volume :many
SELECT campus.campus_id,
       campus.campus_name,
       COUNT(found_item.item_num) AS item_count,
       COALESCE(ROUND(COUNT(found_item.item_num) * 100.0 / NULLIF(SUM(COUNT(found_item.item_num)) OVER(), 0), 1), 0) AS percentage
FROM campus
LEFT JOIN found_item ON campus.campus_id = found_item.campus_id
AND (:year IS NULL OR EXTRACT(YEAR FROM found_item.item_date_received) = :year)
AND (:quarter IS NULL OR EXTRACT(QUARTER FROM found_item.item_date_received) = :quarter)
GROUP BY campus.campus_id, campus.campus_name
ORDER BY item_count DESC;

-- :name get_monthly_trend :many
SELECT
    TO_CHAR(found_item.item_date_received, 'Month YYYY') AS month_label,
    EXTRACT(YEAR FROM found_item.item_date_received) AS trend_year,
    EXTRACT(MONTH FROM found_item.item_date_received) AS trend_month,
    COUNT(*) AS items_received,
    COUNT(claim.claim_num) AS claims_made,
    COALESCE(CASE
        WHEN COUNT(*) = 0 THEN 0
        ELSE ROUND(COUNT(claim.claim_num) * 100.0 / COUNT(*), 1)
    END, 0) AS claim_rate
FROM found_item
LEFT JOIN claim ON found_item.item_num = claim.item_num
WHERE (:campus_id IS NULL OR found_item.campus_id = :campus_id)
AND (:year IS NULL OR EXTRACT(YEAR FROM found_item.item_date_received) = :year)
AND (:quarter IS NULL OR EXTRACT(QUARTER FROM found_item.item_date_received) = :quarter)
GROUP BY month_label, trend_year, trend_month
ORDER BY trend_year DESC, trend_month DESC;
