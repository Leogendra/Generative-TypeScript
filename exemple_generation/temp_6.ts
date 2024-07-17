function reportTelemetry(telemetryService: ITelemetryService, eventName: string, data: ITelemetryData): void {
		if (telemetryService.isTelemetry(eventName)) {

}}