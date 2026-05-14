-- :name get_item_by_num :one
SELECT *
FROM v_item_details
WHERE item_num = :item_num;

-- :name get_items_by_campus_filtered :many
SELECT *,
       COUNT(*) OVER() AS total_count
FROM v_item_details
WHERE campus_id = :campus_id
AND (:item_status IS NULL OR item_status = :item_status)
AND (:category_id IS NULL OR category_id = :category_id)
AND (:search_text IS NULL OR item_name ILIKE :search_text OR item_description ILIKE :search_text)
ORDER BY item_date_received DESC
LIMIT :limit OFFSET :offset;

-- :name get_admin_items_filtered :many
SELECT *,
       COUNT(*) OVER() AS total_count
FROM v_item_details
WHERE (:campus_id IS NULL OR campus_id = :campus_id)
AND (:item_status IS NULL OR item_status = :item_status)
AND (:category_id IS NULL OR category_id = :category_id)
AND (:search_text IS NULL OR item_name ILIKE :search_text OR item_description ILIKE :search_text)
ORDER BY item_date_received DESC
LIMIT :limit OFFSET :offset;

-- :name insert_found_item :scalar
INSERT INTO found_item (item_name, item_description, item_date_received, item_status, item_image_url, category_id, staff_num, campus_id)
VALUES (:item_name, :item_description, :item_date_received, 'in storage', :item_image_url, :category_id, :staff_num, :campus_id)
RETURNING item_num;

-- :name update_item_status :affected
UPDATE found_item
SET item_status = :item_status
WHERE item_num = :item_num;

-- :name update_found_item :affected
UPDATE found_item
SET item_name = :item_name,
    item_description = :item_description,
    category_id = :category_id,
    item_image_url = COALESCE(:item_image_url, item_image_url)
WHERE item_num = :item_num;

-- :name get_all_items :many
SELECT *, COUNT(*) OVER() AS total_count FROM found_item
ORDER BY
  CASE WHEN :sort_text = 'asc' THEN item_date_received END ASC,
  CASE WHEN :sort_text = 'desc' THEN item_date_received END DESC
LIMIT :limit OFFSET :offset;

-- :name get_items_by_search_category_and_campus :many
SELECT *, COUNT(*) OVER() AS total_count FROM found_item 
WHERE campus_id IN :campuses
AND category_id IN :categories
AND (item_name ILIKE :search_text OR item_description ILIKE :search_text)
ORDER BY
  CASE WHEN :sort_text = 'asc' THEN item_date_received END ASC,
  CASE WHEN :sort_text = 'desc' THEN item_date_received END DESC
LIMIT :limit OFFSET :offset;

-- :name get_items_by_search_and_campus :many
SELECT *, COUNT(*) OVER() AS total_count FROM found_item 
WHERE campus_id IN :campuses
AND (item_name ILIKE :search_text OR item_description ILIKE :search_text)
ORDER BY
    CASE WHEN :sort_text = 'asc' THEN item_date_received END ASC,
    CASE WHEN :sort_text = 'desc' THEN item_date_received END DESC
LIMIT :limit OFFSET :offset;

-- :name get_items_by_search_and_category :many
SELECT *, COUNT(*) OVER() AS total_count FROM found_item 
WHERE category_id IN :categories
AND (item_name ILIKE :search_text OR item_description ILIKE :search_text)
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
WHERE (item_name ILIKE :search_text OR item_description ILIKE :search_text)
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
