from src.campaign.infra.campaign_repository import CampaignRepository
from src.offer.infra.offer_repository import OfferRepository
from src.offer.model.request.offer_update import OfferUpdate
from src.offer.routes.port.update_offer_usecase import UpdateOfferUseCase
from src.user.domain.user import User


class UpdateOfferService(UpdateOfferUseCase):

    def __init__(self, offer_repository: OfferRepository, campaign_repository: CampaignRepository):
        self.offer_repository = offer_repository
        self.campaign_repository = campaign_repository

    def update_offer(self, offer_update: OfferUpdate, user: User):
        pass
