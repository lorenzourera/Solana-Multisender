import time

from solana.rpc.api import Client
from spl.token.client import Token
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from spl.token.constants import TOKEN_PROGRAM_ID

from solana.transaction import Transaction
from spl.token.instructions import TransferParams, transfer
from solana.rpc.types import TxOpts

import random
import json



class TokenMap:
    CONTRACT_TOKEN_MAP = {
        'JUP': {
            'token_address': Pubkey.from_string('JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN'),
            'program_id': TOKEN_PROGRAM_ID
        },
        'USDC': {
            'token_address': Pubkey.from_string('EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'),
            'program_id': TOKEN_PROGRAM_ID
        },
        'WSOL': {
            'token_address': Pubkey.from_string('So11111111111111111111111111111111111111112'),
            'program_id': TOKEN_PROGRAM_ID
        },
    }


class SendTokens:

    def __init__(self, private_key: str, address_to: str, amount: float):

        self.client = Client("https://api.mainnet-beta.solana.com")
        self.private_key = Keypair.from_base58_string(private_key)
        self.address_to = Pubkey.from_string(address_to)
        self.amount = amount

    def made_tx(self, token: str, max_attempts=3):

        token_address = TokenMap.CONTRACT_TOKEN_MAP[token.upper()]['token_address']
        program_id = TokenMap.CONTRACT_TOKEN_MAP[token.upper()]['program_id']

        spl_client = Token(conn=self.client, pubkey=token_address, program_id=program_id, payer=self.private_key)

        amount = int(self.amount * 10 ** spl_client.get_mint_info().decimals)
        source_token_account = spl_client.get_accounts_by_owner(owner=self.private_key.pubkey(), commitment=None, encoding='base64').value[0].pubkey

        accounts = spl_client.get_accounts_by_owner(
            owner=self.address_to,
            commitment=None,
            encoding='base64'
        ).value

        if accounts:
            dest_account = accounts[0].pubkey
        else:
            print(f'Not find token address for {self.address_to}')
            for attempt in range(1, max_attempts + 1):
                try:
                    dest_account = spl_client.create_associated_token_account(owner=self.address_to,
                                                                              skip_confirmation=False,
                                                                              recent_blockhash=None)
                    time.sleep(random.randint(12, 20))
                    print(f'Successfully created account {dest_account} for {token}| Owner: {self.address_to}')
                    break  # Exit the loop if account creation was successful
                except Exception as e:
                    if attempt < max_attempts:
                        print(f'Attempt {attempt} failed. Retrying...')
                        time.sleep(random.randint(25, 40))
                    else:
                        print(f'Failed to create account after {max_attempts} attempts.')
                        return f'Failed to create account for {self.address_to}. Error: {str(e)}'

        opts_to_use = TxOpts(preflight_commitment=self.client.commitment)
        txn, signers, opts = spl_client._transfer_args(
            source=source_token_account,
            dest=dest_account,
            owner=self.private_key,
            amount=int(amount),
            multi_signers=None,
            opts=opts_to_use
        )

        receipt = self.client.send_transaction(txn, *signers, opts=opts, recent_blockhash=None)
        json_receipt = receipt.to_json()
        tx_hash = json.loads(json_receipt)["result"]

        time.sleep(random.randint(30, 45))
        if receipt:
            return f'Success {self.amount} {token} send  to {self.address_to}| Tx: https://solscan.io/tx/{tx_hash}'
        else:
            return f'Not get receipt, no transaction for {self.address_to}'
