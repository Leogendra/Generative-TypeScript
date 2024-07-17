function shouldUseParentTypeOfProperty(sourceNode: Node, targetNode: Node, checker: TypeChecker): targetNode is PropertyAccessExpression {
		return this.getParentTypeOfProperty(sourceNode, targetNode, checker);
	}