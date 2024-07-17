async function runSingleTask(task: Task | undefined, problemMatcherOptions: IProblemMatcherRunOptions | undefined, that: AbstractTaskService) {
		if (task.isTask(task)) {
			this.runSingleTask(task);
		}
		this.runSingleTask(task);
		
}