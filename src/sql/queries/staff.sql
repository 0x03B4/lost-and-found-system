-- :name get_staff_by_num :one
SELECT * FROM staff_member
WHERE staff_num = :staff_num;

-- :name get_staff_details :one
SELECT staff_member.staff_num,
       staff_member.staff_fname,
       staff_member.staff_lname,
       staff_member.role_id,
       COALESCE(STRING_AGG(campus.campus_name, ', '), 'All Campuses') AS campuses
FROM staff_member
LEFT JOIN campus_staff_assignment
       ON staff_member.staff_num = campus_staff_assignment.staff_num
LEFT JOIN campus
       ON campus_staff_assignment.campus_id = campus.campus_id
WHERE staff_member.staff_num = :staff_num
GROUP BY staff_member.staff_num,
         staff_member.staff_fname,
         staff_member.staff_lname,
         staff_member.role_id;

-- :name update_staff_password :affected
UPDATE staff_member
SET staff_password_hash = :password_hash
WHERE staff_num = :staff_num;

-- :name get_campuses_by_staff :many
SELECT campus_id FROM campus_staff_assignment
WHERE staff_num = :staff_num;

-- :name get_all_staff_details :many
SELECT staff_member.staff_num,
       staff_member.staff_fname,
       staff_member.staff_lname,
       staff_member.staff_email,
       staff_member.role_id,
       COALESCE(STRING_AGG(campus.campus_name, ', '), 'None') AS campuses,
       (SELECT COUNT(*) FROM found_item WHERE found_item.staff_num = staff_member.staff_num) AS item_count,
       (SELECT COUNT(*) FROM claim WHERE claim.staff_num = staff_member.staff_num) AS claim_count
FROM staff_member
LEFT JOIN campus_staff_assignment
       ON staff_member.staff_num = campus_staff_assignment.staff_num
LEFT JOIN campus
       ON campus_staff_assignment.campus_id = campus.campus_id
GROUP BY staff_member.staff_num,
         staff_member.staff_fname,
         staff_member.staff_lname,
         staff_member.staff_email,
         staff_member.role_id
ORDER BY staff_member.staff_fname ASC, staff_member.staff_lname ASC;

-- :name insert_staff :affected
INSERT INTO staff_member (staff_num, staff_fname, staff_lname, staff_email, staff_password_hash, role_id)
VALUES (:staff_num, :staff_fname, :staff_lname, :staff_email, :staff_password_hash, :role_id);

-- :name insert_campus_assignment :affected
INSERT INTO campus_staff_assignment (staff_num, campus_id)
VALUES (:staff_num, :campus_id);

-- :name delete_campus_assignments :affected
DELETE FROM campus_staff_assignment
WHERE staff_num = :staff_num;


