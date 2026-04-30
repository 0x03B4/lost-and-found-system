-- :name get_all_items :many
SELECT *, COUNT(*) OVER() AS total_count FROM found_item
LIMIT :limit OFFSET :offset;

-- :name get_items_by_search_category_and_campus :many
SELECT *, COUNT(*) OVER() AS total_count FROM found_item 
WHERE campus_id IN :campuses
AND category_id IN :categories
AND item_name ILIKE :search_text
ORDER BY
  CASE WHEN :sort_text = 'asc' THEN item_date_received END ASC,
  CASE WHEN :sort_text = 'desc' THEN item_date_received END DESC
LIMIT :limit OFFSET :offset;

-- :name get_items_by_search_and_campus :many
SELECT *, COUNT(*) OVER() AS total_count FROM found_item 
WHERE campus_id IN :campuses
AND item_name ILIKE :search_text
ORDER BY
    CASE WHEN :sort_text = 'asc' THEN item_date_received END ASC,
    CASE WHEN :sort_text = 'desc' THEN item_date_received END DESC
LIMIT :limit OFFSET :offset;

-- :name get_items_by_search_and_category :many
SELECT *, COUNT(*) OVER() AS total_count FROM found_item 
WHERE category_id IN :categories
AND item_name ILIKE :search_text
ORDER BY
  CASE WHEN :sort_text = 'asc' THEN item_date_received END ASC,
  CASE WHEN :sort_text = 'desc' THEN item_date_received END DESC
LIMIT :limit OFFSET :offset;

-- :name get_items_by_category_and_campus :many
SELECT *, COUNT(*) OVER() AS total_count FROM found_item 
WHERE campus_id IN :campuses
AND category_id IN :categories
ORDER BY
    CASE WHEN :sort_text = 'asc' THEN item_date_received END ASC,
    CASE WHEN :sort_text = 'desc' THEN item_date_received END DESC
LIMIT :limit OFFSET :offset;

-- :name get_items_by_search :many
SELECT *, COUNT(*) OVER() AS total_count FROM found_item 
WHERE item_name ILIKE :search_text
ORDER BY
  CASE WHEN :sort_text = 'asc' THEN item_date_received END ASC,
  CASE WHEN :sort_text = 'desc' THEN item_date_received END DESC
LIMIT :limit OFFSET :offset;

-- :name get_items_by_category :many
SELECT *, COUNT(*) OVER() AS total_count FROM found_item 
WHERE category_id IN :categories
ORDER BY
    CASE WHEN :sort_text = 'asc' THEN item_date_received END ASC,
    CASE WHEN :sort_text = 'desc' THEN item_date_received END DESC
LIMIT :limit OFFSET :offset;

-- :name get_items_by_campus :many
SELECT *, COUNT(*) OVER() AS total_count FROM found_item 
WHERE campus_id IN :campuses
ORDER BY
    CASE WHEN :sort_text = 'asc' THEN item_date_received END ASC,
    CASE WHEN :sort_text = 'desc' THEN item_date_received END DESC
LIMIT :limit OFFSET :offset;
