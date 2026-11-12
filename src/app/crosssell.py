"""Association rules from the active database and its current mining run."""

import pandas as pd
import streamlit as st
from sqlalchemy import text

from src.app.demo_backend import active_session
from src.pipeline.database import create_db_engine
from src.pipeline.reader import read_sql


def render_crosssell_tab(database):
    st.subheader("Cơ hội bán kèm")
    session = active_session()
    run_id = session["association_run_id"] if session and session["database_name"] == database else None
    engine = create_db_engine(database=database)
    try:
        if run_id is None:
            run = pd.read_sql(text(read_sql("dss/association/latest_run.sql")), engine)
        else:
            run = pd.read_sql(text(read_sql("dss/association/run_by_id.sql")), engine, params={"run_id": run_id})
        if run.empty:
            st.warning("Chưa có lần khai phá luật bán kèm.")
            return
        meta = run.iloc[0]
        rules = pd.read_sql(text(read_sql("dss/association/rules_by_run.sql")), engine, params={"run_id": int(meta.run_id)})
    finally:
        engine.dispose()
    a, b, c = st.columns(3)
    a.metric("Số giao dịch phân tích", f"{int(meta.transaction_count):,}")
    b.metric("Số luật phát hiện", f"{int(meta.rules_found):,}")
    c.metric("Số luật lưu trong DB", f"{len(rules):,}")
    st.caption(f"Lần chạy {int(meta.run_id)}, {meta.algorithm}. "
               f"Support tối thiểu {float(meta.min_support):.4f}, "
               f"confidence tối thiểu {float(meta.min_confidence):.2f}, "
               f"lift tối thiểu {float(meta.min_lift):.2f}.")
    if len(rules) != int(meta.rules_found):
        st.info("Run cũ chỉ lưu một phần luật; số luật phát hiện và số luật xem được khác nhau.")
    if rules.empty:
        st.info("Không có luật được lưu cho lần chạy này.")
        return
    left, right = st.columns(2)
    keyword = left.text_input("Tìm sản phẩm", key="crosssell_search")
    maximum = max(1.0, float(rules.lift.max()))
    minimum = right.slider("Lift tối thiểu", min_value=1.0, max_value=maximum,
                           value=1.0, key="crosssell_lift")
    filtered = rules[rules.lift >= minimum].copy()
    if keyword:
        matching = filtered.antecedent_names.str.contains(keyword, case=False, na=False, regex=False)
        matching |= filtered.consequent_names.str.contains(keyword, case=False, na=False, regex=False)
        filtered = filtered[matching]
    filtered["Số giao dịch hỗ trợ ước tính"] = (
        filtered.support * int(meta.transaction_count)).round().astype(int)
    filtered["Support phần trăm"] = (filtered.support * 100).round(3)
    filtered["Confidence phần trăm"] = (filtered.confidence * 100).round(2)
    filtered["Lift"] = filtered.lift.round(2)
    st.dataframe(filtered[[
        "antecedent_names", "consequent_names", "Số giao dịch hỗ trợ ước tính",
        "Support phần trăm", "Confidence phần trăm", "Lift"
    ]].rename(columns={"antecedent_names": "Sản phẩm mua",
                       "consequent_names": "Gợi ý bán kèm"}),
        hide_index=True, width="stretch")
    st.caption(f"Hiển thị {len(filtered):,} trên {len(rules):,} luật lưu trong DB. "
               "Số giao dịch hỗ trợ được ước tính từ support đã làm tròn.")
