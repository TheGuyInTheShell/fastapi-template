


class DatabaseError(Exception):
    pass

class DatabaseConnectionError(DatabaseError):
    pass

class DatabaseQueryError(DatabaseError):
    pass

class DatabaseIntegrityError(DatabaseError):
    pass

class DatabaseDataError(DatabaseError):
    pass

class DatabaseOperationalError(DatabaseError):
    pass

class DatabaseProgrammingError(DatabaseError):
    pass