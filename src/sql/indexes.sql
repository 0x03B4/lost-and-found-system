-- Queries that are affected: get_items_by_campus_filtered, get_admin_items_filtered, get_analytics_summary, get_stats_by_campus, get_items_in_storage_by_campus
CREATE INDEX idx_found_item_campus_status_date ON found_item (campus_id, item_status, item_date_received DESC);

-- Queries that are affected: get_items_by_campus_filtered, get_admin_items_filtered, get_items_by_search_and_campus, get_items_by_category_and_campus
CREATE INDEX idx_found_item_campus_category_date ON found_item (campus_id, category_id, item_date_received DESC);

-- Queries that are affected: get_all_categories_with_counts, get_category_distribution, get_most_lost_category, count_items_by_category
CREATE INDEX idx_found_item_category ON found_item (category_id);

-- Queries that are affected: get_claims_by_campus, get_claims_today_by_staff, get_all_staff_details
CREATE INDEX idx_claim_staff_date ON claim (staff_num, claim_date DESC);

-- Queries that are affected: get_all_staff_details, get_items_logged_today_by_staff
CREATE INDEX idx_found_item_staff ON found_item (staff_num);

-- Queries that are affected: get_global_stats, get_analytics_summary
CREATE INDEX idx_found_item_status ON found_item (item_status);

-- Queries that are affected: get_analytics_summary, get_category_distribution, get_monthly_trend
CREATE INDEX idx_found_item_date_received ON found_item (item_date_received);

-- Queries that are affected: get_campuses_by_staff, get_staff_details, get_all_staff_details
CREATE INDEX idx_campus_staff_assignment_staff ON campus_staff_assignment (staff_num);

-- Queries that are affected: get_category_by_name
CREATE INDEX idx_category_name ON category (category_name);