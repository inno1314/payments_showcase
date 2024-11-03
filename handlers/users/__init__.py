__all__ = ("router",)

from aiogram import Router

from .pay import router as pay_router
from .user_info import router as info_router
from .any import router as any_router


router = Router(name=__name__)

router.include_routers(pay_router, info_router, any_router)
