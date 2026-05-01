-- :name get_staff_by_num :one
SELECT * FROM staff_member
WHERE staff_num = :staff_num;

-- :name get_staff_details :one
SELECT s.staff_num, s.staff_fname, s.staff_lname, s.role_id,
       COALESCE(STRING_AGG(c.campus_name, ', '), 'All Campuses') as campuses
FROM staff_member s
LEFT JOIN campus_staff_assignment csa ON s.staff_num = csa.staff_num
LEFT JOIN campus c ON csa.campus_id = c.campus_id
WHERE s.staff_num = :staff_num
GROUP BY s.staff_num, s.staff_fname, s.staff_lname, s.role_id;

-- :name update_staff_password :affected
UPDATE staff_member
SET staff_password_hash = :password_hash
WHERE staff_num = :staff_num;

-- :name get_campuses_by_staff :many
SELECT campus_id FROM campus_staff_assignment
WHERE staff_num = :staff_num;
