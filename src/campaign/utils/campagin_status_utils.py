from src.campaign.model.campagin_status import CampaignStatus


def is_status_review_to_pending(from_status, to_status):
    return (from_status == CampaignStatus.review.value) and (
        to_status == CampaignStatus.pending.value
    )


def is_status_review_to_tempsave(from_status, to_status):
    return (from_status == CampaignStatus.review.value) and (
        to_status == CampaignStatus.tempsave.value
    )


def is_status_tempsave_to_review(from_status, to_status):
    return (from_status == CampaignStatus.tempsave.value) and (
        to_status == CampaignStatus.review.value
    )


def is_status_to_complete_or_expired(from_status, to_status):
    return (
        from_status
        in (
            CampaignStatus.ongoing.value,
            CampaignStatus.pending.value,
            CampaignStatus.haltbefore.value,
            CampaignStatus.haltafter.value,
        )
    ) and (
        (to_status == CampaignStatus.complete.value) or (to_status == CampaignStatus.expired.value)
    )


def is_status_haltafter_to_ongoing(from_status, to_status):
    return (from_status == CampaignStatus.haltafter.value) and (
        to_status == CampaignStatus.ongoing.value
    )


def is_status_modify_to_haltafter(from_status, to_status):
    return (from_status == CampaignStatus.modify.value) and (
        to_status == CampaignStatus.haltafter.value
    )


def is_status_haltafter_to_modify(from_status, to_status):
    return (from_status == CampaignStatus.haltafter.value) and (
        to_status == CampaignStatus.modify.value
    )


def is_status_haltbefore_to_tempsave(from_status, to_status):
    return (from_status == CampaignStatus.haltbefore.value) and (
        to_status == CampaignStatus.tempsave.value
    )


def is_status_haltbefore_to_pending(from_status, to_status):
    return (from_status == CampaignStatus.haltbefore.value) and (
        to_status == CampaignStatus.pending.value
    )


def is_status_ongoing_to_haltafter(from_status, to_status):
    return (from_status == CampaignStatus.ongoing.value) and (
        to_status == CampaignStatus.haltafter.value
    )


def is_status_pending_to_ongoing(from_status, to_status):
    return (from_status == CampaignStatus.pending.value) and (
        to_status == CampaignStatus.ongoing.value
    )


def is_status_pending_to_haltbefore(from_status, to_status):
    return (from_status == CampaignStatus.pending.value) and (
        to_status == CampaignStatus.haltbefore.value
    )
