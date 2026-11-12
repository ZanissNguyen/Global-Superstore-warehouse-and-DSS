"""Streamlit upload and reconciliation screen for the isolated demo pipeline."""

import pandas as pd
import streamlit as st

from src.app.demo_backend import (
    active_session, history, process_upload, return_to_base, validate_upload,
)


def _metric_table(before, after):
    labels = {
        "bronze_rows": "Dòng Bronze", "silver_rows": "Dòng Silver",
        "gold_rows": "Dòng Gold", "total_sales": "Doanh thu USD",
        "total_profit": "Lợi nhuận USD",
    }
    rows = []
    for key, label in labels.items():
        old, new = float(before[key]), float(after[key])
        rows.append({"Chỉ số": label, "Trước": old, "Sau": new, "Chênh lệch": new - old})
    return pd.DataFrame(rows)


def render_upload_tab():
    st.subheader("Nạp dữ liệu và đối soát")
    st.caption("Chọn một file CSV 500 dòng. Chọn file chỉ xem trước; dữ liệu Gold chỉ đổi sau khi toàn bộ ETL thành công. "
               "Để chuẩn bị lại demo, thay file rồi bấm xử lý lần nữa.")
    session = active_session()
    if session:
        st.info(f"Phiên đang hoạt động: {session['session_id']}, "
                f"lần nạp {session['ingestion_id']}, "
                f"dự báo {session['forecast_3_id']} và {session['forecast_6_id']}, "
                f"bán kèm {session['association_run_id']}.")
        if st.button("Quay về dữ liệu nền", key="demo_return_to_base"):
            return_to_base(session["session_id"])
            st.session_state.pop("demo_result", None)
            st.session_state["demo_upload_version"] = (
                st.session_state.get("demo_upload_version", 0) + 1
            )
            st.cache_data.clear()
            st.rerun()
    else:
        st.info("Đang hiển thị database nền.")
    uploaded = st.file_uploader(
        "File CSV mới", type=["csv"],
        key=f"demo_csv_{st.session_state.get('demo_upload_version', 0)}",
    )
    if uploaded is not None:
        content = uploaded.getvalue()
        try:
            df, preview = validate_upload(content)
        except Exception as exc:
            st.error(f"File chưa hợp lệ: {exc}")
        else:
            a, b, c, d = st.columns(4)
            a.metric("Số dòng", f"{preview['rows']:,}")
            b.metric("Số đơn", f"{preview['orders']:,}")
            c.metric("Doanh thu file", f"${preview['sales']:,.2f}")
            d.metric("Lợi nhuận file", f"${preview['profit']:,.2f}")
            st.caption(f"Ngày đặt hàng từ {preview['first_date']:%d/%m/%Y} đến "
                       f"{preview['last_date']:%d/%m/%Y}. Mã SHA 256: {preview['sha256'][:16]}")
            st.dataframe(df.head(5), hide_index=True, width="stretch")
            if st.button("Xử lý dữ liệu và kích hoạt phiên", type="primary", key="demo_process"):
                with st.status("Đang xử lý file...", expanded=True) as status:
                    def progress(step, state):
                        st.write(f"{step}: {state}")
                    try:
                        result = process_upload(content, uploaded.name, progress)
                    except Exception as exc:
                        status.update(label="Xử lý thất bại; phiên cũ vẫn hoạt động.", state="error")
                        st.error(f"Bước xử lý lỗi: {exc}")
                    else:
                        status.update(label="Đã kích hoạt phiên dữ liệu mới.", state="complete")
                        st.session_state["demo_result"] = result
                        st.cache_data.clear()
                        st.rerun()
    result = st.session_state.get("demo_result")
    if result is None and session and session["metrics_before"] and session["metrics_after"]:
        result = {"session_id": session["session_id"],
                  "before": session["metrics_before"], "after": session["metrics_after"]}
    if result:
        st.markdown("#### Đối soát trước và sau")
        st.dataframe(_metric_table(result["before"], result["after"]),
                     hide_index=True, width="stretch")
        st.caption(f"Phiên {result['session_id']}"
                   + (f", tác vụ {result['job_id']}" if result.get("job_id") else "")
                   + "; "
                   "các số trên lấy từ hai database trước và sau ETL.")
    recent = history()
    if not recent.empty:
        with st.expander("Lịch sử phiên đã kích hoạt"):
            st.dataframe(recent, hide_index=True, width="stretch")
