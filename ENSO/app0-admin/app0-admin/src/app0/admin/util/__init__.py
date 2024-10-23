"""
util module
"""
import random
import string

IDX_USER = 'app0.user'
IDX_APP = 'app0.app'
IDX_GROUP = 'app0.group'
IDX_ROLE = 'app0.role'
IDX_USER_ROLE = 'app0.user_role'
IDX_NOTIFICATION = 'app0.notification'
IDX_BASE_MAIL = 'app0.tmail'
IDX_REGISTRATION = 'app0.registration'
IDX_PLAN = 'app0.plan'
IDX_COUNTER = 'app0.counter'

# roles
ROLE_ADMIN = "App0 Admin"
ROLE_USER = "App0 User"
# user actions
ACT_USER_CREATE = "ACT_USER_CREATE"
ACT_USER_DELETE_USER = "ACT_USER_DELETE_USER"
# registration actions
ACT_REGISTRATION_DELETE = "ACT_REGISTRATION_DELETE"
# plan actions
ACT_PLAN_DELETE = "ACT_PLAN_DELETE"
# role actions
ACT_ROLE_ARCHIVE = "ACT_ROLE_ARCHIVE"
ACT_ROLE_UNARCHIVE = "ACT_ROLE_UNARCHIVE"
# app actions
ACT_APP_ARCHIVE = "ACT_APP_ARCHIVE"
ACT_APP_UNARCHIVE = "ACT_APP_UNARCHIVE"
# user-role actions
ACT_USERROLE_DELETE = "ACT_USERROLE_DELETE"


def rstri(length) -> str:
    """
    get random digits string of length
    """
    return ''.join(random.choice(string.digits) for x in range(length))


def rfloat(base_value: float, percent_range: float) -> float:
    # Calculate the lower and upper bounds based on the percent range
    lower_bound = base_value - (base_value * percent_range / 100)
    upper_bound = base_value + (base_value * percent_range / 100)
    
    # Generate a random float within the calculated bounds
    random_float = random.uniform(lower_bound, upper_bound)
    return random_float
