from src.campaign.infra.campaign_repository import CampaignRepository
from src.offers.infra.offer_repository import OfferRepository
from src.offers.routes.dto.request.offer_update import OfferUpdate
from src.offers.routes.port.update_offer_usecase import UpdateOfferUseCase
from src.users.domain.user import User


class UpdateOfferService(UpdateOfferUseCase):

    def __init__(self, offer_repository: OfferRepository, campaign_repository: CampaignRepository):
        self.offer_repository = offer_repository
        self.campaign_repository = campaign_repository

    def update_offer(self, offer_update: OfferUpdate, user: User):
        pass
