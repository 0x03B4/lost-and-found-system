-- :name get_item_by_num :one
SELECT found_item.item_num, found_item.item_name, found_item.item_description,
       found_item.item_date_received, found_item.item_status, found_item.item_image_url,
       found_item.category_id, found_item.staff_num, found_item.campus_id,
       category.category_name, campus.campus_name
FROM found_item
JOIN category ON found_item.category_id = category.category_id
JOIN campus ON found_item.campus_id = campus.campus_id
WHERE found_item.item_num = :item_num;

-- :name get_items_by_campus_filtered :many
SELECT found_item.item_num, found_item.item_name, found_item.item_description,
       found_item.item_date_received, found_item.item_status, found_item.item_image_url,
       found_item.category_id, found_item.staff_num, found_item.campus_id,
       category.category_name, campus.campus_name,
       COUNT(*) OVER() AS total_count
FROM found_item
JOIN category ON found_item.category_id = category.category_id
JOIN campus ON found_item.campus_id = campus.campus_id
WHERE found_item.campus_id = :campus_id
AND (:item_status IS NULL OR found_item.item_status = :item_status)
AND (:category_id IS NULL OR found_item.category_id = :category_id)
AND (:search_text IS NULL OR found_item.item_name ILIKE :search_text)
ORDER BY found_item.item_date_received DESC
LIMIT :limit OFFSET :offset;

-- :name get_admin_items_filtered :many
SELECT found_item.item_num, found_item.item_name, found_item.item_description,
       found_item.item_date_received, found_item.item_status, found_item.item_image_url,
       found_item.category_id, found_item.staff_num, found_item.campus_id,
       category.category_name, campus.campus_name,
       COUNT(*) OVER() AS total_count
FROM found_item
JOIN category ON found_item.category_id = category.category_id
JOIN campus ON found_item.campus_id = campus.campus_id
WHERE (:campus_id IS NULL OR found_item.campus_id = :campus_id)
AND (:item_status IS NULL OR found_item.item_status = :item_status)
AND (:category_id IS NULL OR found_item.category_id = :category_id)
AND (:search_text IS NULL OR found_item.item_name ILIKE :search_text)
ORDER BY found_item.item_date_received DESC
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
