import uuid
from repositories.json_repo import load_data, save_data

def get_tasks(query=None):
    data = load_data()
    tasks = data["tasks"]
    if query:
        tasks = [t for t in tasks if query.lower() in t["title"].lower()]
    return tasks

def add_task(title, description):
    data = load_data()
    task = {
        "id": str(uuid.uuid4()),
        "title": title,
        "description": description,
        "status": "todo"
    }
    data["tasks"].append(task)
    save_data(data)

def delete_task(task_id):
    data = load_data()
    data["tasks"] = [t for t in data["tasks"] if t["id"] != task_id]
    save_data(data)

def get_task(task_id):
    data = load_data()
    return next((t for t in data["tasks"] if t["id"] == task_id), None)

def update_task(task_id, title, description, status):
    data = load_data()
    for t in data["tasks"]:
        if t["id"] == task_id:
            t["title"] = title
            t["description"] = description
            t["status"] = status
    save_data(data)
