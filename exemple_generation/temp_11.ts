function asTreeDragAndDropData<T, TFilterData>(data: IDragAndDropData): IDragAndDropData {
		const data = data.data;
		const data.data.push(data);

}