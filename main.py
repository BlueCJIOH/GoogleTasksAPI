from src.services import get_lists, create_list, create_task, update_task_lists

if __name__ == "__main__":
    task_lists = get_lists()
    create_list(3)
    create_task(1, task_lists)
    update_task_lists(task_lists)
