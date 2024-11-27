#  KISA  EMMANUEL
#  KATENDE  DERRICK
#  EMURON  IAN


from tkinter import ttk, messagebox, simpledialog
import tkinter as tk
from datetime import datetime, timedelta
import heapq
import matplotlib.pyplot as plt


class Task:
    def __init__(self, task_id, description, deadline, priority, task_type, duration):
        self.task_id = task_id
        self.description = description
        self.deadline = datetime.strptime(deadline, "%Y-%m-%d %H:%M")
        self.priority = priority
        self.task_type = task_type  # 'personal' or 'academic'
        self.duration = duration  # in minutes

    def __lt__(self, other):
        return self.deadline < other.deadline


class Scheduler:
    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        heapq.heappush(self.tasks, task)

    def get_sorted_tasks(self, by="deadline"):
        if by == "deadline":
            return sorted(self.tasks, key=lambda x: x.deadline)
        elif by == "priority":
            return sorted(self.tasks, key=lambda x: x.priority, reverse=True)
        elif by == "type":
            return sorted(self.tasks, key=lambda x: x.task_type)

    def optimize_schedule(self, total_minutes):
        n = len(self.tasks)
        dp = [[0 for _ in range(total_minutes + 1)] for _ in range(n + 1)]

        for i in range(1, n + 1):
            task = self.tasks[i - 1]
            for t in range(total_minutes + 1):
                if task.duration <= t:
                    dp[i][t] = max(dp[i - 1][t], dp[i - 1][t - task.duration] + task.priority)
                else:
                    dp[i][t] = dp[i - 1][t]

        t = total_minutes
        selected_tasks = []
        for i in range(n, 0, -1):
            if dp[i][t] != dp[i - 1][t]:
                selected_tasks.append(self.tasks[i - 1])
                t -= self.tasks[i - 1].duration
        return selected_tasks

    def search_task(self, query):
        if isinstance(query, datetime):
            return [task for task in self.tasks if task.deadline.date() == query.date()]
        elif isinstance(query, str):
            return [task for task in self.tasks if query.lower() in task.description.lower()]
        return []

    def plot_schedule(self):
        fig, ax = plt.subplots()
        start_time = datetime.now()
        for i, task in enumerate(self.tasks):
            start = (task.deadline - start_time).total_seconds() / 60
            ax.broken_barh([(start, task.duration)], (i * 10, 9), facecolors='tab:blue')
            ax.text(start, i * 10 + 5, f"{task.description}", va='center')

        plt.show()


scheduler = Scheduler()


class SchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Scheduling Assistant")

        # Frame for task entry
        self.entry_frame = tk.Frame(root)
        self.entry_frame.pack(pady=10)

        tk.Label(self.entry_frame, text="Task Description").grid(row=0, column=0)
        tk.Label(self.entry_frame, text="Deadline (YYYY-MM-DD HH:MM)").grid(row=0, column=1)
        tk.Label(self.entry_frame, text="Priority").grid(row=0, column=2)
        tk.Label(self.entry_frame, text="Task Type").grid(row=0, column=3)
        tk.Label(self.entry_frame, text="Duration (mins)").grid(row=0, column=4)

        self.desc_entry = tk.Entry(self.entry_frame)
        self.deadline_entry = tk.Entry(self.entry_frame)
        self.priority_entry = tk.Entry(self.entry_frame)
        self.type_entry = tk.Entry(self.entry_frame)
        self.duration_entry = tk.Entry(self.entry_frame)

        self.desc_entry.grid(row=1, column=0)
        self.deadline_entry.grid(row=1, column=1)
        self.priority_entry.grid(row=1, column=2)
        self.type_entry.grid(row=1, column=3)
        self.duration_entry.grid(row=1, column=4)

        tk.Button(self.entry_frame, text="Add Task", command=self.add_task).grid(row=1, column=5)

        # Frame for task display and optimization
        self.task_frame = tk.Frame(root)
        self.task_frame.pack(pady=10)

        self.tree = ttk.Treeview(self.task_frame, columns=("ID", "Description", "Deadline", "Priority", "Type", "Duration"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Deadline", text="Deadline")
        self.tree.heading("Priority", text="Priority")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Duration", text="Duration")

        self.tree.pack()

        tk.Button(root, text="Optimize Schedule", command=self.optimize_schedule).pack(pady=5)
        tk.Button(root, text="Show Gantt Chart", command=self.show_gantt_chart).pack(pady=5)
        tk.Button(root, text="Search Task", command=self.search_task).pack(pady=5)

    def add_task(self):
        try:
            task_id = len(scheduler.tasks) + 1
            description = self.desc_entry.get()
            deadline = self.deadline_entry.get()
            priority = int(self.priority_entry.get())
            task_type = self.type_entry.get()
            duration = int(self.duration_entry.get())

            task = Task(task_id, description, deadline, priority, task_type, duration)
            scheduler.add_task(task)
            self.tree.insert("", "end", values=(task_id, description, deadline, priority, task_type, duration))

            # Clear entries
            self.desc_entry.delete(0, tk.END)
            self.deadline_entry.delete(0, tk.END)
            self.priority_entry.delete(0, tk.END)
            self.type_entry.delete(0, tk.END)
            self.duration_entry.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid task details.")

    def optimize_schedule(self):
        try:
            total_minutes = int(tk.simpledialog.askstring("Optimize Schedule", "Enter available time in minutes:"))
            optimized_tasks = scheduler.optimize_schedule(total_minutes)
            optimized_message = "\n".join([f"{task.description} (Priority: {task.priority})" for task in optimized_tasks])
            messagebox.showinfo("Optimized Tasks", f"Selected tasks for optimized schedule:\n\n{optimized_message}")
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid time in minutes.")

    def search_task(self):
        query = tk.simpledialog.askstring("Search Task", "Enter keyword or date (YYYY-MM-DD):")
        try:
            if "-" in query:
                query_date = datetime.strptime(query, "%Y-%m-%d")
                results = scheduler.search_task(query_date)
            else:
                results = scheduler.search_task(query)

            if results:
                result_message = "\n".join([f"{task.description} (Deadline: {task.deadline}, Priority: {task.priority})" for task in results])
                messagebox.showinfo("Search Results", f"Matching tasks:\n\n{result_message}")
            else:
                messagebox.showinfo("Search Results", "No matching tasks found.")
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid date or keyword.")

    def show_gantt_chart(self):
        scheduler.plot_schedule()


# Run the application
root = tk.Tk()
app = SchedulerApp(root)
root.mainloop()
