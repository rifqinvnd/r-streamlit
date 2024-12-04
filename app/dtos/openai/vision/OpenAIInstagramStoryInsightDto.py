from pydantic import BaseModel, Field


class OpenAIInstagramStoryInsightDto(BaseModel):
    """This data is to describe every aspect of content image insights data"""
    views: int = Field(
        ...,
        description="Content view counts. Get the count from 'Views' or 'Tayangan' (if in Indonesian)."
    )
    views_follower_percentage: str = Field(
        ...,
        description="Content viewed by follower in percentage. Get the percentage from 'Followers' or 'Pengikut' (if in Indonesian)."
    )
    views_non_follower_percentage: str = Field(
        ...,
        description="Content viewed by non-follower in percentage. Get the percentage from 'Non-followers' or 'Bukan pengikut' (if in Indonesian)."
    )
    interactions: int = Field(
        ...,
        description="Content interaction counts. Get the count from 'Interactions' or 'Interaksi' (if in Indonesian)."
    )
    interactions_follower_percentage: str  = Field(
        ...,
        description="Content interaction by follower in percentage. Get the percentage from 'Followers' or 'Pengikut' (if in Indonesian)."
    )
    interactions_non_follower_percentage: str = Field(
        ...,
        description="Content interaction by non-follower in percentage. Get the percentage from 'Non-followers' or 'Bukan pengikut' (if in Indonesian)."
    )
    profile_activity: int = Field(
        ...,
        description="Content profile activity counts. Get the count from 'Profile activity' or 'Aktivitas profil' (if in Indonesian)."
    )
    accounts_reached: int = Field(
        ...,
        description="Content account's reached counts. Get the count from 'Accounts reached' or 'Akun yang dijangkau' (if in Indonesian)."
    )
    likes: int = Field(
        ...,
        description="Content like counts. Get the count from 'Likes' or 'Suka' (if in Indonesian)."
    )
    replies: int = Field(
        ...,
        description="Content reply counts. Get the count from 'Replies' or 'Balasan' (if in Indonesian)."
    )
    shares: int = Field(
        ...,
        description="Content share counts. Get the count from 'Shares' or 'Bagikan' (if in Indonesian)."
    )
    accounts_engaged: int = Field(
        ...,
        description="Content account's engaged counts. Get the count from 'Accounts engaged' or 'Akun yang berinteraksi' (if in Indonesian)."
    )
    forwards: int = Field(
        ...,
        description="Content Instagram story's forward counts. Get the count from 'Forwards' or 'Teruskan' (if in Indonesian)."
    )
    next_story: int = Field(
        ...,
        description="Content Instagram story's next counts. Get the count from 'Next story' or 'Cerita selanjutnya' (if in Indonesian)."
    )
    back: int = Field(
        ...,
        description="Content Instagram story's back counts. Get the count from 'Back' or 'Kembali' (if in Indonesian)."
    )
    exited: int = Field(
        ...,
        description="Content Instagram story's back counts. Get the count from 'Exited' or 'Keluar' (if in Indonesian)."
    )
    profile_visit: int = Field(
        ...,
        description="Content profile visit counts. Get the count from 'Profile visit' or 'Kunjungan profil' (if in Indonesian)."
    )
    follows: int = Field(
        ...,
        description="Content profile follow counts. Get the count from 'Follows' or 'Mengikuti' (if in Indonesian)."
    )
    link_clicks: int = Field(
        ...,
        description="Content link click counts. Get the count from 'Link clicks' or 'Klik tautan' (if in Indonesian)."
    )
    sticker_taps: int = Field(
        ...,
        description="Content sticker tap counts. Get the count from 'Sticker taps' or 'Ketukan stiker' (if in Indonesian)."
    )
