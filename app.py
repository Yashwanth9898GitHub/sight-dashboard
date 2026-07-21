"""
Sight Order Dashboard
----------------------
A clean two-tab Streamlit app:
  - Dashboard: enter new orders (user info + sight + price) and manage active
    (Ordered) orders. Marking an order "Delivered" moves it out of the
    dashboard and into History.
  - History: read-only log of delivered orders with count and revenue charts.
"""
from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

import db

SHOP_NAME = "New Vision Plus Opticians"
SHOP_ICON = "\U0001F453"  # 👓

st.set_page_config(page_title=SHOP_NAME, page_icon=SHOP_ICON, layout="wide")
db.init_db()


def render_header():
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:18px; padding:8px 0 4px 0;">
            <span style="font-size:56px; line-height:1;">{SHOP_ICON}</span>
            <div>
                <div style="font-size:38px; font-weight:800; letter-spacing:0.5px;
                            background:linear-gradient(90deg,#0E3A8A,#2563eb);
                            -webkit-background-clip:text; background-clip:text;
                            color:transparent;">
                    {SHOP_NAME}
                </div>
                <div style="font-size:15px; color:#6b7280; font-weight:500;
                            letter-spacing:1.5px; text-transform:uppercase;">
                    Sight Order Dashboard
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


render_header()
st.divider()

tab_dashboard, tab_history = st.tabs(["Dashboard", "History"])

# ---------------------------------------------------------------------------
# Dashboard tab
# ---------------------------------------------------------------------------
with tab_dashboard:
    with st.expander("New Order Entry", expanded=True):
        with st.form("new_order_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            name = col1.text_input("Name")
            mobile_number = col2.text_input("Mobile Number", max_chars=15)
            age = col3.number_input("Age", min_value=0, max_value=120, step=1)

            col4, col5, col6 = st.columns(3)
            sight = col4.text_input("Sight (prescription)")
            entry_date = col5.date_input("Entry Date", value=date.today())
            price = col6.number_input("Price", min_value=0.0, step=0.01, format="%.2f")

            submitted = st.form_submit_button("Add Order")
            if submitted:
                if not name.strip():
                    st.error("Name is required.")
                elif not mobile_number.strip().isdigit():
                    st.error("Mobile number must contain digits only.")
                elif not sight.strip():
                    st.error("Sight is required.")
                else:
                    db.add_order(
                        name.strip(),
                        mobile_number.strip(),
                        int(age),
                        sight.strip(),
                        entry_date.isoformat(),
                        float(price),
                    )
                    st.success(f"Order added for {name.strip()}.")
                    st.rerun()

    st.subheader("Active Orders")
    active_orders = db.get_orders(db.STATUS_ORDERED)

    if not active_orders:
        st.info("No active orders. Add one above.")
    else:
        header = st.columns([2, 2, 1, 2, 2, 1, 1.5])
        for col, label in zip(
            header, ["Name", "Mobile Number", "Age", "Sight", "Entry Date", "Price", "Action"]
        ):
            col.markdown(f"**{label}**")

        for order in active_orders:
            row = st.columns([2, 2, 1, 2, 2, 1, 1.5])
            row[0].write(order["name"])
            row[1].write(order["mobile_number"])
            row[2].write(order["age"])
            row[3].write(order["sight"])
            row[4].write(order["entry_date"])
            row[5].write(f"{order['price']:.2f}")
            if row[6].button("Mark Delivered", key=f"deliver_{order['id']}"):
                db.mark_delivered(order["id"], date.today().isoformat())
                st.rerun()

# ---------------------------------------------------------------------------
# History tab
# ---------------------------------------------------------------------------
with tab_history:
    st.subheader("Delivered Orders")
    delivered_orders = db.get_orders(db.STATUS_DELIVERED)

    if not delivered_orders:
        st.info("No delivered orders yet.")
    else:
        df = pd.DataFrame(delivered_orders)
        df["delivered_date"] = pd.to_datetime(df["delivered_date"])
        df["delivered_month"] = df["delivered_date"].dt.strftime("%Y-%m")

        st.dataframe(
            df[
                [
                    "name",
                    "mobile_number",
                    "age",
                    "sight",
                    "entry_date",
                    "delivered_date",
                    "price",
                ]
            ].rename(
                columns={
                    "name": "Name",
                    "mobile_number": "Mobile Number",
                    "age": "Age",
                    "sight": "Sight",
                    "entry_date": "Entry Date",
                    "delivered_date": "Delivered Date",
                    "price": "Price",
                }
            ),
            width="stretch",
            hide_index=True,
        )

        with st.expander("Manage Delivered Orders (delete mistaken entries)"):
            header = st.columns([2, 2, 1, 2, 2, 2, 1, 1.5])
            for col, label in zip(
                header,
                ["Name", "Mobile Number", "Age", "Sight", "Entry Date", "Delivered Date", "Price", "Action"],
            ):
                col.markdown(f"**{label}**")

            for order in delivered_orders:
                row = st.columns([2, 2, 1, 2, 2, 2, 1, 1.5])
                row[0].write(order["name"])
                row[1].write(order["mobile_number"])
                row[2].write(order["age"])
                row[3].write(order["sight"])
                row[4].write(order["entry_date"])
                row[5].write(order["delivered_date"])
                row[6].write(f"{order['price']:.2f}")
                if row[7].button("Delete", key=f"delete_history_{order['id']}"):
                    db.delete_order(order["id"])
                    st.rerun()

        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown("**Delivered Orders by Month (Count)**")
            counts = df.groupby("delivered_month").size().reset_index(name="count")
            fig_count = px.pie(counts, names="delivered_month", values="count")
            st.plotly_chart(fig_count, width="stretch")

        with col_right:
            st.markdown("**Revenue by Month**")
            revenue = df.groupby("delivered_month")["price"].sum().reset_index()
            fig_revenue = px.bar(revenue, x="delivered_month", y="price", labels={"price": "Revenue"})
            st.plotly_chart(fig_revenue, width="stretch")

        st.metric("Total Delivered", len(df))
        st.metric("Total Revenue", f"{df['price'].sum():.2f}")
