-- :name get_staff_by_num :one
SELECT * FROM staff_member
WHERE staff_num = :staff_num;

-- :name get_staff_details :one
SELECT staff_num, staff_fname, staff_lname, role_id,
       COALESCE(campuses, 'All Campuses') AS campuses
FROM v_staff_details
WHERE staff_num = :staff_num;

-- :name update_staff_password :affected
UPDATE staff_member
SET staff_password_hash = :password_hash
WHERE staff_num = :staff_num;

-- :name get_campuses_by_staff :many
SELECT campus_id FROM campus_staff_assignment
WHERE staff_num = :staff_num;

-- :name get_all_staff_details :many
SELECT v_staff_details.staff_num,
       v_staff_details.staff_fname,
       v_staff_details.staff_lname,
       v_staff_details.staff_email,
       v_staff_details.role_id,
       v_staff_details.campuses,
       (SELECT COUNT(*) FROM found_item WHERE found_item.staff_num = v_staff_details.staff_num) AS item_count,
       (SELECT COUNT(*) FROM claim WHERE claim.staff_num = v_staff_details.staff_num) AS claim_count
FROM v_staff_details
ORDER BY v_staff_details.staff_fname ASC, v_staff_details.staff_lname ASC;

-- :name insert_staff :affected
INSERT INTO staff_member (staff_num, staff_fname, staff_lname, staff_email, staff_password_hash, role_id)
VALUES (:staff_num, :staff_fname, :staff_lname, :staff_email, :staff_password_hash, :role_id);

-- :name insert_campus_assignment :affected
INSERT INTO campus_staff_assignment (staff_num, campus_id)
VALUES (:staff_num, :campus_id);

-- :name delete_campus_assignments :affected
DELETE FROM campus_staff_assignment
WHERE staff_num = :staff_num;


