SELECT
    antecedent_names AS antecedent,
    consequent_names AS consequent,
    ROUND(support * 100, 2) AS support_pct,
    ROUND(confidence * 100, 2) AS confidence_pct,
    ROUND(lift, 2) AS lift
FROM dss.association_rule
ORDER BY lift DESC
LIMIT :limit;
