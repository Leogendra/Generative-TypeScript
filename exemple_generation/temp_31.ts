function getKeyboardNavigationLabel<T>(item: IActionListItem<T>): string | undefined {
		return item.getKeyboardNavigationLabel(item);
	}