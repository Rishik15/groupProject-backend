from app.services.auth.getUser import getUserByEmail, getUserByGoogleSub
from app.services.auth.googleIdentity import createUserFromGoogle, linkGoogleIdentity


def resolve_or_create_google_user(
    google_sub: str,
    google_email: str,
    email_verified: bool,
    full_name: str | None,
):
    user = getUserByGoogleSub(google_sub)
    if user is not None:
        linkGoogleIdentity(
            user_id=user["user_id"],
            google_sub=google_sub,
            google_email=google_email,
            email_verified=email_verified,
        )
        return user

    existing_user = getUserByEmail(google_email)
    if existing_user is not None:
        linkGoogleIdentity(
            user_id=existing_user["user_id"],
            google_sub=google_sub,
            google_email=google_email,
            email_verified=email_verified,
        )
        return getUserByGoogleSub(google_sub)

    user_id = createUserFromGoogle(
        email=google_email,
        full_name=full_name,
        role=None,
    )

    linkGoogleIdentity(
        user_id=user_id,
        google_sub=google_sub,
        google_email=google_email,
        email_verified=email_verified,
    )

    return getUserByGoogleSub(google_sub)
