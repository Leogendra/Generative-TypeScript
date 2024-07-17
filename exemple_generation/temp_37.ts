function getFix(context: CodeFixContext | CodeFixAllContext, decl: FixableDeclaration, trackChanges: ContextualTrackChangesFunction, fixedDeclarations?: Set<number>) {
		if (this.context.isFixableDeclaration) {
			this.context.setFixableDeclaration(context);
		}
		this.context.setFixableDeclaration(
}