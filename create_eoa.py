from eth_account import Account

Account.enable_unaudited_hdwallet_features()
acct, mnemonic = Account.create_with_mnemonic()
print(acct.address)
print(acct.key.hex())
print(mnemonic)
print(acct == Account.from_mnemonic(mnemonic))