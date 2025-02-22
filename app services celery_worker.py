from celery import Celery
from app.blockchain import TonProcessor, EVMProcessor
from app.models import Transaction, User
from app.core import db

celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)

@celery.task
def process_transaction(tx_hash: str, network: str):
    with db.app.app_context():
        transaction = Transaction.query.filter_by(tx_hash=tx_hash).first()
        if not transaction:
            return
        
        # بررسی وضعیت تراکنش
        if network == 'TON':
            processor = TonProcessor()
