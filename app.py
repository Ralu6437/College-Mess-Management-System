
import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(
    page_title="College Mess Management",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- SESSION DATA ----------
if "bookings" not in st.session_state:
    st.session_state.bookings = []

if "menu" not in st.session_state:
    st.session_state.menu = [
        {
            "Date": str(date.today()),
            "Meal": "Breakfast",
            "Menu": "Idli, Sambar, Chutney",
            "Price": 30
        },
        {
            "Date": str(date.today()),
            "Meal": "Lunch",
            "Menu": "Rice, Dal, Vegetables, Salad",
            "Price": 60
        },
        {
            "Date": str(date.today()),
            "Meal": "Dinner",
            "Menu": "Roti, Paneer Curry, Rice",
            "Price": 70
        }
    ]

if "expenses" not in st.session_state:
    st.session_state.expenses = []

if "attendance" not in st.session_state:
    st.session_state.attendance = []

if "feedback" not in st.session_state:
    st.session_state.feedback = []

if "wastage" not in st.session_state:
    st.session_state.wastage = []


# ---------- SIDEBAR ----------
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
            "Reports"
        ]
    )

    st.divider()
    st.caption("College Mess Management")
    st.caption("Python + Streamlit + Firebase")


# ---------- HEADER ----------
st.title("🍽️ College Mess Management System")
st.caption("Manage meals, attendance, expenses, and food wastage.")
st.divider()


