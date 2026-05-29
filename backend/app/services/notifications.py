from app.core.websocket import connection_manager
from app.models import Task


class NotificationService:
    async def notify_task_status_change(self, task: Task) -> None:
        if task.assignee_id is None:
            return
        message = {
            "event": "TASK_STATUS_UPDATED",
            "task_id": task.id,
            "task_title": task.title,
            "status": task.status.value,
            "message": f"Task #{task.id} status updated to {task.status.value}",
        }
        await connection_manager.send_personal_message(message, task.assignee_id)

    async def notify_task_reassigned(
        self,
        old_assignee_id: int | None,
        new_assignee_id: int | None,
        task: Task,
    ) -> None:
        if old_assignee_id is not None and old_assignee_id != new_assignee_id:
            await connection_manager.send_personal_message(
                {
                    "event": "TASK_REASSIGNED_FROM",
                    "task_id": task.id,
                    "task_title": task.title,
                    "old_assignee_id": old_assignee_id,
                    "new_assignee_id": new_assignee_id,
                    "message": f"Task #{task.id} was reassigned away from you.",
                },
                old_assignee_id,
            )

        if new_assignee_id is not None and new_assignee_id != old_assignee_id:
            await connection_manager.send_personal_message(
                {
                    "event": "TASK_REASSIGNED_TO",
                    "task_id": task.id,
                    "task_title": task.title,
                    "old_assignee_id": old_assignee_id,
                    "new_assignee_id": new_assignee_id,
                    "message": f"Task #{task.id} was assigned to you.",
                },
                new_assignee_id,
            )


notification_service = NotificationService()
