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
