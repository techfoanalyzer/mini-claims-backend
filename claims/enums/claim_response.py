from enum import StrEnum


class ClaimResponse(StrEnum):
    # Success messages
    CLAIM_201_CREATED = "Claim created successfully."
    CLAIM_DETAIL_FETCHED = "Claim fetched successfully."
    CLAIM_LIST_FETCHED = "Claims fetched successfully."
    PLR_SUBMITTED = "PLR submitted successfully."
    PLR_REVIEWED = "PLR reviewed successfully."
    PLR_APPROVED = "PLR approved successfully."
    PLR_SENT_BACK = "PLR sent back successfully."
    REPAIR_STARTED = "Repair started successfully."
    REPAIR_COMPLETED = "Repair completed successfully."
    CLAIM_CLOSED = "Claim closed successfully."

    # Failure messages
    CLAIM_403_NOT_YOURS = "This claim is not assigned to you."
    CLAIM_403_WRONG_ROLE = "Your role cannot perform this action."
    CLAIM_400_WRONG_STATUS = "This claim is not at a stage where that is allowed."
    CLAIM_400_INVALID_DECISION = "Invalid decision. Use 'forward'/'send_back' or 'approve'/'send_back'."
    CLAIM_404_NOT_FOUND = "Claim not found."
    CLAIM_400_MISSING_SURVEYOR = "A claim must have a surveyor assigned at creation."
    CLAIM_400_MISSING_WORKSHOP = "A claim must have a workshop assigned at creation."
    PLR_400_PHOTO_REQUIRED = "A damage photo is required."
    PLR_400_PHOTO_INVALID = "Only image files are allowed."
    PLR_400_PHOTO_TOO_LARGE = "Photo size must not exceed 5MB."