# ---------- DASHBOARD ----------
if page == "Dashboard":
    st.subheader("📊 Dashboard Overview")

    total_bookings = len(st.session_state.bookings)
    total_attendance = len(st.session_state.attendance)
    total_expenses = sum(
        float(x["Amount"])
        for x in st.session_state.expenses
    )
    total_wastage = sum(
        float(x["Quantity (kg)"])
        for x in st.session_state.wastage
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("🍽️ Meal Bookings", total_bookings)
    c2.metric("✅ Meal Attendance", total_attendance)
    c3.metric("💰 Total Expenses", f"₹{total_expenses:,.2f}")
    c4.metric("♻️ Food Wastage", f"{total_wastage:.1f} kg")

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Today's Menu")

        menu_df = pd.DataFrame(st.session_state.menu)

        if not menu_df.empty:
            st.dataframe(
                menu_df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No menu has been added.")

    with right:
        st.subheader("Recent Meal Bookings")

        bookings_df = pd.DataFrame(st.session_state.bookings)

        if not bookings_df.empty:
            st.dataframe(
                bookings_df.tail(5),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No meal bookings yet.")

    st.divider()
    st.subheader("📈 Analytics")

    chart_left, chart_right = st.columns(2)

    with chart_left:
        st.write("Meal Attendance")
        if st.session_state.attendance:
            attendance_df = pd.DataFrame(
                st.session_state.attendance
            )
            chart_data = attendance_df.groupby(
                "Meal"
            ).size().reset_index(name="Count")

            st.bar_chart(
                chart_data.set_index("Meal")["Count"]
            )
        else:
            st.info("Attendance statistics will appear here.")

    with chart_right:
        st.write("Expenses by Category")
        if st.session_state.expenses:
            expenses_df = pd.DataFrame(
                st.session_state.expenses
            )
            chart_data = expenses_df.groupby(
                "Category"
            )["Amount"].sum()

            st.bar_chart(chart_data)
        else:
            st.info("Expense statistics will appear here.")


# ---------- STUDENT PORTAL ----------
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
                ["Breakfast", "Lunch", "Snacks", "Dinner"]
            )
            quantity = st.number_input(
                "Number of Meals",
                min_value=1,
                max_value=10,
                value=1
            )

            submit = st.form_submit_button(
                "Book Meal",
                type="primary"
            )

        if submit:
            if not student_name.strip() or not student_id.strip():
                st.error("Please enter your name and student ID.")
            else:
                st.session_state.bookings.append({
                    "Student Name": student_name.strip(),
                    "Student ID": student_id.strip(),
                    "Date": str(booking_date),
                    "Meal": meal,
                    "Quantity": int(quantity),
                    "Status": "Booked"
                })
                st.success("Meal booking created successfully!")

    with tab2:
        with st.form("attendance_form"):
            attendance_name = st.text_input(
                "Student Name",
                key="attendance_name"
            )
            attendance_id = st.text_input(
                "Student ID",
                key="attendance_id"
            )
            attendance_meal = st.selectbox(
                "Meal Collected",
                ["Breakfast", "Lunch", "Snacks", "Dinner"],
                key="attendance_meal"
            )

            mark_attendance = st.form_submit_button(
                "Record Attendance"
            )

        if mark_attendance:
            if not attendance_name.strip() or not attendance_id.strip():
                st.error("Please enter your name and student ID.")
            else:
                st.session_state.attendance.append({
                    "Student Name": attendance_name.strip(),
                    "Student ID": attendance_id.strip(),
                    "Date": str(date.today()),
                    "Meal": attendance_meal
                })
                st.success("Attendance recorded.")

    with tab3:
        with st.form("feedback_form"):
            feedback_name = st.text_input(
                "Student Name",
                key="feedback_name"
            )
            rating = st.slider("Food Rating", 1, 5, 4)
            comments = st.text_area("Your Feedback")

            feedback_submit = st.form_submit_button(
                "Submit Feedback"
            )

        if feedback_submit:
            if not feedback_name.strip() or not comments.strip():
                st.error("Please enter your name and feedback.")
            else:
                st.session_state.feedback.append({
                    "Student Name": feedback_name.strip(),
                    "Date": str(date.today()),
                    "Rating": int(rating),
                    "Comments": comments.strip()
                })
                st.success("Thank you for your feedback!")


# ---------- ADMIN PORTAL ----------
elif page == "Admin Portal":
    st.subheader("🛠️ Admin Portal")
    st.warning(
        "This is the initial interface preview. "
        "Secure admin authentication will be added in the Firebase integration step."
    )

    tab1, tab2, tab3 = st.tabs(
        ["Add Menu", "Add Expense", "Record Food Wastage"]
    )

    with tab1:
        with st.form("menu_form"):
            menu_date = st.date_input(
                "Menu Date",
                value=date.today(),
                key="menu_date"
            )
            meal_type = st.selectbox(
                "Meal Type",
                ["Breakfast", "Lunch", "Snacks", "Dinner"],
                key="menu_type"
            )
            menu_items = st.text_area(
                "Food Items",
                placeholder="Rice, dal, vegetables..."
            )
            menu_price = st.number_input(
                "Price per Meal (₹)",
                min_value=0,
                value=50
            )

            menu_submit = st.form_submit_button("Add Menu")

        if menu_submit:
            if not menu_items.strip():
                st.error("Please enter the food items.")
            else:
                st.session_state.menu.append({
                    "Date": str(menu_date),
                    "Meal": meal_type,
                    "Menu": menu_items.strip(),
                    "Price": int(menu_price)
                })
                st.success("Menu added successfully!")

    with tab2:
        with st.form("expense_form"):
            expense_date = st.date_input(
                "Expense Date",
                value=date.today()
            )
            category = st.selectbox(
                "Expense Category",
                [
                    "Food Supplies",
                    "Gas",
                    "Staff",
                    "Maintenance",
                    "Electricity",
                    "Other"
                ]
            )
            description = st.text_input("Description")
            amount = st.number_input(
                "Amount (₹)",
                min_value=0.0,
                step=100.0
            )

            expense_submit = st.form_submit_button("Save Expense")

        if expense_submit:
            if not description.strip() or amount <= 0:
                st.error("Enter a description and an amount greater than zero.")
            else:
                st.session_state.expenses.append({
                    "Date": str(expense_date),
                    "Category": category,
                    "Description": description.strip(),
                    "Amount": float(amount)
                })
                st.success("Expense saved successfully!")

    with tab3:
        with st.form("wastage_form"):
            waste_date = st.date_input(
                "Wastage Date",
                value=date.today()
            )
            food_name = st.text_input("Food Item")
            waste_quantity = st.number_input(
                "Wasted Quantity (kg)",
                min_value=0.0,
                step=0.5
            )
            reason = st.selectbox(
                "Reason",
                [
                    "Overproduction",
                    "Spoilage",
                    "Preparation Waste",
                    "Plate Waste",
                    "Other"
                ]
            )

            waste_submit = st.form_submit_button(
                "Save Wastage Record"
            )

        if waste_submit:
            if not food_name.strip() or waste_quantity <= 0:
                st.error("Enter a food item and quantity greater than zero.")
            else:
                st.session_state.wastage.append({
                    "Date": str(waste_date),
                    "Food": food_name.strip(),
                    "Quantity (kg)": float(waste_quantity),
                    "Reason": reason
                })
                st.success("Food wastage record saved.")


# ---------- MEAL MENU ----------
elif page == "Meal Menu":
    st.subheader("🍛 Meal Menu")

    menu_df = pd.DataFrame(st.session_state.menu)

    if not menu_df.empty:
        selected_date = st.date_input(
            "Filter by date",
            value=date.today(),
            key="menu_filter_date"
        )

        filtered = menu_df[
            menu_df["Date"] == str(selected_date)
        ]

        if not filtered.empty:
            st.dataframe(
                filtered,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No menu is available for this date.")

        st.download_button(
            "Download Menu CSV",
            data=menu_df.to_csv(index=False).encode("utf-8"),
            file_name="mess_menu.csv",
            mime="text/csv"
        )
    else:
        st.info("No menu available.")


# ---------- MEAL BOOKINGS ----------
elif page == "Meal Bookings":
    st.subheader("📋 Meal Bookings")

    bookings_df = pd.DataFrame(st.session_state.bookings)

    if not bookings_df.empty:
        st.dataframe(
            bookings_df,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "Download Bookings CSV",
            data=bookings_df.to_csv(index=False).encode("utf-8"),
            file_name="meal_bookings.csv",
            mime="text/csv"
        )
    else:
        st.info("No meal bookings available.")


# ---------- EXPENSES ----------
elif page == "Expenses":
    st.subheader("💰 Mess Expenses")

    expenses_df = pd.DataFrame(st.session_state.expenses)

    if not expenses_df.empty:
        st.metric(
            "Total Expenses",
            f"₹{expenses_df['Amount'].sum():,.2f}"
        )
        st.dataframe(
            expenses_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No expenses recorded.")


# ---------- FOOD WASTAGE ----------
elif page == "Food Wastage":
    st.subheader("♻️ Food Wastage Management")

    waste_df = pd.DataFrame(st.session_state.wastage)

    if not waste_df.empty:
        st.metric(
            "Total Food Wastage",
            f"{waste_df['Quantity (kg)'].sum():.1f} kg"
        )
        st.dataframe(
            waste_df,
            use_container_width=True,
            hide_index=True
        )

        st.bar_chart(
            waste_df.groupby("Food")["Quantity (kg)"].sum()
        )
    else:
        st.info("No food wastage records available.")


# ---------- FEEDBACK ----------
elif page == "Feedback":
    st.subheader("⭐ Student Feedback")

    feedback_df = pd.DataFrame(st.session_state.feedback)

    if not feedback_df.empty:
        average_rating = feedback_df["Rating"].mean()
        st.metric("Average Food Rating", f"{average_rating:.1f} / 5")
        st.dataframe(
            feedback_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No feedback submitted yet.")


# ---------- REPORTS ----------
elif page == "Reports":
    st.subheader("📑 Reports and Downloads")

    report_options = {
        "Meal Menu": st.session_state.menu,
        "Meal Bookings": st.session_state.bookings,
        "Meal Attendance": st.session_state.attendance,
        "Expenses": st.session_state.expenses,
        "Feedback": st.session_state.feedback,
        "Food Wastage": st.session_state.wastage
    }

    for report_name, records in report_options.items():
        if records:
            report_df = pd.DataFrame(records)

            st.download_button(
                f"Download {report_name} CSV",
                data=report_df.to_csv(index=False).encode("utf-8"),
                file_name=report_name.lower().replace(" ", "_") + ".csv",
                mime="text/csv",
                key="report_" + report_name
            )
        else:
            st.write(f"{report_name}: No data yet.")

st.divider()
st.caption("College Mess Management System | Python + Streamlit")
