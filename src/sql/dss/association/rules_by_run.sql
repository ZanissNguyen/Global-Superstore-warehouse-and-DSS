SELECT antecedent_names, consequent_names, support::float AS support,
       confidence::float AS confidence, lift::float AS lift
FROM dss.association_rule WHERE run_id=:run_id ORDER BY lift DESC
