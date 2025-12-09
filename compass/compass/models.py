"""Pydantic models for Compass API data structures."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CalendarEventLocation(BaseModel):
    """Location information for a calendar event."""

    model_config = ConfigDict(populate_by_name=True)

    type: str = Field(
        alias="__type",
        default="CalendarEventLocation:http://jdlf.com.au/ns/data/calendar",
    )
    covering_location_id: Optional[int] = Field(alias="coveringLocationId", default=None)
    covering_location_name: Optional[str] = Field(alias="coveringLocationName", default=None)
    location_id: int = Field(alias="locationId")
    location_name: Optional[str] = Field(alias="locationName", default=None)


class CalendarEventManager(BaseModel):
    """Manager information for a calendar event."""

    model_config = ConfigDict(populate_by_name=True)

    type: str = Field(
        alias="__type",
        default="CalendarEventManager:http://jdlf.com.au/ns/data/calendar",
    )
    covering_import_identifier: Optional[str] = Field(
        alias="coveringImportIdentifier", default=None
    )
    covering_user_id: Optional[int] = Field(alias="coveringUserId", default=None)
    manager_import_identifier: str = Field(alias="managerImportIdentifier")
    manager_user_id: int = Field(alias="managerUserId")


class CompassEvent(BaseModel):
    """Compass calendar event model."""

    model_config = ConfigDict(populate_by_name=True)

    type: str = Field(
        alias="__type", default="CalendarTransport:http://jdlf.com.au/ns/data/calendar"
    )
    activity_id: int = Field(alias="activityId")
    activity_import_identifier: Optional[str] = Field(
        alias="activityImportIdentifier", default=None
    )
    activity_type: int = Field(alias="activityType")
    all_day: bool = Field(alias="allDay")
    attendance_mode: int = Field(alias="attendanceMode")
    attendee_user_id: int = Field(alias="attendeeUserId")
    background_color: str = Field(alias="backgroundColor")
    calendar_id: int = Field(alias="calendarId")
    category_ids: Optional[str] = Field(alias="categoryIds", default=None)
    comment: Optional[str] = Field(default=None)
    description: str
    event_setup_status: Optional[int] = Field(alias="eventSetupStatus", default=None)
    finish: datetime
    guid: str
    in_class_status: Optional[int] = Field(alias="inClassStatus", default=None)
    instance_id: str = Field(alias="instanceId")
    is_recurring: bool = Field(alias="isRecurring")
    learning_task_activity_id: Optional[int] = Field(
        alias="learningTaskActivityId", default=None
    )
    learning_task_id: Optional[int] = Field(alias="learningTaskId", default=None)
    lesson_plan_configured: bool = Field(alias="lessonPlanConfigured")
    location: Optional[str] = Field(default=None)
    locations: Optional[list[CalendarEventLocation]] = Field(default=None)
    long_title: str = Field(alias="longTitle")
    long_title_without_time: str = Field(alias="longTitleWithoutTime")
    manager_id: int = Field(alias="managerId")
    managers: Optional[list[CalendarEventManager]] = Field(default=None)
    minutes_meeting_id: Optional[int] = Field(alias="minutesMeetingId", default=None)
    period: Optional[str] = Field(default=None)
    recurring_finish: Optional[datetime] = Field(alias="recurringFinish", default=None)
    recurring_start: Optional[datetime] = Field(alias="recurringStart", default=None)
    repeat_days: Optional[str] = Field(alias="repeatDays", default=None)
    repeat_forever: bool = Field(alias="repeatForever")
    repeat_frequency: int = Field(alias="repeatFrequency")
    repeat_until: Optional[datetime] = Field(alias="repeatUntil", default=None)
    roll_marked: bool = Field(alias="rollMarked")
    running_status: int = Field(alias="runningStatus")
    session_name: Optional[str] = Field(alias="sessionName", default=None)
    start: datetime
    subject_id: Optional[int] = Field(alias="subjectId", default=None)
    subject_long_name: Optional[str] = Field(alias="subjectLongName", default=None)
    target_student_id: int = Field(alias="targetStudentId")
    teaching_days_only: bool = Field(alias="teachingDaysOnly")
    text_color: Optional[str] = Field(alias="textColor", default=None)
    title: str
    unavailable_pd: Optional[int] = Field(alias="unavailablePd", default=None)


class CompassUser(BaseModel):
    """Compass user details model."""

    model_config = ConfigDict(populate_by_name=True)

    type: str = Field(alias="__type", default="UserDetailsBlob")
    age: Optional[int] = Field(default=None)
    birthday: Optional[datetime] = Field(default=None)
    chronicle_pinned_count: int = Field(alias="chroniclePinnedCount")
    contextual_form_group: str = Field(alias="contextualFormGroup")
    date_of_death: Optional[datetime] = Field(alias="dateOfDeath", default=None)
    gender: Optional[str] = Field(default=None)
    has_email_restriction: bool = Field(alias="hasEmailRestriction")
    is_birthday: bool = Field(alias="isBirthday")
    user_act_student_id: Optional[str] = Field(alias="userACTStudentID", default=None)
    user_access_restrictions: Optional[str] = Field(
        alias="userAccessRestrictions", default=None
    )
    user_compass_person_id: str = Field(alias="userCompassPersonId")
    user_confirmation_photo_path: str = Field(alias="userConfirmationPhotoPath")
    user_details: Optional[str] = Field(alias="userDetails", default=None)
    user_display_code: str = Field(alias="userDisplayCode")
    user_email: str = Field(alias="userEmail")
    user_first_name: str = Field(alias="userFirstName")
    user_flags: list = Field(alias="userFlags", default_factory=list)
    user_form_group: Optional[str] = Field(alias="userFormGroup", default=None)
    user_full_name: str = Field(alias="userFullName")
    user_gender_pronouns: Optional[str] = Field(alias="userGenderPronouns", default=None)
    user_house: Optional[str] = Field(alias="userHouse", default=None)
    user_id: int = Field(alias="userId")
    user_last_name: str = Field(alias="userLastName")
    user_phone_extension: Optional[str] = Field(alias="userPhoneExtension", default=None)
    user_photo_path: str = Field(alias="userPhotoPath")
    user_preferred_last_name: str = Field(alias="userPreferredLastName")
    user_preferred_name: str = Field(alias="userPreferredName")
    user_report_name: str = Field(alias="userReportName")
    user_report_pref_first_last: str = Field(alias="userReportPrefFirstLast")
    user_role: int = Field(alias="userRole")
    user_role_in_school: Optional[str] = Field(alias="userRoleInSchool", default=None)
    user_school_id: str = Field(alias="userSchoolId")
    user_school_url: str = Field(alias="userSchoolURL")
    user_sex: Optional[str] = Field(alias="userSex", default=None)
    user_square_photo_path: str = Field(alias="userSquarePhotoPath")
    user_status: int = Field(alias="userStatus")
    user_sussi_id: str = Field(alias="userSussiID")
    user_time_line_periods: list = Field(
        alias="userTimeLinePeriods", default_factory=list
    )
    user_vsn: Optional[str] = Field(alias="userVSN", default=None)
    user_year_level: Optional[str] = Field(alias="userYearLevel", default=None)
    user_year_level_id: Optional[int] = Field(alias="userYearLevelId", default=None)
