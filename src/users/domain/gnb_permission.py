
from pydantic import BaseModel


class ContentsManager(BaseModel):
    contents: list[str] = ["create", "read", "update", "delete"]
    contents_library: list[str] = ["create", "read", "update", "delete"]


class Dashboard(BaseModel):
    campaigns: list[str] | None = None
    trend_analysis: list[str] | None = None
    audience_analysis: list[str] | None = None


class UserSettings(BaseModel):
    templates: list[str] = ["read"]
    user: list[str] = ["read", "update"]
    offer: list[str] | None = None
    admin: list[str] | None = None


class GNBPermissions(BaseModel):
    campaign: list[str] = ["create", "read", "update", "delete"]
    strategy_manager: list[str] | None = None
    target_audience: list[str] = ["create", "read", "update", "delete"]
    dashboard: Dashboard = Dashboard()
    settings: UserSettings = UserSettings()
    contents_manager: ContentsManager | None = None
