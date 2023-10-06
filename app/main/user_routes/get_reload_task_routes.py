

@app.route('/get_reload_task/<task_id>', methods=['GET'])
def get_reload_task(task_id):
    task = ReloadTask.query.get(task_id)
    if not task:
        return ({"error": "Task not found"}), 404
    return task.to_dict()  # Assuming you have a to_dict() method in your ReloadTask model