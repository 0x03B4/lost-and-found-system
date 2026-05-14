-- Eliminates JOIN repetition in: get_item_by_num, get_items_by_campus_filtered, get_admin_items_filtered
CREATE VIEW v_item_details AS
SELECT found_item.item_num, found_item.item_name, found_item.item_description,
       found_item.item_date_received, found_item.item_status, found_item.item_image_url,
       found_item.category_id, found_item.staff_num, found_item.campus_id,
       category.category_name, campus.campus_name
FROM found_item
JOIN category ON found_item.category_id = category.category_id
JOIN campus ON found_item.campus_id = campus.campus_id;

-- Eliminates complex 4-table JOIN in: get_claim_by_num, get_claim_by_item_num
CREATE VIEW v_claim_details AS
SELECT claim.claim_num, claim.claim_date, claim.item_num, claim.staff_num, claim.claimant_num,
       found_item.item_name, found_item.item_description, found_item.item_status,
       category.category_name,
       staff_member.staff_fname, staff_member.staff_lname,
       claimant.claimant_fname, claimant.claimant_lname, claimant.claimant_email
FROM claim
JOIN found_item ON claim.item_num = found_item.item_num
JOIN category ON found_item.category_id = category.category_id
JOIN staff_member ON claim.staff_num = staff_member.staff_num
JOIN claimant ON claim.claimant_num = claimant.claimant_num;

-- Eliminates duplication in: get_staff_details, get_all_staff_details
CREATE VIEW v_staff_details AS
SELECT staff_member.staff_num,
       staff_member.staff_fname,
       staff_member.staff_lname,
       staff_member.staff_email,
       staff_member.role_id,
       COALESCE(STRING_AGG(campus.campus_name, ', '), 'None') AS campuses
FROM staff_member
LEFT JOIN campus_staff_assignment ON staff_member.staff_num = campus_staff_assignment.staff_num
LEFT JOIN campus ON campus_staff_assignment.campus_id = campus.campus_id
GROUP BY staff_member.staff_num, staff_member.staff_fname, staff_member.staff_lname,
         staff_member.staff_email, staff_member.role_id;

-- Single source of truth for status calculations in: get_global_stats, get_analytics_summary, get_stats_by_campus
CREATE VIEW v_item_status_summary AS
SELECT found_item.campus_id,
       COUNT(*) FILTER (WHERE item_status = 'in storage') AS in_storage,
       COUNT(*) FILTER (WHERE item_status = 'claimed') AS claimed,
       COUNT(*) FILTER (WHERE item_status = 'disposed') AS disposed,
       COUNT(*) AS total_items
FROM found_item
GROUP BY found_item.campus_id;

-- Isolates complex temporal calculations in: get_monthly_trend
CREATE VIEW v_monthly_item_trends AS
SELECT found_item.campus_id,
       TO_CHAR(found_item.item_date_received, 'Month YYYY') AS month_label,
       EXTRACT(YEAR FROM found_item.item_date_received) AS trend_year,
       EXTRACT(MONTH FROM found_item.item_date_received) AS trend_month,
       COUNT(*) AS items_received,
       COUNT(claim.claim_num) AS claims_made
FROM found_item
LEFT JOIN claim ON found_item.item_num = claim.item_num
GROUP BY found_item.campus_id, month_label, trend_year, trend_month;
