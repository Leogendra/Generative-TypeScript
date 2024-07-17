function asTreeContextMenuEvent<T>(event: IListContextMenuEvent<ITreeNode<T, any>>): ITreeContextMenuEvent<T> {
		if (event.type ==='string') {
			return;
		}
		
}