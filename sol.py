from solana.rpc.api import Client
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import Transaction
from solders.system_program import transfer, TransferParams
from solders.message import Message
import base58
import json
import requests
import time
import os
import glob

# Use a more reliable RPC endpoint
RPC_ENDPOINTS = [
    "https://api.devnet.solana.com",
    "https://devnet.solana.com",
    "https://devnet.genesysgo.net",
    "https://devnet.api.rpcpool.com"
]

# Initialize with first endpoint
current_endpoint_index = 0
client = Client(RPC_ENDPOINTS[current_endpoint_index])

def switch_rpc_endpoint():
    """Switch to next RPC endpoint if current one fails"""
    global client, current_endpoint_index
    current_endpoint_index = (current_endpoint_index + 1) % len(RPC_ENDPOINTS)
    new_endpoint = RPC_ENDPOINTS[current_endpoint_index]
    print(f"Switching RPC endpoint to: {new_endpoint}")
    client = Client(new_endpoint)

def load_keypair(filename):
    """Load a keypair from a JSON file"""
    with open(filename, 'r') as f:
        private_key_bytes = json.load(f)
    return Keypair.from_bytes(bytes(private_key_bytes))

def get_balance(pubkey: Pubkey) -> float:
    """Get the balance of an account in SOL"""
    global client
    try:
        response = client.get_balance(pubkey)
        return response.value / 1_000_000_000  # Convert lamports to SOL
    except Exception as e:
        print(f"Error getting balance, switching RPC endpoint: {e}")
        switch_rpc_endpoint()
        response = client.get_balance(pubkey)
        return response.value / 1_000_000_000

def request_airdrop(pubkey: Pubkey, amount: float = 0.5) -> str:
    """Request SOL from the devnet faucet"""
    global client
    print(f"Requesting {amount} SOL from devnet faucet...")
    
    # Try multiple times with different amounts
    amounts_to_try = [0.5, 0.5, 0.5]  # Try 0.5 SOL multiple times instead of larger amounts
    
    for try_amount in amounts_to_try:
        try:
            print(f"Trying to request {try_amount} SOL...")
            # Try the RPC airdrop first
            response = client.request_airdrop(pubkey, int(try_amount * 1_000_000_000))
            if response.value:
                print(f"Successfully requested {try_amount} SOL")
                return response.value
        except Exception as e:
            print(f"RPC airdrop failed for {try_amount} SOL: {e}")
            # Switch RPC endpoint on failure
            switch_rpc_endpoint()
            time.sleep(2)  # Wait before next attempt
    
    # If RPC airdrop fails, try the public faucet
    for try_amount in amounts_to_try:
        try:
            print(f"Trying public faucet for {try_amount} SOL...")
            url = f"https://api.devnet.solana.com/airdrop/{pubkey}/{int(try_amount * 1_000_000_000)}"
            response = requests.post(url)
            if response.status_code == 200:
                print(f"Successfully requested {try_amount} SOL from public faucet")
                return response.json()["signature"]
        except Exception as e:
            print(f"Public faucet request failed for {try_amount} SOL: {e}")
            time.sleep(2)  # Wait before next attempt
    
    raise Exception("Failed to request airdrop from both RPC and public faucet")

def wait_for_confirmation(signature: str, max_retries: int = 30):
    """Wait for transaction confirmation"""
    global client
    print(f"Waiting for confirmation of signature: {signature}")
    for i in range(max_retries):
        try:
            response = client.get_signature_statuses([signature])
            if response.value[0] is not None:
                print("Transaction confirmed!")
                return True
            print(f"Waiting... ({i+1}/{max_retries})")
            time.sleep(2)  # Increased wait time
        except Exception as e:
            print(f"Error checking confirmation: {e}")
            switch_rpc_endpoint()
            time.sleep(2)
    return False

