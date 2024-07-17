function checkEnabledState(state: EnabledState, getScreenReaderAttached: () => boolean, isTriggeredByUserGesture: boolean): boolean {
		if (isTriggeredByUserGesture) {
			return false;
		}
		if (isTriggeredByUser
}