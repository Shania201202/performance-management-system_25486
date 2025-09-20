import streamlit as st
from backend import DatabaseManager
from datetime import date

# Database connection details
DB_DETAILS = {
    'dbname': 'performance management system',  # Replace with your database name
    'user': 'postgres',      # Replace with your user
    'password': 'Shania2012*',  # Replace with your password
    'host': 'localhost'
}

st.set_page_config(layout="wide")
st.title("Performance Management System")

# Function to get employees and create a select box
def get_employee_selection(db):
    employees = db.get_employees()
    employee_names = [emp[1] for emp in employees]
    employee_dict = {name: id for id, name in employees}
    selected_name = st.selectbox("Select Employee", employee_names)
    selected_id = employee_dict.get(selected_name)
    return selected_id

# Function to get goals and create a select box
def get_goal_selection(db, employee_id):
    goals = db.get_goals_by_employee(employee_id)
    if not goals:
        return None, None
    goal_descriptions = [goal[1] for goal in goals]
    goal_dict = {desc: id for id, desc, _, _ , _ in goals}
    selected_desc = st.selectbox("Select Goal", goal_descriptions)
    selected_id = goal_dict.get(selected_desc)
    return selected_id, selected_desc

# Main application logic
with DatabaseManager(**DB_DETAILS) as db:
    if db.conn:
        st.sidebar.header("Navigation")
        page = st.sidebar.radio("Go to", ["Goal & Task Setting", "Progress Tracking", "Feedback", "Reporting", "Business Insights"])

        # --- Goal & Task Setting (CRUD - Create, Read, Update, Delete) ---
        if page == "Goal & Task Setting":
            st.header("🎯 Goal & Task Setting")
            st.subheader("Create a New Goal")
            
            with st.form("new_goal_form"):
                employee_id = get_employee_selection(db)
                manager_id = st.text_input("Manager ID", "1") # Assuming a fixed manager for simplicity
                description = st.text_area("Goal Description", "")
                due_date = st.date_input("Due Date", date.today())
                status = st.selectbox("Status", ['Draft', 'In Progress', 'Completed', 'Cancelled'])
                submitted = st.form_submit_button("Set Goal")
                if submitted and employee_id:
                    goal_id = db.create_goal(employee_id, int(manager_id), description, due_date, status)
                    if goal_id:
                        st.success(f"Goal created successfully with ID: {goal_id}")
                    else:
                        st.error("Failed to create goal.")

            st.subheader("Add Task to a Goal")
            with st.form("new_task_form"):
                employee_id = get_employee_selection(db)
                goal_id, _ = get_goal_selection(db, employee_id)
                task_description = st.text_area("Task Description", "")
                submitted = st.form_submit_button("Add Task")
                if submitted and goal_id:
                    if db.create_task(goal_id, task_description):
                        st.success("Task added successfully.")
                    else:
                        st.error("Failed to add task.")

            st.subheader("View & Manage Goals")
            employee_id = get_employee_selection(db)
            if employee_id:
                goals = db.get_goals_by_employee(employee_id)
                if goals:
                    st.write("---")
                    for goal in goals:
                        goal_id, desc, due, status, manager_name = goal
                        with st.expander(f"Goal ID: {goal_id} - {desc}"):
                            st.write(f"**Description:** {desc}")
                            st.write(f"**Due Date:** {due}")
                            st.write(f"**Status:** {status}")
                            st.write(f"**Manager:** {manager_name}")
                            
                            st.write("---")
                            st.write("**Tasks**")
                            tasks = db.get_tasks_by_goal(goal_id)
                            if tasks:
                                for task in tasks:
                                    task_id, task_desc, is_approved = task
                                    st.checkbox(f"Task: {task_desc}", value=is_approved, key=f"task_{task_id}", disabled=True)
                            else:
                                st.info("No tasks for this goal.")

                            st.write("---")
                            st.subheader("Update Goal Status (Manager Only)")
                            new_status = st.selectbox("Update Status", ['Draft', 'In Progress', 'Completed', 'Cancelled'], key=f"status_update_{goal_id}")
                            if st.button("Update Status", key=f"update_btn_{goal_id}"):
                                if db.update_goal_status(goal_id, new_status):
                                    st.success("Goal status updated.")
                                    st.experimental_rerun()
                                else:
                                    st.error("Failed to update status.")

                            if st.button("Delete Goal", key=f"delete_btn_{goal_id}"):
                                if db.delete_goal(goal_id):
                                    st.success("Goal and associated tasks/feedback deleted.")
                                    st.experimental_rerun()
                                else:
                                    st.error("Failed to delete goal.")

        # --- Progress Tracking ---
        elif page == "Progress Tracking":
            st.header("📈 Progress Tracking")
            st.info("Managers and employees can track progress here.")
            
            selected_employee_id = get_employee_selection(db)
            if selected_employee_id:
                st.subheader("Goals & Tasks")
                goals = db.get_goals_by_employee(selected_employee_id)
                if goals:
                    for goal in goals:
                        goal_id, goal_desc, due, status, _ = goal
                        st.markdown(f"**Goal ID {goal_id}:** {goal_desc} - **Status:** {status}")
                        st.caption(f"Due: {due}")
                        tasks = db.get_tasks_by_goal(goal_id)
                        if tasks:
                            for task in tasks:
                                task_id, task_desc, is_approved = task
                                st.checkbox(f"Task: {task_desc}", value=is_approved, disabled=True, key=f"track_task_{task_id}")
                        else:
                            st.info("No tasks for this goal yet.")
                        st.markdown("---")
                else:
                    st.warning("No goals found for this employee.")

        # --- Feedback ---
        elif page == "Feedback":
            st.header("📝 Feedback")
            
            st.subheader("Provide New Feedback")
            with st.form("new_feedback_form"):
                manager_id = st.text_input("Manager ID", "1") # Assuming a fixed manager
                employee_id = get_employee_selection(db)
                goal_id, _ = get_goal_selection(db, employee_id)
                feedback_text = st.text_area("Feedback Text", "")
                submitted = st.form_submit_button("Submit Feedback")
                if submitted and goal_id:
                    if db.provide_feedback(goal_id, int(manager_id), feedback_text):
                        st.success("Feedback submitted successfully. Automated feedback may have been added.")
                    else:
                        st.error("Failed to submit feedback.")

            st.subheader("View Feedback")
            selected_employee_id = get_employee_selection(db)
            if selected_employee_id:
                goals = db.get_goals_by_employee(selected_employee_id)
                if goals:
                    for goal in goals:
                        goal_id, goal_desc, _, _, _ = goal
                        feedback_list = db.get_feedback_by_goal(goal_id)
                        if feedback_list:
                            st.markdown(f"**Feedback for Goal ID {goal_id}:** {goal_desc}")
                            for feedback in feedback_list:
                                _, feedback_text, manager_name = feedback
                                st.info(f"From {manager_name}: {feedback_text}")
                        st.markdown("---")
                else:
                    st.warning("No goals found for this employee.")
        
        # --- Reporting ---
        elif page == "Reporting":
            st.header("📊 Performance History Report")
            selected_employee_id = get_employee_selection(db)
            if selected_employee_id:
                history = db.get_employee_performance_history(selected_employee_id)
                if history:
                    st.dataframe(history, column_order=['goal_desc', 'due_date', 'status', 'feedback_text'])
                else:
                    st.info("No performance history found for this employee.")
        
        # --- Business Insights ---
        elif page == "Business Insights":
            st.header("🧠 Business Insights")
            insights = db.get_business_insights()
            if insights:
                st.metric(label="Total Goals", value=insights.get('total_goals', 'N/A'))
                st.metric(label="Total Tasks", value=insights.get('total_tasks', 'N/A'))
                st.metric(label="Average Tasks per Goal", value=f"{(insights.get('avg_tasks_per_goal') or 0.0):.2f}")

                
                st.subheader("Goals by Status")
                st.bar_chart(insights.get('goals_by_status', {}))
                
                st.subheader("Most Productive Employee (by completed goals)")
                if insights.get('most_productive_employee'):
                    name, count = insights['most_productive_employee']
                    st.success(f"🥇 **{name}** with **{count}** completed goal(s).")
                else:
                    st.info("No completed goals found yet.")

    else:
        st.error("Failed to connect to the database. Please check your connection details and ensure the server is running.")