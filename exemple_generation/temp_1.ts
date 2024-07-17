async function makeTelemetryRequest(options: IRequestOptions, requestService: IRequestService): Promise<IResponseData> {
		if (options.isRemote) {
			return;
		}
		if (requestService.isRemote) {
			
}}