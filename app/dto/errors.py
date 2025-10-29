class DatabaseError(Exception):
    pass

class BusinessException(Exception):
    """Lỗi nghiệp vụ, ví dụ: dữ liệu người dùng không hợp lệ."""
    pass

class SystemException(Exception):
    """Lỗi hệ thống (DB, mã hóa, ...)."""
    pass

class AgentClientError(Exception):
    pass