def initialize_faucets():
    """Initialize all faucets with airdrops"""
    print("\nInitializing faucets with airdrops...")
    
    # Create faucets directory if it doesn't exist
    if not os.path.exists('faucets'):
        os.makedirs('faucets')
    
    # Get all faucet files
    faucet_files = glob.glob('faucets/faucet_*.json')
    if not faucet_files:
        print("No faucet files found. Please run generate_faucets.py first.")
        return False
    
    # Request airdrops for each faucet
    for faucet_file in faucet_files:
        try:
            print(f"\nProcessing {faucet_file}...")
            keypair = load_keypair(faucet_file)
            balance = get_balance(keypair.pubkey())
            print(f"Current balance: {balance} SOL")
            
            if balance < 1.0:  # Request airdrop if balance is less than 1 SOL
                print(f"Requesting airdrop for {faucet_file}...")
                signature = request_airdrop(keypair.pubkey())
                if wait_for_confirmation(signature):
                    new_balance = get_balance(keypair.pubkey())
                    print(f"New balance: {new_balance} SOL")
                    
                    # If still below 1 SOL, try one more time
                    if new_balance < 1.0:
                        print("Requesting additional airdrop...")
                        time.sleep(5)  # Wait longer between multiple airdrops
                        signature = request_airdrop(keypair.pubkey())
                        if wait_for_confirmation(signature):
                            final_balance = get_balance(keypair.pubkey())
                            print(f"Final balance: {final_balance} SOL")
                else:
                    print(f"Failed to confirm airdrop for {faucet_file}")
            else:
                print(f"Sufficient balance in {faucet_file}")
            
            time.sleep(5)  # Increased wait time between faucets to avoid rate limits
            
        except Exception as e:
            print(f"Error processing {faucet_file}: {e}")
            continue
    
    return True

def find_available_faucet(amount_sol: float):
    """Find a faucet with sufficient balance"""
    # First try the current faucet
    if os.path.exists('faucet.json'):
        try:
            keypair = load_keypair('faucet.json')
            balance = get_balance(keypair.pubkey())
            if balance >= amount_sol:
                print(f"Using current faucet with balance: {balance} SOL")
                return keypair
        except Exception as e:
            print(f"Error with current faucet: {e}")

    # Try faucets in the faucets directory
    if os.path.exists('faucets'):
        faucet_files = glob.glob('faucets/faucet_*.json')
        for faucet_file in faucet_files:
            try:
                keypair = load_keypair(faucet_file)
                balance = get_balance(keypair.pubkey())
                print(f"Checking {faucet_file}: {balance} SOL")
                if balance >= amount_sol:
                    print(f"Found faucet with sufficient balance: {balance} SOL")
                    return keypair
            except Exception as e:
                print(f"Error checking {faucet_file}: {e}")
                continue

    # If no faucet has enough balance, try to get airdrop for the current faucet
    if os.path.exists('faucet.json'):
        try:
            keypair = load_keypair('faucet.json')
            print("Trying to get airdrop for current faucet...")
            signature = request_airdrop(keypair.pubkey())
            if wait_for_confirmation(signature):
                balance = get_balance(keypair.pubkey())
                if balance >= amount_sol:
                    print(f"Successfully got airdrop. New balance: {balance} SOL")
                    return keypair
        except Exception as e:
            print(f"Error getting airdrop: {e}")

    raise Exception("No faucet available with sufficient balance")

def send_sol(destination: str, amount_sol: float):
    # Find a faucet with sufficient balance
    faucet_keypair = find_available_faucet(amount_sol)
    
    pubkey_dest = Pubkey.from_string(destination)
    lamports = int(amount_sol * 1_000_000_000)  # 1 SOL = 1e9 lamports

    # Get the latest blockhash
    recent_blockhash = client.get_latest_blockhash().value.blockhash

    # Create the message
    message = Message.new_with_blockhash(
        instructions=[
            transfer(
                TransferParams(
                    from_pubkey=faucet_keypair.pubkey(),
                    to_pubkey=pubkey_dest,
                    lamports=lamports
                )
            )
        ],
        payer=faucet_keypair.pubkey(),
        blockhash=recent_blockhash
    )
    
    # Create and sign the transaction
    txn = Transaction(
        from_keypairs=[faucet_keypair],
        message=message,
        recent_blockhash=recent_blockhash
    )

    # Convert transaction to bytes and send
    txn_bytes = bytes(txn)
    response = client.send_raw_transaction(txn_bytes)
    return response

def main():
    print("Solana Devnet SOL Transfer")
    print("-------------------------")
    
    # Initialize faucets with airdrops
    if not initialize_faucets():
        print("Failed to initialize faucets. Please check the error messages above.")
        return
    
    # Get destination wallet
    while True:
        to_wallet = input("\nEnter destination wallet address: ").strip()
        try:
            # Validate the wallet address
            Pubkey.from_string(to_wallet)
            break
        except Exception as e:
            print("Invalid wallet address. Please try again.")
    
    # Get amount to send
    while True:
        try:
            amount = float(input("Enter amount of SOL to send: ").strip())
            if amount <= 0:
                print("Amount must be greater than 0")
                continue
            break
        except ValueError:
            print("Invalid amount. Please enter a number.")
    
    print("\nSending transaction...")
    try:
        response = send_sol(to_wallet, amount)
        print("\nTransaction sent successfully!")
        print(f"Transaction signature: {response}")
    except Exception as e:
        print(f"\nError sending transaction: {e}")

if __name__ == "__main__":
    main()
