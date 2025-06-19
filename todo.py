import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk, messagebox, simpledialog, filedialog
from tkcalendar import DateEntry
from datetime import datetime
import json
import os

DATA_FILE = "tasks.json"

# Load tasks from file
def load_tasks():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                data = f.read().strip()
                if not data:
                    return []
                return json.loads(data)
        except json.JSONDecodeError:
            return []
    return []

# Save tasks to file
def save_tasks():
    with open(DATA_FILE, 'w') as f:
        json.dump(tasks, f, indent=4)

# Export current tasks to external JSON file
def export_tasks():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON Files", "*.json")],
        title="Export Tasks"
    )
    if file_path:
        with open(file_path, "w") as f:
            json.dump(tasks, f, indent=4)
        messagebox.showinfo("Export Successful", f"Tasks exported to:\n{file_path}")

# Import tasks from external JSON file
def import_tasks():
    global tasks
    file_path = filedialog.askopenfilename(
        filetypes=[("JSON Files", "*.json")],
        title="Import Tasks"
    )
    if file_path:
        try:
            with open(file_path, "r") as f:
                imported = json.load(f)
                if isinstance(imported, list):
                    tasks = imported
                    save_tasks()
                    update_listbox()
                    messagebox.showinfo("Import Successful", f"Tasks imported from:\n{file_path}")
                else:
                    messagebox.showerror("Invalid Format", "Selected file does not contain a task list.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

# Add Task
def add_task():
    task_text = entry.get().strip()
    priority = priority_var.get()
    due_date = due_date_picker.get_date().strftime('%Y-%m-%d')

    if not task_text:
        messagebox.showwarning("Warning", "Task cannot be empty!")
        return

    tasks.append({"task": task_text, "completed": False, "priority": priority, "due": due_date})

    entry.delete(0, tk.END)
    priority_dropdown.set("Medium")
    due_date_picker.set_date(datetime.now())  # reset picker
    save_tasks()
    update_listbox()

# Delete Task
def delete_task():
    selected = listbox.curselection()
    if not selected:
        messagebox.showwarning("Warning", "Please select a task to delete!")
        return
    index = selected[0]
    task_to_delete = visible_tasks[index]
    tasks.remove(task_to_delete)
    save_tasks()
    update_listbox()

# Edit Task
def edit_task():
    selected = listbox.curselection()
    if not selected:
        messagebox.showwarning("Warning", "Please select a task to edit!", parent=root)
        return

    index = selected[0]
    task_data = visible_tasks[index]

    # Modal popupclear
    edit_window = tk.Toplevel(root)
    edit_window.title("Edit Task")
    edit_window.transient(root)
    edit_window.grab_set()
    edit_window.update_idletasks()
    w = 320
    h = 260
    x = (edit_window.winfo_screenwidth() // 2) - (w // 2)
    y = (edit_window.winfo_screenheight() // 2) - (h // 2)
    edit_window.geometry(f"{w}x{h}+{x}+{y}")

    # Task Entry
    tk.Label(edit_window, text="Task:").pack(pady=5)
    task_entry = tk.Entry(edit_window, width=30)
    task_entry.insert(0, task_data["task"])
    task_entry.pack(pady=2)

    # Priority Dropdown
    tk.Label(edit_window, text="Priority:").pack(pady=5)
    priority_var = tk.StringVar()
    priority_dropdown = ttk.Combobox(edit_window, textvariable=priority_var, values=["Low", "Medium", "High"], state="readonly")
    priority_dropdown.set(task_data.get("priority", "Medium"))
    priority_dropdown.pack()

    # Due Date Picker
    tk.Label(edit_window, text="Due Date:").pack(pady=5)
    due_picker = DateEntry(edit_window, width=15, date_pattern='yyyy-mm-dd')
    try:
        due_picker.set_date(datetime.strptime(task_data.get("due", ""), "%Y-%m-%d"))
    except:
        due_picker.set_date(datetime.now())
    due_picker.pack()

    # Save Button
    def save_changes():
        new_task = task_entry.get().strip()
        new_priority = priority_var.get()
        new_due = due_picker.get_date().strftime('%Y-%m-%d')

        if not new_task:
            messagebox.showerror("Error", "Task cannot be empty.", parent=edit_window)
            return

        task_data["task"] = new_task
        task_data["priority"] = new_priority
        task_data["due"] = new_due
        save_tasks()
        update_listbox()
        edit_window.destroy()

    tk.Button(edit_window, text="Save", command=save_changes, bg="#4CAF50", fg="white", width=10).pack(pady=10)
    edit_window.bind("<Return>", lambda event: save_changes())

# Toggle Complete
def mark_complete():
    selected = listbox.curselection()
    if not selected:
        messagebox.showwarning("Warning", "Please select a task to mark!")
        return
    index = selected[0]
    task = visible_tasks[index]
    task["completed"] = not task["completed"]
    save_tasks()
    update_listbox()

# Clear Completed Tasks
def clear_completed():
    global tasks
    completed_tasks = [task for task in tasks if task["completed"]]

    if not completed_tasks:
        messagebox.showinfo("No Completed Tasks", "There are no completed tasks to clear.")
        return

    tasks = [task for task in tasks if not task["completed"]]
    save_tasks()
    update_listbox()
    messagebox.showinfo("Done", "All completed tasks have been cleared.")

# Update listbox
def update_listbox():
    global visible_tasks
    listbox.delete(0, tk.END)
    visible_tasks = []
    today = datetime.today().date()

    p_filter = priority_filter.get()
    s_filter = status_filter.get()
    only_today = show_today_only.get()

    for i, task in enumerate(tasks):
        if p_filter != "All" and task.get("priority") != p_filter:
            continue
        if s_filter == "Completed" and not task.get("completed"):
            continue
        if s_filter == "Pending" and task.get("completed"):
            continue

        try:
            due = datetime.strptime(task.get("due", ""), "%Y-%m-%d").date()
        except:
            due = None
        if only_today and due != today:
            continue

        visible_tasks.append(task)           

        status = "✓" if task["completed"] else "✗"
        priority = task.get("priority", "Medium")
        due_str = task.get("due", "N/A")
        display = f"[{priority}] {status} {task['task']} (Due: {due_str})"
        listbox.insert(tk.END, display)

        index = listbox.size() - 1

        if task["completed"]:
            listbox.itemconfig(index, {'fg': 'grey'})
        else:
            try:
                due_date = datetime.strptime(due_str, "%Y-%m-%d").date()
                if due_date < today:
                    listbox.itemconfig(index, {'fg': 'red'})
                else:
                    listbox.itemconfig(index, {'fg': 'black'})
            except:
                listbox.itemconfig(index, {'fg': 'black'})

    # Stats update
    total = len(tasks)
    completed = sum(1 for task in tasks if task["completed"])
    pending = total - completed
    stats_var.set(f"Total: {total} | Pending: {pending} | Completed: {completed}")

# --- GUI Setup ---
root = tk.Tk()
root.title("To-Do List App")
# Center the window on the screen
root.update_idletasks()
window_width = 520
window_height = 600
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width // 2) - (window_width // 2)
y = (screen_height // 2) - (window_height // 2)
root.geometry(f'{window_width}x{window_height}+{x}+{y}')

# Title
tk.Label(root, text="My To-Do List", font=("Helvetica", 18, "bold"), bg="#f5f5f5", fg="#333").pack(pady=15)

# Entry frame
entry_frame = tk.Frame(root, bg="#f5f5f5")
entry_frame.pack(pady=5)

entry = tk.Entry(entry_frame, font=("Helvetica", 12), width=22)
entry.grid(row=0, column=0, padx=5)

# Priority dropdown
priority_var = tk.StringVar()
priority_dropdown = ttk.Combobox(entry_frame, textvariable=priority_var, values=["Low", "Medium", "High"], width=10, state="readonly")
priority_dropdown.grid(row=0, column=1, padx=5)
priority_dropdown.set("Medium")  # Default

# Due Date Picker
due_date_label = tk.Label(entry_frame, text="Due:", bg="#f5f5f5")
due_date_label.grid(row=1, column=0, sticky="e", padx=5)

due_date_picker = DateEntry(entry_frame, width=15, date_pattern='yyyy-mm-dd')
due_date_picker.grid(row=1, column=1, padx=5, pady=5)

# Filter frame
filter_frame = tk.Frame(root, bg="#f5f5f5")
filter_frame.pack(pady=5)

# Priority Filter
tk.Label(filter_frame, text="Filter by Priority:", bg="#f5f5f5").grid(row=0, column=0, padx=5)
priority_filter = ttk.Combobox(filter_frame, values=["All", "Low", "Medium", "High"], state="readonly", width=10)
priority_filter.set("All")
priority_filter.grid(row=0, column=1, padx=5)

# Status Filter
tk.Label(filter_frame, text="Status:", bg="#f5f5f5").grid(row=0, column=2, padx=5)
status_filter = ttk.Combobox(filter_frame, values=["All", "Completed", "Pending"], state="readonly", width=10)
status_filter.set("All")
status_filter.grid(row=0, column=3, padx=5)

# Due Today Checkbox
show_today_only = tk.BooleanVar()
tk.Checkbutton(filter_frame, text="Due Today Only", variable=show_today_only, bg="#f5f5f5", command=update_listbox).grid(row=0, column=4, padx=10)


# Bind changes to update listbox
priority_filter.bind("<<ComboboxSelected>>", lambda e: update_listbox())
status_filter.bind("<<ComboboxSelected>>", lambda e: update_listbox())

# Listbox frame
list_frame = tk.Frame(root, bg="#f5f5f5")
list_frame.pack(pady=10)

scrollbar = tk.Scrollbar(list_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

listbox = tk.Listbox(list_frame, font=("Helvetica", 12), width=40, height=15, yscrollcommand=scrollbar.set, selectbackground="#A3C1AD", selectforeground="black")
listbox.pack(side=tk.LEFT, fill=tk.BOTH)
scrollbar.config(command=listbox.yview)

# Define fonts
normal_font = tkFont.Font(listbox, listbox.cget("font"))

# Task stats label
stats_var = tk.StringVar()
stats_label = tk.Label(root, textvariable=stats_var, font=("Helvetica", 10), bg="#f5f5f5", fg="#333")
stats_label.pack()

# Buttons frame
button_frame = tk.Frame(root, bg="#f5f5f5")
button_frame.pack(pady=10)

tk.Button(entry_frame, text="Add Task", command=add_task, bg="#4CAF50", fg="white", width=10).grid(row=0, column=2, padx=5)
tk.Button(button_frame, text="Edit", width=10, command=edit_task, bg="#2196F3", fg="white").grid(row=0, column=0, padx=5, pady=5)
tk.Button(button_frame, text="Delete", width=10, command=delete_task, bg="#f44336", fg="white").grid(row=0, column=1, padx=5, pady=5)
tk.Button(button_frame, text="Mark ✓/✗", width=10, command=mark_complete, bg="#FF9800", fg="white").grid(row=0, column=2, padx=5, pady=5)
tk.Button(button_frame, text="Clear Completed", width=15, command=clear_completed, bg="#9C27B0", fg="white").grid(row=0, column=3, padx=5, pady=5)

# Export/Import frame
file_frame = tk.Frame(root, bg="#f5f5f5")
file_frame.pack(pady=10)

tk.Button(file_frame, text="📤 Export", command=export_tasks, bg="#008CBA", fg="white", width=12).grid(row=0, column=0, padx=10)
tk.Button(file_frame, text="📥 Import", command=import_tasks, bg="#6A1B9A", fg="white", width=12).grid(row=0, column=1, padx=10)

# Initial load
tasks = load_tasks()
visible_tasks = []
update_listbox()

root.mainloop()
