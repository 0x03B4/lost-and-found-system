-- :name get_claimant_by_num :one
SELECT * FROM claimant
WHERE claimant_num = :claimant_num;

-- :name upsert_claimant :affected
INSERT INTO claimant (claimant_num, claimant_name, claimant_email)
VALUES (:claimant_num, :claimant_name, :claimant_email)
ON CONFLICT (claimant_num) DO UPDATE
SET claimant_name = EXCLUDED.claimant_name,
    claimant_email = EXCLUDED.claimant_email;

-- :name insert_claim :scalar
INSERT INTO claim (claim_date, item_num, staff_num, claimant_num)
VALUES (:claim_date, :item_num, :staff_num, :claimant_num)
RETURNING claim_num;

-- :name get_claim_by_num :one
SELECT claim.claim_num, claim.claim_date, claim.item_num, claim.staff_num, claim.claimant_num,
       found_item.item_name, found_item.item_description, found_item.item_status,
       category.category_name,
       staff_member.staff_fname, staff_member.staff_lname,
       claimant.claimant_name, claimant.claimant_email
FROM claim
JOIN found_item ON claim.item_num = found_item.item_num
JOIN category ON found_item.category_id = category.category_id
JOIN staff_member ON claim.staff_num = staff_member.staff_num
JOIN claimant ON claim.claimant_num = claimant.claimant_num
WHERE claim.claim_num = :claim_num;

-- :name get_claim_by_item_num :one
SELECT claim.claim_num, claim.claim_date, claim.item_num, claim.staff_num, claim.claimant_num,
       found_item.item_name, found_item.item_description, found_item.item_status,
       category.category_name,
       staff_member.staff_fname, staff_member.staff_lname,
       claimant.claimant_name, claimant.claimant_email
FROM claim
JOIN found_item ON claim.item_num = found_item.item_num
JOIN category ON found_item.category_id = category.category_id
JOIN staff_member ON claim.staff_num = staff_member.staff_num
JOIN claimant ON claim.claimant_num = claimant.claimant_num
WHERE claim.item_num = :item_num;

-- :name get_claims_by_campus :many
SELECT claim.claim_num, claim.claim_date, claim.item_num, claim.staff_num, claim.claimant_num,
       found_item.item_name,
       claimant.claimant_name,
       COUNT(*) OVER() AS total_count
FROM claim
JOIN found_item ON claim.item_num = found_item.item_num
JOIN claimant ON claim.claimant_num = claimant.claimant_num
WHERE found_item.campus_id = :campus_id
AND (:search_text IS NULL 
    OR found_item.item_name ILIKE :search_text 
    OR claimant.claimant_name ILIKE :search_text
    OR CAST(claimant.claimant_num AS TEXT) ILIKE :search_text
    OR CAST(found_item.item_num AS TEXT) ILIKE REPLACE(REPLACE(UPPER(:search_text), '#ITM-', ''), 'ITM-', '')
    OR CAST(claim.claim_num AS TEXT) ILIKE REPLACE(REPLACE(UPPER(:search_text), '#CLM-', ''), 'CLM-', '')
)
AND (:year IS NULL OR EXTRACT(YEAR FROM claim.claim_date) = :year)
AND (:month IS NULL OR EXTRACT(MONTH FROM claim.claim_date) = :month)
ORDER BY claim.claim_date DESC
LIMIT :limit OFFSET :offset;
