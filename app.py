
import streamlit as st
import pandas as pd
import plotly.express as px

from datetime import date

from database import (
    create_table,
    add_transaction,
    get_transactions,
    delete_transaction
)


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💰",
    layout="wide"
)


# --------------------------------------------------
# INITIALIZE DATABASE
# --------------------------------------------------

create_table()


# --------------------------------------------------
# APPLICATION TITLE
# --------------------------------------------------

st.title("💰 Personal Expense Tracker")

st.write(
    "Track your income, manage your expenses, "
    "and understand your spending habits."
)

st.divider()


# --------------------------------------------------
# SIDEBAR: ADD A TRANSACTION
# --------------------------------------------------

st.sidebar.header("➕ Add Transaction")

transaction_type = st.sidebar.selectbox(
    "Transaction Type",
    ["Expense", "Income"]
)


if transaction_type == "Expense":

    categories = [
        "Food",
        "Travel",
        "Shopping",
        "Education",
        "Bills",
        "Entertainment",
        "Healthcare",
        "Other"
    ]

else:

    categories = [
        "Salary",
        "Freelancing",
        "Business",
        "Gift",
        "Other"
    ]


with st.sidebar.form("transaction_form"):

    amount = st.number_input(
        "Amount (₹)",
        min_value=0.01,
        value=100.0,
        step=50.0
    )

    category = st.selectbox(
        "Category",
        categories
    )

    transaction_date = st.date_input(
        "Date",
        value=date.today()
    )

    description = st.text_input(
        "Description",
        placeholder="Example: Lunch, Bus ticket, Salary"
    )

    submitted = st.form_submit_button(
        "Save Transaction",
        use_container_width=True
    )


    if submitted:

        add_transaction(
            transaction_type,
            amount,
            category,
            transaction_date.isoformat(),
            description.strip()
        )

        st.session_state["transaction_message"] = (
            f"{transaction_type} of ₹{amount:,.2f} saved successfully!"
        )

        st.rerun()


if "transaction_message" in st.session_state:

    st.sidebar.success(
        st.session_state.pop("transaction_message")
    )


# --------------------------------------------------
# LOAD TRANSACTIONS
# --------------------------------------------------

df = get_transactions()


# --------------------------------------------------
# DASHBOARD SUMMARY
# --------------------------------------------------

if df.empty:

    total_income = 0.0
    total_expenses = 0.0

else:

    total_income = df.loc[
        df["transaction_type"] == "Income",
        "amount"
    ].sum()

    total_expenses = df.loc[
        df["transaction_type"] == "Expense",
        "amount"
    ].sum()


balance = total_income - total_expenses


# --------------------------------------------------
# DISPLAY SUMMARY CARDS
# --------------------------------------------------

col1, col2, col3 = st.columns(3)


col1.metric(
    "💵 Total Income",
    f"₹{total_income:,.2f}"
)

col2.metric(
    "💸 Total Expenses",
    f"₹{total_expenses:,.2f}"
)

col3.metric(
    "🏦 Remaining Balance",
    f"₹{balance:,.2f}",
    delta=f"₹{balance:,.2f}"
)


st.divider()


# --------------------------------------------------
# TRANSACTION HISTORY
# --------------------------------------------------

st.subheader("📋 Transaction History")


if df.empty:

    st.info(
        "No transactions available. "
        "Add your first income or expense using the sidebar."
    )

else:

    # Filter by transaction type
    filter_type = st.selectbox(
        "Filter Transactions",
        ["All", "Income", "Expense"]
    )

    if filter_type == "All":

        filtered_df = df.copy()

    else:

        filtered_df = df[
            df["transaction_type"] == filter_type
        ].copy()


    # Prepare table for display
    display_df = filtered_df.rename(
        columns={
            "id": "ID",
            "transaction_type": "Type",
            "amount": "Amount (₹)",
            "category": "Category",
            "date": "Date",
            "description": "Description"
        }
    )

    display_columns = [
        "ID",
        "Type",
        "Amount (₹)",
        "Category",
        "Date",
        "Description"
    ]

    st.dataframe(
        display_df[display_columns],
        use_container_width=True,
        hide_index=True
    )


    # --------------------------------------------------
    # DELETE A TRANSACTION
    # --------------------------------------------------

    st.subheader("🗑️ Delete Transaction")

    transaction_ids = df["id"].tolist()

    selected_id = st.selectbox(
        "Select Transaction ID",
        transaction_ids
    )

    if st.button("Delete Selected Transaction"):

        delete_transaction(selected_id)

        st.success(
            f"Transaction ID {selected_id} deleted successfully."
        )

        st.rerun()


st.divider()


# --------------------------------------------------
# EXPENSE CHART
# --------------------------------------------------

st.subheader("📊 Expenses by Category")


if df.empty:

    st.info("Add expenses to see your spending chart.")

else:

    expense_df = df[
        df["transaction_type"] == "Expense"
    ].copy()

    if expense_df.empty:

        st.info("You haven't recorded any expenses yet.")

    else:

        category_totals = (
            expense_df
            .groupby("category", as_index=False)["amount"]
            .sum()
            .sort_values("amount", ascending=False)
        )

        fig = px.pie(
            category_totals,
            names="category",
            values="amount",
            title="Expense Distribution",
            hole=0.4
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# --------------------------------------------------
# EXPENSE SUMMARY BAR CHART
# --------------------------------------------------

st.subheader("📈 Spending Summary")


if not df.empty:

    expense_df = df[
        df["transaction_type"] == "Expense"
    ].copy()

    if not expense_df.empty:

        daily_expenses = (
            expense_df
            .groupby("date", as_index=False)["amount"]
            .sum()
            .sort_values("date")
        )

        daily_expenses["date"] = pd.to_datetime(
            daily_expenses["date"]
        )

        fig_bar = px.bar(
            daily_expenses,
            x="date",
            y="amount",
            title="Daily Expenses",
            labels={
                "date": "Date",
                "amount": "Amount (₹)"
            }
        )

        st.plotly_chart(
            fig_bar,
            use_container_width=True
        )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Personal Expense Tracker | Built with Python, "
    "Streamlit, SQLite, Pandas and Plotly."
)