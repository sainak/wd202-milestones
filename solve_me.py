from http.server import BaseHTTPRequestHandler, HTTPServer


class TasksCommand:
    TASKS_FILE = "tasks.txt"
    COMPLETED_TASKS_FILE = "completed.txt"

    current_items = {}
    completed_items = []

    def read_current(self):
        try:
            file = open(self.TASKS_FILE, "r")
            for line in file.readlines():
                item = line[:-1].split(" ")
                self.current_items[int(item[0])] = " ".join(item[1:])
            file.close()
        except Exception:
            pass

    def read_completed(self):
        try:
            file = open(self.COMPLETED_TASKS_FILE, "r")
            self.completed_items = file.readlines()
            file.close()
        except Exception:
            pass

    def write_current(self):
        with open(self.TASKS_FILE, "w+") as f:
            f.truncate(0)
            for key in sorted(self.current_items.keys()):
                f.write(f"{key} {self.current_items[key]}\n")

    def write_completed(self):
        with open(self.COMPLETED_TASKS_FILE, "w+") as f:
            f.truncate(0)
            for item in self.completed_items:
                f.write(f"{item}\n")

    def runserver(self):
        address = "127.0.0.1"
        port = 8000
        server_address = (address, port)
        httpd = HTTPServer(server_address, TasksServer)
        print(f"Started HTTP Server on http://{address}:{port}")
        httpd.serve_forever()

    def run(self, command, args):
        self.read_current()
        self.read_completed()
        if command == "add":
            self.add(args)
        elif command == "done":
            self.done(args)
        elif command == "delete":
            self.delete(args)
        elif command == "ls":
            self.ls()
        elif command == "report":
            self.report()
        elif command == "runserver":
            self.runserver()
        elif command == "help":
            self.help()

    def help(self):
        print(
            """Usage :-
$ python tasks.py add 2 hello world # Add a new item with priority 2 and text "hello world" to the list
$ python tasks.py ls # Show incomplete priority list items sorted by priority in ascending order
$ python tasks.py del PRIORITY_NUMBER # Delete the incomplete item with the given priority number
$ python tasks.py done PRIORITY_NUMBER # Mark the incomplete item with the given PRIORITY_NUMBER as complete
$ python tasks.py help # Show usage
$ python tasks.py report # Statistics
$ python tasks.py runserver # Starts the tasks management server"""
        )

    def add(self, args):
        priority, task = int(args[0]), args[1]
        if priority not in self.current_items:
            self.current_items[priority] = task
        else:
            _priority, _task = priority, task
            task_priorities = sorted(self.current_items.keys())
            i = task_priorities.index(priority)
            for key in task_priorities[i:]:
                if key == _priority:
                    temp_task = self.current_items[key]
                    self.current_items[key] = _task
                    _task = temp_task
                    _priority += 1
                else:
                    self.current_items[_priority] = temp_task
                    break
            else:
                self.current_items[_priority] = temp_task
        self.write_current()
        print(f'Added task: "{task}" with priority {priority}')

    def done(self, args):
        priority = int(args[0])
        try:
            self.completed_items.append(self.current_items[priority])
            del self.current_items[priority]
            self.write_current()
            self.write_completed()
            print("Marked item as done.")
        except KeyError:
            print(f"Error: no incomplete item with priority {priority} exists.")

    def delete(self, args):
        priority = int(args[0])
        try:
            del self.current_items[priority]
            print(f"Deleted item with priority {priority}")
            self.write_current()
        except KeyError:
            print(
                f"Error: item with priority {priority} does not exist. Nothing deleted."
            )

    def ls(self):
        for i, key in enumerate(sorted(self.current_items.keys())):
            print(f"{i+1}. {self.current_items[key]} [{key}]")

    def report(self):
        print("Pending :", len(self.current_items))
        for i, key in enumerate(sorted(self.current_items.keys())):
            print(f"{i+1}. {self.current_items[key]} [{key}]")
        print("\nCompleted :", len(self.completed_items))
        for i, item in enumerate(self.completed_items):
            print(f"{i+1}. {item}")

    def _html_style(self):
        return """
        <style>
        table, th, td {
            border: 1px solid black;
            border-collapse: collapse;
            padding: 15px;
        }
        </style>
        """

    def render_pending_tasks(self):
        self.read_current()
        table_header = """
        <table>
            <tr>
                <th>Index</th>
                <th>Priority</th>
                <th>Task</th>
            </tr>
        """
        table_footer = "</table>"
        table_rows = ""
        for i, key in enumerate(sorted(self.current_items.keys())):
            table_rows += f"""
            <tr>
                <th>{i+1}</th>
                <td>{key}</td>
                <td>{self.current_items[key]}</td>
            </tr>
            """
        return self._html_style() + table_header + table_rows + table_footer

    def render_completed_tasks(self):
        self.read_completed()
        table_header = """
        <table>
            <tr>
                <th>Index</th>
                <th>Task</th>
            </tr>
        """
        table_footer = "</table>"
        table_rows = ""
        for i, item in enumerate(self.completed_items):
            table_rows += f"""
            <tr>
                <th>{i+1}</th>
                <td>{item}</td>
            </tr>
            """
        return self._html_style() + table_header + table_rows + table_footer


class TasksServer(TasksCommand, BaseHTTPRequestHandler):
    def do_GET(self):
        task_command_object = TasksCommand()
        if self.path == "/tasks":
            content = task_command_object.render_pending_tasks()
        elif self.path == "/completed":
            content = task_command_object.render_completed_tasks()
        else:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("content-type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode())
