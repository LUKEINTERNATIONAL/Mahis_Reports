
DB_CONFIG_AWS_TEST = {
    'host': 'hostname',
    'user': 'user',
    'password': 'password',
    'database': 'database',
    'port': 3306
}

SSH_CONFIG_TEST = {
    'ssh_host': 'aws_host',
    'ssh_port': 22,
    'ssh_user': 'ubuntu',
    'ssh_pkey': 'key.pem',  # Path to your private key
    'remote_bind_address': ('path_to_db_endpoint', 3306)
}

DB_CONFIG_AWS_PROD = {

}


QERY_OPD_PROD = """
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
    INNER JOIN facilities AS l ON u.location_id = l.code
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
ORDER BY Date asc
"""

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

# on test use INNER JOIN facilities AS l ON u.location_id = l.code COLLATE utf8mb3_general_ci


QERY2 = """
SELECT 
    e.visit_id, 
    e.encounter_id, 
    e.patient_id, 
    et.name AS encounter_type, 
    e.encounter_datetime, 
    p.gender, 
    CONCAT(pn.given_name, ' ', pn.family_name) AS full_name,
    CASE 
        WHEN TIMESTAMPDIFF(YEAR, p.birthdate, CURDATE()) < 10 THEN '0-9'
        WHEN TIMESTAMPDIFF(YEAR, p.birthdate, CURDATE()) BETWEEN 10 AND 19 THEN '10-19'
        WHEN TIMESTAMPDIFF(YEAR, p.birthdate, CURDATE()) BETWEEN 20 AND 29 THEN '20-29'
        WHEN TIMESTAMPDIFF(YEAR, p.birthdate, CURDATE()) BETWEEN 30 AND 39 THEN '30-39'
        WHEN TIMESTAMPDIFF(YEAR, p.birthdate, CURDATE()) BETWEEN 40 AND 49 THEN '40-49'
        WHEN TIMESTAMPDIFF(YEAR, p.birthdate, CURDATE()) BETWEEN 50 AND 59 THEN '50-59'
        WHEN TIMESTAMPDIFF(YEAR, p.birthdate, CURDATE()) BETWEEN 60 AND 69 THEN '60-69'
        WHEN TIMESTAMPDIFF(YEAR, p.birthdate, CURDATE()) BETWEEN 70 AND 79 THEN '70-79'
        ELSE '80+'
    END AS AgeBand,
    CASE
    -- Match times between 07:30 and 16:30 (same day)
        WHEN TIME(e.encounter_datetime) BETWEEN '07:30:00' AND '16:30:00' THEN 'day'
    
        -- Everything else is night
        ELSE 'night'
    END AS timeDay,
    CASE
        WHEN et.name = 'Airway Assessment' then 'Primary Assessment'
        WHEN et.name = 'Breathing Assessment' then 'Primary Assessment'
        WHEN et.name = 'CIRCULATION_ASSESSMENT' then 'Primary Assessment'
        WHEN et.name = 'EXPOSURE_ASSESSMENT' then 'Primary Assessment'
        WHEN et.name = 'Primary Disability Assessment' then 'Primary Assessment'
        WHEN et.name = 'CHEST ASSESSMENT' then 'Secondary Assessment'
        WHEN et.name = 'EXTREMITIES ASSESSMENT' then 'Secondary Assessment'
        WHEN et.name = 'HEAD AND NECK ASSESSMENT' then 'Secondary Assessment'
        WHEN et.name = 'NEUROLOGICAL EXAMINATION' then 'Secondary Assessment'
        WHEN et.name = 'ABDOMEN AND PELVIS ASSESSMENT' then 'Secondary Assessment'
        WHEN et.name = 'PROCEDURES DONE' then 'Monitoring Chart'
        WHEN et.name = 'FAMILY MEDICAL HISTORY' then 'Sample History'
        WHEN et.name = 'DIAGNOSIS' then 'Diagnosis'
    END AS Assessment_Type,
    cn.name AS obs_value_coded,
    c.name AS concept_name,
    o.value_text as Value,
    o.value_numeric as ValueN,
    cnn.name as Value_name
FROM encounter e
JOIN encounter_type et ON e.encounter_type = et.encounter_type_id
JOIN patient pa ON e.patient_id = pa.patient_id
JOIN person p ON pa.patient_id = p.person_id
LEFT JOIN obs o ON e.encounter_id = o.encounter_id AND o.voided = 0
LEFT JOIN concept_name cn ON o.value_coded = cn.concept_id AND cn.locale = 'en' AND cn.concept_name_type = 'FULLY_SPECIFIED'
LEFT JOIN concept_name c ON o.concept_id = c.concept_id
LEFT JOIN concept co ON o.value_text = co.uuid
LEFT JOIN concept_name cnn ON co.concept_id = cnn.concept_id
LEFT JOIN users u ON e.creator = u.user_id
LEFT JOIN person_name pn ON u.person_id = pn.person_id
WHERE e.voided = 0;
"""