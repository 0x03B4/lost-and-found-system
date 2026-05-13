CREATE TABLE category (
    category_id SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    category_name VARCHAR(30) UNIQUE NOT NULL
);

CREATE TABLE campus (
    campus_id VARCHAR(3) PRIMARY KEY,
    campus_name VARCHAR(15) UNIQUE NOT NULL,

    CONSTRAINT ck_campus_id_limit
        CHECK (UPPER(campus_id) IN ('MAF', 'POT', 'VAN'))
);

CREATE TABLE building (
    campus_id VARCHAR(3) NOT NULL,
    building_code VARCHAR(5) NOT NULL,

    CONSTRAINT pk_building
        PRIMARY KEY (campus_id, building_code),

    CONSTRAINT fk_building_campus
        FOREIGN KEY (campus_id) REFERENCES campus(campus_id)
);

CREATE TABLE role (
    role_id VARCHAR(5) PRIMARY KEY,
    role_name VARCHAR(30) UNIQUE NOT NULL,

    CONSTRAINT ck_role_id_limit
        CHECK (UPPER(role_id) IN ('ADMIN', 'STAFF'))
);

CREATE TABLE staff_member (
    staff_num INTEGER PRIMARY KEY,
    staff_fname VARCHAR(50) NOT NULL,
    staff_lname VARCHAR(50) NOT NULL,
    staff_email CITEXT UNIQUE NOT NULL,
    staff_password_hash VARCHAR(255) NOT NULL,
    role_id VARCHAR(5) NOT NULL,

    CONSTRAINT ck_staff_member_num_range
        CHECK (staff_num BETWEEN 0 AND 99999999),
    CONSTRAINT ck_staff_member_nwu_email
        CHECK (staff_email ~ '^[A-Za-z0-9._%+-]+@nwu\.ac\.za$'),
    CONSTRAINT fk_staff_member_role
        FOREIGN KEY (role_id) REFERENCES role(role_id)
);

CREATE TABLE found_item (
    item_num BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    item_name TEXT NOT NULL,
    item_description TEXT NOT NULL,
    item_date_received TIMESTAMPTZ NOT NULL,
    item_status TEXT NOT NULL,
    item_image_url TEXT,
    category_id SMALLINT NOT NULL,
    staff_num INTEGER NOT NULL,
    campus_id VARCHAR(3) NOT NULL,

    CONSTRAINT ck_found_item_status
        CHECK (LOWER(item_status) IN ('in storage', 'disposed', 'claimed')),
    CONSTRAINT fk_found_item_category
        FOREIGN KEY (category_id) REFERENCES category(category_id),
    CONSTRAINT fk_found_item_staff_member
        FOREIGN KEY (staff_num) REFERENCES staff_member(staff_num),
    CONSTRAINT fk_found_item_campus
        FOREIGN KEY (campus_id) REFERENCES campus(campus_id)
);

CREATE TABLE claimant (
    claimant_num INTEGER PRIMARY KEY,
    claimant_fname VARCHAR(50) NOT NULL,
    claimant_lname VARCHAR(50) NOT NULL,
    claimant_email CITEXT UNIQUE NOT NULL,

    CONSTRAINT ck_claimant_claimant_num_range
        CHECK (claimant_num BETWEEN 0 AND 99999999),
    CONSTRAINT ck_claimant_email
        CHECK (claimant_email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

CREATE TABLE claim (
    claim_num BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    claim_date TIMESTAMPTZ NOT NULL,
    item_num BIGINT UNIQUE NOT NULL,
    staff_num INTEGER NOT NULL,
    claimant_num INTEGER NOT NULL,

    CONSTRAINT fk_claim_found_item
        FOREIGN KEY (item_num) REFERENCES found_item(item_num),
    CONSTRAINT fk_claim_staff_member
        FOREIGN KEY (staff_num) REFERENCES staff_member(staff_num),
    CONSTRAINT fk_claim_claimant
        FOREIGN KEY (claimant_num) REFERENCES claimant(claimant_num)
);

CREATE TABLE campus_staff_assignment (
    staff_num INTEGER NOT NULL,
    campus_id VARCHAR(3) NOT NULL,

    CONSTRAINT pk_assignment
        PRIMARY KEY (staff_num, campus_id),

    CONSTRAINT fk_campus_staff_assignment_staff_member
        FOREIGN KEY (staff_num) REFERENCES staff_member(staff_num),
    CONSTRAINT fk_campus_staff_assignment_campus
        FOREIGN KEY (campus_id) REFERENCES campus(campus_id)
);
