class Task:
    def __init__(self, task_id, name, description, priority='normal', status='pending'):
        self.task_id = task_id
        self.name = name
        self.description = description
        self.priority = priority
        self.status = "Pending"
    
    def mark_completed(self):
        self.status = "Completed"

    def __str__(self):
        return f'"{self.name}" ({self.status}, Priority: {self.priority})'


class TaskManager:
    def __init__(self):
        self.stack = []
        self.queue = []
        self.task_counter = 1

    def add_task(self, name, description, priority):
      
        if priority.lower() not in ("high", "normal", "low"):
            print("Invalid priority! Please enter High, Normal, or Low.")
            return
        
        task = Task(self.task_counter, name, description, priority.lower())
        self.task_counter += 1
        if priority.lower() == "high":
            self.stack.append(task)
            print(f"-> Task '{name}' added successfully to the priority stack!")
        else:
            self.queue.append(task)
            print(f"-> Task '{name}' added successfully to the normal queue!")

    def view_tasks(self):
        print("Priority Stack (High Priority):")
        if self.stack:
            for task in reversed(self.stack):  
                print(f"[{task.task_id}] {task}")
        else:
            print("[Empty]")

        print("Normal Queue (Normal Priority):")
        if self.queue:
            for task in self.queue:  
                print(f"[{task.task_id}] {task}")
        else:
            print("[Empty]")

    def complete_task(self):
        if self.stack:
            task = self.stack.pop()
            task.mark_completed()
            print(f"-> Task '{task.name}' marked as completed!")
        elif self.queue:
            task = self.queue.pop(0)
            task.mark_completed()
            print(f"-> Task '{task.name}' marked as completed!")
        else:
            print("No tasks available to complete.")

    def remove_completed(self):
        initial_stack_len = len(self.stack)
        initial_queue_len = len(self.queue)
        self.stack = [task for task in self.stack if task.status != "Completed"]
        self.queue = [task for task in self.queue if task.status != "Completed"]
        print(f"-> Completed tasks removed successfully!")

    def increase_priority(self, task_id):
        task = None
        for t in self.queue:
            if t.task_id == task_id:
                task = t
                break

        if task:
            self.queue.remove(task)
            task.priority = "high"
            self.stack.append(task)
            print(f"-> Task '{task.name}' moved to high priority!")
        else:
            print(f"-> Task with ID {task_id} not found in the queue.")

def main():
    manager = TaskManager()


    task1 = Task(manager.task_counter, "Clean the house", "Vacuum and dust the living room", "low")
    manager.task_counter += 1
    task2 = Task(manager.task_counter, "Submit assignment", "Math homework due tomorrow", "normal")
    manager.task_counter += 1


    manager.queue.append(task1)
    manager.queue.append(task2)


    print("Task Management System")
    print("-----------------------")
    print("Commands:")
    print("1. Add a task")
    print("2. View tasks")
    print("3. Complete a task")
    print("4. Increase priority")
    print("5. Remove completed tasks")
    print("6. Exit")

    print()

    print("Initial State:")
    print("-----------------------")

    print("Priority Stack (High Priority):")
    if manager.stack:
        for task in reversed(manager.stack):
            print(f"[{task.task_id}] {task}")
    else:
        print("[Empty]")

    print()

    print("Normal Queue (Normal Priority):")
    if manager.queue:
        for task in manager.queue:
            print(f"[{task.task_id}] {task}")
    else:
        print("[Empty]")

    while True:
        choice = input("\nChoose an option: ")

        if choice == "1":
            name = input("Enter task name: ").strip()
            if not name:
                print("Task name cannot be empty!")
                continue
            description = input("Enter task description: ").strip()
            if not description:
                print("Task description cannot be empty!")
                continue
            priority = input("Enter task priority (High/Normal/Low): ").strip()
            manager.add_task(name, description, priority)
            print("\nUpdated State:")
            print("-----------------------")
            manager.view_tasks()

        elif choice == "2":
            print("Current Tasks:")
            manager.view_tasks()

        elif choice == "3":
            manager.complete_task()
            print("\nUpdated State:")
            print("-----------------------")
            manager.view_tasks()

        elif choice == "4":
            try:
                task_id = int(input("Enter task ID to increase priority: "))
                manager.increase_priority(task_id)
                print("\nUpdated State:")
                print("-----------------------")
                manager.view_tasks()
            except ValueError:
                print("Invalid input. Please enter a valid task ID.")

        elif choice == "5":
            manager.remove_completed()
            print("\nUpdated State:")
            print("-----------------------")
            manager.view_tasks()

        elif choice == "6":
            print("Thank you for using the Task Management System!")
            break

        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()
