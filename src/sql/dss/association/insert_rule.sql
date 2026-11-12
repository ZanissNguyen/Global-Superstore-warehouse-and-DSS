INSERT INTO dss.association_rule (
    run_id, antecedents, consequents, antecedent_names, consequent_names,
    support, confidence, lift
) VALUES (
    :run_id, :ant, :con, :ant_name, :con_name, :supp, :conf, :lift
)
