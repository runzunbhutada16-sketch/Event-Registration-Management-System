import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import mysql.connector


# =====================================================
# DATABASE CONNECTION
# =====================================================

root = tk.Tk()
root.withdraw()

password = simpledialog.askstring(
    "MySQL Login",
    "Enter MySQL root password:",
    show="*"
)

try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password=password,
        database="EventDB"
    )
    cursor = db.cursor()

except mysql.connector.Error as e:
    messagebox.showerror(
        "Database Connection Error",
        "Could not connect to EventDB.\n\n" + str(e)
    )
    root.destroy()
    raise SystemExit


# =====================================================
# FUNCTIONS
# =====================================================

def clear_entries():
    name_entry.delete(0, tk.END)
    email_entry.delete(0, tk.END)
    phone_entry.delete(0, tk.END)


def clear_table():
    for item in table.get_children():
        table.delete(item)


def set_columns(*columns):
    table["columns"] = columns

    for column in columns:
        table.heading(column, text=column)
        table.column(column, width=170)


# =====================================================
# ADD USER
# =====================================================

def add_user():
    name = name_entry.get().strip()
    email = email_entry.get().strip()
    phone = phone_entry.get().strip()

    if not name or not email:
        messagebox.showwarning(
            "Missing Information",
            "Name and Email are required."
        )
        return

    try:
        cursor.execute(
            """
            INSERT INTO Users (name, email, phone)
            VALUES (%s, %s, %s)
            """,
            (name, email, phone)
        )

        db.commit()

        messagebox.showinfo(
            "Success",
            "User added successfully!"
        )

        clear_entries()
        show_users()

    except mysql.connector.Error as e:

        if e.errno == 1062:
            messagebox.showwarning(
                "Duplicate Email",
                "This email is already registered."
            )
        else:
            messagebox.showerror(
                "Database Error",
                str(e)
            )


# =====================================================
# VIEW USERS
# =====================================================

def show_users():
    try:
        cursor.execute(
            "SELECT user_id, name, email, phone FROM Users"
        )

        rows = cursor.fetchall()

        set_columns(
            "ID",
            "Name",
            "Email",
            "Phone"
        )

        clear_table()

        for row in rows:
            table.insert("", tk.END, values=row)

    except mysql.connector.Error as e:
        messagebox.showerror(
            "Database Error",
            str(e)
        )


# =====================================================
# UPDATE USER
# =====================================================

def update_user():
    user_id = user_id_update_entry.get().strip()
    name = name_entry.get().strip()
    email = email_entry.get().strip()
    phone = phone_entry.get().strip()

    if not user_id:
        messagebox.showwarning(
            "Missing ID",
            "Enter User ID to update."
        )
        return

    if not name or not email:
        messagebox.showwarning(
            "Missing Information",
            "Enter Name and Email."
        )
        return

    try:
        cursor.execute(
            """
            UPDATE Users
            SET name = %s, email = %s, phone = %s
            WHERE user_id = %s
            """,
            (name, email, phone, user_id)
        )

        if cursor.rowcount == 0:
            messagebox.showwarning(
                "Not Found",
                "User ID does not exist."
            )
            return

        db.commit()

        messagebox.showinfo(
            "Success",
            "User updated successfully!"
        )

        user_id_update_entry.delete(0, tk.END)
        clear_entries()
        show_users()

    except mysql.connector.Error as e:

        if e.errno == 1062:
            messagebox.showwarning(
                "Duplicate Email",
                "This email is already used."
            )
        else:
            messagebox.showerror(
                "Database Error",
                str(e)
            )


# =====================================================
# DELETE USER
# =====================================================

