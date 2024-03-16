from send_tokens import SendTokens
import time
import random


def app():
    with open('address_multisend.txt', 'r') as file:
        success_send = 0
        fail_send = 0
        failed_wallets = []

        for address in file:
            res = SendTokens(
                private_key='PrivateKey',
                address_to=address.rstrip(),
                amount=0.02,
            ).made_tx(token='USDC')
            print(res)
            if 'Success' in res:
                success_send += 1
            else:
                fail_send += 1
                failed_wallets.append(address.rstrip())

    if failed_wallets:
        with open('failed_wallets.txt', 'w') as file:  # Исправлено здесь, добавлен контекстный менеджер
            for wallet in failed_wallets:
                file.write(wallet + '\n')
        return f'Success amount wallet: {success_send} | Not success : {fail_send} | Check failed_wallets.txt'
    return f'Success all wallets!'


if __name__ == '__main__':
    print('Start now')
    time.sleep(random.randint(5,10))
    print(app())
