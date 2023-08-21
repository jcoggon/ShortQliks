fetch('/get_all_reload_tasks')
    .then(response => response.json())
    .then(data => {
        const taskList = document.getElementById('task-list');
        data.forEach(task => {
            const row = document.createElement('tr');
            Object.values(task).forEach(value => {
                const cell = document.createElement('td');
                cell.textContent = value;
                row.appendChild(cell);
            });
            const editCell = document.createElement('td');
            const editLink = document.createElement('a');
            editLink.href = `/update_task_page/${task.id}`;
            editLink.textContent = 'Edit';
            editCell.appendChild(editLink);
            row.appendChild(editCell);
            taskList.appendChild(row);
        });
    });