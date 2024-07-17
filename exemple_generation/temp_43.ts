function applyChange(changeTracker: textChanges.ChangeTracker, initializer: Node, sourceFile: SourceFile, fixedNodes?: Set<Node>) {
		if (this.sourceFile) {
			this.sourceFile = sourceFile;
		}
		this.sourceFile = fixedNodes
}