from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,Field
from datetime import date
from typing import List

from fastapi.responses import JSONResponse


app = FastAPI()



class Subtask(BaseModel):
    id: int 
    title: str
    completed: bool
    

class Task(BaseModel):
    id: int
    title: str
    description: str
    completed: bool = False 
    priority: int = Field(...,ge=1,le=5)
    due_date: date
    subtask: list[Subtask] = [] 


    


tasks_list: List[Task] = []



@app.get("/tasks")
async def get_all_tasks():
    return {"data":tasks_list}

@app.get("/tasks/{task_id}")
async def get_task_with_id(task_id: int):
    task = next((t for t in tasks_list if t.id == task_id), None)
    if task is None:
        raise HTTPException(status_code=404, detail="Task no encontrado")
    else:
        return{"data":task}
        
@app.post("/tasks")
async def create_task(task: Task):
    tasks_list.append(task)
    return {"message":"Task create", "task":task}

@app.put("/tasks/{task_id}")
async def update_task_with_id(task_id: int, task: Task):
    for index,t in enumerate(tasks_list):
        if t.id == task_id:
            tasks_list[index] = task
            return {"message":"Task update", "task":task}
        else:
            raise HTTPException(status_code=404, detail="Task no encontrado")


@app.delete("/tasks/{task_id}")
async def delete_task_with_id(task_id: int):
    task = next((t for t in tasks_list if t.id == task_id), None)
    tasks_list.remove(task)
    return {"message":"Task delete"}

