import time
from camunda.external_task.external_task import ExternalTask, TaskResult
from camunda.external_task.external_task_worker import ExternalTaskWorker

default_config = {
    "maxTasks": 1,
    "lockDuration": 10000,
    "asyncResponseTimeout": 5000,
    "retries": 3,
    "retryTimeout": 5000,
    "sleepSeconds": 30
}

def handle_task(task: ExternalTask) -> TaskResult:
  
    print("hi from IID :D")
    print(task)
    
    return task.complete(task.get_variables())

if __name__ == '__main__':
   ExternalTaskWorker(worker_id="1", config=default_config).subscribe("iid", handle_task)
