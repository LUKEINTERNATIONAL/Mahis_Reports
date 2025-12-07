
DB_CONFIG = {
    'host': 'hostname',
    'user': 'user',
    'password': 'password',
    'database': 'database',
    'port': 3306
}

SSH_CONFIG = {
    'ssh_host': 'aws_host',
    'ssh_port': 22,
    'ssh_user': 'ubuntu',
    'ssh_pkey': 'key.pem',  # Path to your private key
    'remote_bind_address': ('path_to_db_endpoint', 3306)
}

# For local database connection
DB_CONFIG_LOCAL = {
    'host': 'localhost',
    'user': 'user',
    'password': 'password',
    'database': 'local_database',
    'port': 3306
}


# on production remove COLLATE utf8mb3_general_ci
QERY_OPD_TEST = """
SELECT 
    main.*,
    CASE 
        WHEN visit_days = 1 THEN 'New'
        ELSE 'Revisit'
    END AS new_revisit
FROM (
    SELECT 
        p.person_id,
        e.encounter_id,
        gender AS Gender, 
        FLOOR(DATEDIFF(CURRENT_DATE, birthdate) / 365) AS Age, 
        CASE 
            WHEN FLOOR(DATEDIFF(CURRENT_DATE, birthdate) / 365) < 5 THEN 'Under 5'
            ELSE 'Over 5'
        END AS Age_Group,
        DATE(e.encounter_datetime) AS Date, 
        pr.name AS Program, 
        l.name AS Facility,
        l.code AS Facility_CODE, 
        u.username AS User, 
        l.district AS District, 
        et.name AS Encounter,
        pa.state_province AS Home_district,
        pa.township_division AS TA,
        pa.city_village AS Village,
        v.visit_days,
        cn.name AS obs_value_coded,
        c.name AS concept_name,
        o.value_text as Value,
        o.value_numeric as ValueN,
        d.name as DrugName,
        cnn.name as Value_name
    FROM person AS p
    JOIN patient AS pa2 ON p.person_id = pa2.patient_id
    JOIN person_address AS pa ON p.person_id = pa.person_id
    JOIN encounter AS e ON p.person_id = e.patient_id
    JOIN encounter_type AS et ON e.encounter_type = et.encounter_type_id
    INNER JOIN program AS pr ON e.program_id = pr.program_id
    INNER JOIN users AS u ON e.provider_id = u.user_id
    INNER JOIN facilities AS l ON u.location_id = l.code COLLATE utf8mb3_general_ci
    -- Join with precomputed visit days
    JOIN (
        SELECT patient_id, COUNT(DISTINCT DATE(encounter_datetime)) AS visit_days
        FROM encounter
        GROUP BY patient_id
    ) AS v ON v.patient_id = p.person_id
    LEFT JOIN obs o ON o.encounter_id = e.encounter_id
    LEFT JOIN concept_name cn ON o.value_coded = cn.concept_id AND cn.locale = 'en' AND cn.concept_name_type = 'FULLY_SPECIFIED'
    LEFT JOIN concept_name c ON o.concept_id = c.concept_id
    LEFT JOIN concept co ON o.value_text = co.uuid
    LEFT JOIN concept_name cnn ON co.concept_id = cnn.concept_id
    LEFT JOIN drug as d on o.value_drug = d.drug_id
    WHERE p.voided = 0
    {date_filter}
) AS main

"""