from . import basic_logger

basic_logger.initialize_project_logger(
    name=__name__,
    path_dir_where_to_store_logs="",
    is_stdout_debug=False,
    is_to_propagate_to_root_logger=False,
)


## TODO Python Logging Learning