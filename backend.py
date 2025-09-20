import psycopg2

class DatabaseManager:
    def __init__(self, dbname, user, password, host='localhost'):
        self.conn = None
        self.cursor = None
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host
            )
            self.cursor = self.conn.cursor()
        except psycopg2.OperationalError as e:
            print(f"Error connecting to database: {e}")
            self.conn = None
            self.cursor = None

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    # --- C - CREATE ---
    def create_goal(self, employee_id, manager_id, description, due_date, status):
        try:
            self.cursor.execute(
                """INSERT INTO goals (employee_id, manager_id, description, due_date, status) VALUES (%s, %s, %s, %s, %s) RETURNING goal_id""",
                (employee_id, manager_id, description, due_date, status)
            )
            self.conn.commit()
            return self.cursor.fetchone()[0]
        except Exception as e:
            print(f"Error creating goal: {e}")
            self.conn.rollback()
            return None

    def create_task(self, goal_id, description):
        try:
            self.cursor.execute(
                """INSERT INTO tasks (goal_id, description) VALUES (%s, %s)""",
                (goal_id, description)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error creating task: {e}")
            self.conn.rollback()
            return False

    def provide_feedback(self, goal_id, manager_id, feedback_text):
        try:
            # Automated feedback trigger
            automated_text = self._check_for_automated_feedback(goal_id)
            if automated_text:
                full_feedback = f"{feedback_text}\n\n[Automated Feedback]: {automated_text}"
            else:
                full_feedback = feedback_text

            self.cursor.execute(
                """INSERT INTO feedback (goal_id, manager_id, feedback_text) VALUES (%s, %s, %s)""",
                (goal_id, manager_id, full_feedback)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error providing feedback: {e}")
            self.conn.rollback()
            return False
            
    def _check_for_automated_feedback(self, goal_id):
        # Example trigger: check if goal is 'Completed'
        self.cursor.execute("SELECT status FROM goals WHERE goal_id = %s", (goal_id,))
        status = self.cursor.fetchone()
        if status and status[0] == 'Completed':
            return "Goal has been successfully completed, great job!"
        return None

    # --- R - READ ---
    def get_employees(self):
        self.cursor.execute("SELECT employee_id, name FROM employees")
        return self.cursor.fetchall()

    def get_goals_by_employee(self, employee_id):
        self.cursor.execute("""
            SELECT g.goal_id, g.description, g.due_date, g.status, e.name AS manager_name
            FROM goals g
            JOIN employees e ON g.manager_id = e.employee_id
            WHERE g.employee_id = %s
        """, (employee_id,))
        return self.cursor.fetchall()

    def get_tasks_by_goal(self, goal_id):
        self.cursor.execute("SELECT task_id, description, is_approved FROM tasks WHERE goal_id = %s", (goal_id,))
        return self.cursor.fetchall()
    
    def get_feedback_by_goal(self, goal_id):
        self.cursor.execute("""
            SELECT f.feedback_id, f.feedback_text, e.name AS manager_name
            FROM feedback f
            JOIN employees e ON f.manager_id = e.employee_id
            WHERE f.goal_id = %s
        """, (goal_id,))
        return self.cursor.fetchall()

    def get_employee_performance_history(self, employee_id):
        self.cursor.execute("""
            SELECT g.description AS goal_desc, g.due_date, g.status, f.feedback_text
            FROM goals g
            LEFT JOIN feedback f ON g.goal_id = f.goal_id
            WHERE g.employee_id = %s
            ORDER BY g.due_date DESC
        """, (employee_id,))
        return self.cursor.fetchall()

    # --- U - UPDATE ---
    def update_goal_status(self, goal_id, new_status):
        try:
            self.cursor.execute(
                """UPDATE goals SET status = %s WHERE goal_id = %s""",
                (new_status, goal_id)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating goal status: {e}")
            self.conn.rollback()
            return False

    def update_task_approval(self, task_id, is_approved):
        try:
            self.cursor.execute(
                """UPDATE tasks SET is_approved = %s WHERE task_id = %s""",
                (is_approved, task_id)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating task approval: {e}")
            self.conn.rollback()
            return False

    # --- D - DELETE ---
    def delete_goal(self, goal_id):
        try:
            # Delete associated tasks and feedback first
            self.cursor.execute("DELETE FROM feedback WHERE goal_id = %s", (goal_id,))
            self.cursor.execute("DELETE FROM tasks WHERE goal_id = %s", (goal_id,))
            self.cursor.execute("DELETE FROM goals WHERE goal_id = %s", (goal_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting goal: {e}")
            self.conn.rollback()
            return False
            
    # --- Business Insights ---
    def get_business_insights(self):
        insights = {}
        try:
            # Total number of goals
            self.cursor.execute("SELECT COUNT(*) FROM goals")
            insights['total_goals'] = self.cursor.fetchone()[0]

            # Total number of tasks
            self.cursor.execute("SELECT COUNT(*) FROM tasks")
            insights['total_tasks'] = self.cursor.fetchone()[0]

            # Average tasks per goal
            self.cursor.execute("SELECT AVG(task_count) FROM (SELECT goal_id, COUNT(*) AS task_count FROM tasks GROUP BY goal_id) AS task_counts")
            insights['avg_tasks_per_goal'] = self.cursor.fetchone()[0]

            # Goals per status
            self.cursor.execute("SELECT status, COUNT(*) FROM goals GROUP BY status")
            insights['goals_by_status'] = dict(self.cursor.fetchall())
            
            # Most productive employee (by completed goals)
            self.cursor.execute("""
                SELECT e.name, COUNT(*) AS completed_goals
                FROM goals g
                JOIN employees e ON g.employee_id = e.employee_id
                WHERE g.status = 'Completed'
                GROUP BY e.name
                ORDER BY completed_goals DESC
                LIMIT 1
            """)
            insights['most_productive_employee'] = self.cursor.fetchone()

        except Exception as e:
            print(f"Error fetching business insights: {e}")
            return {}
        return insights