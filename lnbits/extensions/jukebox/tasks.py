import asyncio
import json
import httpx

from lnbits.core import db as core_db
from lnbits.core.models import Payment
from lnbits.tasks import register_invoice_listener

from .crud import get_jukebox, update_jukebox_payment


async def wait_for_paid_invoices():
    invoice_queue = asyncio.Queue()
    register_invoice_listener(invoice_queue)

    while True:
        payment = await invoice_queue.get()
        await on_invoice_paid(payment)


async def on_invoice_paid(payment: Payment) -> None:
    if "jukebox" != payment.extra.get("tag"):
        # not a jukebox invoice
        return
    await update_jukebox_payment(payment.payment_hash, paid=True)