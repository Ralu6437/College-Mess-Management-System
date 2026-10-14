import streamlit as st
import pandas as pd
from datetime import date
from firebase_config import db

st.set_page_config(
    page_title="College Mess Management",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------- FIRESTORE HELPERS ----------------

def load_records(collection):
    """Read all records from a Firestore collection."""
    try:
        documents = db.collection(collection).stream()
        records = []
        for document in documents:
            record = document.to_dict()
            record["_id"] = document.id
            records.append(record)
        return records
    except Exception as error:
        st.error(f"Could not load {collection}: {error}")
        return []


def save_record(collection, data):
    """Save one record to Firestore."""
    try:
        db.collection(collection).add(data)
        return True
    except Exception as error:
        st.error(f"Could not save data to {collection}: {error}")
        return False


def seed_default_menu():
    """Add starter menu only if the menu collection is empty."""
    try:
        collection = db.collection("menu")
        if next(collection.limit(1).stream(), None) is None:
            today = str(date.today())
            defaults = [
                {
                    "Date": today,
                    "Meal": "Breakfast",
                    "Menu": "Idli, Sambar, Chutney",
                    "Price": 30,
                },
                {
                    "Date": today,
                    "Meal": "Lunch",
                    "Menu": "Rice, Dal, Vegetables, Salad",
                    "Price": 60,
                },
                {
                    "Date": today,
                    "Meal": "Dinner",
                    "Menu": "Roti, Paneer Curry, Rice",
                    "Price": 70,
                },
            ]
            for item in defaults:
                collection.add(item)
    except Exception as error:
        st.error(f"Could not initialize menu: {error}")


# Seed menu, then load every collection from Firestore.
seed_default_menu()

menu = load_records("menu")
bookings = load_records("bookings")
attendance = load_records("attendance")
expenses = load_records("expenses")
feedback = load_records("feedback")
wastage = load_records("wastage")


# ---------------- SIDEBAR ----------------

with st.sidebar:
    st.title("🍽️ Mess Manager")
    st.caption("College Mess Management System")
    st.divider()

    page = st.radio(
        "NAVIGATION",
        [
            "Dashboard",
            "Student Portal",
            "Admin Portal",
            "Meal Menu",
            "Meal Bookings",
            "Expenses",
            "Food Wastage",
            "Feedback",
            "Reports",
        ],
    )

    st.divider()
    st.caption("College Mess Management")
    st.caption("Python + Streamlit + Firebase Firestore")


# ---------------- HEADER ----------------

st.title("🍽️ College Mess Management System")
st.caption("Manage meals, attendance, expenses, and food wastage.")
st.divider()


# ---------------- DASHBOARD ----------------

if page == "Dashboard":
    st.subheader("📊 Dashboard Overview")

    total_expenses = sum(float(x.get("Amount", 0)) for x in expenses)
    total_wastage = sum(
        float(x.get("Quantity (kg)", 0)) for x in wastage
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🍽️ Meal Bookings", len(bookings))
    c2.metric("✅ Meal Attendance", len(attendance))
    c3.metric("💰 Total Expenses", f"₹{total_expenses:,.2f}")
    c4.metric("♻️ Food Wastage", f"{total_wastage:.1f} kg")

    st.divider()
    left, right = st.columns(2)

    with left:
        st.subheader("Today's Menu")
        today_menu = [
            {k: v for k, v in x.items() if k != "_id"}
            for x in menu
            if x.get("Date") == str(date.today())
        ]
        if today_menu:
            st.dataframe(
                pd.DataFrame(today_menu),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No menu has been added for today.")

    with right:
        st.subheader("Recent Meal Bookings")
        if bookings:
            recent = [
                {k: v for k, v in x.items() if k != "_id"}
                for x in bookings[-5:]
            ]
            st.dataframe(
                pd.DataFrame(recent),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No meal bookings yet.")

    st.divider()
    st.subheader("📈 Analytics")
    chart_left, chart_right = st.columns(2)

    with chart_left:
        st.write("Meal Attendance")
        if attendance:
            df = pd.DataFrame(attendance)
            st.bar_chart(df.groupby("Meal").size())
        else:
            st.info("Attendance statistics will appear here.")

    with chart_right:
        st.write("Expenses by Category")
        if expenses:
            df = pd.DataFrame(expenses)
            st.bar_chart(df.groupby("Category")["Amount"].sum())
        else:
            st.info("Expense statistics will appear here.")


# ---------------- STUDENT PORTAL ----------------

elif page == "Student Portal":
    st.subheader("🎓 Student Portal")
    st.write("Book meals, record attendance, and submit feedback.")

    tab1, tab2, tab3 = st.tabs(
        ["Book a Meal", "Record Attendance", "Submit Feedback"]
    )

    with tab1:
        with st.form("booking_form"):
            student_name = st.text_input("Student Name")
            student_id = st.text_input("Student ID")
            booking_date = st.date_input("Meal Date", value=date.today())
            meal = st.selectbox(
                "Select Meal",
                ["Breakfast", "Lunch", "Snacks", "Dinner"],
            )
            quantity = st.number_input(
                "Number of Meals", min_value=1, max_value=10, value=1
            )
            submit = st.form_submit_button("Book Meal", type="primary")

        if submit:
            if not student_name.strip() or not student_id.strip():
                st.error("Please enter your name and student ID.")
            else:
                ok = save_record(
                    "bookings",
                    {
                        "Student Name": student_name.strip(),
                        "Student ID": student_id.strip(),
                        "Date": str(booking_date),
                        "Meal": meal,
                        "Quantity": int(quantity),
                        "Status": "Booked",
                    },
                )
                if ok:
                    st.success("Meal booking saved permanently!")
                    st.rerun()

    with tab2:
        with st.form("attendance_form"):
            attendance_name = st.text_input(
                "Student Name", key="attendance_name"
            )
            attendance_id = st.text_input(
                "Student ID", key="attendance_id"
            )
            attendance_meal = st.selectbox(
                "Meal Collected",
                ["Breakfast", "Lunch", "Snacks", "Dinner"],
                key="attendance_meal",
            )
            mark_attendance = st.form_submit_button("Record Attendance")

        if mark_attendance:
            if not attendance_name.strip() or not attendance_id.strip():
                st.error("Please enter your name and student ID.")
            else:
                ok = save_record(
                    "attendance",
                    {
                        "Student Name": attendance_name.strip(),
                        "Student ID": attendance_id.strip(),
                        "Date": str(date.today()),
                        "Meal": attendance_meal,
                    },
                )
                if ok:
                    st.success("Attendance saved permanently!")
                    st.rerun()

    with tab3:
        with st.form("feedback_form"):
            feedback_name = st.text_input("Student Name", key="feedback_name")
            rating = st.slider("Food Rating", 1, 5, 4)
            comments = st.text_area("Your Feedback")
            feedback_submit = st.form_submit_button("Submit Feedback")

        if feedback_submit:
            if not feedback_name.strip() or not comments.strip():
                st.error("Please enter your name and feedback.")
            else:
                ok = save_record(
                    "feedback",
                    {
                        "Student Name": feedback_name.strip(),
                        "Date": str(date.today()),
                        "Rating": int(rating),
                        "Comments": comments.strip(),
                    },
                )
                if ok:
                    st.success("Feedback saved permanently!")
                    st.rerun()


# ---------------- ADMIN PORTAL ----------------

elif page == "Admin Portal":
    st.subheader("🛠️ Admin Portal")
    st.warning(
        "Admin authentication is not configured yet. "
        "Do not publish this app for unrestricted use until access is secured."
    )

    tab1, tab2, tab3 = st.tabs(
        ["Add Menu", "Add Expense", "Record Food Wastage"]
    )

    with tab1:
        with st.form("menu_form"):
            menu_date = st.date_input(
                "Menu Date", value=date.today(), key="menu_date"
            )
            meal_type = st.selectbox(
                "Meal Type",
                ["Breakfast", "Lunch", "Snacks", "Dinner"],
                key="menu_type",
            )
            menu_items = st.text_area(
                "Food Items", placeholder="Rice, dal, vegetables..."
            )
            menu_price = st.number_input(
                "Price per Meal (₹)", min_value=0, value=50
            )
            menu_submit = st.form_submit_button("Add Menu")

        if menu_submit:
            if not menu_items.strip():
                st.error("Please enter the food items.")
            else:
                ok = save_record(
                    "menu",
                    {
                        "Date": str(menu_date),
                        "Meal": meal_type,
                        "Menu": menu_items.strip(),
                        "Price": int(menu_price),
                    },
                )
                if ok:
                    st.success("Menu saved permanently!")
                    st.rerun()

    with tab2:
        with st.form("expense_form"):
            expense_date = st.date_input(
                "Expense Date", value=date.today()
            )
            category = st.selectbox(
                "Expense Category",
                [
                    "Food Supplies",
                    "Gas",
                    "Staff",
                    "Maintenance",
                    "Electricity",
                    "Other",
                ],
            )
            description = st.text_input("Description")
            amount = st.number_input(
                "Amount (₹)", min_value=0.0, step=100.0
            )
            expense_submit = st.form_submit_button("Save Expense")

        if expense_submit:
            if not description.strip() or amount <= 0:
                st.error("Enter a description and an amount greater than zero.")
            else:
                ok = save_record(
                    "expenses",
                    {
                        "Date": str(expense_date),
                        "Category": category,
                        "Description": description.strip(),
                        "Amount": float(amount),
                    },
                )
                if ok:
                    st.success("Expense saved permanently!")
                    st.rerun()

    with tab3:
        with st.form("wastage_form"):
            waste_date = st.date_input(
                "Wastage Date", value=date.today()
            )
            food_name = st.text_input("Food Item")
            waste_quantity = st.number_input(
                "Wasted Quantity (kg)", min_value=0.0, step=0.5
            )
            reason = st.selectbox(
                "Reason",
                [
                    "Overproduction",
                    "Spoilage",
                    "Preparation Waste",
                    "Plate Waste",
                    "Other",
                ],
            )
            waste_submit = st.form_submit_button("Save Wastage Record")

        if waste_submit:
            if not food_name.strip() or waste_quantity <= 0:
                st.error("Enter a food item and quantity greater than zero.")
            else:
                ok = save_record(
                    "wastage",
                    {
                        "Date": str(waste_date),
                        "Food": food_name.strip(),
                        "Quantity (kg)": float(waste_quantity),
                        "Reason": reason,
                    },
                )
                if ok:
                    st.success("Food wastage saved permanently!")
                    st.rerun()


# ---------------- MEAL MENU ----------------

elif page == "Meal Menu":
    st.subheader("🍛 Meal Menu")
    menu_df = pd.DataFrame(
        [{k: v for k, v in x.items() if k != "_id"} for x in menu]
    )

    if not menu_df.empty:
        selected_date = st.date_input(
            "Filter by date", value=date.today(), key="menu_filter_date"
        )
        filtered = menu_df[menu_df["Date"] == str(selected_date)]
        if not filtered.empty:
            st.dataframe(filtered, use_container_width=True, hide_index=True)
        else:
            st.info("No menu is available for this date.")

        st.download_button(
            "Download Menu CSV",
            data=menu_df.to_csv(index=False).encode("utf-8"),
            file_name="mess_menu.csv",
            mime="text/csv",
        )
    else:
        st.info("No menu available.")


# ---------------- MEAL BOOKINGS ----------------

elif page == "Meal Bookings":
    st.subheader("📋 Meal Bookings")
    df = pd.DataFrame(
        [{k: v for k, v in x.items() if k != "_id"} for x in bookings]
    )
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download Bookings CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="meal_bookings.csv",
            mime="text/csv",
        )
    else:
        st.info("No meal bookings available.")


# ---------------- EXPENSES ----------------

elif page == "Expenses":
    st.subheader("💰 Mess Expenses")
    df = pd.DataFrame(
        [{k: v for k, v in x.items() if k != "_id"} for x in expenses]
    )
    if not df.empty:
        st.metric("Total Expenses", f"₹{df['Amount'].sum():,.2f}")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download Expenses CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="expenses.csv",
            mime="text/csv",
        )
    else:
        st.info("No expenses recorded.")


# ---------------- FOOD WASTAGE ----------------

elif page == "Food Wastage":
    st.subheader("♻️ Food Wastage Management")
    df = pd.DataFrame(
        [{k: v for k, v in x.items() if k != "_id"} for x in wastage]
    )
    if not df.empty:
        st.metric("Total Food Wastage", f"{df['Quantity (kg)'].sum():.1f} kg")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.bar_chart(df.groupby("Food")["Quantity (kg)"].sum())
        st.download_button(
            "Download Wastage CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="food_wastage.csv",
            mime="text/csv",
        )
    else:
        st.info("No food wastage records available.")


# ---------------- FEEDBACK ----------------

elif page == "Feedback":
    st.subheader("⭐ Student Feedback")
    df = pd.DataFrame(
        [{k: v for k, v in x.items() if k != "_id"} for x in feedback]
    )
    if not df.empty:
        st.metric("Average Food Rating", f"{df['Rating'].mean():.1f} / 5")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download Feedback CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="feedback.csv",
            mime="text/csv",
        )
    else:
        st.info("No feedback submitted yet.")


# ---------------- REPORTS ----------------

elif page == "Reports":
    st.subheader("📑 Reports and Downloads")

    report_options = {
        "Meal Menu": menu,
        "Meal Bookings": bookings,
        "Meal Attendance": attendance,
        "Expenses": expenses,
        "Feedback": feedback,
        "Food Wastage": wastage,
    }

    for report_name, records in report_options.items():
        clean_records = [
            {k: v for k, v in record.items() if k != "_id"}
            for record in records
        ]
        if clean_records:
            df = pd.DataFrame(clean_records)
            st.download_button(
                f"Download {report_name} CSV",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name=report_name.lower().replace(" ", "_") + ".csv",
                mime="text/csv",
                key="report_" + report_name,
            )
        else:
            st.write(f"{report_name}: No data yet.")

st.divider()
st.caption("College Mess Management System | Python + Streamlit + Firestore")
