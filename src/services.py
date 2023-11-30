import datetime
import logging

from googleapiclient.errors import HttpError

from src.auth import create_service

SCOPES = ["https://www.googleapis.com/auth/tasks"]
API_NAME = "tasks"

service = create_service(API_NAME, SCOPES)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def get_lists() -> list:
    response = service.tasklists().list().execute()
    items = [el["id"] for el in response.get("items")]
    nextPageToken = response.get("nextPageToken")
    while nextPageToken:
        response = service.tasklists().list(pageToken=nextPageToken).execute()
        items.extend([el["id"] for el in response.get("items")])
        nextPageToken = response.get("nextPageToken")
    logging.info("successfully finished")
    return items


def create_list(len_) -> None:
    try:
        for el in range(len_):
            service.tasklists().insert(body={"title": f"mylist{el}"}).execute()
        logging.info("successfully finished")
    except HttpError as err:
        logging.error(err)


def create_task(len_, task_lists):
    try:
        for list_ in task_lists:
            for task in range(len_):
                service.tasks().insert(
                    tasklist=f"{list_}",
                    body={
                        "title": f"task{task}",
                        "description": "task_description",
                        "status": "needsAction",
                        "due": "",
                    },
                ).execute()
        logging.info("successfully finished")
    except HttpError as err:
        logging.error(err)


def update_task_lists(task_lists: list) -> None:
    try:
        for list_ in task_lists:
            response = (
                service.tasks()
                .list(
                    tasklist=list_,
                    showCompleted=False,
                    fields="nextPageToken,items(id, due)",
                )
                .execute()
            )
            tasks = list(
                map(
                    lambda el: (el["id"], el.get("due")),
                    response.get("items", []),
                )
            )
            nextPageToken = response.get("nextPageToken")
            while nextPageToken:
                response = (
                    service.tasks()
                    .list(
                        tasklist=list_,
                        showCompleted=False,
                        pageToken=nextPageToken,
                        fields="nextPageToken,items(id, due)",
                    )
                    .execute()
                )
                tasks.extend(
                    list(
                        map(
                            lambda el: (el["id"], el.get("due")),
                            response.get("items", []),
                        )
                    )
                )
                nextPageToken = response.get("nextPageToken")
            for task in tasks:
                if not task[1]:
                    service.tasks().patch(
                        tasklist=list_,
                        task=task[0],
                        body={
                            "due": (
                                           datetime.datetime.now() + datetime.timedelta(hours=1)
                                   ).isoformat()
                                   + "Z"
                        },
                    ).execute()
        logging.info("successfully finished")
    except HttpError as err:
        logging.error(err)
