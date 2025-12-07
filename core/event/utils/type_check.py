def type_check(args_types, kwargs_types, args, kwargs):


    if len(args_types) != len(args):


        raise ValueError("Number of arguments does not match")


    if len(kwargs_types) != len(kwargs):


        raise ValueError("Number of keyword arguments does not match")


    for arg, arg_type in zip(args, args_types):


        if not isinstance(arg, arg_type):


            raise TypeError(f"Argument {arg} is not of type {arg_type}")


    for key, value in kwargs.items():

        if not isinstance(value, kwargs_types[key]):


            raise TypeError(f"Argument {key} is not of type {kwargs_types[key]}")
