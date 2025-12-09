"""
Test fixtures for family management.

Provides sample data for children, organisations, and communication channels
for use in unit and integration tests.
"""

from datetime import date, datetime, timedelta
from uuid import uuid4


# Sample child data
CHILD_1 = {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Emma Johnson",
    "date_of_birth": date(2015, 6, 15),
    "gender": "female",
    "interests": "Soccer, reading, science experiments",
}

CHILD_2 = {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "name": "Liam Smith",
    "date_of_birth": date(2017, 3, 22),
    "gender": "male",
    "interests": "Basketball, video games, coding",
}

CHILD_3 = {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "name": "Olivia Brown",
    "date_of_birth": date(2018, 9, 10),
    "gender": "female",
    "interests": "Dancing, art, music",
}

# Sample child with minimal data (only required fields)
CHILD_MINIMAL = {
    "id": "880e8400-e29b-41d4-a716-446655440003",
    "name": "Noah Davis",
    "date_of_birth": date(2016, 12, 5),
}


# Sample organisation data
ORG_SCHOOL_1 = {
    "id": "990e8400-e29b-41d4-a716-446655440010",
    "name": "Springfield Elementary School",
    "type": "school",
    "address": "123 Main St, Springfield, VIC 3000",
    "contact_info": {
        "phone": "+61 3 9876 5432",
        "email": "admin@springfield.edu.au",
        "website": "https://springfield.edu.au",
    },
}

ORG_DAYCARE_1 = {
    "id": "aa0e8400-e29b-41d4-a716-446655440011",
    "name": "Sunshine Daycare Center",
    "type": "daycare",
    "address": "456 Oak Ave, Melbourne, VIC 3001",
    "contact_info": {
        "phone": "+61 3 9123 4567",
        "email": "info@sunshine-daycare.com.au",
    },
}

ORG_SPORTS_1 = {
    "id": "bb0e8400-e29b-41d4-a716-446655440012",
    "name": "Melbourne Junior Soccer Club",
    "type": "sports_team",
    "address": "789 Sports Rd, Melbourne, VIC 3002",
    "contact_info": {
        "phone": "+61 3 9555 1234",
        "email": "coach@mjsc.org.au",
        "website": "https://mjsc.org.au",
    },
}

# Sample organisation with minimal data (only required fields)
ORG_MINIMAL = {
    "id": "cc0e8400-e29b-41d4-a716-446655440013",
    "name": "Tiny Tots Kindergarten",
    "type": "kindergarten",
}


# Sample communication channel data
CHANNEL_COMPASS_1 = {
    "id": "dd0e8400-e29b-41d4-a716-446655440020",
    "organisation_id": "990e8400-e29b-41d4-a716-446655440010",  # Springfield Elementary
    "channel_type": "compass",
    "credential_source": "compass_springfield",
    "config": {
        "base_url": "https://springfield.compass.education",
        "sync_interval_hours": 24,
    },
    "is_active": True,
    "last_sync_at": datetime.now() - timedelta(hours=2),
    "last_sync_status": "success",
}

CHANNEL_COMPASS_2 = {
    "id": "ee0e8400-e29b-41d4-a716-446655440021",
    "organisation_id": "aa0e8400-e29b-41d4-a716-446655440011",  # Sunshine Daycare
    "channel_type": "compass",
    "credential_source": "compass_sunshine",
    "config": {
        "base_url": "https://sunshine.compass.education",
        "sync_interval_hours": 12,
    },
    "is_active": True,
    "last_sync_at": None,  # Never synced
    "last_sync_status": "pending",
}

# Sample channel with minimal data
CHANNEL_MINIMAL = {
    "id": "ff0e8400-e29b-41d4-a716-446655440022",
    "organisation_id": "bb0e8400-e29b-41d4-a716-446655440012",  # Soccer Club
    "channel_type": "other",
    "is_active": False,
}


# Sample child-organisation associations
ASSOCIATION_1 = {
    "child_id": "550e8400-e29b-41d4-a716-446655440000",  # Emma
    "organisation_id": "990e8400-e29b-41d4-a716-446655440010",  # Springfield Elementary
}

ASSOCIATION_2 = {
    "child_id": "550e8400-e29b-41d4-a716-446655440000",  # Emma
    "organisation_id": "bb0e8400-e29b-41d4-a716-446655440012",  # Soccer Club
}

ASSOCIATION_3 = {
    "child_id": "660e8400-e29b-41d4-a716-446655440001",  # Liam
    "organisation_id": "990e8400-e29b-41d4-a716-446655440010",  # Springfield Elementary
}

ASSOCIATION_4 = {
    "child_id": "770e8400-e29b-41d4-a716-446655440002",  # Olivia
    "organisation_id": "aa0e8400-e29b-41d4-a716-446655440011",  # Sunshine Daycare
}


# Sample credentials
CREDENTIAL_COMPASS_1 = {
    "source": "compass_springfield",
    "username": "parent1@example.com",
    "password": "Test_Password_123!",
}

CREDENTIAL_COMPASS_2 = {
    "source": "compass_sunshine",
    "username": "parent2@example.com",
    "password": "Another_Password_456!",
}


# Validation test data
INVALID_CHILD_FUTURE_DATE = {
    "name": "Future Child",
    "date_of_birth": date.today() + timedelta(days=1),  # Future date - should fail validation
}

INVALID_CHILD_MISSING_NAME = {
    "date_of_birth": date(2015, 1, 1),
    # Missing required 'name' field
}

INVALID_ORG_MISSING_TYPE = {
    "name": "Missing Type School",
    # Missing required 'type' field
}

INVALID_ORG_INVALID_TYPE = {
    "name": "Invalid Type School",
    "type": "university",  # Not in valid enum
}

DUPLICATE_ORG_NAME = {
    "id": "duplicat-e840-41d4-a716-446655440099",
    "name": "Springfield Elementary School",  # Duplicate of ORG_SCHOOL_1
    "type": "school",
}


def generate_child_data(**overrides):
    """
    Generate child data with optional field overrides.

    Args:
        **overrides: Fields to override in the default child data

    Returns:
        dict: Child data with overrides applied
    """
    data = {
        "id": str(uuid4()),
        "name": "Test Child",
        "date_of_birth": date(2015, 1, 1),
    }
    data.update(overrides)
    return data


def generate_organisation_data(**overrides):
    """
    Generate organisation data with optional field overrides.

    Args:
        **overrides: Fields to override in the default organisation data

    Returns:
        dict: Organisation data with overrides applied
    """
    data = {
        "id": str(uuid4()),
        "name": f"Test Organisation {uuid4().hex[:8]}",  # Unique name
        "type": "school",
    }
    data.update(overrides)
    return data


def generate_channel_data(organisation_id, **overrides):
    """
    Generate communication channel data with optional field overrides.

    Args:
        organisation_id: ID of the parent organisation
        **overrides: Fields to override in the default channel data

    Returns:
        dict: Channel data with overrides applied
    """
    data = {
        "id": str(uuid4()),
        "organisation_id": organisation_id,
        "channel_type": "compass",
        "is_active": True,
    }
    data.update(overrides)
    return data
