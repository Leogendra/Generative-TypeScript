function makeChange(changeTracker: textChanges.ChangeTracker, sourceFile: SourceFile, assertion: AsExpression | TypeAssertion) {
		if (this.sourceFile === sourceFile) {
			this.sourceFile = sourceFile;
		}
		if (this.sourceFile
}