from pydantic import BaseModel, Field


class Tier(BaseModel):
    id: int
    name: str
    min_points: int
    discount_percent: int
    birthday_bonus: int
    benefits: list[str]


class Member(BaseModel):
    id: int
    name: str
    phone: str
    birthday: str
    points: int
    tier_id: int
    tier_name: str
    discount_percent: int
    birthday_bonus: int
    benefits: list[str]
    created_at: str


class MemberCreate(BaseModel):
    name: str = Field(min_length=1, max_length=40)
    phone: str = Field(min_length=6, max_length=20)
    birthday: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")


class PointRule(BaseModel):
    id: int
    name: str
    description: str
    amount_per_point: float
    multiplier: float
    active: bool


class EarnPointsRequest(BaseModel):
    member_id: int
    amount: float = Field(gt=0)
    rule_id: int


class Gift(BaseModel):
    id: int
    name: str
    points_cost: int
    stock: int
    description: str
    active: bool


class RedeemGiftRequest(BaseModel):
    member_id: int
    gift_id: int


class Transaction(BaseModel):
    id: int
    member_id: int
    member_name: str | None = None
    type: str
    points: int
    note: str
    created_at: str


class Voucher(BaseModel):
    id: int
    member_id: int
    member_name: str | None = None
    title: str
    value: str
    status: str
    issued_at: str
    expires_at: str


class OperationResult(BaseModel):
    member: Member
    transaction: Transaction | None = None
    voucher: Voucher | None = None
    message: str


class Dashboard(BaseModel):
    members_count: int
    total_points: int
    gifts_count: int
    active_vouchers: int


class TierHistory(BaseModel):
    id: int
    member_id: int
    from_tier_id: int | None = None
    to_tier_id: int
    from_tier_name: str | None = None
    to_tier_name: str
    reason: str
    created_at: str


class MemberStats(BaseModel):
    total_spent: float
    total_points: int
    earn_count: int
    earn_points: int
    redeem_count: int
    redeem_points: int
    voucher_count: int
    unused_voucher_count: int


class MemberProfile(BaseModel):
    member: Member
    stats: MemberStats
    transactions: list[Transaction]
    vouchers: list[Voucher]
    tier_history: list[TierHistory]
