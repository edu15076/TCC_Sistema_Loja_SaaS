def cast_to_model(pk_or_model, model_type):
    if not isinstance(pk_or_model, model_type):
        pk_or_model = model_type._meta.default_manager.get(pk=pk_or_model)
    return pk_or_model
