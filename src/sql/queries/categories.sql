-- :name get_all_categories :many
SELECT * FROM category
ORDER BY category_name ASC;

-- :name get_all_categories_with_counts :many
SELECT category.category_id, category.category_name, COUNT(found_item.item_num) AS item_count
FROM category
LEFT JOIN found_item ON category.category_id = found_item.category_id
GROUP BY category.category_id, category.category_name
ORDER BY category.category_name ASC;

-- :name get_category_by_id :one
SELECT * FROM category WHERE category_id = :category_id;

-- :name get_category_by_name :one
SELECT * FROM category WHERE LOWER(category_name) = LOWER(:category_name);

-- :name insert_category :scalar
INSERT INTO category (category_name)
VALUES (:category_name)
RETURNING category_id;

-- :name delete_category :affected
DELETE FROM category WHERE category_id = :category_id;

-- :name count_items_by_category :scalar
SELECT COUNT(*) FROM found_item WHERE category_id = :category_id;