def delete_user():
    user_id = user_id_update_entry.get().strip()

    if not user_id:
        messagebox.showwarning(
            "Missing ID",
            "Enter User ID to delete."
        )
        return

    try:
        cursor.execute(
            """
            SELECT registration_id
            FROM Registrations
            WHERE user_id = %s
            """,
            (user_id,)
        )

        if cursor.fetchone():
            messagebox.showwarning(
                "Cannot Delete",
                "This user has event registrations.\n"
                "Delete their registrations first."
            )
            return

        cursor.execute(
            "DELETE FROM Users WHERE user_id = %s",
            (user_id,)
        )

        if cursor.rowcount == 0:
            messagebox.showwarning(
                "Not Found",
                "User ID does not exist."
            )
            return

        db.commit()

        messagebox.showinfo(
            "Success",
            "User deleted successfully!"
        )

        user_id_update_entry.delete(0, tk.END)
        show_users()

    except mysql.connector.Error as e:
        db.rollback()
        messagebox.showerror(
            "Database Error",
            str(e)
        )


# =====================================================
# VIEW EVENTS
# =====================================================

def show_events():
    try:
        cursor.execute(
            """
            SELECT event_id, title, event_date, venue
            FROM Events
            """
        )

        rows = cursor.fetchall()

        set_columns(
            "ID",
            "Event",
            "Date",
            "Venue"
        )

        clear_table()

        for row in rows:
            table.insert("", tk.END, values=row)

    except mysql.connector.Error as e:
        messagebox.showerror(
            "Database Error",
            str(e)
        )


# =====================================================
# REGISTER FOR EVENT
# =====================================================

def register_event():
    user_id = user_id_entry.get().strip()
    event_id = event_id_entry.get().strip()

    if not user_id or not event_id:
        messagebox.showwarning(
            "Missing Information",
            "Enter User ID and Event ID."
        )
        return

    try:

        # Check user
        cursor.execute(
            "SELECT user_id FROM Users WHERE user_id = %s",
            (user_id,)
        )

        if cursor.fetchone() is None:
            messagebox.showwarning(
                "Invalid User",
                "User ID does not exist."
            )
            return

        # Check event
        cursor.execute(
            "SELECT event_id FROM Events WHERE event_id = %s",
            (event_id,)
        )

        if cursor.fetchone() is None:
            messagebox.showwarning(
                "Invalid Event",
                "Event ID does not exist."
            )
            return

        # Check duplicate registration
        cursor.execute(
            """
            SELECT registration_id
            FROM Registrations
            WHERE user_id = %s AND event_id = %s
            """,
            (user_id, event_id)
        )

        if cursor.fetchone() is not None:
            messagebox.showwarning(
                "Already Registered",
                "This user is already registered for this event."
            )
            return

        # Insert registration
        cursor.execute(
            """
            INSERT INTO Registrations
            (user_id, event_id)
            VALUES (%s, %s)
            """,
            (user_id, event_id)
        )

        db.commit()

        messagebox.showinfo(
            "Success",
            "Event registered successfully!"
        )

        user_id_entry.delete(0, tk.END)
        event_id_entry.delete(0, tk.END)

        show_registrations()

    except mysql.connector.Error as e:
        db.rollback()

        messagebox.showerror(
            "Database Error",
            str(e)
        )


# =====================================================
# VIEW REGISTRATIONS
# =====================================================

def show_registrations():
    try:
        cursor.execute(
            """
            SELECT
                r.registration_id,
                u.name,
                e.title,
                e.event_date
            FROM Registrations r
            JOIN Users u
                ON r.user_id = u.user_id
            JOIN Events e
                ON r.event_id = e.event_id
            ORDER BY r.registration_id
            """
        )

        rows = cursor.fetchall()

        set_columns(
            "ID",
            "Participant",
            "Event",
            "Date"
        )

        clear_table()

        for row in rows:
            table.insert("", tk.END, values=row)

    except mysql.connector.Error as e:
        messagebox.showerror(
            "Database Error",
            str(e)
        )


# =====================================================
# MAIN WINDOW
# =====================================================

root.deiconify()

root.title(
    "Event Registration Management System"
)

root.geometry("950x650")

root.resizable(True, True)


# =====================================================
# TITLE
# =====================================================

title = tk.Label(
    root,
    text="EVENT REGISTRATION MANAGEMENT SYSTEM",
    font=("Arial", 20, "bold")
)

title.pack(pady=15)


# =====================================================
# USER MANAGEMENT
# =====================================================

