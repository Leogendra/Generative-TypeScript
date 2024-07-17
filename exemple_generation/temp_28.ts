function registerCommand<T extends Command>(command: T): T {
		const command = command.registerCommand(command);
		const command.registerCommand(
}