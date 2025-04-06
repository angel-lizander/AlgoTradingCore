import datetime
from TelegramBot.telegram_bot import sendMessage


def triggerPosition(Position, PositionType): 
        message =  '''Orden colocada
 <b>Order Type</b>:{PositionType}
 <b>Stop Loss</b>:{sl}
 <b>Take Profit</b>: {tp}
 <b>Open Price</b>: {op}'''.format(sl=Position.sl, tp=Position.tp, op=Position.price, PositionType=PositionType)
        sendMessage(message, 'HTML')
                      
def welcomebot(account, balance, profit: str):
        message =  '''Bot iniciado
                      <b>Account</b>:{account}
                      <b>Balance</b>: {balance}
                      <b>Profit</b>: {profit}'''.format(account=account, balance=balance, profit=profit)
        sendMessage(message, 'HTML')

def closetbot(history,account):

    from_date=datetime.now()
    to_date=datetime.timedelta(hours=9)

    history_orders=history(from_date,to_date)

    
    message =  '''Mercado cerrado
                      <b>Account</b>:{account}
                      <b>Balance</b>: {balance}
                      <b>Profit</b>: {profit}
                      <b>Today orders</b> {history_orders}
                      
                      '''.format(account=account.login, balance=account.balance, profit=account.profit, history_orders=history_orders)
    sendMessage(message, 'HTML')

def closetbot(account, balance, profit: str):
        message =  '''Day journal, bot has closed 
                      <b>Account</b>:{account}
                      <b>Balance</b>: {balance}
                      <b>Profit</b>: {profit}'''.format(account=account, balance=balance, profit=profit)
        sendMessage(message, 'HTML')


def sendInfo(account, mesasge: str):
        message =  '''Info
<b>Account</b>:{account}
{mesasge}'''.format(account=account, mesasge=mesasge)
        sendMessage(message, 'HTML')