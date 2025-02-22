from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.blockchain import EVMProcessor, TonProcessor
from app.services.conversion import CurrencyConverter
from app.models import Transaction
from app.core import db
from app.services.celery_worker import process_transaction

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/process-payment', methods=['POST'])
@jwt_required()
def process_payment():
    data = request.get_json()
    
    # تبدیل ارز به USDT
    try:
        usdt_amount = CurrencyConverter.to_usdt(data['amount'], data['currency'])
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
    # ایجاد تراکنش در بلاکچین
    if data['network'] == 'TON':
        processor = TonProcessor()
        tx_hash = processor.transfer(data['wallet'], usdt_amount)
    else:
        processor = EVMProcessor(network=data['network'])
        tx_hash = processor.transfer_erc20(
            data['wallet'],
            usdt_amount,
            Config.CONTRACT_ADDRESSES[data['currency']]
        )
    
    # ذخیره در دیتابیس
    transaction = Transaction(
        user_id=data['user_id'],
        tx_hash=tx_hash,
        amount=usdt_amount,
        currency=data['currency'],
        network=data['network']
    )
    db.session.add(transaction)
    db.session.commit()
    
    # شروع پردازش ناهمزمان
    process_transaction.delay(tx_hash, data['network'])
    
    return jsonify({'tx_hash': tx_hash}), 202
