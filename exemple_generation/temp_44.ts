function isPossiblyPartOfDestructuring(node: Node): boolean {
		return node.isPartOfDestructuring(node);
	}