user_frame = tk.LabelFrame(
    root,
    text="User Management",
    padx=10,
    pady=10
)

user_frame.pack(
    fill="x",
    padx=20,
    pady=5
)


tk.Label(
    user_frame,
    text="Name"
).grid(
    row=0,
    column=0,
    padx=5,
    pady=5
)

name_entry = tk.Entry(
    user_frame,
    width=20
)

name_entry.grid(
    row=0,
    column=1,
    padx=5
)


tk.Label(
    user_frame,
    text="Email"
).grid(
    row=0,
    column=2,
    padx=5
)

email_entry = tk.Entry(
    user_frame,
    width=22
)

email_entry.grid(
    row=0,
    column=3,
    padx=5
)


tk.Label(
    user_frame,
    text="Phone"
).grid(
    row=0,
    column=4,
    padx=5
)

phone_entry = tk.Entry(
    user_frame,
    width=16
)

phone_entry.grid(
    row=0,
    column=5,
    padx=5
)


# User ID for Update/Delete

tk.Label(
    user_frame,
    text="User ID"
).grid(
    row=1,
    column=0,
    padx=5,
    pady=10
)

user_id_update_entry = tk.Entry(
    user_frame,
    width=10
)

user_id_update_entry.grid(
    row=1,
    column=1,
    padx=5
)


tk.Button(
    user_frame,
    text="Add User",
    width=12,
    command=add_user
).grid(
    row=1,
    column=2,
    padx=5
)


tk.Button(
    user_frame,
    text="View Users",
    width=12,
    command=show_users
).grid(
    row=1,
    column=3,
    padx=5
)


tk.Button(
    user_frame,
    text="Update User",
    width=12,
    command=update_user
).grid(
    row=1,
    column=4,
    padx=5
)


tk.Button(
    user_frame,
    text="Delete User",
    width=12,
    command=delete_user
).grid(
    row=1,
    column=5,
    padx=5
)


# =====================================================
# EVENT REGISTRATION
# =====================================================

reg_frame = tk.LabelFrame(
    root,
    text="Event Registration",
    padx=10,
    pady=10
)

reg_frame.pack(
    fill="x",
    padx=20,
    pady=5
)


tk.Label(
    reg_frame,
    text="User ID"
).grid(
    row=0,
    column=0,
    padx=5
)

user_id_entry = tk.Entry(
    reg_frame,
    width=15
)

user_id_entry.grid(
    row=0,
    column=1,
    padx=5
)


tk.Label(
    reg_frame,
    text="Event ID"
).grid(
    row=0,
    column=2,
    padx=5
)

event_id_entry = tk.Entry(
    reg_frame,
    width=15
)

event_id_entry.grid(
    row=0,
    column=3,
    padx=5
)


tk.Button(
    reg_frame,
    text="Register",
    width=12,
    command=register_event
).grid(
    row=0,
    column=4,
    padx=10
)


tk.Button(
    reg_frame,
    text="View Events",
    width=15,
    command=show_events
).grid(
    row=1,
    column=2,
    padx=5,
    pady=10
)


tk.Button(
    reg_frame,
    text="View Registrations",
    width=18,
    command=show_registrations
).grid(
    row=1,
    column=3,
    padx=5
)


# =====================================================
# RESULT TABLE
# =====================================================

table_frame = tk.Frame(root)

table_frame.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=10
)


table = ttk.Treeview(
    table_frame,
    show="headings"
)

table.pack(
    side="left",
    fill="both",
    expand=True
)


scrollbar = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=table.yview
)

scrollbar.pack(
    side="right",
    fill="y"
)

table.configure(
    yscrollcommand=scrollbar.set
)


set_columns(
    "ID",
    "Name/Event",
    "Email/Date",
    "Phone/Venue"
)


# =====================================================
# CLOSE APPLICATION
# =====================================================

def close_app():
    try:
        cursor.close()
        db.close()
    except:
        pass

    root.destroy()


root.protocol(
    "WM_DELETE_WINDOW",
    close_app
)


# =====================================================
# START APPLICATION
# =====================================================

root.mainloop()