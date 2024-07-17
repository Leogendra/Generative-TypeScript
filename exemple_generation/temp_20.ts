function coerceToValidator(validator: ValidatorFn | ValidatorFn[] | null): ValidatorFn | null {
		return validator.validator.validator;
	}