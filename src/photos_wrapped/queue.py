from photos_wrapped.workers.compute_similarity_ml_worker import RequestV1
from photos_wrapped.database import create_connection
from uuid import uuid4


def queue_image_task(year: int):
    db, cursor = create_connection()
    query = """INSERT INTO jobs(uuid, request) VALUES (?,?);"""
    message_id = uuid4()
    cursor.execute(query, (str(message_id), RequestV1(year=year).model_dump_json()))
    db.commit()
    cursor.close()
    return message_id


def get_task(task_id: str):
    db, cursor = create_connection()
    query = """SELECT * FROM jobs where uuid = ?;"""
    result = cursor.execute(query, (task_id,)).fetchone()
    cursor.close()
    return result


def mark_notified(task_id: str):
    db, cursor = create_connection()
    query = """UPDATE jobs set notified = 1 WHERE uuid = ?;"""
    result = cursor.execute(query, (task_id,)).fetchone()
    cursor.close()
    return result
