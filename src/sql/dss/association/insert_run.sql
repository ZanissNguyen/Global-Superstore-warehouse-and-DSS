INSERT INTO dss.association_run (
    algorithm, min_support, min_confidence, min_lift, transaction_count, rules_found
) VALUES (
    'Pairwise association mining', :min_supp, :min_conf, :min_lift, :tx_cnt, :rules_cnt
) RETURNING run_id
